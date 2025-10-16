# 📦 HƯỚNG DẪN CÀI ĐẶT CHI TIẾT

## Detailed Installation Guide

---

## 🖥️ YÊU CẦU HỆ THỐNG

### Phần cứng tối thiểu:

- **CPU**: Intel Core i3 hoặc tương đương
- **RAM**: 4GB (khuyến nghị 8GB)
- **Ổ cứng**: 2GB dung lượng trống
- **Webcam**: USB webcam hoặc laptop webcam
- **GPU**: Không bắt buộc (NVIDIA GPU với CUDA sẽ nhanh hơn)

### Hệ điều hành:

- ✅ Windows 10/11
- ✅ Ubuntu 20.04+
- ✅ macOS 10.15+

### Phần mềm:

- **Python**: 3.8, 3.9, 3.10 hoặc 3.11
- **pip**: Package manager (thường đi kèm Python)
- **Git**: (Optional) Để clone repository

---

## 📋 CÀI ĐẶT PYTHON

### Windows:

1. Download Python từ: https://www.python.org/downloads/
2. Chạy installer
3. ✅ **QUAN TRỌNG**: Tick "Add Python to PATH"
4. Chọn "Install Now"
5. Kiểm tra:

```bash
python --version
pip --version
```

### Ubuntu/Linux:

```bash
# Cập nhật package list
sudo apt update

# Cài Python 3 và pip
sudo apt install python3 python3-pip python3-venv

# Kiểm tra
python3 --version
pip3 --version
```

### macOS:

```bash
# Cài Homebrew (nếu chưa có)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Cài Python
brew install python@3.10

# Kiểm tra
python3 --version
pip3 --version
```

---

## 🚀 CÀI ĐẶT PROJECT

### Bước 1: Tải project

**Cách 1**: Download ZIP

- Giải nén vào thư mục mong muốn

**Cách 2**: Clone từ Git (nếu có)

```bash
git clone <repository-url>
cd "Tiểu luận xử lí ảnh"
```

### Bước 2: Tạo môi trường ảo (Virtual Environment)

**Tại sao cần?**

- Tránh conflict với các package khác
- Dễ quản lý dependencies
- Best practice cho Python projects

**Windows**:

```bash
# Tạo venv
python -m venv venv

# Kích hoạt
venv\Scripts\activate

# Bạn sẽ thấy (venv) ở đầu dòng lệnh
```

**Linux/Mac**:

```bash
# Tạo venv
python3 -m venv venv

# Kích hoạt
source venv/bin/activate

# Bạn sẽ thấy (venv) ở đầu dòng lệnh
```

### Bước 3: Upgrade pip

```bash
python -m pip install --upgrade pip
```

### Bước 4: Cài đặt thư viện

**Cách 1**: Cài tất cả từ requirements.txt (Khuyến nghị)

```bash
pip install -r requirements.txt
```

**Cách 2**: Cài từng package (nếu gặp lỗi)

```bash
# Core libraries
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install facenet-pytorch mtcnn
pip install opencv-python pillow numpy

# Data processing
pip install pandas openpyxl

# Reporting
pip install reportlab fpdf

# Others
pip install scikit-learn scipy python-dateutil pytz
```

**Lưu ý về PyTorch**:

- **CPU only** (nhẹ hơn, chậm hơn):

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

- **CUDA 11.8** (cho GPU NVIDIA):

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

- **CUDA 12.1**:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### Bước 5: Kiểm tra cài đặt

Tạo file `test_installation.py`:

```python
import sys
print(f"Python version: {sys.version}")

try:
    import torch
    print(f"✅ PyTorch: {torch.__version__}")
    print(f"   CUDA available: {torch.cuda.is_available()}")
except:
    print("❌ PyTorch not installed")

try:
    import cv2
    print(f"✅ OpenCV: {cv2.__version__}")
except:
    print("❌ OpenCV not installed")

try:
    import numpy
    print(f"✅ NumPy: {numpy.__version__}")
except:
    print("❌ NumPy not installed")

try:
    from facenet_pytorch import MTCNN
    print("✅ facenet-pytorch: OK")
except:
    print("❌ facenet-pytorch not installed")

try:
    import pandas
    print(f"✅ Pandas: {pandas.__version__}")
except:
    print("❌ Pandas not installed")

try:
    from openpyxl import Workbook
    print("✅ openpyxl: OK")
except:
    print("❌ openpyxl not installed")

try:
    from reportlab.pdfgen import canvas
    print("✅ reportlab: OK")
except:
    print("❌ reportlab not installed")

print("\n🎉 Installation check completed!")
```

Chạy:

```bash
python test_installation.py
```

---

## 🔧 XỬ LÝ LỖI CÀI ĐẶT

### Lỗi 1: "pip not found" hoặc "command not found"

**Nguyên nhân**: Python chưa được thêm vào PATH

**Giải pháp Windows**:

```bash
# Thay vì python, dùng đường dẫn đầy đủ
C:\Users\<YourName>\AppData\Local\Programs\Python\Python310\python.exe -m pip install -r requirements.txt
```

**Giải pháp Linux/Mac**:

```bash
# Dùng python3 thay vì python
python3 -m pip install -r requirements.txt
```

### Lỗi 2: "Microsoft Visual C++ ... is required"

**Nguyên nhân**: Windows thiếu C++ build tools

**Giải pháp**:

1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Cài "Desktop development with C++"
3. Restart và thử lại

### Lỗi 3: "ERROR: Could not install packages due to OSError"

**Nguyên nhân**: Quyền truy cập

**Giải pháp**:

```bash
# Thêm --user flag
pip install --user -r requirements.txt
```

### Lỗi 4: PyTorch quá lớn / chậm download

**Giải pháp**: Cài CPU-only version

