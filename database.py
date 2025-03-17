import sqlite3
from datetime import datetime
from security import SecurityManager
import logging

class DatabaseManager:
    def __init__(self, db_name, security_manager):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.security = security_manager
        self.setup_database()
        logging.basicConfig(filename='school_fee_system.log', level=logging.INFO)

    def setup_database(self):
        try:
            # Updated users table to include security question and answer
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                               (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, 
                               security_question TEXT, security_answer TEXT)''')
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS students
                               (id INTEGER PRIMARY KEY, name TEXT, form TEXT, 
                               parent_email TEXT, parent_phone TEXT, 
                               total_paid INTEGER DEFAULT 0)''')
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS payments
                               (id INTEGER PRIMARY KEY, student_id INTEGER, 
                               amount INTEGER, date TEXT,
                               FOREIGN KEY(student_id) REFERENCES students(id))''')
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Database setup failed: {str(e)}")

    def has_users(self):
        self.cursor.execute("SELECT COUNT(*) FROM users")
        return self.cursor.fetchone()[0] > 0

    def register_user(self, username, password, question, answer):
        hashed_password = self.security.hash_password(password)
        hashed_answer = self.security.hash_password(answer)
        try:
            self.cursor.execute("INSERT INTO users (username, password, security_question, security_answer) VALUES (?, ?, ?, ?)",
                              (username, hashed_password, question, hashed_answer))
            self.conn.commit()
            logging.info(f"User registered: {username}")
        except sqlite3.Error as e:
            logging.error(f"User registration failed: {str(e)}")
            raise

    def authenticate_user(self, username, password):
        hashed = self.security.hash_password(password)
        self.cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed))
        return self.cursor.fetchone() is not None

    def get_user_security_info(self, username):
        self.cursor.execute("SELECT username, security_question, security_answer FROM users WHERE username=?", (username,))
        return self.cursor.fetchone()

    def verify_security_answer(self, username, answer):
        hashed_answer = self.security.hash_password(answer)
        self.cursor.execute("SELECT security_answer FROM users WHERE username=?", (username,))
        stored_answer = self.cursor.fetchone()
        return stored_answer and stored_answer[0] == hashed_answer

    def update_password(self, username, new_password):
        hashed = self.security.hash_password(new_password)
        self.cursor.execute("UPDATE users SET password=? WHERE username=?", (hashed, username))
        self.conn.commit()
        logging.info(f"Password updated for user: {username}")

    def add_student(self, name, form, email, phone):
        encrypted_email = self.security.encrypt_data(email)
        encrypted_phone = self.security.encrypt_data(phone)
        self.cursor.execute("INSERT INTO students (name, form, parent_email, parent_phone) VALUES (?, ?, ?, ?)",
                          (name, form, encrypted_email, encrypted_phone))
        self.conn.commit()

    def update_payment(self, student_id, amount):
        self.cursor.execute("SELECT total_paid FROM students WHERE id=?", (student_id,))
        total_paid = self.cursor.fetchone()[0]
        new_total = total_paid + amount
        self.cursor.execute("UPDATE students SET total_paid=? WHERE id=?", (new_total, student_id))
        self.cursor.execute("INSERT INTO payments (student_id, amount, date) VALUES (?, ?, ?)",
                          (student_id, amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.conn.commit()
        return new_total

    def get_student(self, student_id):
        self.cursor.execute("SELECT name, form, parent_email, parent_phone, total_paid FROM students WHERE id=?", 
                          (student_id,))
        row = self.cursor.fetchone()
        if row:
            name, form, enc_email, enc_phone, total_paid = row
            return (name, form, self.security.decrypt_data(enc_email), 
                   self.security.decrypt_data(enc_phone), total_paid)
        return None

    def get_all_students(self):
        self.cursor.execute("SELECT id, name, form, total_paid FROM students")
        return self.cursor.fetchall()

    def search_students(self, term):
        self.cursor.execute("SELECT id, name, form, total_paid FROM students WHERE name LIKE ? OR id LIKE ?",
                          (f"%{term}%", f"%{term}%"))
        return self.cursor.fetchall()

    def get_payment_history(self, student_id):
        self.cursor.execute("SELECT date, amount FROM payments WHERE student_id=?", (student_id,))
        return self.cursor.fetchall()