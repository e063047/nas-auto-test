# NAS 自動化測試計畫 (TEST PLAN)

**裝置**：WD My Cloud EX2 Ultra  
**韌體版本**：5.33.102  
**硬體**：Drive1 (2TB) + Drive2 (8TB)，RAID 1  
**目標 IP**：192.168.135.215  
**測試方法**：Playwright Web UI 自動化（模擬真實使用者瀏覽器操作）  
**制定日期**：2026-08-19  

---

## 測試範圍說明

| 層級 | 說明 |
|------|------|
| **BAT** (Build Acceptance Test) | 快速冒煙測試，驗證核心功能可正常運作，約 15–20 分鐘跑完 |
| **FULL Test** | 完整測試，涵蓋正向、反向、UX/可用性、壓力與效能，完整執行約 2–3 小時 |

---

## BAT（快速冒煙測試）

### BAT-01：登入與登出
| ID | 測試項目 | 操作步驟 | 預期結果 |
|----|---------|---------|---------|
| BAT-01-01 | 正常登入 | 輸入正確帳號 admin / 密碼，點擊登入 | 成功進入 Dashboard，顯示裝置狀態 |
| BAT-01-02 | 登出 | 點擊右上角選單 → 登出 | 返回登入頁，Session 清除 |

### BAT-02：Dashboard 基本資訊
| ID | 測試項目 | 操作步驟 | 預期結果 |
|----|---------|---------|---------|
| BAT-02-01 | 儲存容量顯示 | 進入 Home Dashboard | 顯示可用容量（1.94 TB free）且數值合理 |
| BAT-02-02 | 裝置健康狀態 | 查看 Diagnostics 區塊 | 顯示 "Healthy" |
| BAT-02-03 | 韌體版本顯示 | 查看 Firmware 欄位 | 顯示正確版本號（5.33.102）|
| BAT-02-04 | CPU / RAM 圖表 | 查看 Device Activity | 圖表元件正常渲染，無 JS 錯誤 |

### BAT-03：使用者管理基本功能
| ID | 測試項目 | 操作步驟 | 預期結果 |
|----|---------|---------|---------|
| BAT-03-01 | 使用者列表載入 | 點選 Users | 顯示現有使用者清單（含 admin）|
| BAT-03-02 | 新增使用者 | 點擊 Add → 填寫用戶名、密碼 → 儲存 | 新使用者出現在清單中 |
| BAT-03-03 | 刪除使用者 | 選取測試用戶 → 刪除 | 使用者從清單中移除 |

### BAT-04：共享資料夾基本功能
| ID | 測試項目 | 操作步驟 | 預期結果 |
|----|---------|---------|---------|
| BAT-04-01 | 共享列表載入 | 點選 Shares | 顯示 Public、TimeMachineBackup 等 Share |
| BAT-04-02 | 查看 Share 詳情 | 點選 Public | 顯示 Share 屬性（Volume、Public 開關、FTP 等）|
| BAT-04-03 | 新增 Share | 點擊 Add → 填名稱 → 儲存 | 新 Share 出現在清單 |

### BAT-05：儲存 RAID 狀態
| ID | 測試項目 | 操作步驟 | 預期結果 |
|----|---------|---------|---------|
| BAT-05-01 | RAID 狀態頁載入 | Storage → RAID | 顯示 RAID 1，狀態 "Good" |
| BAT-05-02 | 磁碟狀態頁載入 | Storage → Disk Status | 顯示 Drive1/Drive2 溫度與健康狀態 |

### BAT-06：基本設定存取
| ID | 測試項目 | 操作步驟 | 預期結果 |
|----|---------|---------|---------|
| BAT-06-01 | Settings General 載入 | Settings → General | 顯示裝置名稱、時區、NTP 等設定 |
| BAT-06-02 | Settings Network 載入 | Settings → Network | 顯示 IP、MAC、各服務開關 |
| BAT-06-03 | 韌體版本頁載入 | Settings → Firmware Update | 顯示當前版本及更新按鈕 |

### BAT-07：韌體升級（Firmware Upgrade）
| ID | 測試項目 | 操作步驟 | 預期結果 |
|----|---------|---------|---------|
| BAT-07-01 | 手動上傳韌體並啟動升級 | Settings → Firmware Update → Update From File → 上傳合法 .bin 韌體檔 → 確認執行 | 升級進度頁面正常顯示，裝置完成重啟後韌體版本更新 |
| BAT-07-02 | 升級完成後版本確認 | 升級重啟後登入 → 查看 Firmware 欄位 | 顯示新版本號，與上傳檔案版本一致 |
| BAT-07-03 | 升級期間 UI 狀態 | 升級進行中觀察 UI | 顯示明確進度或等待提示，不出現空白頁或無回應 |

