# -*- coding: utf-8 -*-
"""
Module Anti-Spoofing - Phát hiện giả mạo khuôn mặt
Anti-Spoofing Module for Face Liveness Detection
"""

import cv2
import numpy as np
from scipy import ndimage
import config
import os

class AntiSpoofing:
    """Class phát hiện giả mạo khuôn mặt (printed photo, video replay, 3D mask)"""
    
    def __init__(self):
        """Khởi tạo Anti-Spoofing detector"""
        self.blink_counter = 0
        self.blink_frames = []
        self.prev_ear = 0
        
        # Load Haar Cascade cho phát hiện mắt
        self.eye_cascade = None
        cascade_candidates = []
        try:
            cascade_candidates.append(cv2.data.haarcascades + 'haarcascade_eye.xml')
        except Exception:
            pass

        # Try to find cascade relative to cv2 package
        try:
            cv2_pkg = os.path.dirname(cv2.__file__)
            cascade_candidates.append(os.path.join(cv2_pkg, 'data', 'haarcascade_eye.xml'))
        except Exception:
            pass

        # Try local project paths
        cascade_candidates.append(os.path.join(os.getcwd(), 'data', 'models', 'haarcascade_eye.xml'))
        cascade_candidates.append(os.path.join(os.path.dirname(__file__), 'data', 'models', 'haarcascade_eye.xml'))

        loaded = False
        for p in cascade_candidates:
            if not p:
                continue
            try:
                if os.path.exists(p):
                    clf = cv2.CascadeClassifier(p)
                    # Check if loaded
                    if hasattr(clf, 'empty') and not clf.empty():
                        self.eye_cascade = clf
                        print(f"✅ Loaded eye cascade from: {p}")
                        loaded = True
                        break
            except Exception as e:
                # continue to next candidate
                print(f"⚠️ Error loading cascade from {p}: {e}")
                continue

        if not loaded:
            # As a last resort try default constructor (may still fail internally)
            try:
                clf = cv2.CascadeClassifier()
                if hasattr(clf, 'empty') and not clf.empty():
                    self.eye_cascade = clf
                    print("✅ Loaded default CascadeClassifier (no file path)")
                else:
                    self.eye_cascade = None
                    print("⚠️ Eye cascade not available; eye-based anti-spoofing disabled.")
            except Exception:
                self.eye_cascade = None
                print("⚠️ Eye cascade not available; eye-based anti-spoofing disabled.")
    
    def calculate_ear(self, eye_landmarks):
        """
        Tính Eye Aspect Ratio (EAR) để phát hiện nháy mắt
        
        Args:
            eye_landmarks: Tọa độ các điểm landmark của mắt
        
        Returns:
            ear: Eye Aspect Ratio
        """
        # EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
        # p1-p6 là các điểm landmark của mắt
        
        if eye_landmarks is None or len(eye_landmarks) < 6:
            return 0.0
        
        # Tính khoảng cách vertical
        vertical1 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        vertical2 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        
        # Tính khoảng cách horizontal
        horizontal = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        
        if horizontal == 0:
            return 0.0
        
        ear = (vertical1 + vertical2) / (2.0 * horizontal)
        return ear
    
    def detect_blink(self, landmarks):
        """
        Phát hiện nháy mắt dựa trên EAR
        
        Args:
            landmarks: Face landmarks từ MTCNN (5 điểm)
        
        Returns:
            is_blinking: True nếu đang nháy mắt
            blink_detected: True nếu phát hiện được nháy mắt hoàn chỉnh
        """
        if landmarks is None:
            return False, False
        
        # MTCNN trả về 5 landmarks: left_eye, right_eye, nose, mouth_left, mouth_right
        left_eye = landmarks[0]
        right_eye = landmarks[1]
        
        # Giả lập EAR đơn giản dựa trên vị trí mắt
        # (Trong thực tế, cần 68 landmarks để tính EAR chính xác)
        eye_distance = np.linalg.norm(left_eye - right_eye)
        
        # Giả định: nếu không có landmarks chi tiết, sử dụng phương pháp đơn giản
        # Lưu vào buffer để phát hiện pattern
        self.blink_frames.append(eye_distance)
        
        if len(self.blink_frames) > 10:
            self.blink_frames.pop(0)
        
        # Phát hiện biến động đột ngột (có thể là nháy mắt)
        if len(self.blink_frames) >= 5:
            variance = np.var(self.blink_frames)
            if variance > 10:  # Threshold
                return True, True
        
        return False, False
    
    def texture_analysis(self, face_image):
        """
        Phân tích texture để phát hiện ảnh in
        Ảnh in thường có texture đồng nhất hơn khuôn mặt thật
        
        Args:
            face_image: numpy array (RGB)
        
        Returns:
            score: Điểm liveness (0-1), càng cao càng giống người thật
        """
        # Convert sang grayscale
        gray = cv2.cvtColor(face_image, cv2.COLOR_RGB2GRAY)
        
        # 1. Phân tích Local Binary Pattern (LBP)
        lbp = self._compute_lbp(gray)
        lbp_variance = np.var(lbp)
        
        # 2. Phân tích frequency domain (FFT)
        fft = np.fft.fft2(gray)
        fft_shift = np.fft.fftshift(fft)
        magnitude = np.abs(fft_shift)
        
        # Khuôn mặt thật có nhiều high-frequency components hơn
        h, w = magnitude.shape
        center_h, center_w = h // 2, w // 2
        high_freq = magnitude[0:center_h//2, :].sum() + magnitude[center_h+center_h//2:, :].sum()
        total_freq = magnitude.sum()
        high_freq_ratio = high_freq / (total_freq + 1e-6)
        
        # 3. Phân tích edge density
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (gray.shape[0] * gray.shape[1])
        
        # 4. Phân tích color distribution
        # Khuôn mặt thật có phân bố màu phức tạp hơn
        hsv = cv2.cvtColor(face_image, cv2.COLOR_RGB2HSV)
        hist = cv2.calcHist([hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
        hist_variance = np.var(hist)
        
        # Tổng hợp các chỉ số
        # Normalize và weighted sum
        lbp_score = min(lbp_variance / 1000, 1.0) * 0.25
        freq_score = min(high_freq_ratio * 10, 1.0) * 0.25
        edge_score = min(edge_density * 20, 1.0) * 0.25
        color_score = min(hist_variance / 10000, 1.0) * 0.25
        
        total_score = lbp_score + freq_score + edge_score + color_score
        
        return total_score
    
    def _compute_lbp(self, image):
        """Tính Local Binary Pattern"""
        rows, cols = image.shape
        lbp = np.zeros((rows-2, cols-2), dtype=np.uint8)
        
        for i in range(1, rows-1):
            for j in range(1, cols-1):
                center = image[i, j]
                code = 0
                
                # 8 neighbors
                code |= (image[i-1, j-1] > center) << 7
                code |= (image[i-1, j] > center) << 6
                code |= (image[i-1, j+1] > center) << 5
                code |= (image[i, j+1] > center) << 4
                code |= (image[i+1, j+1] > center) << 3
                code |= (image[i+1, j] > center) << 2
                code |= (image[i+1, j-1] > center) << 1
                code |= (image[i, j-1] > center) << 0
                
                lbp[i-1, j-1] = code
        
        return lbp
    
    def motion_analysis(self, current_frame, prev_frame):
        """
        Phân tích chuyển động để phát hiện video replay
        Video replay thường có chuyển động không tự nhiên
        
        Args:
            current_frame: Frame hiện tại (RGB)
            prev_frame: Frame trước đó (RGB)
        
        Returns:
            score: Điểm liveness (0-1)
        """
        if prev_frame is None:
            return 0.5
        
        # Check if sizes match
        if current_frame.shape != prev_frame.shape:
            return 0.5
        
        # Convert sang grayscale
        gray1 = cv2.cvtColor(prev_frame, cv2.COLOR_RGB2GRAY)
        gray2 = cv2.cvtColor(current_frame, cv2.COLOR_RGB2GRAY)
        
        # Resize to same size if needed
        if gray1.shape != gray2.shape:
            gray2 = cv2.resize(gray2, (gray1.shape[1], gray1.shape[0]))
        
        # Tính optical flow
        flow = cv2.calcOpticalFlowFarneback(
            gray1, gray2, None,
            pyr_scale=0.5, levels=3, winsize=15,
            iterations=3, poly_n=5, poly_sigma=1.2, flags=0
        )
        
        # Tính magnitude và angle
        magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        
        # Video replay thường có pattern chuyển động đồng nhất
        # Người thật có vi chuyển động (micro-movements) tự nhiên hơn
        
        # 1. Tính variance của magnitude
        mag_variance = np.var(magnitude)
        
        # 2. Tính entropy của angle distribution
        angle_hist, _ = np.histogram(angle, bins=36, range=(0, 2*np.pi))
        angle_hist = angle_hist / (angle_hist.sum() + 1e-6)
        entropy = -np.sum(angle_hist * np.log2(angle_hist + 1e-6))
        
        # 3. Tính average magnitude
        avg_magnitude = np.mean(magnitude)
        
        # Scoring
        variance_score = min(mag_variance / 10, 1.0) * 0.4
        entropy_score = min(entropy / 5, 1.0) * 0.3
        magnitude_score = min(avg_magnitude / 5, 1.0) * 0.3
        
        total_score = variance_score + entropy_score + magnitude_score
        
        return total_score
    
    def depth_analysis(self, face_image):
        """
        Phân tích độ sâu để phát hiện mặt nạ 3D hoặc ảnh phẳng
        
        Args:
            face_image: numpy array (RGB)
        
        Returns:
            score: Điểm liveness (0-1)
        """
        # Convert sang grayscale
        gray = cv2.cvtColor(face_image, cv2.COLOR_RGB2GRAY)
        
        # 1. Phân tích gradient để ước lượng độ sâu
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
        
        gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
        
        # 2. Phân tích shadow và highlight
        # Khuôn mặt 3D thật có shadow/highlight tự nhiên
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Tính ratio của dark và bright regions
        dark_ratio = np.sum(binary == 0) / binary.size
        bright_ratio = np.sum(binary == 255) / binary.size
        
        # 3. Phân tích contour complexity
        contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contour_complexity = len(contours)
        
        # Scoring
        gradient_score = min(np.mean(gradient_magnitude) / 50, 1.0) * 0.4
        contrast_score = min(abs(dark_ratio - bright_ratio) * 5, 1.0) * 0.3
        complexity_score = min(contour_complexity / 100, 1.0) * 0.3
        
        total_score = gradient_score + contrast_score + complexity_score
        
        return total_score
    
    def check_liveness(self, face_image, landmarks=None, prev_frame=None):
        """
        Kiểm tra tổng hợp liveness
        
        Args:
            face_image: numpy array (RGB)
            landmarks: Face landmarks từ MTCNN
            prev_frame: Frame trước đó để phân tích motion
        
        Returns:
            is_real: True nếu là người thật
            score: Điểm liveness (0-1)
            details: Dictionary chứa chi tiết các phương pháp
        """
        scores = {}
        
        # 1. Texture analysis
        if config.USE_TEXTURE_ANALYSIS:
            texture_score = self.texture_analysis(face_image)
            scores['texture'] = texture_score
        
        # 2. Blink detection
        if config.USE_BLINK_DETECTION and landmarks is not None:
            is_blinking, blink_detected = self.detect_blink(landmarks)
            scores['blink'] = 1.0 if blink_detected else 0.3
        
        # 3. Motion analysis
        if config.USE_MOTION_ANALYSIS and prev_frame is not None:
            motion_score = self.motion_analysis(face_image, prev_frame)
            scores['motion'] = motion_score
        
        # 4. Depth analysis
        if config.USE_DEPTH_ANALYSIS:
            depth_score = self.depth_analysis(face_image)
            scores['depth'] = depth_score
        
        # Tính tổng điểm (weighted average)
        if len(scores) > 0:
            total_score = np.mean(list(scores.values()))
        else:
            total_score = 0.5
        
        # Quyết định
        is_real = total_score >= config.LIVENESS_THRESHOLD
        
        return is_real, total_score, scores


# Test module
if __name__ == "__main__":
    print("🧪 Testing Anti-Spoofing Module...")
    
    detector = AntiSpoofing()
    
    # Test với webcam
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    prev_frame = None
    
    print("📹 Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Test anti-spoofing
        is_real, score, details = detector.check_liveness(frame, prev_frame=prev_frame)
        
        # Display results
        color = (0, 255, 0) if is_real else (0, 0, 255)
        status = "REAL" if is_real else "FAKE"
        
        cv2.putText(frame, f"Status: {status}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(frame, f"Score: {score:.2f}", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        # Display detail scores
        y_pos = 110
        for method, method_score in details.items():
            cv2.putText(frame, f"{method}: {method_score:.2f}", (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            y_pos += 30
        
        cv2.imshow('Anti-Spoofing Test', frame)
        
        prev_frame = frame.copy()
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Test completed!")
