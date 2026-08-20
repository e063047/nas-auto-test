// ── State ──────────────────────────────────────────────────────────────────────
let ws = null;
let testTree = {};
let resultMap = {};
let currentState = "IDLE";

// ── WebSocket ──────────────────────────────────────────────────────────────────
function connectWS() {
  ws = new WebSocket(`ws://${location.host}/ws`);

  ws.onopen = () => {
    document.getElementById("ws-dot").classList.add("connected");
    appendLog("INFO", "WebSocket 已連線");
  };

  ws.onclose = () => {
    document.getElementById("ws-dot").classList.remove("connected");
    appendLog("WARN", "WebSocket 斷線，5 秒後重連...");
    setTimeout(connectWS, 5000);
  };

  ws.onerror = () => appendLog("ERROR", "WebSocket 錯誤");

  ws.onmessage = (evt) => {
    const msg = JSON.parse(evt.data);
    switch (msg.event) {
      case "state":       handleStateChange(msg.data);   break;
      case "log":         handleLog(msg.data);            break;
      case "progress":    handleProgress(msg.data);       break;
      case "results":     handleResults(msg.data);        break;
      case "current_test": handleCurrentTest(msg.data);  break;
    }
  };
}

// ── Keep-alive ping ────────────────────────────────────────────────────────────
setInterval(() => { if (ws && ws.readyState === WebSocket.OPEN) ws.send("ping"); }, 20000);

// ── State Machine ──────────────────────────────────────────────────────────────
function handleStateChange(state) {
  currentState = state;
  const badge = document.getElementById("state-badge");
  badge.textContent = state;
  badge.className = `state-${state}`;

  const s = document.getElementById("btn-start");
  const p = document.getElementById("btn-pause");
  const r = document.getElementById("btn-resume");
  const a = document.getElementById("btn-abort");

  s.disabled = (state === "RUNNING" || state === "PAUSED");
  p.disabled = (state !== "RUNNING");
  r.disabled = (state !== "PAUSED");
  a.disabled = (state === "IDLE" || state === "COMPLETED" || state === "ABORTED");

  appendLog("INFO", `狀態變更 → ${state}`);
}

// ── Log ────────────────────────────────────────────────────────────────────────
function handleLog(data) {
  appendLog(data.level, `[${data.ts}] ${data.msg}`);
}

function appendLog(level, msg) {
  const area = document.getElementById("log-area");
  const line = document.createElement("div");
  line.className = "log-line";
  line.innerHTML = `<span class="log-ts">${new Date().toLocaleTimeString()}</span>`
    + `<span class="log-${level}">${escHtml(msg)}</span>`;
  area.appendChild(line);
  area.scrollTop = area.scrollHeight;
}

