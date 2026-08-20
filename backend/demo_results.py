"""
Pre-recorded results from actual test run on WD My Cloud EX2 Ultra.
Used by Demo Mode — no real NAS connection required.
"""

DEMO_RESULTS = [
    # ── BAT ──────────────────────────────────────────────────────────────────
    {"id": "BAT-01-01", "result": "PASS", "msg": "Login successful — Dashboard loaded", "duration": 5.0},
    {"id": "BAT-01-02", "result": "PASS", "msg": "Logout successful — login form reappeared", "duration": 6.4},
    {"id": "BAT-02-01", "result": "PASS", "msg": "Capacity displayed", "duration": 5.0},
    {"id": "BAT-02-02", "result": "PASS", "msg": "Device Healthy", "duration": 5.1},
    {"id": "BAT-02-03", "result": "PASS", "msg": "Firmware version: 5.33.102", "duration": 4.9},
    {"id": "BAT-05-01", "result": "PASS", "msg": "RAID status Good", "duration": 7.1},
    {"id": "BAT-05-02", "result": "PASS", "msg": "Disk status visible with drive info", "duration": 7.6},
    {"id": "BAT-06-01", "result": "PASS", "msg": "Settings General loaded", "duration": 7.4},
    {"id": "BAT-06-02", "result": "PASS", "msg": "Settings Network loaded", "duration": 7.2},
    {"id": "BAT-06-03", "result": "PASS", "msg": "Firmware Update page loaded", "duration": 7.4},
    {"id": "BAT-07-01", "result": "PASS", "msg": "Manual firmware update UI elements present", "duration": 7.5},
    {"id": "BAT-07-02", "result": "PASS", "msg": "Check for Updates responded with version info", "duration": 8.4},
    # ── F-AUTH ───────────────────────────────────────────────────────────────
    {"id": "F-AUTH-01", "result": "PASS", "msg": "Login OK → Dashboard", "duration": 5.0},
    {"id": "F-AUTH-02", "result": "PASS", "msg": "Wrong password blocked with error message", "duration": 4.1},
    {"id": "F-AUTH-03", "result": "PASS", "msg": "Empty username blocked — login form still shown", "duration": 5.0},
    {"id": "F-AUTH-04", "result": "PASS", "msg": "Empty password blocked on login page", "duration": 4.0},
    {"id": "F-AUTH-07", "result": "PASS", "msg": "Enter key triggered login successfully", "duration": 5.2},
    {"id": "F-AUTH-08", "result": "PASS", "msg": "Password field type='password' — characters masked", "duration": 1.8},
    {"id": "F-AUTH-09", "result": "PASS", "msg": "Back button did not restore authenticated session", "duration": 8.4},
    # ── F-DASH ───────────────────────────────────────────────────────────────
    {"id": "F-DASH-01", "result": "PASS", "msg": "Capacity data with unit displayed", "duration": 5.0},
    {"id": "F-DASH-02", "result": "PASS", "msg": "CPU/RAM section present on dashboard", "duration": 4.9},
    {"id": "F-DASH-04", "result": "PASS", "msg": "Diagnostics: Healthy", "duration": 5.0},
    {"id": "F-DASH-05", "result": "PASS", "msg": "Hibernate confirmation dialog appeared", "duration": 11.3},
    {"id": "F-DASH-06", "result": "PASS", "msg": "Reboot confirmation dialog appeared", "duration": 11.3},
    {"id": "F-DASH-07", "result": "PASS", "msg": "Dashboard loaded in 1.40s (<5s)", "duration": 3.2},
    # ── F-USR ────────────────────────────────────────────────────────────────
    {"id": "F-USR-01", "result": "PASS", "msg": "User 'qa_autotest_user' created and visible in list", "duration": 12.4},
    {"id": "F-USR-04", "result": "PASS", "msg": "User 'qa_autotest_user' deleted — list item removed from DOM", "duration": 12.4},
    {"id": "F-USR-06", "result": "PASS", "msg": "Duplicate username 'admin' blocked — dialog stayed open with error icon", "duration": 12.8},
    {"id": "F-USR-09", "result": "PASS", "msg": "Admin still visible after delete attempt — protected", "duration": 11.7},
    # ── F-SHR ────────────────────────────────────────────────────────────────
    {"id": "F-SHR-01", "result": "PASS", "msg": "Share 'qa_autotest_share' created", "duration": 12.2},
    {"id": "F-SHR-08", "result": "PASS", "msg": "Duplicate share name blocked with error", "duration": 12.2},
    {"id": "F-SHR-11", "result": "PASS", "msg": "Share usage displayed: ['28KB']", "duration": 10.6},
    # ── F-STR / F-DSK ────────────────────────────────────────────────────────
    {"id": "F-STR-01", "result": "PASS", "msg": "RAID status displayed with volume info", "duration": 7.0},
    {"id": "F-STR-02", "result": "PASS", "msg": "Auto-Rebuild setting found on Storage page", "duration": 7.0},
    {"id": "F-DSK-01", "result": "PASS", "msg": "Disk status with temperature/health info visible", "duration": 8.0},
    {"id": "F-DSK-03", "result": "PASS", "msg": "Temps [48, 56]°C all in 0–70°C range", "duration": 8.0},
    # ── F-GEN ────────────────────────────────────────────────────────────────
    {"id": "F-GEN-11", "result": "PASS", "msg": "Drive Sleep toggle changed (True→False) and AJAX saved", "duration": 10.4},
    # ── F-FTP ────────────────────────────────────────────────────────────────
    {"id": "F-FTP-01", "result": "PASS", "msg": "FTP upload OK: qa_ftp_test.txt in /Public listing", "duration": 7.5},
    {"id": "F-FTP-02", "result": "PASS", "msg": "FTP download MD5 match: 6832d01bb08c3cdc614bd8552bd1aaf0", "duration": 0.1},
    {"id": "F-FTP-03", "result": "PASS", "msg": "FTP delete OK: qa_ftp_test.txt removed", "duration": 0.2},
    {"id": "F-FTP-06", "result": "PASS", "msg": "FTP wrong password rejected: 530 Login authentication failed", "duration": 5.3},
    # ── F-SSH ────────────────────────────────────────────────────────────────
    {"id": "F-SSH-01", "result": "PASS", "msg": "SSH file created at /shares/Public/qa_ssh_test.txt", "duration": 0.6},
    {"id": "F-SSH-02", "result": "PASS", "msg": "SFTP upload/download MD5 match: 540bd78bd9de5e70f4248b838a58819c", "duration": 0.4},
    {"id": "F-SSH-04", "result": "PASS", "msg": "SSH wrong password rejected: Authentication failed.", "duration": 0.3},
    # ── F-SMB ────────────────────────────────────────────────────────────────
    {"id": "F-SMB-01", "result": "PASS", "msg": "SMB mounted and file written: qa_smb_test.txt", "duration": 4.0},
    {"id": "F-SMB-02", "result": "PASS", "msg": "SMB read MD5 match: ef53d4d50e5a09a103562570ff3ecdb4", "duration": 1.8},
    {"id": "F-SMB-03", "result": "PASS", "msg": "SMB delete OK: qa_smb_test.txt removed", "duration": 1.6},
    {"id": "F-SMB-07", "result": "PASS", "msg": "SMB wrong password correctly rejected (mount failed)", "duration": 0.3},
    # ── F-NFS ────────────────────────────────────────────────────────────────
    {"id": "F-NFS-01", "result": "PASS", "msg": "NFS mounted 192.168.x.x:/nfs/Public at /tmp/qa_nas_nfs", "duration": 0.1},
    {"id": "F-NFS-02", "result": "PASS", "msg": "NFS write OK: qa_nfs_test.txt", "duration": 0.3},
    {"id": "F-NFS-03", "result": "PASS", "msg": "NFS read MD5 match: a2d64612b225202689314cd66c1f42ba", "duration": 0.2},
    # ── F-FW ─────────────────────────────────────────────────────────────────
    {"id": "F-FW-01", "result": "PASS", "msg": "Online update check completed with version info", "duration": 15.4},
    {"id": "F-FW-02", "result": "PASS", "msg": "Auto Update set to ON and persisted", "duration": 16.6},
    {"id": "F-FW-03", "result": "PASS", "msg": "Auto Update set to OFF and persisted", "duration": 16.7},
    {"id": "F-FW-08", "result": "PASS", "msg": "File input accepted for validation (actual rejection on upload submit)", "duration": 8.6},
    {"id": "F-FW-11", "result": "PASS", "msg": "Firmware version info: 5.33.102", "duration": 7.4},
    {"id": "F-FW-12", "result": "PASS", "msg": "Upgrade UI loaded (confirmation dialog may require valid firmware)", "duration": 10.7},
    # ── UX ───────────────────────────────────────────────────────────────────
    {"id": "UX-01", "result": "PASS", "msg": "All pages <5s: Users=0.04s, Shares=0.03s, Apps=0.03s, Storage=0.03s", "duration": 5.2},
    {"id": "UX-10", "result": "PASS", "msg": "Login form visible at 375px viewport width", "duration": 1.8},
]

DEMO_MAP = {r["id"]: r for r in DEMO_RESULTS}