---

## FULL Test（完整測試）

---

### MODULE 1：認證與 Session 管理

#### 1.1 登入功能

| ID | 類型 | 測試項目 | 操作步驟 | 預期結果 |
|----|------|---------|---------|---------|
| F-AUTH-01 | 正向 | 正確帳密登入 | admin / 123456789 | 進入 Dashboard |
| F-AUTH-02 | 反向 | 錯誤密碼登入 | admin / wrongpassword | 顯示錯誤訊息，不得進入系統 |
| F-AUTH-03 | 反向 | 空白帳號登入 | 留空帳號欄位 | 顯示欄位必填提示 |
| F-AUTH-04 | 反向 | 空白密碼登入 | 留空密碼欄位 | 顯示欄位必填提示 |
| F-AUTH-05 | 反向 | 連續 5 次錯誤 | 連續輸入錯誤密碼 5 次 | 顯示帳號鎖定警告（account_locked）|
| F-AUTH-06 | 安全 | Session Timeout | 登入後靜置超過 10 分鐘 | 自動登出，返回登入頁 |
| F-AUTH-07 | UX | 登入頁 Enter 鍵送出 | 填完密碼後按 Enter | 觸發登入動作，無需點擊按鈕 |
| F-AUTH-08 | UX | 密碼欄位遮蔽 | 輸入密碼時 | 字元以 ● 顯示 |
| F-AUTH-09 | UX | 登入後返回上一頁 | 登出後按瀏覽器返回鍵 | 不應直接回到已驗證頁面 |

---

### MODULE 2：Dashboard（首頁儀表板）

| ID | 類型 | 測試項目 | 預期結果 |
|----|------|---------|---------|
| F-DASH-01 | 正向 | 容量數據正確性 | 顯示容量與磁碟實際空間一致 |
| F-DASH-02 | 正向 | CPU/RAM 即時圖表 | 動態更新，數值在 0–100% 範圍內 |
| F-DASH-03 | 正向 | Network Activity 即時更新 | 上下行流量圖表動態刷新 |
| F-DASH-04 | 正向 | 裝置 Diagnostics 狀態 | 正常狀態顯示 "Healthy" |
| F-DASH-05 | UX | 快捷操作：Hibernate | 點擊 Hibernate → 出現確認對話框 |
| F-DASH-06 | UX | 快捷操作：Reboot | 點擊 Reboot → 出現確認對話框 |
| F-DASH-07 | UX | 頁面響應時間 | Dashboard 完整載入 < 5 秒 |
| F-DASH-08 | UX | 說明連結可點擊性 | User Manual、Help Center 等連結正確開啟 |

---

### MODULE 3：使用者管理（Users）

#### 3.1 使用者 CRUD

| ID | 類型 | 測試項目 | 操作步驟 | 預期結果 |
|----|------|---------|---------|---------|
| F-USR-01 | 正向 | 新增本地使用者 | Add → 填用戶名、密碼、Email → 儲存 | 使用者出現在清單 |
| F-USR-02 | 正向 | 修改使用者密碼 | 選擇使用者 → 修改密碼 → 儲存 | 新密碼可正常登入 |
| F-USR-03 | 正向 | 設定使用者 Share 存取權限 | 選擇使用者 → 設定 Read/Write/No Access | 對應 Share 存取行為正確 |
| F-USR-04 | 正向 | 刪除使用者 | 選擇使用者 → 刪除 | 使用者從清單消失 |
| F-USR-05 | 正向 | 批次新增使用者 | Add Multiple Users → 匯入 | 多位使用者同時建立 |
| F-USR-06 | 反向 | 新增重複用戶名 | 建立已存在的用戶名 | 顯示「用戶名已存在」錯誤 |
| F-USR-07 | 反向 | 密碼欄位空白 | 新增時不填密碼 | 顯示必填錯誤，無法儲存 |
| F-USR-08 | 反向 | 用戶名含特殊字元 | 用戶名填入 `admin@#!` | 顯示格式錯誤 |
| F-USR-09 | 反向 | 刪除 admin 帳號 | 嘗試刪除 admin | 應被禁止，顯示保護訊息 |
| F-USR-10 | UX | 使用者搜尋/篩選 | 在多使用者環境中搜尋 | 即時過濾顯示結果 |

