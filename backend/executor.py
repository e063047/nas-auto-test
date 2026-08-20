import asyncio
import sys
import time
import traceback
from enum import Enum
from typing import List, Dict, Any, Optional

sys.path.insert(0, '/Users/winnielee/Library/Python/3.9/lib/python/site-packages')

from ws_manager import manager


class State(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    ABORTED = "ABORTED"
    COMPLETED = "COMPLETED"


class TestResult(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"


class Executor:
    def __init__(self):
        self.state = State.IDLE
        self._pause_flag = False
        self._abort_flag = False
        self._current_task: Optional[asyncio.Task] = None
        self.results: List[Dict] = []
        self.nas_ip: str = ""
        self.nas_user: str = ""
        self.nas_pass: str = ""

    # ── State helpers ──────────────────────────────────────────────────────

    async def _emit(self, event: str, data: Any = None):
        await manager.broadcast({"event": event, "data": data})

    async def _log(self, msg: str, level: str = "INFO"):
        ts = time.strftime("%H:%M:%S")
        await manager.broadcast({"event": "log", "data": {"ts": ts, "level": level, "msg": msg}})

    async def _set_state(self, state: State):
        self.state = state
        await self._emit("state", state.value)

    # ── Control API ────────────────────────────────────────────────────────

    async def start(self, nas_ip: str, nas_user: str, nas_pass: str, test_ids: List[str], demo: bool = False):
        if self.state == State.RUNNING:
            return
        self.nas_ip = nas_ip
        self.nas_user = nas_user
        self.nas_pass = nas_pass
        self._pause_flag = False
        self._abort_flag = False
        self.results = []
        await self._set_state(State.RUNNING)
        if demo:
            self._current_task = asyncio.create_task(self._run_demo(test_ids))
        else:
            self._current_task = asyncio.create_task(self._run_suite(test_ids))

    def pause(self):
        """Graceful pause: set flag, current test case will finish first."""
        if self.state == State.RUNNING:
            self._pause_flag = True

    async def resume(self):
        if self.state == State.PAUSED:
            self._pause_flag = False
            await self._set_state(State.RUNNING)

    def abort(self):
        self._abort_flag = True
        self._pause_flag = False
        if self._current_task:
            self._current_task.cancel()

    # ── Runner ─────────────────────────────────────────────────────────────

    async def _run_suite(self, test_ids: List[str]):
        from test_registry import TEST_REGISTRY

        total = len(test_ids)
        await self._emit("progress", {"current": 0, "total": total})
        await self._log(f"Starting suite: {total} test cases on {self.nas_ip}")

        try:
            for idx, tid in enumerate(test_ids):
                # ── Abort check ──
                if self._abort_flag:
                    await self._log("Suite aborted by user.", "WARN")
                    await self._set_state(State.ABORTED)
                    return

                # ── Graceful pause: wait here between test cases ──
                if self._pause_flag:
                    await self._set_state(State.PAUSED)
                    await self._log("Suite paused. Waiting for resume...", "WARN")
                    while self._pause_flag and not self._abort_flag:
                        await asyncio.sleep(0.5)
                    if self._abort_flag:
                        await self._log("Suite aborted during pause.", "WARN")
                        await self._set_state(State.ABORTED)
                        return
                    await self._set_state(State.RUNNING)
                    await self._log("Suite resumed.", "INFO")

                test_fn = TEST_REGISTRY.get(tid)
                if not test_fn:
                    await self._log(f"[SKIP] {tid}: not found in registry", "WARN")
                    self.results.append({"id": tid, "result": TestResult.SKIP, "msg": "not in registry", "duration": 0})
                    continue

                await self._log(f"[RUN ] ({idx+1}/{total}) {tid}")
                await self._emit("current_test", {"id": tid, "index": idx + 1, "total": total})

                t0 = time.monotonic()
                result, msg, screenshot = TestResult.ERROR, "", None
                try:
                    ret = await test_fn(self.nas_ip, self.nas_user, self.nas_pass)
                    if len(ret) == 3:
                        result, msg, screenshot = ret
                    else:
                        result, msg = ret
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    msg = traceback.format_exc()
                    result = TestResult.ERROR
                finally:
                    duration = round(time.monotonic() - t0, 2)

                self.results.append({
                    "id": tid, "result": result, "msg": msg,
                    "duration": duration, "screenshot": screenshot
                })
                level = "INFO" if result == TestResult.PASS else "ERROR"
                await self._log(f"[{result.value}] {tid} ({duration}s) {msg}", level)
                await self._emit("progress", {"current": idx + 1, "total": total})

        except asyncio.CancelledError:
            await self._set_state(State.ABORTED)
            return

        passed = sum(1 for r in self.results if r["result"] == TestResult.PASS)
        failed = sum(1 for r in self.results if r["result"] == TestResult.FAIL)
        await self._log(f"Suite complete. PASS={passed} FAIL={failed} TOTAL={total}")
        await self._set_state(State.COMPLETED)
        await self._emit("results", self.results)

    # ── Demo Runner ────────────────────────────────────────────────────────

    async def _run_demo(self, test_ids: List[str]):
        """Simulate test execution using pre-recorded results. No NAS required."""
        from demo_results import DEMO_MAP

        total = len(test_ids)
        await self._emit("progress", {"current": 0, "total": total})
        await self._log(f"[DEMO MODE] Replaying {total} pre-recorded results (no NAS connection)")

        try:
            for idx, tid in enumerate(test_ids):
                if self._abort_flag:
                    await self._log("Demo aborted by user.", "WARN")
                    await self._set_state(State.ABORTED)
                    return

                if self._pause_flag:
                    await self._set_state(State.PAUSED)
                    await self._log("Demo paused. Waiting for resume...", "WARN")
                    while self._pause_flag and not self._abort_flag:
                        await asyncio.sleep(0.5)
                    if self._abort_flag:
                        await self._set_state(State.ABORTED)
                        return
                    await self._set_state(State.RUNNING)
                    await self._log("Demo resumed.", "INFO")

                await self._emit("current_test", {"id": tid, "index": idx + 1, "total": total})
                await self._log(f"[RUN ] ({idx+1}/{total}) {tid}")

                rec = DEMO_MAP.get(tid)
                if rec:
                    # Simulate realistic execution time (capped at 2s for demo)
                    delay = min(rec["duration"] * 0.3, 2.0)
                    await asyncio.sleep(delay)
                    result  = TestResult(rec["result"])
                    msg     = rec["msg"]
                    screenshot = f"{tid}.png"
                    duration = rec["duration"]
                else:
                    await asyncio.sleep(0.5)
                    result, msg, screenshot, duration = TestResult.SKIP, "Not in demo dataset", None, 0

                self.results.append({
                    "id": tid, "result": result, "msg": msg,
                    "duration": duration, "screenshot": screenshot
                })
                level = "INFO" if result == TestResult.PASS else "ERROR"
                await self._log(f"[{result.value}] {tid} ({duration}s) {msg}", level)
                await self._emit("progress", {"current": idx + 1, "total": total})

        except asyncio.CancelledError:
            await self._set_state(State.ABORTED)
            return

        passed = sum(1 for r in self.results if r["result"] == TestResult.PASS)
        failed = sum(1 for r in self.results if r["result"] == TestResult.FAIL)
        await self._log(f"[DEMO] Complete. PASS={passed} FAIL={failed} TOTAL={total}")
        await self._set_state(State.COMPLETED)
        await self._emit("results", self.results)


executor = Executor()
