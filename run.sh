#!/bin/bash
# ===================================================================
#  AI ATTENDANCE SYSTEM - LAUNCHER
#  Hệ thống chấm công thông minh với Anti-Spoofing
# ===================================================================

echo ""
echo "============================================================"
echo "   AI ATTENDANCE SYSTEM - ANTI-SPOOFING"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python chưa được cài đặt!"
    echo "Vui lòng cài Python 3.8+ từ: https://www.python.org/downloads/"
    exit 1
fi

echo "[OK] Python đã được cài đặt: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[WARNING] Virtual environment chưa được tạo!"
    echo "[INFO] Đang tạo virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Không thể tạo virtual environment!"
        exit 1
    fi
    echo "[OK] Virtual environment đã được tạo"
    echo ""
fi

# Activate virtual environment
echo "[INFO] Kích hoạt virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] Không thể kích hoạt virtual environment!"
    exit 1
fi

echo "[OK] Virtual environment đã kích hoạt"
echo ""

# Check if packages are installed
echo "[INFO] Kiểm tra các thư viện..."
python -c "import torch, cv2, facenet_pytorch" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[WARNING] Các thư viện chưa được cài đặt đầy đủ!"
    echo "[INFO] Đang cài đặt thư viện từ requirements.txt..."
    echo ""
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Lỗi khi cài đặt thư viện!"
        exit 1
    fi
    echo ""
    echo "[OK] Các thư viện đã được cài đặt"
    echo ""
fi

echo "[OK] Tất cả thư viện đã sẵn sàng"
echo ""

# Create data directories if not exist
mkdir -p data/database
mkdir -p data/models
mkdir -p data/attendance_logs
mkdir -p data/reports
mkdir -p data/temp

echo "============================================================"
echo "   KHỞI ĐỘNG ỨNG DỤNG..."
echo "============================================================"
echo ""

# Run the application
python main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Ứng dụng gặp lỗi!"
    echo "Vui lòng kiểm tra log file: data/system.log"
    exit 1
fi

echo ""
echo "[INFO] Ứng dụng đã đóng"
