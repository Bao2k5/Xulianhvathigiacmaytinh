# -*- coding: utf-8 -*-
"""
Giao diện chính cho hệ thống chấm công AI
Main GUI for AI Attendance System
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
from PIL import Image, ImageTk
import threading
from datetime import datetime
import os

import config
from database import DatabaseManager
from face_recognition import FaceRecognizer
from anti_spoofing import AntiSpoofing
from report_exporter import ReportExporter

class AttendanceApp:
    """Ứng dụng chấm công AI với giao diện Tkinter"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        
        # Initialize modules
        print("🔧 Initializing modules...")
        self.db = DatabaseManager()
        self.face_recognizer = FaceRecognizer()
        self.anti_spoofing = AntiSpoofing()
        self.report_exporter = ReportExporter()
        
        # Load embeddings
        embeddings = self.db.load_face_embeddings()
        if embeddings:
            self.face_recognizer.load_embeddings(embeddings)
        
        # Camera variables
        self.camera = None
        self.is_camera_running = False
        self.current_frame = None
        self.prev_frame = None
        
        # Registration variables
        self.registration_mode = False
        self.registration_images = []
        self.registration_employee_id = None
        self.registration_name = None
        self.registration_poses = []  # Danh sách góc đã chụp
        self.current_pose_index = 0   # Góc hiện tại
        self.pose_names = ["CHÍNH DIỆN", "NGHIÊNG TRÁI", "NGHIÊNG PHẢI", "CÚI XUỐNG", "NGƯỚC LÊN"]
        self.pose_captured = [False] * 5  # Trạng thái đã chụp
        self.pose_timer = 0  # Bộ đếm thời gian giữ tư thế
        self.pose_hold_duration = 2.0  # 2 giây
        self.current_face_for_registration = None  # Lưu ảnh mặt hiện tại
        
        # Setup UI
        self.setup_ui()
        
        print("✅ Application initialized!")
    
    def setup_ui(self):
        """Thiết lập giao diện"""
        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Camera feed
        left_panel = ttk.LabelFrame(main_container, text="📹 Camera", padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Camera display
        self.camera_label = ttk.Label(left_panel)
        self.camera_label.pack(fill=tk.BOTH, expand=True)
        
        # Camera controls
        camera_controls = ttk.Frame(left_panel)
        camera_controls.pack(fill=tk.X, pady=(10, 0))
        
        self.btn_start_camera = ttk.Button(camera_controls, text="🎥 Bật Camera", 
                                           command=self.start_camera)
        self.btn_start_camera.pack(side=tk.LEFT, padx=5)
        
        self.btn_stop_camera = ttk.Button(camera_controls, text="⏹️ Tắt Camera", 
                                          command=self.stop_camera, state=tk.DISABLED)
        self.btn_stop_camera.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(left_panel, text="📷 Camera chưa khởi động", 
                                      font=("Segoe UI", 10, "bold"))
        self.status_label.pack(pady=10)
        
        # Right panel - Controls
        right_panel = ttk.Frame(main_container, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        
        # Notebook for tabs
        notebook = ttk.Notebook(right_panel)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Chấm công
        tab_attendance = ttk.Frame(notebook)
        notebook.add(tab_attendance, text="⏰ Chấm công")
        self.setup_attendance_tab(tab_attendance)
        
        # Tab 2: Đăng ký
        tab_register = ttk.Frame(notebook)
        notebook.add(tab_register, text="➕ Đăng ký NV")
        self.setup_register_tab(tab_register)
        
        # Tab 3: Quản lý
        tab_manage = ttk.Frame(notebook)
        notebook.add(tab_manage, text="👥 Quản lý")
        self.setup_manage_tab(tab_manage)
        
        # Tab 4: Báo cáo
        tab_report = ttk.Frame(notebook)
        notebook.add(tab_report, text="📊 Báo cáo")
        self.setup_report_tab(tab_report)
    
    def setup_attendance_tab(self, parent):
        """Setup tab chấm công"""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(frame, text="Chấm công tự động", 
                         font=("Segoe UI", 12, "bold"))
        title.pack(pady=10)
        
        # Info
        info_text = """
        Hướng dẫn:
        1. Bật camera
        2. Đứng trước camera
        3. Hệ thống tự động nhận diện
        4. Chấm công thành công ✓
        
        🔒 Anti-Spoofing: BẬT
        - Phát hiện ảnh in
        - Phát hiện video giả
        - Phát hiện mặt nạ 3D
        """
        info_label = ttk.Label(frame, text=info_text, justify=tk.LEFT)
        info_label.pack(pady=10)
        
        # Last attendance log
        log_frame = ttk.LabelFrame(frame, text="📝 Lịch sử gần nhất", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.attendance_log = tk.Text(log_frame, height=15, width=40, 
                                      state=tk.DISABLED, wrap=tk.WORD)
        self.attendance_log.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.attendance_log.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.attendance_log.config(yscrollcommand=scrollbar.set)
    
    def setup_register_tab(self, parent):
        """Setup tab đăng ký nhân viên"""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(frame, text="Đăng ký nhân viên mới", 
                         font=("Segoe UI", 12, "bold"))
        title.pack(pady=10)
        
        # Form
        form_frame = ttk.Frame(frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(form_frame, text="Mã nhân viên:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_emp_id = ttk.Entry(form_frame, width=30)
        self.entry_emp_id.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(form_frame, text="Họ tên:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_name = ttk.Entry(form_frame, width=30)
        self.entry_name.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(form_frame, text="Phòng ban:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_dept = ttk.Entry(form_frame, width=30)
        self.entry_dept.grid(row=2, column=1, pady=5, padx=5)
        
        ttk.Label(form_frame, text="Chức vụ:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.entry_position = ttk.Entry(form_frame, width=30)
        self.entry_position.grid(row=3, column=1, pady=5, padx=5)
        
        # Instructions
        info_text = """📸 Hướng dẫn chụp ảnh:
        
🎯 Hệ thống yêu cầu 5 góc mặt để nhận diện tốt hơn:
  1️⃣ CHÍNH DIỆN - Nhìn thẳng vào camera
  2️⃣ NGHIÊNG TRÁI - Xoay mặt sang trái 45°
  3️⃣ NGHIÊNG PHẢI - Xoay mặt sang phải 45°
  4️⃣ CÚI XUỐNG - Cúi đầu xuống nhẹ
  5️⃣ NGƯỚC LÊN - Ngước đầu lên nhẹ

⚠️ Lưu ý:
  • Ánh sáng đầy đủ
  • Không đeo khẩu trang/kính đen
  • Giữ mặt trong khung hình
        """
        ttk.Label(frame, text=info_text, justify=tk.LEFT, 
                 foreground="blue").pack(pady=10)
        
        # Progress
        self.register_progress = ttk.Label(frame, text="Chưa bắt đầu", 
                                           font=("Segoe UI", 10, "bold"),
                                           foreground="gray")
        self.register_progress.pack(pady=5)
        
        # Pose instruction (hiển thị góc cần chụp)
        self.pose_instruction = ttk.Label(frame, text="", 
                                         font=("Segoe UI", 14, "bold"),
                                         foreground="red")
        self.pose_instruction.pack(pady=10)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        
        self.btn_start_register = ttk.Button(btn_frame, text="📸 Bắt đầu đăng ký", 
                                             command=self.start_registration)
        self.btn_start_register.pack(side=tk.LEFT, padx=5)
        
        self.btn_cancel_register = ttk.Button(btn_frame, text="❌ Hủy", 
                                              command=self.cancel_registration, 
                                              state=tk.DISABLED)
        self.btn_cancel_register.pack(side=tk.LEFT, padx=5)
    
    def setup_manage_tab(self, parent):
        """Setup tab quản lý nhân viên"""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(frame, text="Danh sách nhân viên", 
                         font=("Segoe UI", 12, "bold"))
        title.pack(pady=10)
        
        # Treeview
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'Họ tên', 'Phòng ban')
        self.employee_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.employee_tree.heading(col, text=col)
            self.employee_tree.column(col, width=120)
        
        self.employee_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, 
                                 command=self.employee_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.employee_tree.config(yscrollcommand=scrollbar.set)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="🔄 Làm mới", 
                  command=self.refresh_employee_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Xóa NV", 
                  command=self.delete_employee).pack(side=tk.LEFT, padx=5)
        
        # Load data
        self.refresh_employee_list()
    
    def setup_report_tab(self, parent):
        """Setup tab báo cáo"""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(frame, text="Xuất báo cáo chấm công", 
                         font=("Segoe UI", 12, "bold"))
        title.pack(pady=10)
        
        # Date range
        date_frame = ttk.LabelFrame(frame, text="Khoảng thời gian", padding=10)
        date_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(date_frame, text="Từ ngày (DD/MM/YYYY):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_start_date = ttk.Entry(date_frame, width=20)
        self.entry_start_date.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(date_frame, text="Đến ngày (DD/MM/YYYY):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_end_date = ttk.Entry(date_frame, width=20)
        self.entry_end_date.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(date_frame, text="(Để trống = tất cả)", 
                 font=("Segoe UI", 8, "italic")).grid(row=2, column=0, columnspan=2, pady=5)
        
        # Export buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="📊 Xuất Excel", 
                  command=lambda: self.export_report('excel')).pack(pady=5, fill=tk.X)
        ttk.Button(btn_frame, text="📄 Xuất PDF", 
                  command=lambda: self.export_report('pdf')).pack(pady=5, fill=tk.X)
        ttk.Button(btn_frame, text="📦 Xuất cả 2", 
                  command=lambda: self.export_report('both')).pack(pady=5, fill=tk.X)
        
        # Statistics
        stats_frame = ttk.LabelFrame(frame, text="📈 Thống kê nhanh", padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.stats_label = ttk.Label(stats_frame, text="Đang tải...", justify=tk.LEFT)
        self.stats_label.pack()
        
        self.update_statistics()
    
    def start_camera(self):
        """Khởi động camera"""
        if not self.is_camera_running:
            self.camera = cv2.VideoCapture(config.CAMERA_INDEX)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
            
            if self.camera.isOpened():
                self.is_camera_running = True
                self.btn_start_camera.config(state=tk.DISABLED)
                self.btn_stop_camera.config(state=tk.NORMAL)
                self.status_label.config(text="✅ Camera đang hoạt động")
                
                # Start camera thread
                thread = threading.Thread(target=self.update_camera_feed, daemon=True)
                thread.start()
            else:
                messagebox.showerror("Lỗi", "Không thể khởi động camera!")
    
    def stop_camera(self):
        """Dừng camera"""
        self.is_camera_running = False
        if self.camera:
            self.camera.release()
        
        self.btn_start_camera.config(state=tk.NORMAL)
        self.btn_stop_camera.config(state=tk.DISABLED)
        self.status_label.config(text="📷 Camera đã tắt")
        self.camera_label.config(image='')
    
    def update_camera_feed(self):
        """Update camera feed và xử lý nhận diện - JARVIS STYLE"""
        import time
        import numpy as np
        frame_count = 0
        process_every_n_frames = 5
        skip_anti_spoofing = True
        
        # Biến lưu thông tin box để vẽ mượt (không nháy)
        last_boxes = []
        last_names = []
        last_probs = []
        scan_line_y = 0  # Vị trí đường quét
        scan_speed = 10  # Tốc độ quét CỰC NHANH
        pulse_alpha = 0  # Hiệu ứng pulse
        particle_positions = []  # Hiệu ứng hạt
        
        # SCAN CHỈ 1 LẦN mỗi mặt
        face_scan_status = {}  # {box_id: progress (0-100)}
        face_scan_complete = {}  # {box_id: True/False}
        
        while self.is_camera_running:
            ret, frame = self.camera.read()
            if not ret:
                time.sleep(0.01)
                continue
            
            frame_count += 1
            small_frame = cv2.resize(frame, (640, 480))
            display_frame = small_frame.copy()
            
            # Chỉ xử lý nhận diện mỗi N frames
            if frame_count % process_every_n_frames == 0:
                faces, boxes, probs, landmarks = self.face_recognizer.detect_faces(small_frame)
                
                if boxes is not None and len(boxes) > 0:
                    # Cập nhật thông tin mới
                    last_boxes = []
                    last_names = []
                    last_probs = []
                    
                    for i, (face, box, prob, landmark) in enumerate(zip(faces, boxes, probs, landmarks)):
                        
                        if skip_anti_spoofing or self.registration_mode:
                            is_real = True
                        else:
                            is_real, liveness_score, details = self.anti_spoofing.check_liveness(
                                face, landmark, self.prev_frame
                            )
                        
                        if is_real:
                            if self.registration_mode:
                                # Lưu ảnh mặt hiện tại để chụp sau 2s
                                self.current_face_for_registration = face.copy()
                                
                                # Hiển thị hướng dẫn góc cần chụp với countdown
                                if self.current_pose_index < len(self.pose_names):
                                    remaining_time = max(0, self.pose_hold_duration - self.pose_timer)
                                    name = f"{self.pose_names[self.current_pose_index]} ({remaining_time:.1f}s)"
                                else:
                                    name = "HOÀN THÀNH"
                                color = (0, 255, 255)  # Cyan
                            else:
                                employee_id, name, distance = self.face_recognizer.recognize_face(face)
                                
                                if employee_id:
                                    color = (0, 255, 0)  # Green - Success
                                    self.log_attendance(employee_id, name, prob, distance)
                                else:
                                    name = "UNKNOWN"
                                    color = (0, 165, 255)  # Orange
                            
                            # Lưu thông tin để vẽ mượt
                            last_boxes.append((box, color))
                            last_names.append(name)
                            last_probs.append(prob)
                        else:
                            # Fake detected
                            last_boxes.append((box, (0, 0, 255)))  # Red
                            last_names.append("FAKE DETECTED")
                            last_probs.append(prob)
                
                self.prev_frame = small_frame.copy()
            
            # VẼ KHUNG NGẦU KIỂU JARVIS HUD
            for idx, (box_info) in enumerate(last_boxes):
                box, color = box_info
                x1, y1, x2, y2 = [int(b) for b in box]
                
                # Hiệu ứng pulse (nhấp nháy nhẹ)
                pulse_intensity = int(50 * np.sin(pulse_alpha * 0.15))
                color_pulse = tuple([min(255, max(0, c + pulse_intensity)) for c in color])
                
                # Màu sáng hơn cho hiệu ứng glow
                color_bright = tuple([min(255, c + 80) for c in color])
                color_dim = tuple([c // 3 for c in color])
                
                # BỎ CORNER BOXES - Không vẽ ô vuông nữa
                
                # === HẠT NĂNG LƯỢNG XUNG QUANH (PARTICLES) ===
                # Tạo hiệu ứng hạt bay xung quanh mặt
                if frame_count % 3 == 0 and len(particle_positions) < 20:
                    # Thêm hạt mới
                    particle_x = np.random.randint(x1, x2)
                    particle_y = np.random.randint(y1, y2)
                    particle_positions.append({
                        'x': particle_x, 
                        'y': particle_y,
                        'vx': np.random.randint(-2, 3),
                        'vy': np.random.randint(-2, 3),
                        'life': 30,
                        'box_idx': idx
                    })
                
                # Vẽ và cập nhật hạt
                particles_to_remove = []
                for i, particle in enumerate(particle_positions):
                    if particle['box_idx'] == idx and particle['life'] > 0:
                        # Kiểm tra loại particle
                        if particle.get('type') == 'data':
                            # Data stream particles (số 0/1)
                            alpha = particle['life'] / 20
                            data_text = str(np.random.randint(0, 2))  # 0 hoặc 1
                            data_color = (255, 255, 0) if alpha > 0.5 else (255, 200, 0)  # Cyan fade
                            cv2.putText(display_frame, data_text, (particle['x'], particle['y']),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, data_color, 1)
                        else:
                            # Energy particles gốc
                            particle_size = int(2 + (particle['life'] / 15))
                            alpha = particle['life'] / 30
                            particle_color = tuple([int(c * alpha) for c in color_bright])
                            cv2.circle(display_frame, (particle['x'], particle['y']), particle_size, particle_color, -1)
                        
                        # Cập nhật vị trí
                        particle['x'] += particle['vx']
                        particle['y'] += particle['vy']
                        particle['life'] -= 1
                    else:
                        particles_to_remove.append(i)
                
                # Xóa hạt hết hiệu lực
                for i in reversed(particles_to_remove):
                    particle_positions.pop(i)
                
                # === SPIDER WEB SCAN - CHỈ 1 LẦN ===
                # Màu xám trắng nhẹ
                gray_white = (200, 200, 200)  # Xám nhạt
                
                # Tạo ID duy nhất cho mặt này (dựa vào TÊN thay vì vị trí để không lặp)
                if idx < len(last_names):
                    face_id = last_names[idx]  # Dùng tên người
                else:
                    face_id = f"unknown_{idx}"
                
                # Khởi tạo scan status nếu chưa có
                if face_id not in face_scan_status:
                    face_scan_status[face_id] = 0
                    face_scan_complete[face_id] = False
                
                # Chỉ quét nếu chưa hoàn thành
                if not face_scan_complete[face_id]:
                    # Tăng progress
                    face_scan_status[face_id] += 8  # Quét nhanh hơn
                    if face_scan_status[face_id] >= 100:
                        face_scan_status[face_id] = 100
                        face_scan_complete[face_id] = True  # Đánh dấu đã xong - KHÔNG BAO GIỜ QUÉT LẠI
                
                # Lấy progress hiện tại
                scan_progress = face_scan_status.get(face_id, 0)
                
                # CHỈ VẼ HIỆU ỨNG NẾU ĐANG QUÉT (0-99)
                if scan_progress < 100:
                    # Tính tâm mặt
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    max_radius = int(np.sqrt((x2-x1)**2 + (y2-y1)**2) / 2)
                    
                    # Bán kính hiện tại dựa vào progress (quét từ trong ra ngoài)
                    current_radius = int((scan_progress / 100.0) * max_radius)
                    
                    # VẼ MẠNG NHỆN (SPIDER WEB)
                    # 1. Vẽ các vòng tròn đồng tâm
                    num_circles = 5
                    for i in range(1, num_circles + 1):
                        radius = int((i / num_circles) * current_radius)
                        if radius > 0:
                            alpha = 0.4 - (i / num_circles) * 0.3  # Mờ dần từ trong ra ngoài
                            overlay = display_frame.copy()
                            cv2.circle(overlay, (center_x, center_y), radius, gray_white, 1)
                            cv2.addWeighted(overlay, alpha, display_frame, 1 - alpha, 0, display_frame)
                    
                    # 2. Vẽ các đường tia từ tâm ra (spokes)
                    num_spokes = 16  # 16 đường tia
                    for i in range(num_spokes):
                        angle = (i / num_spokes) * 360
                        angle_rad = np.radians(angle)
                        
                        # Điểm cuối của tia
                        end_x = int(center_x + current_radius * np.cos(angle_rad))
                        end_y = int(center_y + current_radius * np.sin(angle_rad))
                        
                        # Vẽ tia mờ
                        overlay = display_frame.copy()
                        cv2.line(overlay, (center_x, center_y), (end_x, end_y), gray_white, 1)
                        cv2.addWeighted(overlay, 0.3, display_frame, 0.7, 0, display_frame)
                    
                    # 3. Vẽ viền ngoài hiện tại (sáng hơn)
                    if current_radius > 0:
                        cv2.circle(display_frame, (center_x, center_y), current_radius, gray_white, 2)
                
                # === KHUNG VIỀN NGOÀI (BỎ CROSSHAIR) ===
                # Vẽ viền ngoài mờ (shadow 3D)
                for offset in range(3, 0, -1):
                    alpha_val = 0.2 * (4 - offset)
                    shadow_color = tuple([int(c * alpha_val) for c in color])
                    cv2.rectangle(display_frame, (x1-offset, y1-offset), (x2+offset, y2+offset), shadow_color, 1)
                
                # Tính tâm (dùng cho panel connection)
                center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
                
                # === THÔNG TIN TEXT KIỂU HUD ===
                if idx < len(last_names):
                    # Tên
                    label_name = f"{last_names[idx]}"
                    # Độ chính xác
                    label_conf = f"CONF: {last_probs[idx]:.1%}" if idx < len(last_probs) else ""
                    # Khoảng cách (giả định)
                    label_dist = f"DIST: {np.random.randint(50, 150)} cm"
                    
                    # Vẽ panel thông tin bên trái
                    panel_x = x1 - 150
                    if panel_x < 10:
                        panel_x = x2 + 10
                    panel_y = y1
                    
                    # Nền panel
                    panel_w, panel_h = 140, 80
                    overlay = display_frame.copy()
                    cv2.rectangle(overlay, (panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h), (0, 0, 0), -1)
                    cv2.addWeighted(overlay, 0.8, display_frame, 0.2, 0, display_frame)
                    
                    # Viền panel
                    cv2.rectangle(display_frame, (panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h), color_bright, 2)
                    cv2.line(display_frame, (panel_x + 5, panel_y + 25), (panel_x + panel_w - 5, panel_y + 25), color_dim, 1)
                    
                    # Text header
                    cv2.putText(display_frame, "SCAN RESULT", (panel_x + 10, panel_y + 18),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, color_bright, 1)
                    
                    # Tên (to và sáng)
                    cv2.putText(display_frame, label_name, (panel_x + 10, panel_y + 42),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3)  # Outline
                    cv2.putText(display_frame, label_name, (panel_x + 10, panel_y + 42),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_bright, 1)
                    
                    # Confidence
                    cv2.putText(display_frame, label_conf, (panel_x + 10, panel_y + 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.35, color_pulse, 1)
                    
                    # Distance
                    cv2.putText(display_frame, label_dist, (panel_x + 10, panel_y + 75),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.35, color_dim, 1)
                    
                    # Đường kết nối từ panel đến mặt
                    cv2.line(display_frame, (panel_x + panel_w, panel_y + 40), (x1, center_y), color_dim, 1)
            
            # === HUD OVERLAY - THÔNG TIN HỆ THỐNG ===
            # Timestamp
            timestamp = time.strftime("%H:%M:%S")
            cv2.putText(display_frame, f"TIME: {timestamp}", (10, 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            
            # FPS counter
            cv2.putText(display_frame, f"FPS: {int(1/0.03)}", (10, 45),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Face count
            cv2.putText(display_frame, f"FACES: {len(last_boxes)}", (10, 65),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 165, 0), 1)
            
            # System status
            status_text = "ACTIVE" if len(last_boxes) > 0 else "STANDBY"
            status_color = (0, 255, 0) if len(last_boxes) > 0 else (128, 128, 128)
            cv2.putText(display_frame, f"STATUS: {status_text}", (10, 85),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 1)
            
            # Tăng vị trí đường quét (CỰC NHANH)
            scan_line_y = (scan_line_y + scan_speed) % 200
            pulse_alpha = (pulse_alpha + 1) % 360
            
            # Dọn dẹp face_scan_status cho các mặt không còn hiển thị
            current_face_ids = set()
            for box_info in last_boxes:
                box, _ = box_info
                x1, y1, x2, y2 = [int(b) for b in box]
                face_id = f"{x1}_{y1}_{x2}_{y2}"
                current_face_ids.add(face_id)
            
            # Xóa các face_id cũ không còn trong frame
            face_scan_status = {k: v for k, v in face_scan_status.items() if k in current_face_ids}
            face_scan_complete = {k: v for k, v in face_scan_complete.items() if k in current_face_ids}
            
            # === XỬ LÝ ĐĂNG KÝ TỰ ĐỘNG THEO THỜI GIAN ===
            if self.registration_mode and self.current_face_for_registration is not None:
                # Tăng bộ đếm thời gian (mỗi frame = 0.03s)
                self.pose_timer += 0.03
                
                # Vẽ thanh progress bar cho countdown
                if self.current_pose_index < 5:
                    bar_width = 300
                    bar_height = 30
                    bar_x = (640 - bar_width) // 2
                    bar_y = 420
                    
                    # Nền thanh
                    cv2.rectangle(display_frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
                    cv2.rectangle(display_frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 2)
                    
                    # Thanh progress
                    progress = min(1.0, self.pose_timer / self.pose_hold_duration)
                    progress_width = int(bar_width * progress)
                    color_bar = (0, int(255 * (1 - progress)), int(255 * progress))  # Chuyển từ đỏ sang xanh
                    cv2.rectangle(display_frame, (bar_x, bar_y), (bar_x + progress_width, bar_y + bar_height), color_bar, -1)
                    
                    # Text countdown
                    remaining = max(0, self.pose_hold_duration - self.pose_timer)
                    text = f"{remaining:.1f}s"
                    cv2.putText(display_frame, text, (bar_x + bar_width // 2 - 30, bar_y + 22),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Khi đủ thời gian, chụp ảnh
                if self.pose_timer >= self.pose_hold_duration:
                    self.capture_pose_image()
            
            # Convert và display
            display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            display_frame = cv2.resize(display_frame, (800, 600))
            photo = ImageTk.PhotoImage(image=Image.fromarray(display_frame))
            
            self.camera_label.config(image=photo)
            self.camera_label.image = photo
            
            time.sleep(0.03)  # Giảm delay để mượt hơn
    
    def start_registration(self):
        """Bắt đầu đăng ký nhân viên"""
        employee_id = self.entry_emp_id.get().strip()
        name = self.entry_name.get().strip()
        
        if not employee_id or not name:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập Mã NV và Họ tên!")
            return
        
        if not self.is_camera_running:
            messagebox.showwarning("Cảnh báo", "Vui lòng bật camera trước!")
            return
        
        self.registration_mode = True
        self.registration_images = []
        self.registration_poses = []
        self.current_pose_index = 0
        self.pose_captured = [False] * 5
        self.pose_timer = 0
        self.current_face_for_registration = None
        self.registration_employee_id = employee_id
        self.registration_name = name
        
        self.btn_start_register.config(state=tk.DISABLED)
        self.btn_cancel_register.config(state=tk.NORMAL)
        self.register_progress.config(text="📸 Giữ tư thế 2 giây - Góc 1/5", foreground="blue")
        self.pose_instruction.config(text=f"➡️ {self.pose_names[0]}", foreground="red")
    
    def capture_registration_image(self, face):
        """KHÔNG DÙNG NỮA - Giữ để tương thích"""
        pass
    
    def capture_pose_image(self):
        """Chụp ảnh góc hiện tại sau khi giữ đủ 2 giây"""
        if self.current_pose_index >= 5:
            return  # Đã đủ 5 góc
        
        if self.current_face_for_registration is None:
            return
        
        # Kiểm tra nếu góc này chưa chụp
        if not self.pose_captured[self.current_pose_index]:
            # Chụp ảnh
            self.registration_images.append(self.current_face_for_registration.copy())
            self.registration_poses.append(self.pose_names[self.current_pose_index])
            self.pose_captured[self.current_pose_index] = True
            
            # Cập nhật UI
            count = self.current_pose_index + 1
            self.register_progress.config(
                text=f"✅ Đã chụp góc {count}/5: {self.pose_names[self.current_pose_index]}",
                foreground="green"
            )
            
            # Chuyển sang góc tiếp theo
            self.current_pose_index += 1
            self.pose_timer = 0  # Reset timer
            self.current_face_for_registration = None
            
            if self.current_pose_index < 5:
                # Còn góc cần chụp
                self.pose_instruction.config(
                    text=f"➡️ TIẾP THEO: {self.pose_names[self.current_pose_index]}",
                    foreground="red"
                )
                # Delay 1 giây để người dùng chuẩn bị
                self.root.after(1000, self.ready_for_next_pose)
            else:
                # Đã đủ 5 góc
                self.pose_instruction.config(text="🎉 HOÀN THÀNH!", foreground="green")
                self.root.after(500, self.complete_registration)
    
    def ready_for_next_pose(self):
        """Sẵn sàng chụp góc tiếp theo"""
        if self.current_pose_index < 5:
            self.register_progress.config(
                text=f"📸 Giữ tư thế 2 giây - Góc {self.current_pose_index + 1}/5",
                foreground="blue"
            )
    
    def complete_registration(self):
        """Hoàn tất đăng ký"""
        self.registration_mode = False
        
        # Kiểm tra đã đủ 5 góc chưa
        if len(self.registration_images) < 5:
            messagebox.showwarning("Cảnh báo", f"Chưa đủ 5 góc mặt! Hiện có {len(self.registration_images)}/5")
            return
        
        # Add to database
        dept = self.entry_dept.get().strip()
        position = self.entry_position.get().strip()
        
        success = self.db.add_employee(
            self.registration_employee_id,
            self.registration_name,
            dept, position
        )
        
        if success:
            # Register face với 5 góc
            self.face_recognizer.register_face(
                self.registration_employee_id,
                self.registration_name,
                self.registration_images
            )
            
            # Save embeddings
            embeddings = self.face_recognizer.save_embeddings()
            self.db.save_face_embeddings(embeddings)
            
            # Thông báo chi tiết
            poses_text = "\n".join([f"  ✓ {pose}" for pose in self.registration_poses])
            messagebox.showinfo("Thành công", 
                              f"Đã đăng ký nhân viên {self.registration_name}!\n\n"
                              f"Đã chụp 5 góc mặt:\n{poses_text}")
            
            # Reset form
            self.entry_emp_id.delete(0, tk.END)
            self.entry_name.delete(0, tk.END)
            self.entry_dept.delete(0, tk.END)
            self.entry_position.delete(0, tk.END)
            
            self.refresh_employee_list()
        else:
            messagebox.showerror("Lỗi", "Mã nhân viên đã tồn tại!")
        
        self.btn_start_register.config(state=tk.NORMAL)
        self.btn_cancel_register.config(state=tk.DISABLED)
        self.register_progress.config(text="Chưa bắt đầu", foreground="gray")
        self.pose_instruction.config(text="")
        
        # Reset biến
        self.registration_images = []
        self.registration_poses = []
        self.current_pose_index = 0
        self.pose_captured = [False] * 5
    
    def cancel_registration(self):
        """Hủy đăng ký"""
        self.registration_mode = False
        self.registration_images = []
        self.registration_poses = []
        self.current_pose_index = 0
        self.pose_captured = [False] * 5
        self.pose_timer = 0
        self.current_face_for_registration = None
        
        self.btn_start_register.config(state=tk.NORMAL)
        self.btn_cancel_register.config(state=tk.DISABLED)
        self.register_progress.config(text="Đã hủy", foreground="gray")
        self.pose_instruction.config(text="")
    
    def log_attendance(self, employee_id, name, confidence, distance):
        """Ghi nhận chấm công"""
        # Check time between check-ins
        last_checkin = self.db.get_last_checkin(employee_id)
        
        if last_checkin:
            last_time = datetime.strptime(last_checkin['datetime'], config.DATETIME_FORMAT)
            time_diff = (datetime.now() - last_time).total_seconds()
            
            if time_diff < config.MIN_TIME_BETWEEN_CHECKINS:
                return  # Too soon
        
        # Determine if late
        current_time = datetime.now()
        work_start = datetime.strptime(config.WORK_START_TIME, "%H:%M").time()
        is_late = current_time.time() > work_start
        
        # Log to database
        self.db.log_attendance(
            employee_id, "Check-in", "Success",
            confidence, int(is_late),
            f"Distance: {distance:.3f}"
        )
        
        # Update UI
        log_text = f"[{current_time.strftime(config.DATETIME_FORMAT)}]\n"
        log_text += f"✅ {name} ({employee_id})\n"
        log_text += f"Confidence: {confidence:.2f}\n"
        if is_late:
            log_text += "⚠️ ĐI MUỘN\n"
        log_text += "-" * 40 + "\n\n"
        
        self.attendance_log.config(state=tk.NORMAL)
        self.attendance_log.insert('1.0', log_text)
        self.attendance_log.config(state=tk.DISABLED)
    
    def refresh_employee_list(self):
        """Làm mới danh sách nhân viên"""
        # Clear tree
        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)
        
        # Load employees
        employees = self.db.get_all_employees()
        
        for emp in employees:
            self.employee_tree.insert('', tk.END, values=(
                emp['employee_id'],
                emp['name'],
                emp['department'] or ''
            ))
    
    def delete_employee(self):
        """Xóa nhân viên"""
        selection = self.employee_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên cần xóa!")
            return
        
        item = self.employee_tree.item(selection[0])
        employee_id = item['values'][0]
        name = item['values'][1]
        
        confirm = messagebox.askyesno("Xác nhận", 
                                      f"Bạn có chắc muốn xóa nhân viên {name}?\n\n"
                                      f"Thao tác này sẽ xóa:\n"
                                      f"✓ Thông tin nhân viên\n"
                                      f"✓ Dữ liệu khuôn mặt đã đăng ký\n"
                                      f"✓ Lịch sử chấm công")
        if confirm:
            # Xóa trong database
            self.db.delete_employee(employee_id)
            
            # Xóa face embeddings trong bộ nhớ
            if employee_id in self.face_recognizer.known_embeddings:
                del self.face_recognizer.known_embeddings[employee_id]
                print(f"✅ Đã xóa face embedding của {employee_id} khỏi bộ nhớ")
            
            if employee_id in self.face_recognizer.known_names:
                del self.face_recognizer.known_names[employee_id]
                print(f"✅ Đã xóa tên của {employee_id} khỏi bộ nhớ")
            
            # Lưu lại embeddings sau khi xóa
            embeddings = self.face_recognizer.save_embeddings()
            self.db.save_face_embeddings(embeddings)
            print(f"✅ Đã cập nhật file embeddings")
            
            # Refresh danh sách
            self.refresh_employee_list()
            messagebox.showinfo("Thành công", f"Đã xóa hoàn toàn nhân viên {name}!\n\n"
                              f"Hệ thống sẽ không còn nhận diện khuôn mặt này nữa.")
    
    def export_report(self, format_type):
        """Xuất báo cáo"""
        start_date = self.entry_start_date.get().strip() or None
        end_date = self.entry_end_date.get().strip() or None
        
        try:
            if format_type == 'excel':
                path = self.report_exporter.export_to_excel(start_date, end_date)
                messagebox.showinfo("Thành công", f"Đã xuất báo cáo Excel:\n{path}")
            elif format_type == 'pdf':
                path = self.report_exporter.export_to_pdf(start_date, end_date)
                messagebox.showinfo("Thành công", f"Đã xuất báo cáo PDF:\n{path}")
            else:  # both
                excel_path, pdf_path = self.report_exporter.generate_full_report(start_date, end_date)
                messagebox.showinfo("Thành công", 
                                  f"Đã xuất báo cáo:\nExcel: {excel_path}\nPDF: {pdf_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi xuất báo cáo: {str(e)}")
    
    def update_statistics(self):
        """Cập nhật thống kê"""
        try:
            logs = self.db.get_attendance_logs()
            employees = self.db.get_all_employees()
            
            total_logs = len(logs)
            total_employees = len(employees)
            total_late = sum(1 for log in logs if log['is_late'])
            
            today = datetime.now().strftime(config.DATE_FORMAT)
            today_logs = [log for log in logs if log['datetime'].startswith(today)]
            today_count = len(today_logs)
            
            stats_text = f"""
            📊 Tổng quan hệ thống:
            
            👥 Tổng số nhân viên: {total_employees}
            📝 Tổng lượt chấm công: {total_logs}
            ⚠️ Số lần đi muộn: {total_late}
            
            📅 Hôm nay ({today}):
            ✓ Đã chấm công: {today_count} lượt
            """
            
            self.stats_label.config(text=stats_text)
        except Exception as e:
            self.stats_label.config(text=f"Lỗi: {str(e)}")
    
    def on_closing(self):
        """Xử lý khi đóng ứng dụng"""
        self.stop_camera()
        self.root.destroy()


def main():
    """Main function"""
    print("=" * 60)
    print("🚀 AI ATTENDANCE SYSTEM - ANTI-SPOOFING")
    print("=" * 60)
    
    root = tk.Tk()
    app = AttendanceApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
