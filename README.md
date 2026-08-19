# NAS Auto Test Framework

Web-First 自動化測試框架，針對 **WD My Cloud EX2 Ultra** 設計，可擴充至其他 WD NAS 產品線。

## 功能特色

- **Web UI 儀表板**：勾選測試項目、即時 Log 串流、進度條、HTML/PDF/JUnit XML 報告下載
- **LAN 自動搜尋**：後端掃描局域網 NAS IP，前端下拉選單選擇
- **Graceful Pause**：暫停時讓當前 Test Case 跑完再 hold，保護 NAS 檔案系統完整性
- **59 個測試案例**：BAT (12) + FULL (45) + UX (2)
- **多協定驗證**：FTP、SSH/SFTP、SMB、NFS 全部含 MD5 校驗

## 系統需求

| 項目 | 需求 |
|------|------|
| 作業系統 | macOS 12+ 或 Ubuntu 20.04+ |
| Python | 3.9 以上 |
| 網路 | 測試機與 NAS 須在同一局域網 |

## 快速安裝

```bash
git clone https://github.com/YOUR_USERNAME/nas-auto-test.git
cd nas-auto-test
bash setup.sh
```

## 啟動

```bash
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8765
```

瀏覽器開啟 `http://localhost:8765`

同局域網的其他電腦可用 `http://你的IP:8765` 直接連線操作。

## 使用方式

1. 在左側 IP 下拉選單選擇 NAS（或手動輸入 IP）
2. 輸入帳號 / 密碼
3. 勾選要執行的測試項目
4. 點「開始」— 即時 Log 會在右側串流顯示
5. 執行完畢後點「下載 HTML 報告」

## 測試案例覆蓋

| 模組 | 測試數 |
|------|--------|
| BAT（冒煙測試）| 12 |
| 認證與 Session | 7 |
| Dashboard | 6 |
| 使用者管理 | 4 |
| 共享資料夾 | 3 |
| 儲存 / 磁碟 | 4 |
| General Settings | 1 |
| FTP | 4 |
| SSH / SFTP | 3 |
| SMB | 4 |
| NFS | 3 |
| 韌體升級 | 6 |
| UX / 可用性 | 2 |
| **合計** | **59** |

## 注意事項

- **SSH 帳號**：WD NAS 的 SSH 帳號為 `sshd`，與 Web 管理帳號 `admin` 不同
- **NFS**：macOS 需要 `sudo mount_nfs`，setup.sh 會自動設定免密碼規則
- **SMB**：使用 macOS 內建 `mount_smbfs`，掛載至 `/tmp/qa_nas_smb`
- **F-AUTH-03**：空白 username 登入回傳 FAIL 屬正常（NAS 韌體安全漏洞，框架正確偵測）

## 專案結構

```
├── backend/
│   ├── main.py            # FastAPI 後端、WebSocket、報告生成
│   ├── executor.py        # 測試執行器（狀態機 + Graceful Pause）
│   ├── test_registry.py   # 59 個測試函數 + TEST_TREE
│   ├── scanner.py         # LAN NAS 掃描器
│   ├── ws_manager.py      # WebSocket 連線管理
│   └── requirements.txt
├── frontend/
│   ├── index.html         # 儀表板 HTML
│   ├── app.js             # 前端邏輯
│   └── style.css
├── reports/               # 自動生成的測試報告
├── TEST_PLAN.md           # 測試計畫文件
├── setup.sh               # 一鍵安裝腳本
└── README.md
```
