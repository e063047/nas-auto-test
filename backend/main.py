import sys
import os
import json
import asyncio
import time
import base64
import xml.etree.ElementTree as ET
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional

from ws_manager import manager
from scanner import discover_nas
from executor import executor, State
from test_registry import TEST_TREE

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
REPORTS_DIR = Path(__file__).parent.parent / "reports"
SCREENSHOT_DIR = REPORTS_DIR / "screenshots"
DEMO_SCREENSHOT_DIR = Path(__file__).parent.parent / "demo" / "screenshots"
REPORTS_DIR.mkdir(exist_ok=True)
SCREENSHOT_DIR.mkdir(exist_ok=True)

app = FastAPI(title="NAS Auto Test Dashboard")

# ── Static frontend files ──────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/")
async def root():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


# ── WebSocket ──────────────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        # Send current state immediately on connect
        await ws.send_json({"event": "state", "data": executor.state.value})
        while True:
            await ws.receive_text()   # keep connection alive; client sends pings
    except WebSocketDisconnect:
        manager.disconnect(ws)


# ── NAS Discovery ──────────────────────────────────────────────────────────────

@app.get("/api/scan")
async def scan_nas(subnet: Optional[str] = None):
    """Trigger LAN scan. Returns list of discovered NAS devices."""
    await manager.broadcast({"event": "log", "data": {
        "ts": time.strftime("%H:%M:%S"), "level": "INFO",
        "msg": f"Starting LAN scan{f' on {subnet}.*' if subnet else ' (ARP only)'}..."
    }})
    devices = await discover_nas(subnet_prefix=subnet)
    await manager.broadcast({"event": "log", "data": {
        "ts": time.strftime("%H:%M:%S"), "level": "INFO",
        "msg": f"Scan complete. Found {len(devices)} NAS device(s)."
    }})
    return {"devices": devices}


# ── Test Tree ──────────────────────────────────────────────────────────────────

@app.get("/api/test-tree")
async def get_test_tree():
    return TEST_TREE


# ── Execution Control ──────────────────────────────────────────────────────────

class StartPayload(BaseModel):
    nas_ip: str
    nas_user: str
    nas_pass: str
    ssh_user: str = ""   # SSH account (may differ from web admin, e.g. 'sshd' on WD NAS)
    test_ids: List[str]
    demo: bool = False   # Demo mode: replay pre-recorded results without real NAS


@app.post("/api/start")
async def start_tests(payload: StartPayload):
    if executor.state == State.RUNNING:
        raise HTTPException(status_code=409, detail="Tests already running")
    if not payload.demo:
        import test_registry
        test_registry.SSH_USER = payload.ssh_user or payload.nas_user
    await executor.start(
        payload.nas_ip, payload.nas_user, payload.nas_pass, payload.test_ids,
        demo=payload.demo
    )
    return {"status": "started", "count": len(payload.test_ids), "demo": payload.demo}


@app.post("/api/pause")
async def pause_tests():
    if executor.state != State.RUNNING:
        raise HTTPException(status_code=409, detail="Not running")
    executor.pause()
    return {"status": "pause_requested"}


@app.post("/api/resume")
async def resume_tests():
    if executor.state != State.PAUSED:
        raise HTTPException(status_code=409, detail="Not paused")
    await executor.resume()
    return {"status": "resumed"}


@app.post("/api/abort")
async def abort_tests():
    executor.abort()
    return {"status": "aborted"}


@app.get("/api/status")
async def get_status():
    return {
        "state": executor.state.value,
        "results": executor.results,
    }


# ── Report Generation ──────────────────────────────────────────────────────────

# ── Screenshot serving ─────────────────────────────────────────────────────────

@app.get("/api/screenshot/{test_id}")
async def get_screenshot(test_id: str):
    # Check live screenshots first, fall back to pre-recorded demo screenshots
    path = SCREENSHOT_DIR / f"{test_id}.png"
    if not path.exists():
        path = DEMO_SCREENSHOT_DIR / f"{test_id}.png"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Screenshot not found")
    return FileResponse(str(path), media_type="image/png")


def _screenshot_b64(filename: Optional[str]) -> Optional[str]:
    if not filename:
        return None
    path = SCREENSHOT_DIR / filename
    if not path.exists():
        path = DEMO_SCREENSHOT_DIR / filename
    if not path.exists():
        return None
    return base64.b64encode(path.read_bytes()).decode()


# ── Report helpers ─────────────────────────────────────────────────────────────