#### 3.2 群組管理

| ID | 類型 | 測試項目 | 預期結果 |
|----|------|---------|---------|
| F-GRP-01 | 正向 | 建立使用者群組 | 群組出現在清單 |
| F-GRP-02 | 正向 | 將使用者加入群組 | 使用者顯示為群組成員 |
| F-GRP-03 | 正向 | 設定群組 Share 權限 | 群組成員套用對應存取限制 |
| F-GRP-04 | 正向 | 刪除群組 | 群組消失，成員仍保留 |

---

### MODULE 4：共享資料夾（Shares）

#### 4.1 Share CRUD

| ID | 類型 | 測試項目 | 操作步驟 | 預期結果 |
|----|------|---------|---------|---------|
| F-SHR-01 | 正向 | 新增私有 Share | Add → 填名稱、設 Public OFF → 儲存 | Share 建立，Public 標記 OFF |
| F-SHR-02 | 正向 | 新增公開 Share | Add → 設 Public ON → 儲存 | Share 建立，匿名可存取 |
| F-SHR-03 | 正向 | 修改 Share 名稱 | 選 Share → 修改名稱 → 儲存 | 名稱更新，路徑對應改變 |
| F-SHR-04 | 正向 | 啟用 Recycle Bin | Share 設定 → Recycle Bin ON | 刪除檔案移至回收桶而非直接刪除 |
| F-SHR-05 | 正向 | 啟用 / 停用 FTP Access | Share → FTP ON/OFF | FTP 連線存取行為對應改變 |
| F-SHR-06 | 正向 | 啟用 NFS Access | Share → NFS ON → 設定允許主機 | NFS 掛載成功 |
| F-SHR-07 | 正向 | Mobile & Web App Access | Share → ON | App 可看到此 Share |
| F-SHR-08 | 反向 | 新增重複名稱 Share | 建立已存在名稱 | 顯示名稱衝突錯誤 |
| F-SHR-09 | 反向 | 刪除有資料的 Share | Share 內有檔案時刪除 | 顯示警告：資料將被刪除 |
| F-SHR-10 | 反向 | Share 名稱含特殊字元 | 填入 `test/share` | 顯示格式錯誤 |
| F-SHR-11 | UX | Share 使用量顯示 | 查看 Share Usage 欄位 | 顯示已使用大小（如 16KB）|

---

### MODULE 5：Apps 應用程式

| ID | 類型 | 測試項目 | 操作步驟 | 預期結果 |
|----|------|---------|---------|---------|
| F-APP-01 | 正向 | App Store 清單載入 | 點選 Apps | 顯示可安裝 App 清單及說明 |
| F-APP-02 | 正向 | 安裝 App（如 Internal Backups）| 點擊 Install | 安裝進度顯示，完成後移至已安裝清單 |
| F-APP-03 | 正向 | 啟動 / 停止已安裝 App | 點選已安裝 App → 啟動/停止 | 狀態正確切換 |
| F-APP-04 | 正向 | 卸載 App | 選已安裝 App → Uninstall | App 從已安裝清單消失 |
| F-APP-05 | 正向 | 手動安裝 App（Upload .bin）| Install an app manually → 上傳檔案 | 安裝成功或顯示明確錯誤 |
| F-APP-06 | 反向 | 安裝錯誤格式檔案 | 上傳非 .bin 格式 | 顯示格式不支援錯誤 |
| F-APP-07 | UX | App 說明文字顯示 | 點選 App | 顯示功能描述，截斷部分有「More」展開 |

---

### MODULE 6：Cloud Access

| ID | 類型 | 測試項目 | 操作步驟 | 預期結果 |
|----|------|---------|---------|---------|
| F-CLD-01 | 正向 | 查看 Cloud Access 狀態 | Cloud Access 頁面 | 顯示目前啟用/停用狀態 |
| F-CLD-02 | 正向 | 為使用者啟用 Cloud Access | 選擇使用者 → Enable | 狀態變為已啟用 |
| F-CLD-03 | 正向 | 停用 Cloud Access | 關閉 Cloud Access | 狀態顯示 Disabled |
| F-CLD-04 | UX | Help 連結正確 | 點選說明連結 | 開啟對應說明頁面 |

---

