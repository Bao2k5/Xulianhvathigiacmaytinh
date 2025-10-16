# 🚀 HƯỚNG DẪN NHANH - QUICK START GUIDE

## ⚡ Bắt đầu trong 5 phút!

### Bước 1: Cài đặt Python

Đảm bảo đã cài Python 3.8+:

```bash
python --version
```

### Bước 2: Cài thư viện

```bash
pip install -r requirements.txt
```

### Bước 3: Chạy chương trình

```bash
python main.py
```

---

## 📝 SỬ DỤNG CƠ BẢN

### 1. Đăng ký nhân viên đầu tiên

1. Mở tab **"➕ Đăng ký NV"**
2. Điền:
   - Mã NV: `NV001`
   - Họ tên: `Nguyễn Văn A`
   - Phòng ban: `IT`
3. Click **"📸 Bắt đầu đăng ký"**
4. Nhìn vào camera → Hệ thống tự chụp 5 ảnh
5. Xong! ✅

### 2. Chấm công

1. Mở tab **"⏰ Chấm công"**
2. Click **"🎥 Bật Camera"**
3. Đứng trước camera
4. Hệ thống tự động nhận diện và chấm công

### 3. Xem báo cáo

1. Mở tab **"📊 Báo cáo"**
2. Click **"📊 Xuất Excel"**
3. File sẽ được lưu trong thư mục `data/reports/`

---

## 🎯 TIPS QUAN TRỌNG

### ✅ Để có kết quả tốt nhất:

**Ánh sáng**:

- 💡 Đủ sáng (không quá tối hoặc quá sáng)
- 🪟 Tránh ánh sáng ngược (backlight)
- 🌞 Ánh sáng tự nhiên là tốt nhất

**Tư thế**:

- 👤 Nhìn thẳng vào camera
- 📏 Khoảng cách 50-100cm
- 😊 Không cần cười, tự nhiên là được

**Tránh**:

- ❌ Đeo kính đen/khẩu trang (khi đăng ký)
- ❌ Che khuôn mặt
- ❌ Di chuyển quá nhanh

### ⚠️ Xử lý lỗi nhanh:

**Camera không bật?**

```python
# Thử đổi camera index trong config.py
CAMERA_INDEX = 0  # Thử 0, 1, 2...
```

**Nhận diện sai?**

```python
# Giảm threshold trong config.py
FACE_RECOGNITION_THRESHOLD = 0.5  # Giảm từ 0.6
```

**Cứ báo FAKE?**

```python
# Giảm liveness threshold
LIVENESS_THRESHOLD = 0.5  # Giảm từ 0.7
```

---

## 📊 DEMO DATA (Test)

Nếu muốn test nhanh, thêm nhân viên mẫu:

```python
# Chạy trong Python console
from database import DatabaseManager
db = DatabaseManager()

db.add_employee("NV001", "Nguyễn Văn A", "IT", "Developer")
db.add_employee("NV002", "Trần Thị B", "HR", "Manager")
db.add_employee("NV003", "Lê Văn C", "Sales", "Staff")
```

---

## 🔧 CẤU HÌNH NHANH

### config.py - Các thông số quan trọng:

```python
# === CHẤM CÔNG ===
MIN_TIME_BETWEEN_CHECKINS = 300  # 5 phút
WORK_START_TIME = "08:00"
LATE_THRESHOLD_MINUTES = 15

# === NHẬN DIỆN ===
FACE_RECOGNITION_THRESHOLD = 0.6  # Độ chặt
NUM_IMAGES_FOR_REGISTRATION = 5   # Số ảnh đăng ký

# === ANTI-SPOOFING ===
LIVENESS_THRESHOLD = 0.7
USE_TEXTURE_ANALYSIS = True
USE_BLINK_DETECTION = True
USE_MOTION_ANALYSIS = True
USE_DEPTH_ANALYSIS = True

# === CAMERA ===
CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
```

---

## 📦 KIỂM TRA CÀI ĐẶT

Chạy script kiểm tra:

```python
import torch
import cv2
from facenet_pytorch import MTCNN

print("✅ Python:", "OK")
print("✅ PyTorch:", torch.__version__)
print("✅ OpenCV:", cv2.__version__)
print("✅ MTCNN:", "OK")
print("✅ CUDA available:", torch.cuda.is_available())
```

---