def _build_html_report(results, nas_ip: str, with_screenshots: bool = True) -> str:
    passed = sum(1 for r in results if r["result"] == "PASS")
    failed = sum(1 for r in results if r["result"] == "FAIL")
    total = len(results)
    ts = time.strftime("%Y-%m-%d %H:%M:%S")

    rows = ""
    for r in results:
        color = {"PASS": "#2ecc71", "FAIL": "#e74c3c", "SKIP": "#f39c12", "ERROR": "#e74c3c"}.get(r["result"], "#999")
        ss_html = ""
        if with_screenshots and r.get("screenshot"):
            b64 = _screenshot_b64(r["screenshot"])
            if b64:
                ss_html = f'<br><img src="data:image/png;base64,{b64}" style="max-width:100%;border-radius:6px;margin-top:8px;border:1px solid #ddd" />'
        rows += f"""
        <tr>
          <td style="font-weight:600;white-space:nowrap">{r['id']}</td>
          <td style="color:{color};font-weight:bold;white-space:nowrap">{r['result']}</td>
          <td style="white-space:nowrap">{r['duration']}s</td>
          <td style="white-space:pre-wrap;font-size:12px">{r['msg'][:400]}{ss_html}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <title>NAS Auto Test Report - {ts}</title>
  <style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 32px; background: #f5f6fa; color: #2c3e50; }}
    h1 {{ color: #2c3e50; }}
    .summary {{ display:flex; gap:24px; margin-bottom:24px; flex-wrap:wrap; }}
    .card {{ background:#fff; border-radius:8px; padding:20px 32px; box-shadow:0 2px 8px rgba(0,0,0,.08); text-align:center; min-width:120px; }}
    .card .num {{ font-size:2.5em; font-weight:bold; }}
    .pass {{ color:#2ecc71; }} .fail {{ color:#e74c3c; }} .total {{ color:#3498db; }}
    table {{ width:100%; border-collapse:collapse; background:#fff; border-radius:8px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,.08); }}
    th {{ background:#2c3e50; color:#fff; padding:12px 16px; text-align:left; }}
    td {{ padding:10px 16px; border-bottom:1px solid #ecf0f1; vertical-align:top; }}
    tr:last-child td {{ border-bottom:none; }}
    tr:hover {{ background:#f8f9fa; }}
    .footer {{ margin-top:24px; color:#7f8c8d; font-size:13px; text-align:center; }}
  </style>
</head>
<body>
  <h1>NAS Automation Test Report</h1>
  <p>Device: <b>{nas_ip}</b> &nbsp;|&nbsp; Generated: {ts}</p>
  <div class="summary">
    <div class="card"><div class="num total">{total}</div><div>Total</div></div>
    <div class="card"><div class="num pass">{passed}</div><div>PASS</div></div>
    <div class="card"><div class="num fail">{failed}</div><div>FAIL</div></div>
    <div class="card"><div class="num" style="color:#f39c12">{total - passed - failed}</div><div>OTHER</div></div>
  </div>
  <table>
    <thead><tr><th>Test ID</th><th>Result</th><th>Duration</th><th>Message / Screenshot</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <div class="footer">NAS Auto Test Framework &mdash; WD My Cloud EX2 Ultra</div>
</body>
</html>"""


# ── Report endpoints ───────────────────────────────────────────────────────────

@app.get("/api/report/html")
async def download_html_report():
    if not executor.results:
        raise HTTPException(status_code=404, detail="No results available")
    html = _build_html_report(executor.results, executor.nas_ip, with_screenshots=True)
    report_path = REPORTS_DIR / f"report_{time.strftime('%Y%m%d_%H%M%S')}.html"
    report_path.write_text(html, encoding="utf-8")
    return FileResponse(str(report_path), media_type="text/html", filename=report_path.name)


@app.get("/api/report/pdf")
async def download_pdf_report():
    """Generate PDF by rendering the HTML report through headless Chromium."""
    if not executor.results:
        raise HTTPException(status_code=404, detail="No results available")

    from playwright.async_api import async_playwright

    html = _build_html_report(executor.results, executor.nas_ip, with_screenshots=True)
    html_path = REPORTS_DIR / f"_tmp_report.html"
    html_path.write_text(html, encoding="utf-8")

    pdf_path = REPORTS_DIR / f"report_{time.strftime('%Y%m%d_%H%M%S')}.pdf"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"file://{html_path.resolve()}", timeout=15000)
        await page.wait_for_load_state("networkidle")
        await page.pdf(path=str(pdf_path), format="A4", print_background=True,
                       margin={"top": "20mm", "bottom": "20mm", "left": "15mm", "right": "15mm"})
        await browser.close()

    html_path.unlink(missing_ok=True)
    return FileResponse(str(pdf_path), media_type="application/pdf", filename=pdf_path.name)


@app.get("/api/report/junit")
async def download_junit_report():
    """Generate JUnit XML for CI/CD integration."""
    if not executor.results:
        raise HTTPException(status_code=404, detail="No results available")

    results = executor.results
    passed = sum(1 for r in results if r["result"] == "PASS")
    failed = sum(1 for r in results if r["result"] != "PASS")
    total_time = sum(r["duration"] for r in results)
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")

    suite = ET.Element("testsuite", {
        "name": f"NAS Auto Test - {executor.nas_ip}",
        "tests": str(len(results)),
        "failures": str(failed),
        "errors": "0",
        "time": str(round(total_time, 2)),
        "timestamp": ts,
    })

    for r in results:
        tc = ET.SubElement(suite, "testcase", {
            "name": r["id"],
            "classname": r["id"].split("-")[0],
            "time": str(r["duration"]),
        })
        if r["result"] in ("FAIL", "ERROR"):
            failure = ET.SubElement(tc, "failure" if r["result"] == "FAIL" else "error",
                                    {"message": r["msg"][:200]})
            failure.text = r["msg"]
        if r.get("screenshot"):
            props = ET.SubElement(tc, "properties")
            prop = ET.SubElement(props, "property", {
                "name": "screenshot",
                "value": f"/api/screenshot/{r['id']}"
            })

    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(suite, encoding="unicode")
    xml_path = REPORTS_DIR / f"report_{time.strftime('%Y%m%d_%H%M%S')}.xml"
    xml_path.write_text(xml_str, encoding="utf-8")
    return FileResponse(str(xml_path), media_type="application/xml", filename=xml_path.name)


@app.get("/api/report/json")
async def download_json_report():
    if not executor.results:
        raise HTTPException(status_code=404, detail="No results available")
    return JSONResponse({
        "device": executor.nas_ip,
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total": len(executor.results),
            "pass": sum(1 for r in executor.results if r["result"] == "PASS"),
            "fail": sum(1 for r in executor.results if r["result"] == "FAIL"),
        },
        "results": [
            {**r, "screenshot_url": f"/api/screenshot/{r['id']}" if r.get("screenshot") else None}
            for r in executor.results
        ]
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