### MODULE 7：儲存管理（Storage）

#### 7.1 RAID 管理

| ID | 類型 | 測試項目 | 操作步驟 | 預期結果 |
|----|------|---------|---------|---------|
| F-STR-01 | 正向 | RAID 狀態顯示 | Storage → RAID | 顯示 RAID 1, Volume_1, Good, 1.96TB |
| F-STR-02 | 正向 | Auto-Rebuild 狀態確認 | 查看 Auto-Rebuild 開關 | 顯示 ON |
| F-STR-03 | 正向 | Change RAID Mode（UI 確認）| 點擊 Change RAID Mode | 顯示選項與警告，不實際執行 |
| F-STR-04 | UX | RAID 頁面警告提示 | 點擊 RAID Mode 變更 | 必須顯示資料風險警告 |

#### 7.2 磁碟健康

| ID | 類型 | 測試項目 | 操作步驟 | 預期結果 |
|----|------|---------|---------|---------|
| F-DSK-01 | 正向 | Disk Status 頁面 | Storage → Disk Status | 顯示 Drive1/Drive2 溫度、健康狀態 |
| F-DSK-02 | 正向 | S.M.A.R.T. Data 查看 | 點選 Drive1 S.M.A.R.T. Data | 顯示 SMART 詳細屬性表 |
| F-DSK-03 | 正向 | 磁碟溫度合理性 | 查看溫度顯示 | 溫度在正常範圍（0–70°C）|

#### 7.3 iSCSI

| ID | 類型 | 測試項目 | 操作步驟 | 預期結果 |
|----|------|---------|---------|---------|
| F-iSC-01 | 正向 | 啟用 iSCSI 服務 | iSCSI → ON | 服務啟用，可建立 Target |
| F-iSC-02 | 正向 | 建立 iSCSI Target | Create iSCSI Target → 填名稱、大小 | Target 建立成功 |
| F-iSC-03 | 正向 | 停用 iSCSI | iSCSI → OFF | 服務停止 |
| F-iSC-04 | 反向 | Target 名稱重複 | 建立同名 Target | 顯示名稱衝突錯誤 |

---

### MODULE 8：系統設定 General

| ID | 類型 | 測試項目 | 操作步驟 | 預期結果 |
|----|------|---------|---------|---------|
| F-GEN-01 | 正向 | 修改裝置名稱 | Device Name 欄位修改 → 儲存 | 裝置名稱更新，頁面標題對應改變 |
| F-GEN-02 | 正向 | 修改時區 | Time Zone 下拉選單 → 儲存 | 系統時間對應調整 |
| F-GEN-03 | 正向 | NTP 開關 | NTP Service ON/OFF | 自動對時服務對應啟停 |
| F-GEN-04 | 正向 | 修改 NTP Server | 填入自訂 NTP Server → 儲存 | 系統使用新 Server 對時 |
| F-GEN-05 | 正向 | Drive Sleep 設定 | ON/OFF 切換 | 磁碟休眠行為對應改變 |
| F-GEN-06 | 正向 | LED 開關 | LED ON/OFF | 機身 LED 燈對應亮滅 |
| F-GEN-07 | 正向 | Web Access Timeout | 修改逾時時間 → 儲存 | Session 在指定時間後到期 |
| F-GEN-08 | 正向 | Time Machine 設定 | Configure >> → 設定 Quota | Time Machine Backup 功能正常 |
| F-GEN-09 | 正向 | Recycle Bin 清空 | Recycle Bin → Clear | 所有 Share 的資源回收桶清空 |
| F-GEN-10 | 反向 | 裝置名稱含非法字元 | Device Name 填入 `NAS/test` | 顯示格式錯誤，不儲存 |
| F-GEN-11 | UX | 設定儲存後出現確認提示 | 修改任一設定 → 儲存 | 顯示「儲存成功」Toast 或 Banner |

---

### MODULE 9：網路設定（Network）

#### 9.1 網路基本設定

| ID | 類型 | 測試項目 | 操作步驟 | 預期結果 |
|----|------|---------|---------|---------|
| F-NET-01 | 正向 | 切換 DHCP 模式 | IPv4 Mode → DHCP → 儲存 | 裝置從 DHCP 取得 IP |
| F-NET-02 | 正向 | 設定 Static IP | IPv4 Mode → Static → 填 IP/Mask/GW → 儲存 | 裝置使用靜態 IP |
| F-NET-03 | 正向 | Jumbo Frame 開啟 | Jumbo Frame → 9000 → 儲存 | MTU 更新為 9000 |
| F-NET-04 | 反向 | 填入無效 IP | Static IP 填 `999.999.999.999` | 顯示 IP 格式錯誤 |
| F-NET-05 | 反向 | DNS 填入非 IP 字元 | DNS 欄位填入文字 | 顯示格式錯誤 |