## 🎓 CHO TIỂU LUẬN

### Các file quan trọng cần demo:

1. **main.py** → Chạy ứng dụng
2. **face_recognition.py** → Giải thích MTCNN + FaceNet
3. **anti_spoofing.py** → Giải thích các phương pháp
4. **config.py** → Các tham số có thể điều chỉnh

### Nội dung trình bày:

#### Slide 1: Giới thiệu

- Tên đề tài
- Mục tiêu
- Ứng dụng thực tế

#### Slide 2: Công nghệ

- MTCNN (Face Detection)
- FaceNet (Face Recognition)
- Anti-Spoofing (4 phương pháp)

#### Slide 3: Kiến trúc

- Sơ đồ luồng xử lý
- Giải thích từng module

#### Slide 4: Demo

- Video demo chạy thực tế
- Đăng ký nhân viên
- Chấm công
- Xuất báo cáo

#### Slide 5: Kết quả

- Độ chính xác
- Tốc độ xử lý
- Khả năng chống giả mạo

#### Slide 6: Kết luận

- Ưu điểm
- Hạn chế
- Hướng phát triển

---

## 📸 DEMO SCENARIOS

### Scenario 1: Chấm công thành công

```
1. Nhân viên đã đăng ký
2. Đứng trước camera
3. Hệ thống nhận diện
4. Hiển thị tên + viền xanh
5. Ghi log chấm công
```

### Scenario 2: Phát hiện giả mạo

```
1. Cầm ảnh in ra trước camera
2. Hệ thống phát hiện texture bất thường
3. Hiển thị "FAKE DETECTED" + viền đỏ
4. Từ chối chấm công
5. Ghi log spoofing attempt
```

### Scenario 3: Người lạ

```
1. Người chưa đăng ký
2. Đứng trước camera
3. Hệ thống không match được
4. Hiển thị "Unknown" + viền cam
5. Không ghi log chấm công
```

---

## 🏆 CHECKLIST TRƯỚC KHI DEMO

- [ ] Đã cài đặt đầy đủ thư viện
- [ ] Camera hoạt động bình thường
- [ ] Đã đăng ký ít nhất 2-3 nhân viên
- [ ] Ánh sáng phòng đủ sáng
- [ ] Đã test chạy thử không lỗi
- [ ] Chuẩn bị ảnh in để demo anti-spoofing
- [ ] File slides/tài liệu đã sẵn sàng
- [ ] Đã tạo vài bản ghi chấm công mẫu
- [ ] Test xuất báo cáo Excel/PDF
- [ ] Backup code và data

---

## 💡 CÂU HỎI THƯỜNG GẶP (FAQ)

**Q: Mất bao lâu để đăng ký 1 người?**  
A: Khoảng 10-15 giây (chụp 5 ảnh)

**Q: Có thể nhận diện khi đeo khẩu trang không?**  
A: Không. Cần thấy toàn bộ khuôn mặt để chính xác

**Q: Nhận diện được bao nhiêu người?**  
A: Không giới hạn (lý thuyết). Đã test với 100+ người

**Q: Có cần Internet không?**  
A: KHÔNG. Hoạt động offline hoàn toàn

**Q: Có thể chạy trên Raspberry Pi không?**  
A: Được nhưng sẽ chậm. Khuyến nghị PC/Laptop

**Q: Database lưu ở đâu?**  
A: SQLite local trong thư mục `data/database/`

**Q: Có thể dùng nhiều camera không?**  
A: Hiện tại chỉ 1 camera. Có thể mở rộng

**Q: Xuất báo cáo định kỳ được không?**  
A: Manual. Có thể viết thêm script tự động

---

## 🚀 NEXT STEPS

Sau khi hoàn thành tiểu luận:

1. **Cải thiện**:

   - Thêm tính năng mới
   - Optimize performance
   - Cải thiện UI

2. **Deploy**:

   - Lên server
   - Tạo web interface
   - Mobile app

3. **Research**:
   - Paper về anti-spoofing
   - Dataset mới
   - Model training

---

## 📞 HỖ TRỢ

Gặp vấn đề? Kiểm tra:

1. `data/system.log` - Log file
2. README.md - Tài liệu đầy đủ
3. Code có comments chi tiết

---

**Chúc bạn thành công với tiểu luận!** 🎓✨

Made with ❤️ for Computer Vision students
