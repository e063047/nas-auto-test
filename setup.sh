#!/usr/bin/env bash
# NAS Auto Test Framework — 一鍵安裝腳本
# 支援 macOS (Homebrew) / Ubuntu / Debian
set -e

echo "======================================================"
echo "  NAS Auto Test Framework — 環境安裝"
echo "======================================================"

# ── 偵測作業系統 ──────────────────────────────────────────
OS="$(uname -s)"
echo "▶ 作業系統：$OS"

# ── Python 3.9+ 檢查 ──────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "✗ 找不到 python3，請先安裝 Python 3.9+"
    exit 1
fi
PY_VER=$(python3 -c "import sys; print('%d.%d' % sys.version_info[:2])")
echo "▶ Python 版本：$PY_VER"

# ── pip 升級 ──────────────────────────────────────────────
echo "▶ 升級 pip..."
python3 -m pip install --upgrade pip --quiet

# ── 安裝 Python 依賴 ──────────────────────────────────────
echo "▶ 安裝 Python 套件..."
python3 -m pip install -r backend/requirements.txt --quiet

# ── 安裝 Playwright 瀏覽器（headless Chromium）────────────
echo "▶ 安裝 Playwright Chromium..."
python3 -m playwright install chromium

# ── macOS：NFS 掛載需要 passwordless sudo ─────────────────
if [ "$OS" = "Darwin" ]; then
    echo ""
    echo "▶ [macOS] 設定 NFS 掛載免密碼 sudo..."
    SUDOERS_FILE="/etc/sudoers.d/nas_nfs_test"
    if [ ! -f "$SUDOERS_FILE" ]; then
        echo "$(whoami) ALL=(ALL) NOPASSWD: /sbin/mount_nfs, /sbin/umount" \
            | sudo tee "$SUDOERS_FILE" > /dev/null
        sudo chmod 440 "$SUDOERS_FILE"
        echo "  ✓ sudoers 已設定"
    else
        echo "  ✓ sudoers 已存在，略過"
    fi
fi

# ── Linux：安裝 nfs-common（NFS 客戶端）───────────────────
if [ "$OS" = "Linux" ]; then
    echo "▶ [Linux] 安裝 nfs-common..."
    sudo apt-get install -y nfs-common smbclient 2>/dev/null || true
fi

# ── 建立報告目錄 ──────────────────────────────────────────
mkdir -p reports/screenshots

echo ""
echo "======================================================"
echo "  ✅ 安裝完成！"
echo ""
echo "  啟動方式："
echo "    cd backend"
echo "    python3 -m uvicorn main:app --host 0.0.0.0 --port 8765"
echo ""
echo "  然後開啟瀏覽器：http://localhost:8765"
echo "======================================================"