```bash
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Lỗi 5: "No module named 'cv2'"

**Nguyên nhân**: OpenCV chưa cài đúng

**Giải pháp**:

```bash
pip uninstall opencv-python opencv-contrib-python
pip install opencv-python
```

### Lỗi 6: "DLL load failed" (Windows)

**Nguyên nhân**: Thiếu Visual C++ Redistributable

**Giải pháp**:
Download và cài: https://aka.ms/vs/17/release/vc_redist.x64.exe

---

## 🎮 CHẠY ỨNG DỤNG

### Lần đầu chạy:

```bash
# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Chạy ứng dụng
python main.py
```

### Các lần sau:

```bash
# Vào thư mục project
cd "path\to\Tiểu luận xử lí ảnh"

# Kích hoạt venv (nếu chưa)
venv\Scripts\activate  # Windows
# hoặc
source venv/bin/activate  # Linux/Mac

# Chạy
python main.py
```

### Thoát virtual environment:

```bash
deactivate
```

---

## 🧪 TEST CHỨC NĂNG

### Test 1: Camera

```bash
# Tạo file test_camera.py
import cv2

cap = cv2.VideoCapture(0)
if cap.isOpened():
    print("✅ Camera OK")
    ret, frame = cap.read()
    if ret:
        print(f"✅ Frame size: {frame.shape}")
        cv2.imshow('Test', frame)
        cv2.waitKey(2000)
else:
    print("❌ Camera not working")

cap.release()
cv2.destroyAllWindows()
```

### Test 2: Face Detection

```bash
# Chạy trong Python console
from face_recognition import FaceRecognizer
recognizer = FaceRecognizer()
print("✅ Face Recognizer loaded")
```

### Test 3: Database

```bash
# Chạy trong Python console
from database import DatabaseManager
db = DatabaseManager()
employees = db.get_all_employees()
print(f"✅ Database OK. Total employees: {len(employees)}")
```

---

## 📊 BENCHMARK HIỆU NĂNG

### Test tốc độ xử lý:

```python
import time
import cv2
from face_recognition import FaceRecognizer

recognizer = FaceRecognizer()
cap = cv2.VideoCapture(0)

frame_count = 0
start_time = time.time()

while frame_count < 100:
    ret, frame = cap.read()
    if ret:
        faces, boxes, probs, landmarks = recognizer.detect_faces(frame)
        frame_count += 1

end_time = time.time()
fps = frame_count / (end_time - start_time)

print(f"Average FPS: {fps:.2f}")
print(f"Time per frame: {1000/fps:.2f} ms")

cap.release()
```

**Kết quả mong đợi**:

- CPU: 5-10 FPS
- GPU: 25-30 FPS

---

## 🔄 UPDATE VÀ BẢO TRÌ

### Update thư viện:

```bash
# Update tất cả
pip install --upgrade -r requirements.txt

# Update 1 package cụ thể
pip install --upgrade torch
```

### Backup database:

```bash
# Windows
copy "data\database\*" "backup\"

# Linux/Mac
cp -r data/database/ backup/
```

### Export danh sách package hiện tại:

```bash
pip freeze > requirements_current.txt
```

---

## 🐛 DEBUGGING

### Enable debug mode:

Trong `config.py`, thêm:

```python
LOG_LEVEL = "DEBUG"
```

### Xem log:

```bash
# Xem log file
notepad data\system.log  # Windows
cat data/system.log      # Linux/Mac

# Theo dõi real-time
tail -f data/system.log  # Linux/Mac
```

### Check GPU usage (nếu có):

```python
import torch
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
print(torch.cuda.memory_allocated())
```

---

## 📱 MOBILE/WEB DEPLOYMENT (Advanced)

### Flask Web App (Optional):

```bash
pip install flask flask-cors

# Tạo web_app.py
from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)

@app.route('/')
def index():
    return "AI Attendance System - Web Interface"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## 🎓 CHO MÔI TRƯỜNG HỌC THUẬT

### Cài đặt trên máy Lab:

Nếu không có quyền admin:

```bash
# Cài local
pip install --user -r requirements.txt

# Hoặc dùng venv
python -m venv venv
```

### Chạy trên Google Colab:

```python
# Upload files to Colab
!pip install facenet-pytorch mtcnn opencv-python

# Run
!python main.py
```

### Chạy trên Kaggle Notebook:

```python
# Kaggle đã có sẵn hầu hết packages
!pip install facenet-pytorch mtcnn

# Run code
```

---

## ✅ CHECKLIST CÀI ĐẶT HOÀN CHỈNH

- [ ] Python 3.8+ đã cài đặt
- [ ] pip đã upgrade lên bản mới nhất
- [ ] Virtual environment đã tạo và kích hoạt
- [ ] Tất cả packages trong requirements.txt đã cài
- [ ] Test script chạy thành công
- [ ] Camera hoạt động bình thường
- [ ] main.py chạy không lỗi
- [ ] Có thể tạo window GUI
- [ ] Database được khởi tạo
- [ ] Có thể đăng ký nhân viên mẫu

---

## 📞 HỖ TRỢ

Nếu vẫn gặp vấn đề:

1. ✅ Đọc lại hướng dẫn kỹ
2. ✅ Check log file: `data/system.log`
3. ✅ Search lỗi trên Google/Stack Overflow
4. ✅ Check Python version compatibility
5. ✅ Thử cài lại từ đầu trong venv mới

---

## 🎉 HOÀN TẤT!

Sau khi cài đặt xong:

1. Đọc `QUICKSTART.md` để bắt đầu sử dụng
2. Đọc `README.md` để hiểu chi tiết hệ thống
3. Đọc `ALGORITHM_EXPLANATION.md` cho phần lý thuyết

**Chúc bạn thành công với tiểu luận!** 🎓✨
