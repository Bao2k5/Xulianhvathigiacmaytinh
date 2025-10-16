# -*- coding: utf-8 -*-
"""
Cấu hình hệ thống chấm công AI
Configuration file for AI Attendance System
"""

import os

# ==================== ĐƯỜNG DẪN THƯ MỤC ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DATABASE_DIR = os.path.join(DATA_DIR, 'database')
MODELS_DIR = os.path.join(DATA_DIR, 'models')
ATTENDANCE_DIR = os.path.join(DATA_DIR, 'attendance_logs')
REPORTS_DIR = os.path.join(DATA_DIR, 'reports')
TEMP_DIR = os.path.join(DATA_DIR, 'temp')

# Tạo thư mục nếu chưa tồn tại
for directory in [DATA_DIR, DATABASE_DIR, MODELS_DIR, ATTENDANCE_DIR, REPORTS_DIR, TEMP_DIR]:
    os.makedirs(directory, exist_ok=True)

# ==================== CẤU HÌNH DATABASE ====================
DATABASE_PATH = os.path.join(DATABASE_DIR, 'attendance.db')
EMBEDDINGS_PATH = os.path.join(DATABASE_DIR, 'face_embeddings.pkl')

# ==================== CẤU HÌNH FACE RECOGNITION ====================
# MTCNN settings
MTCNN_MIN_FACE_SIZE = 40
MTCNN_THRESHOLDS = [0.6, 0.7, 0.7]
MTCNN_FACTOR = 0.709

# FaceNet settings
FACENET_IMAGE_SIZE = 160
FACE_RECOGNITION_THRESHOLD = 0.6  # Ngưỡng nhận diện (càng nhỏ càng chặt)
MIN_CONFIDENCE = 0.95  # Độ tin cậy tối thiểu của MTCNN

# ==================== CẤU HÌNH ANTI-SPOOFING ====================
ENABLE_ANTI_SPOOFING = True
LIVENESS_THRESHOLD = 0.7  # Ngưỡng phát hiện người thật
BLINK_THRESHOLD = 0.2  # EAR threshold cho phát hiện nháy mắt
BLINK_CONSECUTIVE_FRAMES = 3  # Số frame liên tiếp để xác nhận nháy mắt

# Phương pháp anti-spoofing
USE_TEXTURE_ANALYSIS = True  # Phân tích texture (ảnh in)
USE_BLINK_DETECTION = True   # Phát hiện nháy mắt
USE_MOTION_ANALYSIS = True   # Phân tích chuyển động
USE_DEPTH_ANALYSIS = True    # Phân tích độ sâu

# ==================== CẤU HÌNH CHẤM CÔNG ====================
MIN_TIME_BETWEEN_CHECKINS = 300  # 5 phút (giây) - Thời gian tối thiểu giữa 2 lần chấm công
WORK_START_TIME = "08:00"
WORK_END_TIME = "17:00"
LATE_THRESHOLD_MINUTES = 15  # Đi muộn nếu sau 15 phút

# ==================== CẤU HÌNH CAMERA ====================
CAMERA_INDEX = 0  # 0 cho webcam mặc định, thử 1, 2 nếu lỗi
CAMERA_WIDTH = 640  # Giảm resolution để tăng tốc
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# ==================== CẤU HÌNH GIAO DIỆN ====================
WINDOW_TITLE = "AI Attendance System - Anti-Spoofing"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FONT_FAMILY = "Segoe UI"
FONT_SIZE = 10

# Màu sắc
COLOR_SUCCESS = "#4CAF50"
COLOR_WARNING = "#FF9800"
COLOR_DANGER = "#F44336"
COLOR_INFO = "#2196F3"
COLOR_PRIMARY = "#1976D2"

# ==================== CẤU HÌNH XUẤT BÁO CÁO ====================
REPORT_FORMAT = ['excel', 'pdf']  # Các định dạng hỗ trợ
EXCEL_SHEET_NAME = "Attendance Report"
PDF_TITLE = "Báo Cáo Chấm Công"
COMPANY_NAME = "CÔNG TY XYZ"
REPORT_LOGO_PATH = None  # Đường dẫn đến logo công ty (nếu có)

# ==================== CẤU HÌNH LOGGING ====================
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = os.path.join(DATA_DIR, 'system.log')
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# ==================== CẤU HÌNH KHÁC ====================
LANGUAGE = "vi"  # vi: Tiếng Việt, en: English
DATE_FORMAT = "%d/%m/%Y"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"

# Số lượng ảnh để đăng ký 1 người
NUM_IMAGES_FOR_REGISTRATION = 5

# Timeout cho các thao tác (giây)
CAMERA_TIMEOUT = 30
PROCESSING_TIMEOUT = 10

print(f"✅ Configuration loaded successfully!")
print(f"📁 Database path: {DATABASE_PATH}")
print(f"📁 Data directory: {DATA_DIR}")
