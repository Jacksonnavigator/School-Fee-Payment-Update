import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import platform
import re
import os
from datetime import datetime

class UIManager:
    def __init__(self, root, db_manager, notif_manager, backup_manager, fee_structure, security_manager):
        self.root = root
        self.root.title("School Fee Management System")
        self.root.geometry("1200x800")
        self.root.configure(bg="#e6f3fa")  # Light blue background
        self.db = db_manager
        self.notif = notif_manager
        self.backup = backup_manager
        self.fee_structure = fee_structure
        self.security = security_manager
        self.logged_in = False
        
        # Configure ttk style for modern look
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TButton", font=("Arial", 10, "bold"), padding=5)
        self.style.configure("TLabel", font=("Arial", 11), background="#e6f3fa")
        self.style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#3498db", foreground="white")
        self.style.configure("Treeview", font=("Arial", 10), rowheight=25)
        self.style.map("TButton", background=[('active', '#2980b9')], foreground=[('active', 'white')])
        
        # Hide root window until login
        self.root.withdraw()
        self.show_login()

    def validate_email(self, value):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, value) is not None

    def validate_phone(self, value):
        pattern = r'^\+\d{10,15}$'
        return re.match(pattern, value) is not None

    def show_login(self):
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Login")
        self.login_window.geometry("300x250")  # Increased height for extra button
        self.login_window.configure(bg="#d5e8f7")  # Soft blue background
        self.login_window.resizable(False, False)  # Prevent resizing

        ttk.Label(self.login_window, text="Username:", background="#d5e8f7").pack(pady=10)
        self.username_entry = ttk.Entry(self.login_window)
        self.username_entry.pack(pady=5)

        ttk.Label(self.login_window, text="Password:", background="#d5e8f7").pack(pady=10)
        self.password_entry = ttk.Entry(self.login_window, show="*")
        self.password_entry.pack(pady=5)

        ttk.Button(self.login_window, text="Login", style="Accent.TButton",
                  command=lambda: self.authenticate(self.username_entry.get(), self.password_entry.get())).pack(pady=10)

        ttk.Button(self.login_window, text="Forgot Password?", style="Link.TButton",
                  command=self.recover_password).pack(pady=5)

        # Custom button styles
        self.style.configure("Accent.TButton", background="#3498db", foreground="white")
        self.style.configure("Link.TButton", background="#d5e8f7", foreground="#3498db", font=("Arial", 9, "underline"))
        self.style.map("Link.TButton", background=[('active', '#d5e8f7')], foreground=[('active', '#2980b9')])

        # Check if this is the first run
        if not self.db.has_users():
            self.login_window.destroy()
            self.register_first_user()

    def authenticate(self, username, password):
        if self.db.authenticate_user(username, password):
            self.logged_in = True
            self.login_window.destroy()
            self.root.deiconify()  # Show the main window
            self.create_main_ui()
        else:
            messagebox.showerror("Error", "Invalid credentials!")

    def register_first_user(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("Register First User")
        register_window.geometry("400x400")
        register_window.configure(bg="#d5e8f7")
        register_window.resizable(False, False)

        ttk.Label(register_window, text="Register First User", font=("Arial", 14, "bold"), 
                 background="#d5e8f7").pack(pady=20)

        ttk.Label(register_window, text="Username:", background="#d5e8f7").pack(pady=5)
        username_entry = ttk.Entry(register_window)
        username_entry.pack(pady=5)

        ttk.Label(register_window, text="Password:", background="#d5e8f7").pack(pady=5)
        password_entry = ttk.Entry(register_window, show="*")
        password_entry.pack(pady=5)

        ttk.Label(register_window, text="Confirm Password:", background="#d5e8f7").pack(pady=5)
        confirm_entry = ttk.Entry(register_window, show="*")
        confirm_entry.pack(pady=5)

        ttk.Label(register_window, text="Security Question:", background="#d5e8f7").pack(pady=5)
        question_entry = ttk.Entry(register_window)
        question_entry.pack(pady=5)
        question_entry.insert(0, "What is your mother's maiden name?")  # Default suggestion

        ttk.Label(register_window, text="Security Answer:", background="#d5e8f7").pack(pady=5)
        answer_entry = ttk.Entry(register_window, show="*")
        answer_entry.pack(pady=5)

        def register():
            username = username_entry.get().strip()
            password = password_entry.get()
            confirm = confirm_entry.get()
            question = question_entry.get().strip()
            answer = answer_entry.get().strip()

            if not all([username, password, confirm, question, answer]):
                messagebox.showerror("Error", "All fields are required!")
                return
            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match!")
                return
            if len(password) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters!")
                return

            self.db.register_user(username, password, question, answer)
            messagebox.showinfo("Success", "User registered successfully! Please log in.")
            register_window.destroy()
            self.show_login()

        ttk.Button(register_window, text="Register", style="Accent.TButton", command=register).pack(pady=20)

    def recover_password(self):
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter your username first!")
            return

        user_data = self.db.get_user_security_info(username)
        if not user_data:
            messagebox.showerror("Error", "Username not found!")
            return

        _, question, _ = user_data  # Unpack username, question, hashed_answer

        recovery_window = tk.Toplevel(self.root)
        recovery_window.title("Password Recovery")
        recovery_window.geometry("350x250")
        recovery_window.configure(bg="#d5e8f7")

        ttk.Label(recovery_window, text="Security Question:", background="#d5e8f7").pack(pady=10)
        ttk.Label(recovery_window, text=question, background="#d5e8f7", wraplength=300).pack(pady=5)
        answer_entry = ttk.Entry(recovery_window, show="*")
        answer_entry.pack(pady=5)

        def verify_and_reset():
            answer = answer_entry.get().strip()
            if self.db.verify_security_answer(username, answer):
                new_password = simpledialog.askstring("Reset Password", "Enter new password:", show="*", parent=recovery_window)
                if new_password and len(new_password) >= 6:
                    self.db.update_password(username, new_password)
                    messagebox.showinfo("Success", "Password reset successfully! Please log in.")
                    recovery_window.destroy()
                elif new_password:
                    messagebox.showerror("Error", "Password must be at least 6 characters!")
                else:
                    messagebox.showerror("Error", "Password cannot be empty!")
            else:
                messagebox.showerror("Error", "Incorrect answer!")

        ttk.Button(recovery_window, text="Submit", style="Accent.TButton", command=verify_and_reset).pack(pady=20)

    def create_main_ui(self):
        # Header
        header_frame = ttk.Frame(self.root, style="Header.TFrame")
        header_frame.pack(fill="x", pady=10)
        ttk.Label(header_frame, text="School Fee Management System", 
                 font=("Arial", 24, "bold"), foreground="white", background="#2c3e50").pack(pady=10)
        self.style.configure("Header.TFrame", background="#2c3e50")

        # Main frame with scrollable canvas
        main_frame = ttk.Frame(self.root)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Left panel (Student Info)
        left_panel = ttk.LabelFrame(main_frame, text="Student Information", style="Panel.TLabelframe")
        left_panel.pack(side="left", fill="y", padx=10, pady=10)
        self.style.configure("Panel.TLabelframe", background="#ffffff", foreground="#2c3e50")
        self.style.configure("Panel.TLabelframe.Label", font=("Arial", 14, "bold"))

        # Canvas for scrollable left panel
        left_canvas = tk.Canvas(left_panel, bg="#ffffff", highlightthickness=0)
        left_scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=left_canvas.yview)
        left_scrollable_frame = ttk.Frame(left_canvas)
        left_scrollable_frame.bind("<Configure>", lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all")))
        left_canvas.create_window((0, 0), window=left_scrollable_frame, anchor="nw")
        left_canvas.configure(yscrollcommand=left_scrollbar.set)
        left_canvas.pack(side="left", fill="both", expand=True)
        left_scrollbar.pack(side="right", fill="y")

        # Student form fields
        ttk.Label(left_scrollable_frame, text="Student Name:").grid(row=0, column=0, pady=5, padx=10, sticky="w")
        self.name_entry = ttk.Entry(left_scrollable_frame)
        self.name_entry.grid(row=1, column=0, pady=5, padx=10)

        ttk.Label(left_scrollable_frame, text="Form:").grid(row=2, column=0, pady=5, padx=10, sticky="w")
        self.form_combo = ttk.Combobox(left_scrollable_frame, values=list(self.fee_structure.keys()))
        self.form_combo.grid(row=3, column=0, pady=5, padx=10)

        ttk.Label(left_scrollable_frame, text="Parent Email:").grid(row=4, column=0, pady=5, padx=10, sticky="w")
        self.email_entry = ttk.Entry(left_scrollable_frame)
        self.email_entry.config(validate="key", 
                              validatecommand=(self.root.register(self.validate_email_callback), '%P'))
        self.email_entry.grid(row=5, column=0, pady=5, padx=10)

        ttk.Label(left_scrollable_frame, text="Parent Phone:").grid(row=6, column=0, pady=5, padx=10, sticky="w")
        self.phone_entry = ttk.Entry(left_scrollable_frame)
        self.phone_entry.config(validate="key",
                              validatecommand=(self.root.register(self.validate_phone_callback), '%P'))
        self.phone_entry.grid(row=7, column=0, pady=5, padx=10)

        ttk.Label(left_scrollable_frame, text="Search Student:").grid(row=8, column=0, pady=5, padx=10, sticky="w")
        self.search_entry = ttk.Entry(left_scrollable_frame)
        self.search_entry.grid(row=9, column=0, pady=5, padx=10)

        # Buttons with colors
        btn_frame = ttk.Frame(left_scrollable_frame)
        btn_frame.grid(row=10, column=0, pady=20, padx=10)
        ttk.Button(btn_frame, text="Add Student", style="Green.TButton", command=self.add_student).pack(pady=5, fill="x")
        ttk.Button(btn_frame, text="Make Payment", style="Blue.TButton", command=self.make_payment_window).pack(pady=5, fill="x")
        ttk.Button(btn_frame, text="View Records", style="Purple.TButton", command=self.view_records).pack(pady=5, fill="x")
        ttk.Button(btn_frame, text="Search", style="Orange.TButton", command=self.search_student).pack(pady=5, fill="x")
        ttk.Button(btn_frame, text="Payment History", style="Teal.TButton", command=self.view_payment_history).pack(pady=5, fill="x")
        ttk.Button(btn_frame, text="Backup", style="Gray.TButton", command=self.backup_database).pack(pady=5, fill="x")
        ttk.Button(btn_frame, text="Logout", style="Red.TButton", command=self.logout).pack(pady=5, fill="x")

        # Button styles
        self.style.configure("Green.TButton", background="#27ae60", foreground="white")
        self.style.configure("Blue.TButton", background="#3498db", foreground="white")
        self.style.configure("Purple.TButton", background="#8e44ad", foreground="white")
        self.style.configure("Orange.TButton", background="#e67e22", foreground="white")
        self.style.configure("Teal.TButton", background="#16a085", foreground="white")
        self.style.configure("Gray.TButton", background="#7f8c8d", foreground="white")
        self.style.configure("Red.TButton", background="#c0392b", foreground="white")

        # Right panel (Records) with scrollbar
        right_panel = ttk.LabelFrame(main_frame, text="Records", style="Panel.TLabelframe")
        right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        right_canvas = tk.Canvas(right_panel, bg="#ffffff", highlightthickness=0)
        right_scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=right_canvas.yview)
        right_scrollable_frame = ttk.Frame(right_canvas)
        right_scrollable_frame.bind("<Configure>", lambda e: right_canvas.configure(scrollregion=right_canvas.bbox("all")))
        right_canvas.create_window((0, 0), window=right_scrollable_frame, anchor="nw")
        right_canvas.configure(yscrollcommand=right_scrollbar.set)
        right_canvas.pack(side="left", fill="both", expand=True)
        right_scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(right_scrollable_frame, columns=("ID", "Name", "Form", "Paid", "Remaining"), 
                                show="headings", style="Treeview")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Form", text="Form")
        self.tree.heading("Paid", text="Amount Paid")
        self.tree.heading("Remaining", text="Remaining")
        self.tree.pack(fill="both", expand=True)

    def validate_email_callback(self, value):
        valid = self.validate_email(value)
        self.email_entry.config(style="TEntry" if valid or not value else "Invalid.TEntry")
        self.style.configure("Invalid.TEntry", background="#ffcccc")
        return True

    def validate_phone_callback(self, value):
        valid = self.validate_phone(value)
        self.phone_entry.config(style="TEntry" if valid or not value else "Invalid.TEntry")
        self.style.configure("Invalid.TEntry", background="#ffcccc")
        return True

    def add_student(self):
        name, form, email, phone = (self.name_entry.get().strip(), self.form_combo.get(), 
                                  self.email_entry.get().strip(), self.phone_entry.get().strip())
        if not all([name, form, email, phone]) or not self.validate_email(email) or not self.validate_phone(phone):
            messagebox.showerror("Error", "Invalid input!")
            return
        self.db.add_student(name, form, email, phone)
        messagebox.showinfo("Success", "Student added!")
        self.clear_entries()
        self.view_records()

    def make_payment_window(self):
        payment_window = tk.Toplevel(self.root)
        payment_window.title("Make Payment")
        payment_window.geometry("400x300")
        payment_window.configure(bg="#d5e8f7")

        ttk.Label(payment_window, text="Student ID:", background="#d5e8f7").pack(pady=10)
        id_entry = ttk.Entry(payment_window)
        id_entry.pack(pady=5)

        ttk.Label(payment_window, text="Amount (TSH):", background="#d5e8f7").pack(pady=10)
        amount_entry = ttk.Entry(payment_window)
        amount_entry.pack(pady=5)

        def process_payment():
            try:
                student_id, amount = int(id_entry.get()), int(amount_entry.get())
                student = self.db.get_student(student_id)
                if not student:
                    messagebox.showerror("Error", "Student not found!")
                    return
                name, form, email, _, total_paid = student
                new_total = self.db.update_payment(student_id, amount)
                if self.notif.send_email(name, form, email, amount, new_total, self.fee_structure[form]):
                    messagebox.showinfo("Success", "Payment processed and email sent!")
                else:
                    messagebox.showwarning("Warning", "Payment processed but email failed!")
                self.generate_receipt(student_id, name, form, amount, new_total)
                payment_window.destroy()
                self.view_records()
            except ValueError:
                messagebox.showerror("Error", "Invalid input! Please enter numeric values.")

        ttk.Button(payment_window, text="Submit Payment", style="Green.TButton", command=process_payment).pack(pady=20)

    def generate_receipt(self, student_id, name, form, amount, total_paid):
        filename = f"receipt_{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        c.setFillColorRGB(0.17, 0.62, 0.86)  # Blue color for header
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(300, 750, "School Fee Payment Receipt")
        c.setFillColorRGB(0, 0, 0)  # Black for text
        c.setFont("Helvetica", 12)
        c.drawString(100, 720, "-" * 80)
        c.drawString(100, 700, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(100, 680, f"Student ID: {student_id}")
        c.drawString(100, 660, f"Student Name: {name}")
        c.drawString(100, 640, f"Form: {form}")
        c.drawString(100, 620, f"Amount Paid: {amount:,} TSH")
        c.drawString(100, 600, f"Total Paid: {total_paid:,} TSH")
        c.drawString(100, 580, f"Remaining: {self.fee_structure[form] - total_paid:,} TSH")
        c.drawString(100, 540, "Thank you for your payment!")
        c.drawString(100, 520, "-" * 80)
        c.showPage()
        c.save()
        
        if platform.system() == "Windows":
            os.startfile(filename)
        elif platform.system() == "Darwin":
            os.system(f"open {filename}")
        else:
            os.system(f"xdg-open {filename}")

    def view_records(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for id, name, form, paid in self.db.get_all_students():
            remaining = self.fee_structure[form] - paid
            self.tree.insert("", "end", values=(id, name, form, f"{paid:,}", f"{remaining:,}"))

    def search_student(self):
        term = self.search_entry.get()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for id, name, form, paid in self.db.search_students(term):
            remaining = self.fee_structure[form] - paid
            self.tree.insert("", "end", values=(id, name, form, f"{paid:,}", f"{remaining:,}"))

    def view_payment_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Payment History")
        history_window.geometry("600x400")
        history_window.configure(bg="#d5e8f7")

        ttk.Label(history_window, text="Enter Student ID:", background="#d5e8f7").pack(pady=10)
        id_entry = ttk.Entry(history_window)
        id_entry.pack(pady=5)

        # Scrollable Treeview
        history_frame = ttk.Frame(history_window)
        history_frame.pack(fill="both", expand=True, pady=10)
        history_canvas = tk.Canvas(history_frame, bg="#ffffff", highlightthickness=0)
        history_scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=history_canvas.yview)
        history_scrollable_frame = ttk.Frame(history_canvas)
        history_scrollable_frame.bind("<Configure>", lambda e: history_canvas.configure(scrollregion=history_canvas.bbox("all")))
        history_canvas.create_window((0, 0), window=history_scrollable_frame, anchor="nw")
        history_canvas.configure(yscrollcommand=history_scrollbar.set)
        history_canvas.pack(side="left", fill="both", expand=True)
        history_scrollbar.pack(side="right", fill="y")

        tree = ttk.Treeview(history_scrollable_frame, columns=("Date", "Amount"), show="headings", style="Treeview")
        tree.heading("Date", text="Date")
        tree.heading("Amount", text="Amount (TSH)")
        tree.pack(fill="both", expand=True)

        def show_history():
            for item in tree.get_children():
                tree.delete(item)
            for date, amount in self.db.get_payment_history(id_entry.get()):
                tree.insert("", "end", values=(date, f"{amount:,}"))

        ttk.Button(history_window, text="Show History", style="Blue.TButton", command=show_history).pack(pady=10)

    def backup_database(self):
        backup_file = self.backup.create_backup()
        if backup_file:
            messagebox.showinfo("Success", f"Backup created: {backup_file}")
        else:
            messagebox.showerror("Error", "Backup failed!")

    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.form_combo.set("")
        self.email_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.search_entry.delete(0, tk.END)

    def logout(self):
        self.logged_in = False
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.withdraw()  # Hide root window again
        self.show_login()