#### 9.2 檔案傳輸服務

> **連線驗證原則**：所有協定測試除驗證 UI 開關狀態外，**必須實際發起連線、寫入測試檔案至 NAS 磁碟、讀取回來比對內容**，方視為通過。測試機為同一台 Mac（SMB 使用 `mount_smbfs`，NFS 使用 `mount_nfs`）。

**FTP**

| ID | 類型 | 測試項目 | 操作步驟 | 預期結果 |
|----|------|---------|---------|---------|
| F-FTP-01 | 正向 | 啟用 FTP 並實際連線寫入 | UI 將 FTP → ON → 儲存；以 `curl ftp://admin:pw@192.168.135.215/Public/` 上傳測試檔 `ftp_test.txt` | 上傳成功（HTTP 226），NAS Share 內可見該檔案 |
| F-FTP-02 | 正向 | FTP 讀取驗證 | 用 FTP 下載剛上傳的 `ftp_test.txt` | 下載內容與原始檔案 MD5 一致 |
| F-FTP-03 | 正向 | FTP 刪除檔案 | 透過 FTP 刪除 `ftp_test.txt` | 檔案從 Share 消失 |
| F-FTP-04 | 正向 | 停用 FTP 後連線被拒 | UI 將 FTP → OFF → 儲存；再次嘗試 FTP 連線 | 連線被拒絕（Connection refused），確認 UI 關閉生效 |
| F-FTP-05 | 正向 | FTP 設定（Port / 被動模式）| Configure >> → 修改 Port 或 Passive Mode 範圍 → 儲存；以新 Port 連線 | 連線成功，可寫入讀取 |
| F-FTP-06 | 反向 | FTP 錯誤帳密連線 | 使用錯誤密碼 FTP 連線 | 認證失敗（530 Login incorrect），無法存取 |
| F-FTP-07 | 反向 | FTP 連線 Public Share 匿名讀寫 | Share Public ON → FTP 匿名連線 | 依 Share 設定，允許或拒絕匿名存取 |

**NFS**

| ID | 類型 | 測試項目 | 操作步驟 | 預期結果 |
|----|------|---------|---------|---------|
| F-NFS-01 | 正向 | 啟用 NFS 並掛載 | UI 將 NFS → ON → 設定允許主機（Mac IP）→ 儲存；Mac 執行 `sudo mount_nfs 192.168.135.215:/nfs/Public /mnt/nas_nfs` | 掛載成功，`/mnt/nas_nfs` 可列目錄 |
| F-NFS-02 | 正向 | NFS 寫入驗證 | 向掛載路徑寫入 `nfs_test.txt`（含固定內容）| 檔案寫入成功，NAS Web UI 的 Share Usage 數值增加 |
| F-NFS-03 | 正向 | NFS 讀取驗證 | 讀取 `nfs_test.txt` | 內容與寫入時完全一致（MD5 比對）|
| F-NFS-04 | 正向 | 停用 NFS 後掛載失敗 | UI 將 NFS → OFF → 儲存；嘗試重新 mount | 掛載失敗（Connection refused），確認 UI 關閉生效 |
| F-NFS-05 | 反向 | 未授權主機嘗試 NFS 掛載 | 設定允許 IP 後，用其他 IP 嘗試掛載 | 掛載被拒絕（Permission denied）|

**SSH**

| ID | 類型 | 測試項目 | 操作步驟 | 預期結果 |
|----|------|---------|---------|---------|
| F-SSH-01 | 正向 | SSH 連線並寫入檔案 | UI 確認 SSH → ON；Mac 執行 `ssh admin@192.168.135.215`；在 Share 路徑建立 `ssh_test.txt` | SSH 登入成功，檔案建立並可在 Web UI Share 中確認 |
| F-SSH-02 | 正向 | SFTP 傳輸驗證 | `sftp admin@192.168.135.215` → put `sftp_test.txt` → get 驗證 | 上傳/下載成功，MD5 一致 |
| F-SSH-03 | 正向 | 停用 SSH 後連線被拒 | UI 將 SSH → OFF → 儲存；嘗試 SSH 連線 | 連線被拒絕（Connection refused）|
| F-SSH-04 | 反向 | SSH 錯誤帳密 | 使用錯誤密碼 SSH 連線 | 認證失敗，連線中斷 |

