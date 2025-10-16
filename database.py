# -*- coding: utf-8 -*-
"""
Module quản lý Database cho hệ thống chấm công
Database Management Module for Attendance System
"""

import sqlite3
import pickle
import os
from datetime import datetime
import pandas as pd
import config

try:
    import pymongo
except Exception:
    pymongo = None

class DatabaseManager:
    """Quản lý database SQLite cho hệ thống chấm công"""
    
    def __init__(self):
        self.db_path = config.DATABASE_PATH
        self.embeddings_path = config.EMBEDDINGS_PATH
        # Initialize MongoDB client for storing embeddings (optional)
        self.mongo_client = None
        self.mongo_db = None
        self.mongo_collection = None
        if pymongo is not None:
            try:
                self.mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
                self.mongo_db = self.mongo_client.get_database('face_db')
                self.mongo_collection = self.mongo_db.get_collection('faces')
            except Exception as e:
                print(f"⚠️ Failed to initialize MongoDB client: {e}")
        self.init_database()
    
    def init_database(self):
        """Khởi tạo database và các bảng cần thiết"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Bảng nhân viên
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                department TEXT,
                position TEXT,
                email TEXT,
                phone TEXT,
                date_registered TEXT NOT NULL,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        # Bảng lịch sử chấm công
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL,
                datetime TEXT NOT NULL,
                type TEXT NOT NULL,
                status TEXT NOT NULL,
                confidence REAL,
                is_late INTEGER DEFAULT 0,
                notes TEXT,
                FOREIGN KEY (employee_id) REFERENCES employees (employee_id)
            )
        ''')
        
        # Bảng lưu thông tin anti-spoofing
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS spoofing_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                datetime TEXT NOT NULL,
                liveness_score REAL,
                is_real INTEGER,
                detection_method TEXT,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully!")
    
    def add_employee(self, employee_id, name, department="", position="", email="", phone=""):
        """Thêm nhân viên mới"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO employees (employee_id, name, department, position, email, phone, date_registered)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (employee_id, name, department, position, email, phone, datetime.now().strftime(config.DATETIME_FORMAT)))
            
            conn.commit()
            print(f"✅ Added employee: {name} (ID: {employee_id})")
            return True
        except sqlite3.IntegrityError:
            print(f"❌ Employee ID {employee_id} already exists!")
            return False
        finally:
            conn.close()
    
    def get_employee(self, employee_id):
        """Lấy thông tin nhân viên"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM employees WHERE employee_id = ? AND is_active = 1', (employee_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'employee_id': result[1],
                'name': result[2],
                'department': result[3],
                'position': result[4],
                'email': result[5],
                'phone': result[6],
                'date_registered': result[7],
                'is_active': result[8]
            }
        return None
    
    def get_all_employees(self):
        """Lấy danh sách tất cả nhân viên"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM employees WHERE is_active = 1 ORDER BY name')
        results = cursor.fetchall()
        conn.close()
        
        employees = []
        for result in results:
            employees.append({
                'id': result[0],
                'employee_id': result[1],
                'name': result[2],
                'department': result[3],
                'position': result[4],
                'email': result[5],
                'phone': result[6],
                'date_registered': result[7]
            })
        return employees
    
    def delete_employee(self, employee_id):
        """Xóa nhân viên (soft delete)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE employees SET is_active = 0 WHERE employee_id = ?', (employee_id,))
        conn.commit()
        conn.close()
        print(f"✅ Deleted employee ID: {employee_id}")
    
    def log_attendance(self, employee_id, attendance_type, status, confidence=0.0, is_late=0, notes=""):
        """Ghi nhận chấm công"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO attendance_logs (employee_id, datetime, type, status, confidence, is_late, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (employee_id, datetime.now().strftime(config.DATETIME_FORMAT), 
              attendance_type, status, confidence, is_late, notes))
        
        conn.commit()
        conn.close()
        print(f"✅ Logged attendance: {employee_id} - {attendance_type} - {status}")
    
    def get_attendance_logs(self, start_date=None, end_date=None, employee_id=None):
        """Lấy lịch sử chấm công"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT a.*, e.name, e.department 
            FROM attendance_logs a
            JOIN employees e ON a.employee_id = e.employee_id
            WHERE 1=1
        '''
        params = []
        
        if start_date:
            query += ' AND datetime >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND datetime <= ?'
            params.append(end_date)
        
        if employee_id:
            query += ' AND a.employee_id = ?'
            params.append(employee_id)
        
        query += ' ORDER BY datetime DESC'
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        logs = []
        for result in results:
            logs.append({
                'id': result[0],
                'employee_id': result[1],
                'datetime': result[2],
                'type': result[3],
                'status': result[4],
                'confidence': result[5],
                'is_late': result[6],
                'notes': result[7],
                'employee_name': result[8],
                'department': result[9]
            })
        return logs
    
    def get_last_checkin(self, employee_id, date=None):
        """Lấy lần chấm công cuối cùng của nhân viên"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if date is None:
            date = datetime.now().strftime(config.DATE_FORMAT)
        
        cursor.execute('''
            SELECT * FROM attendance_logs 
            WHERE employee_id = ? AND datetime LIKE ?
            ORDER BY datetime DESC LIMIT 1
        ''', (employee_id, f"{date}%"))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'employee_id': result[1],
                'datetime': result[2],
                'type': result[3],
                'status': result[4],
                'confidence': result[5],
                'is_late': result[6],
                'notes': result[7]
            }
        return None
    
    def log_spoofing_attempt(self, liveness_score, is_real, method, notes=""):
        """Ghi nhận phát hiện giả mạo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO spoofing_logs (datetime, liveness_score, is_real, detection_method, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().strftime(config.DATETIME_FORMAT), liveness_score, is_real, method, notes))
        
        conn.commit()
        conn.close()
    
    def save_face_embeddings(self, embeddings_dict):
        """Lưu face embeddings"""
        # embeddings_dict expected shape: {'embeddings': {id: vector, ...}, 'names': {id: name, ...}}
        embeddings = None
        names = None
        if isinstance(embeddings_dict, dict):
            embeddings = embeddings_dict.get('embeddings')
            names = embeddings_dict.get('names')

        # If MongoDB is available, persist embeddings there (preferred)
        if self.mongo_collection is not None:
            try:
                # If there are no embeddings, clear the collection
                if not embeddings or len(embeddings) == 0:
                    self.mongo_collection.delete_many({})
                    print(f"✅ No embeddings left — cleared MongoDB collection: {self.mongo_collection.name}")
                    return

                # Upsert each embedding document
                for emp_id, emb in embeddings.items():
                    doc = {
                        'employee_id': emp_id,
                        'embedding': emb.tolist() if hasattr(emb, 'tolist') else emb,
                        'name': names.get(emp_id) if names else None,
                        'updated_at': datetime.now().strftime(config.DATETIME_FORMAT)
                    }
                    self.mongo_collection.replace_one({'employee_id': emp_id}, doc, upsert=True)

                print(f"✅ Saved {len(embeddings)} face embeddings to MongoDB collection: {self.mongo_collection.name}")
                return
            except Exception as e:
                print(f"⚠️ Failed to save embeddings to MongoDB: {e}")

        # Fallback: save to local file (legacy)
        try:
            with open(self.embeddings_path, 'wb') as f:
                pickle.dump(embeddings_dict, f)
            print(f"✅ Saved {len(embeddings or {})} face embeddings to: {self.embeddings_path}")
        except Exception as e:
            print(f"⚠️ Failed to save embeddings to file: {e}")
    
    def load_face_embeddings(self):
        """Đọc face embeddings"""
        # Try to load from MongoDB first
        if self.mongo_collection is not None:
            try:
                docs = list(self.mongo_collection.find({}))
                embeddings = {}
                names = {}
                for d in docs:
                    emp_id = d.get('employee_id')
                    emb = d.get('embedding')
                    if emp_id and emb is not None:
                        embeddings[emp_id] = emb
                        names[emp_id] = d.get('name')
                print(f"✅ Loaded {len(embeddings)} face embeddings from MongoDB")
                return {'embeddings': embeddings, 'names': names}
            except Exception as e:
                print(f"⚠️ Failed to load embeddings from MongoDB: {e}")

        # Fallback: load from local file (legacy)
        if os.path.exists(self.embeddings_path):
            try:
                with open(self.embeddings_path, 'rb') as f:
                    embeddings = pickle.load(f)
                print(f"✅ Loaded {len(embeddings.get('embeddings',{}))} face embeddings from file")
                return embeddings
            except Exception as e:
                print(f"⚠️ Failed to load embeddings from file: {e}")

        return {}
    
    def export_to_excel(self, start_date=None, end_date=None, output_path=None):
        """Xuất báo cáo ra Excel"""
        logs = self.get_attendance_logs(start_date, end_date)
        
        if not logs:
            print("❌ No data to export!")
            return None
        
        df = pd.DataFrame(logs)
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(config.REPORTS_DIR, f"attendance_report_{timestamp}.xlsx")
        
        # Tạo Excel writer với nhiều sheets
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Sheet 1: Chi tiết chấm công
            df.to_excel(writer, sheet_name='Chi tiết', index=False)
            
            # Sheet 2: Thống kê theo nhân viên
            summary = df.groupby('employee_name').agg({
                'id': 'count',
                'is_late': 'sum',
                'confidence': 'mean'
            }).reset_index()
            summary.columns = ['Nhân viên', 'Số lần chấm công', 'Số lần đi muộn', 'Độ tin cậy TB']
            summary.to_excel(writer, sheet_name='Thống kê', index=False)
        
        print(f"✅ Exported report to: {output_path}")
        return output_path

# Test
if __name__ == "__main__":
    db = DatabaseManager()
    
    # Test thêm nhân viên
    # db.add_employee("NV001", "Nguyễn Văn A", "IT", "Developer", "nva@company.com", "0123456789")
    # db.add_employee("NV002", "Trần Thị B", "HR", "Manager", "ttb@company.com", "0987654321")
    
    # Test lấy danh sách nhân viên
    employees = db.get_all_employees()
    print(f"\n📋 Total employees: {len(employees)}")
    for emp in employees:
        print(f"  - {emp['name']} ({emp['employee_id']})")