function escHtml(s) {
  return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

function clearLog() {
  document.getElementById("log-area").innerHTML = "";
}

// ── Progress ───────────────────────────────────────────────────────────────────
function handleProgress(data) {
  const pct = data.total ? Math.round(data.current / data.total * 100) : 0;
  document.getElementById("progress-fill").style.width = pct + "%";
  document.getElementById("progress-pct").textContent = pct + "%";
  document.getElementById("progress-label").textContent =
    data.current > 0 ? `執行中 ${data.current} / ${data.total}` : "準備中...";
}

function handleCurrentTest(data) {
  document.getElementById("progress-label").textContent =
    `執行中 ${data.index}/${data.total}：${data.id}`;
}

// ── Results ────────────────────────────────────────────────────────────────────
let fullResults = [];

function handleResults(results) {
  fullResults = results;
  results.forEach(r => { resultMap[r.id] = r; });
  refreshTestTree();

  const pass  = results.filter(r => r.result === "PASS").length;
  const fail  = results.filter(r => r.result === "FAIL").length;
  const total = results.length;
  document.getElementById("pill-total").textContent = `總計 ${total}`;
  document.getElementById("pill-pass").textContent  = `PASS ${pass}`;
  document.getElementById("pill-fail").textContent  = `FAIL ${fail}`;

  document.getElementById("progress-label").textContent =
    `完成 — PASS ${pass} / FAIL ${fail} / 共 ${total}`;
}

// ── Detail / Screenshot Panel ──────────────────────────────────────────────────
function showDetail(testId) {
  const r = fullResults.find(x => x.id === testId);
  if (!r) return;

  const panel = document.getElementById("detail-panel");
  panel.style.display = "block";

  document.getElementById("detail-title").textContent = testId;

  const badge = document.getElementById("detail-result-badge");
  badge.textContent = r.result;
  const colors = { PASS: "#2ecc71", FAIL: "#e74c3c", ERROR: "#e74c3c", SKIP: "#f39c12" };
  badge.style.background = colors[r.result] || "#2d3154";
  badge.style.color = "#fff";

  document.getElementById("detail-msg").textContent =
    `耗時：${r.duration}s\n\n${r.msg || "(no message)"}`;

  const img = document.getElementById("detail-screenshot");
  const wrap = document.getElementById("detail-screenshot-wrap");
  if (r.screenshot) {
    img.src = `/api/screenshot/${testId}?t=${Date.now()}`;
    img.style.display = "block";
    wrap.style.display = "block";
    img.onclick = () => window.open(img.src, "_blank");
  } else {
    img.style.display = "none";
    wrap.style.display = "none";
  }

  panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function closeDetail() {
  document.getElementById("detail-panel").style.display = "none";
}

// ── Test Tree ──────────────────────────────────────────────────────────────────
async function loadTestTree() {
  const res = await fetch("/api/test-tree");
  testTree = await res.json();
  renderTestTree();
}

function renderTestTree() {
  const container = document.getElementById("test-tree");
  container.innerHTML = "";

  for (const [suiteKey, suite] of Object.entries(testTree)) {
    const suiteDiv = document.createElement("div");

    // Suite header with checkbox
    const suiteHdr = document.createElement("div");
    suiteHdr.className = "suite-header";
    const suiteCb = makeCheckbox(`suite-${suiteKey}`, true, () => toggleSuite(suiteKey));
    suiteHdr.appendChild(suiteCb);
    suiteHdr.appendChild(document.createTextNode(` ${suite.label}`));
    suiteHdr.addEventListener("click", e => { if (e.target !== suiteCb) suiteCb.click(); });
    suiteDiv.appendChild(suiteHdr);

    for (const [groupKey, group] of Object.entries(suite.groups)) {
      if (!group.tests || group.tests.length === 0) continue;

      const groupDiv = document.createElement("div");
      const groupHdr = document.createElement("div");
      groupHdr.className = "group-header";
      const groupCb = makeCheckbox(`group-${groupKey}`, true, () => toggleGroup(groupKey));
      groupHdr.appendChild(groupCb);
      groupHdr.appendChild(document.createTextNode(` ${group.label}`));
      groupHdr.addEventListener("click", e => { if (e.target !== groupCb) groupCb.click(); });
      groupDiv.appendChild(groupHdr);

      for (const test of group.tests) {
        const item = document.createElement("div");
        item.className = "test-item";
        item.id = `item-${test.id}`;

        const cb = makeCheckbox(`cb-${test.id}`, true, null);
        cb.dataset.testId = test.id;
        cb.dataset.group  = groupKey;
        cb.dataset.suite  = suiteKey;

        const dot = document.createElement("span");
        dot.className = "result-dot";
        dot.id = `dot-${test.id}`;

        const label = document.createElement("span");
        label.textContent = ` ${test.id} — ${test.label}`;
        label.style.cursor = "pointer";
        label.addEventListener("click", () => showDetail(test.id));

        item.appendChild(cb);
        item.appendChild(dot);
        item.appendChild(label);
        groupDiv.appendChild(item);
      }
      suiteDiv.appendChild(groupDiv);
    }
    container.appendChild(suiteDiv);
  }
}

function refreshTestTree() {
  for (const [id, r] of Object.entries(resultMap)) {
    const result = typeof r === "string" ? r : r.result;
    const dot = document.getElementById(`dot-${id}`);
    if (dot) {
      dot.className = `result-dot ${result}`;
      dot.title = result;
    }
  }
}

function makeCheckbox(id, checked, onChange) {
  const cb = document.createElement("input");
  cb.type = "checkbox";
  cb.id = id;
  cb.checked = checked;
  if (onChange) cb.addEventListener("change", onChange);
  return cb;
}

function toggleSuite(suiteKey) {
  const suite = testTree[suiteKey];
  const suiteCb = document.getElementById(`suite-${suiteKey}`);
  const checked = suiteCb.checked;
  for (const group of Object.values(suite.groups)) {
    for (const test of (group.tests || [])) {
      const cb = document.getElementById(`cb-${test.id}`);
      if (cb) cb.checked = checked;
    }
  }
}

function toggleGroup(groupKey) {
  const groupCb = document.getElementById(`group-${groupKey}`);
  const checked = groupCb.checked;
  document.querySelectorAll(`[data-group="${groupKey}"]`).forEach(cb => { cb.checked = checked; });
}

function getSelectedTestIds() {
  return [...document.querySelectorAll('input[data-test-id]:checked')]
    .map(cb => cb.dataset.testId);
}

function selectAll()  { document.querySelectorAll('input[type=checkbox]').forEach(cb => cb.checked = true); }
function selectNone() { document.querySelectorAll('input[type=checkbox]').forEach(cb => cb.checked = false); }

// ── NAS Scan ───────────────────────────────────────────────────────────────────
async function scanNAS() {
  appendLog("INFO", "掃描局域網中，請稍候...");
  const subnet = prompt("請輸入子網路前綴（如 192.168.1），留空則僅用 ARP 快速搜尋：", "");
  const url = subnet ? `/api/scan?subnet=${encodeURIComponent(subnet)}` : "/api/scan";
  try {
    const res = await fetch(url);
    const data = await res.json();
    const sel = document.getElementById("nas-select");
    sel.innerHTML = '<option value="">— 選擇 NAS IP —</option>';
    if (data.devices.length === 0) {
      appendLog("WARN", "未發現 NAS 裝置，請確認網路或手動輸入 IP。");
      return;
    }
    data.devices.forEach(d => {
      const opt = document.createElement("option");
      opt.value = d.ip;
      opt.textContent = `${d.ip}  (${d.hostname})`;
      sel.appendChild(opt);
    });
    sel.value = data.devices[0].ip;
    appendLog("INFO", `發現 ${data.devices.length} 台 NAS：${data.devices.map(d => d.ip).join(", ")}`);
  } catch (e) {
    appendLog("ERROR", "掃描失敗：" + e.message);
  }
}

// ── Execution Control ──────────────────────────────────────────────────────────
function getNasConfig() {
  const ip      = document.getElementById("nas-ip-input").value.trim()
                || document.getElementById("nas-select").value;
  const user    = document.getElementById("nas-user").value.trim();
  const pass    = document.getElementById("nas-pass").value;
  const sshUser = document.getElementById("nas-ssh-user").value.trim();
  return { ip, user, pass, sshUser };
}

async function startTests() {
  resultMap = {};
  refreshTestTree();

  const { ip, user, pass, sshUser } = getNasConfig();
  if (!ip)   { alert("請先選擇或輸入 NAS IP"); return; }
  if (!user) { alert("請輸入帳號"); return; }
  if (!pass) { alert("請輸入密碼"); return; }

  const ids = getSelectedTestIds();
  if (ids.length === 0) { alert("請至少勾選一個測試項目"); return; }

  appendLog("INFO", `準備執行 ${ids.length} 個測試案例 → ${ip}`);
  document.getElementById("progress-fill").style.width = "0%";
  document.getElementById("progress-pct").textContent = "0%";
  document.getElementById("pill-total").textContent = "總計 0";
  document.getElementById("pill-pass").textContent  = "PASS 0";
  document.getElementById("pill-fail").textContent  = "FAIL 0";

  await fetch("/api/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      nas_ip: ip, nas_user: user, nas_pass: pass,
      ssh_user: sshUser,
      test_ids: ids
    })
  });
}

async function pauseTests() {
  await fetch("/api/pause", { method: "POST" });
  appendLog("WARN", "暫停指令已送出，等待當前測試完成...");
}

async function resumeTests() {
  await fetch("/api/resume", { method: "POST" });
}

async function abortTests() {
  if (!confirm("確定要中斷測試執行？")) return;
  await fetch("/api/abort", { method: "POST" });
}

// ── Report Download ────────────────────────────────────────────────────────────
function downloadReport(fmt) {
  window.open(`/api/report/${fmt}`, "_blank");
}

// ── Init ───────────────────────────────────────────────────────────────────────
connectWS();
loadTestTree();