#### 9.3 Windows / SMB 服務

> **連線驗證原則**：Mac 使用 `mount_smbfs` 實際掛載 NAS Share，執行寫入/讀取/刪除操作後再 unmount，確認協定端對端功能正常。

| ID | 類型 | 測試項目 | 操作步驟 | 預期結果 |
|----|------|---------|---------|---------|
| F-SMB-01 | 正向 | SMB 掛載並寫入驗證 | UI 確認 SMB 服務啟用；Mac 執行 `mount_smbfs //admin:pw@192.168.135.215/Public /mnt/nas_smb`；寫入 `smb_test.txt` | 掛載成功，檔案寫入 NAS；Web UI Share 中可見該檔案 |
| F-SMB-02 | 正向 | SMB 讀取驗證 | 讀取 `smb_test.txt` | 內容與寫入時 MD5 一致 |
| F-SMB-03 | 正向 | SMB 刪除驗證 | 刪除 `smb_test.txt`，unmount | 檔案從 NAS 移除，Web UI 確認 |
| F-SMB-04 | 正向 | SMB Protocol 版本設定 | UI 設 SMB 2, SMB 3 → 儲存；重新掛載 | 掛載成功，協定版本符合設定（可用 `smbutil statshares` 確認）|
| F-SMB-05 | 正向 | NT LAN Manager NTLMv2 設定 | UI 設 NTLMv2 only → 儲存；重新掛載 | 掛載成功，認證使用 NTLMv2 |
| F-SMB-06 | 正向 | 修改 Workgroup | Workgroup 欄位修改 → 儲存 | 裝置在區網中以新 Workgroup 名稱顯示 |
| F-SMB-07 | 反向 | SMB 錯誤帳密掛載 | 使用錯誤帳密掛載 | 掛載失敗（Authentication error）|
| F-SMB-08 | 反向 | 存取無權限 Share | 以無權限帳號嘗試掛載私有 Share | 掛載失敗（Permission denied）|
| F-AD-01 | 正向 | Active Directory 設定 | AD → ON → 填入 AD 域設定 | NAS 加入 AD 域 |

#### 9.4 動態 DNS 與遠端存取

| ID | 類型 | 測試項目 | 操作步驟 | 預期結果 |
|----|------|---------|---------|---------|
| F-DDNS-01 | 正向 | 設定 Dynamic DNS | DDNS → ON → 填入服務商與帳密 | DDNS 記錄更新 |
| F-RDA-01 | 正向 | 啟用 Remote Dashboard Access | Remote Dashboard Access → ON | 可從外部網路存取管理介面 |
| F-RDA-02 | 正向 | HTTPS Redirect 啟用 | HTTPS Redirect → ON | HTTP 自動跳轉 HTTPS |

---

### MODULE 10：系統工具（Utilities）

| ID | 類型 | 測試項目 | 操作步驟 | 預期結果 |
|----|------|---------|---------|---------|
| F-UTL-01 | 正向 | Disk Quick Test | Disk Test → Quick Test → 執行 | 顯示測試進度，完成後顯示結果 |
| F-UTL-02 | 正向 | System Test | System Test → 執行 | 顯示系統自我診斷結果 |
| F-UTL-03 | 正向 | 查看 System Logs | View Logs | 顯示系統日誌列表 |
| F-UTL-04 | 正向 | Restore to Default (System Only) | System Only → Restore → 確認 | 系統設定恢復預設，資料保留 |
| F-UTL-05 | 正向 | 匯出 System Config | Save Config File | 下載 .tar.gz 設定備份檔 |
| F-UTL-06 | 正向 | 匯入 System Config | Import File → 上傳 | 設定還原成功 |
| F-UTL-07 | 正向 | Scan Disk | Scan Disk → 執行 | 顯示掃描進度與結果 |
| F-UTL-08 | 正向 | 建立 ISO Share | Create ISO Share → 選擇 ISO 檔 | ISO 掛載為可瀏覽的 Share |
| F-UTL-09 | 正向 | Flash System LED | Flash System LED → ON | 裝置 LED 開始閃爍 |
| F-UTL-10 | 反向 | 匯入錯誤格式的 Config | 上傳非 config 格式檔 | 顯示格式錯誤，不執行還原 |
| F-UTL-11 | UX | Reboot 確認對話框 | Device Power → Reboot | 顯示確認對話框，點取消不執行 |
| F-UTL-12 | UX | Full Disk Test 警告 | Disk Test → Full Test | 顯示時間預估警告 |

