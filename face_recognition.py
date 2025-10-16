# -*- coding: utf-8 -*-
"""
Module Face Detection và Recognition sử dụng MTCNN và FaceNet
Face Detection & Recognition Module using MTCNN and FaceNet
"""

import cv2
import numpy as np
import torch
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
import config
import pymongo

#Kết nối MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["face_db"]
col = db["faces"]

class FaceRecognizer:
    def delete_all_employees(self):
        """Xóa toàn bộ dữ liệu nhân viên khỏi RAM và MongoDB"""
        self.known_embeddings = {}
        self.known_names = {}
        col.delete_many({})
        print("Đã xóa toàn bộ dữ liệu nhân viên khỏi hệ thống.")
    def delete_employee(self, employee_id):
        """Xóa dữ liệu nhân viên khỏi RAM và MongoDB"""
        # Xóa khỏi RAM
        if employee_id in self.known_embeddings:
            del self.known_embeddings[employee_id]
        if employee_id in self.known_names:
            del self.known_names[employee_id]
        # Xóa trên MongoDB
        col.delete_one({"employee_id": employee_id})
        print(f"Đã xóa nhân viên {employee_id} khỏi hệ thống.")
    """Class nhận diện khuôn mặt sử dụng MTCNN và FaceNet"""
    
    def __init__(self):
        """Khởi tạo MTCNN và FaceNet model"""
        # Kiểm tra GPU
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"🖥️  Using device: {self.device}")
        
        # Khởi tạo MTCNN cho face detection
        self.mtcnn = MTCNN(
            image_size=config.FACENET_IMAGE_SIZE,
            margin=0,
            min_face_size=config.MTCNN_MIN_FACE_SIZE,
            thresholds=config.MTCNN_THRESHOLDS,
            factor=config.MTCNN_FACTOR,
            post_process=True,
            device=self.device,
            keep_all=True  # Detect tất cả khuôn mặt trong ảnh
        )
        
        # Khởi tạo FaceNet (InceptionResnetV1) để extract embeddings
        print("⏳ Loading FaceNet model...")
        self.facenet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        print("✅ FaceNet model loaded successfully!")
        
        # Dictionary lưu face embeddings
        self.known_embeddings = {}
        self.known_names = {} 

    def save_face_to_mongodb(self, employee_id, name, embedding):
        doc = {
            "employee_id": employee_id,
            "name": name,
            "embedding": embedding.tolist()  # numpy array -> list
        }
        col.replace_one({"employee_id": employee_id}, doc, upsert=True)
        print(f"Đã lưu khuôn mặt {name} vào MongoDB.")

    def load_all_embeddings_from_mongodb(self):
        faces = list(col.find({}))
        self.known_embeddings = {f["employee_id"]: np.array(f["embedding"]) for f in faces}
        self.known_names = {f["employee_id"]: f["name"] for f in faces}
        print(f"Đã tải {len(self.known_embeddings)} khuôn mặt từ MongoDB.")
    def detect_faces(self, image):
        """
        Phát hiện khuôn mặt trong ảnh sử dụng MTCNN
        
        Args:
            image: numpy array (BGR format from OpenCV)
        
        Returns:
            faces: List of face tensors
            boxes: List of bounding boxes [x1, y1, x2, y2]
            probs: List of confidence scores
        """
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        boxes, probs, landmarks = self.mtcnn.detect(image_rgb, landmarks=True)
        
        if boxes is None:
            return None, None, None, None
        
        # Filter faces with confidence > threshold
        valid_indices = probs > config.MIN_CONFIDENCE
        boxes = boxes[valid_indices]
        probs = probs[valid_indices]
        
        if landmarks is not None:
            landmarks = landmarks[valid_indices]
        
        if len(boxes) == 0:
            return None, None, None, None
        
        # Extract and align faces
        faces = []
        for box in boxes:
            x1, y1, x2, y2 = [int(b) for b in box]
            
            # Kiểm tra box hợp lệ
            if x2 <= x1 or y2 <= y1:
                continue
                
            face = image_rgb[y1:y2, x1:x2]
            
            # Kiểm tra face không rỗng
            if face.size == 0 or face.shape[0] == 0 or face.shape[1] == 0:
                continue
            
            # Resize to FaceNet input size
            face = cv2.resize(face, (config.FACENET_IMAGE_SIZE, config.FACENET_IMAGE_SIZE))
            faces.append(face)
        
        return faces, boxes, probs, landmarks
    
    def get_embedding(self, face_image):
        """
        Trích xuất face embedding từ ảnh khuôn mặt
        
        Args:
            face_image: numpy array (RGB format)
        
        Returns:
            embedding: 512-dimensional vector
        """
        # Convert to tensor
        face_tensor = torch.from_numpy(face_image).permute(2, 0, 1).float()
        face_tensor = (face_tensor - 127.5) / 128.0  # Normalize
        face_tensor = face_tensor.unsqueeze(0).to(self.device)
        
        # Get embedding
        with torch.no_grad():
            embedding = self.facenet(face_tensor)
        
        return embedding.cpu().numpy()[0]
    
    def register_face(self, employee_id, name, face_images):
        """
        Đăng ký khuôn mặt mới
        
        Args:
            employee_id: ID nhân viên
            name: Tên nhân viên
            face_images: List các ảnh khuôn mặt (RGB format)
        
        Returns:
            success: True nếu đăng ký thành công
        """
        embeddings = []
        
        for face_image in face_images:
            embedding = self.get_embedding(face_image)
            embeddings.append(embedding)
        
        # Tính embedding trung bình
        avg_embedding = np.mean(embeddings, axis=0)
        #Lưu vào MongoDB
        self.save_face_to_mongodb(employee_id, name, avg_embedding)
        # Lưu vào dictionary
        self.known_embeddings[employee_id] = avg_embedding
        self.known_names[employee_id] = name
        
        print(f"✅ Registered face for {name} (ID: {employee_id})")
        return True
    
    def recognize_face(self, face_image):
        """
        Nhận diện khuôn mặt
        
        Args:
            face_image: numpy array (RGB format)
        
        Returns:
            employee_id: ID của nhân viên (hoặc None)
            name: Tên nhân viên (hoặc "Unknown")
            distance: Khoảng cách Euclidean
        """
        if len(self.known_embeddings) == 0:
            return None, "Unknown", 1.0
        
        # Get embedding của khuôn mặt cần nhận diện
        embedding = self.get_embedding(face_image)
        
        # So sánh với tất cả embeddings đã lưu
        min_distance = float('inf')
        best_match_id = None
        
        for employee_id, known_embedding in self.known_embeddings.items():
            # Tính Euclidean distance
            distance = np.linalg.norm(embedding - known_embedding)
            
            if distance < min_distance:
                min_distance = distance
                best_match_id = employee_id
        
        # Kiểm tra threshold
        if min_distance < config.FACE_RECOGNITION_THRESHOLD:
            name = self.known_names.get(best_match_id, "Unknown")
            return best_match_id, name, min_distance
        else:
            return None, "Unknown", min_distance
    
    def load_embeddings(self, embeddings_dict):
        """Load face embeddings từ database"""
        self.known_embeddings = embeddings_dict.get('embeddings', {})
        self.known_names = embeddings_dict.get('names', {})
        print(f"✅ Loaded {len(self.known_embeddings)} face embeddings")
    
    def save_embeddings(self):
        """Lưu face embeddings"""
        return {
            'embeddings': self.known_embeddings,
            'names': self.known_names
        }
    
    def draw_detections(self, image, boxes, names, probs):
        """
        Vẽ bounding boxes và tên lên ảnh
        
        Args:
            image: numpy array (BGR)
            boxes: List of bounding boxes
            names: List of names
            probs: List of confidence scores
        
        Returns:
            image: Ảnh đã vẽ annotations
        """
        image_draw = image.copy()
        
        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = [int(b) for b in box]
            name = names[i] if i < len(names) else "Unknown"
            prob = probs[i] if i < len(probs) else 0.0
            
            # Chọn màu
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            
            # Vẽ bounding box
            cv2.rectangle(image_draw, (x1, y1), (x2, y2), color, 2)
            
            # Vẽ label
            label = f"{name} ({prob:.2f})"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(image_draw, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), color, -1)
            cv2.putText(image_draw, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return image_draw

    def clear_memory(self):
        """Xóa toàn bộ dữ liệu khuôn mặt trong RAM"""
        self.known_embeddings = {}
        self.known_names = {}
        print("Đã xóa toàn bộ dữ liệu khuôn mặt trong RAM.")


# Test module
if __name__ == "__main__":
    print("🧪 Testing Face Recognition Module...")
    
    # Khởi tạo
    recognizer = FaceRecognizer()
    # Xóa toàn bộ dữ liệu nhân viên khỏi RAM và MongoDB
    recognizer.delete_all_employees()
    print("Đã xóa sạch toàn bộ dữ liệu nhân viên!")
    
    # Test với webcam
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    
    print("📹 Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, -1)
        faces, boxes, probs, landmarks = recognizer.detect_faces(frame)
        
        if boxes is not None:
            # Draw detections
            names = ["Unknown"] * len(boxes)
            frame = recognizer.draw_detections(frame, boxes, names, probs)
        
        # Display
        cv2.imshow('Face Detection Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Test completed!")
  