---

### MODULE 11：通知設定（Notifications）

| ID | 類型 | 測試項目 | 操作步驟 | 預期結果 |
|----|------|---------|---------|---------|
| F-NTF-01 | 正向 | 設定 Alert Email | 啟用 → 填 SMTP 與收件人 → 儲存 | 測試郵件寄出成功 |
| F-NTF-02 | 正向 | 設定通知等級 | 選 Critical Only / All | 對應等級的事件才觸發通知 |
| F-NTF-03 | 反向 | Email 格式錯誤 | 填入非 Email 格式字串 | 顯示格式錯誤 |
| F-NTF-04 | UX | 切換通知等級即時更新 | 點選不同等級 Radio Button | 選項即時切換無需重新載入頁面 |

---

### MODULE 12：韌體升級（Firmware Upgrade）

#### 12.1 線上更新

| ID | 類型 | 測試項目 | 操作步驟 | 預期結果 |
|----|------|---------|---------|---------|
| F-FW-01 | 正向 | 檢查線上更新 | Settings → Firmware Update → Check for Updates | 顯示「已是最新版」或顯示可用新版本資訊 |
| F-FW-02 | 正向 | 啟用 Auto Update | Auto Update → ON → 儲存 | 開關狀態儲存為 ON，系統於新韌體發布時自動下載更新 |
| F-FW-03 | 正向 | 停用 Auto Update | Auto Update → OFF → 儲存 | 開關狀態儲存為 OFF，不自動更新 |

#### 12.2 手動升級（Manual Upgrade）

| ID | 類型 | 測試項目 | 操作步驟 | 預期結果 |
|----|------|---------|---------|---------|
| F-FW-04 | 正向 | 手動上傳韌體並執行升級 | Update From File → 選取合法 .bin 韌體檔 → 上傳 → 點擊確認升級 | 顯示升級進度，裝置自動重啟並完成升級 |
| F-FW-05 | 正向 | 升級後版本號驗證 | 升級重啟後登入 → Settings → Firmware Update | 頁面顯示新版本號，與上傳韌體版本一致 |
| F-FW-06 | 正向 | 升級後系統功能完整性 | 升級完成後執行 BAT 全套 | 所有 BAT 項目通過，無功能迴歸 |
| F-FW-07 | 正向 | 升級後使用者/設定保留確認 | 升級前記錄用戶清單與設定值，升級後比對 | 使用者帳號、Share、網路設定均完整保留 |
| F-FW-08 | 反向 | 上傳非韌體格式檔案 | Update From File → 上傳 .txt 或 .jpg | 顯示「不支援的檔案格式」錯誤，不執行升級 |
| F-FW-09 | 反向 | 上傳損毀的韌體檔案 | 上傳 checksum 不符的 .bin 檔 | 顯示「韌體驗證失敗」錯誤，裝置保持現有版本 |
| F-FW-10 | 反向 | 上傳不同機型韌體 | 上傳非 EX2 Ultra 機型的韌體 | 顯示「韌體機型不相容」錯誤 |

#### 12.3 UX / 升級流程體驗

| ID | 類型 | 測試項目 | 操作步驟 | 預期結果 |
|----|------|---------|---------|---------|
| F-FW-11 | UX | 版本資訊顯示完整性 | 查看 Firmware Update 頁面 | 顯示當前版本（5.33.102）、最後更新時間 |
| F-FW-12 | UX | 升級前確認對話框 | 點擊升級後 | 出現確認警告（「升級期間請勿斷電」），需明確確認才執行 |
| F-FW-13 | UX | 升級進度回饋 | 升級執行中 | 顯示進度條或 Spinner，避免使用者誤以為當機 |
| F-FW-14 | UX | Firmware Release Notes 連結 | 點擊 Firmware Release Notes | 正確開啟 WD 官方版本說明頁面 |

---

## UX / 可用性測試（跨模組）

| ID | 測試項目 | 驗證方式 | 預期結果 |
|----|---------|---------|---------|
| UX-01 | 頁面載入時間 | 測量各主要頁面 DOMContentLoaded | 所有頁面 < 5 秒 |
| UX-02 | 導覽列一致性 | 在所有頁面截圖比對導覽列 | 導覽列在所有頁面位置與項目一致 |
| UX-03 | 操作成功回饋 | 每次儲存操作後 | 出現明確的成功提示（Toast / Modal）|
| UX-04 | 操作失敗回饋 | 反向測試中驗證 | 錯誤訊息明確、具體（不只 "Error"）|
| UX-05 | 確認對話框一致性 | 破壞性操作前（刪除、格式化、重啟）| 必須出現確認對話框，避免誤操作 |
| UX-06 | 表單 Tab 鍵順序 | 在表單中按 Tab | 游標依邏輯順序移動 |
| UX-07 | 長操作進度顯示 | Disk Test、Scan Disk 等 | 顯示進度條或 Spinner，不讓使用者懷疑當機 |
| UX-08 | 瀏覽器後退鍵行為 | 操作後按瀏覽器返回 | 不出現意外狀態或白屏 |
| UX-09 | 頁面語言一致性 | 檢查所有頁面文字 | 無中英混雜、無未翻譯 Key（如 `_login_msg8`）|
| UX-10 | 行動裝置 Viewport | 以 375px 寬度開啟 | 主要功能可正常操作（或有提示建議桌機使用）|

---

## 壓力與效能測試（Stress & Performance）

| ID | 類型 | 測試項目 | 測試方法 | 通過標準 |
|----|------|---------|---------|---------|
| SP-01 | 效能 | 首頁載入基準 | 測量 Home 頁面完整載入時間（10次平均）| P95 < 5 秒 |
| SP-02 | 效能 | 使用者列表大量載入 | 建立 50 個使用者後載入 Users 頁 | 載入 < 5 秒，無 JS 錯誤 |
| SP-03 | 效能 | Share 列表大量載入 | 建立 30 個 Share 後載入 Shares 頁 | 載入 < 5 秒 |
| SP-04 | 壓力 | 多標籤頁同時操作 | 同時開啟 5 個瀏覽器 Tab 操作管理介面 | 不出現 Session 衝突或資料錯亂 |
| SP-05 | 壓力 | 連續快速切換頁面 | 快速點擊所有主選單 10 次循環 | 不出現頁面當機或資料遺失 |
| SP-06 | 效能 | Disk Test 期間 UI 回應 | 執行 Quick Test 中持續操作 UI | UI 不卡頓，測試在背景正常進行 |
| SP-07 | 壓力 | 長時間 Session 穩定性 | 保持頁面開啟並操作 60 分鐘 | 不出現意外登出或記憶體洩漏導致卡頓 |
| SP-08 | 效能 | S.M.A.R.T. 資料載入 | 點開 Drive S.M.A.R.T. Data | 資料 < 3 秒內顯示 |

---

## 測試資料規劃

| 類別 | 測試資料 | 說明 |
|------|---------|------|
| 使用者 | `test_user_01` ~ `test_user_50` | 壓力測試用批次建立 |
| Share | `test_share_01` ~ `test_share_30` | 壓力測試用 |
| 密碼（弱）| `123`、`admin`、空字串 | 反向測試用 |
| 特殊字元 | `test/name`、`admin@#!`、超長字串（256字元）| 邊界測試用 |
| ISO 檔 | 合法 .iso 檔（小型）、非 .iso 格式檔案 | App / ISO Mount 測試用 |
| Config | 合法 config 備份檔、損毀 config 檔 | Utilities 測試用 |

---

## 測試執行優先順序

```
P0 (Critical)  ：BAT 全部 + F-AUTH + F-STR（RAID/磁碟健康）
P1 (High)      ：F-USR + F-SHR + F-NET（FTP/NFS/SMB）
P2 (Medium)    ：F-GEN + F-UTL + F-APP + UX 測試
P3 (Low)       ：F-CLD + F-DDNS + F-FW + SP 壓力效能
```

---

## 預估測試案例統計

| 層級 | 數量 |
|------|------|
| BAT | 19 個 |
| FULL（正向）| 84 個 |
| FULL（反向）| 38 個 |
| UX 測試 | 14 個 |
| 壓力/效能 | 8 個 |
| **總計** | **163 個** |

---

*本測試計畫由 Principal Test Automation Architect 與 QA Lead 共同制定。*  
*請 QA Lead 審核後回覆 APPROVE，即可進入階段 2 開發 Web 測試框架。*
