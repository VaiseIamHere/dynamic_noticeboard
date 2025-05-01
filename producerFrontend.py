import tkinter as tk
from tkinter import messagebox, ttk
import requests
import hashlib
import json
import os

BACKEND_URL = "https://noticeboard-backend-kmwd.onrender.com"
# BACKEND_URL = "http://localhost:5000"
CONFIG_FILE = "admin_config.json"

class NoticeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notice Management System")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # Initialize frames
        self.auth_frame = tk.Frame(root)
        self.main_frame = tk.Frame(root)
        self.send_frame = tk.Frame(root)
        self.delete_frame = tk.Frame(root)
        self.login_frame = tk.Frame(root)
        self.register_frame = tk.Frame(root)
        
        self.notices = []
        self.selected_items = []
        self.current_user = None
        
        # Start with auth screen
        self.show_auth_screen()
        
    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()
            
    def hide_all_frames(self):
        self.auth_frame.pack_forget()
        self.main_frame.pack_forget()
        self.send_frame.pack_forget()
        self.delete_frame.pack_forget()
        self.login_frame.pack_forget()
        self.register_frame.pack_forget()
        
    def hash_password(self, password):
        """Simple password hashing"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_admin_data(self):
        """Load admin data from config file"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_admin_data(self, data):
        """Save admin data to config file"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f)
            
    def show_auth_screen(self):
        """Show initial authentication options screen"""
        self.hide_all_frames()
        self.clear_frame(self.auth_frame)
        
        title_label = tk.Label(self.auth_frame, text="Notice Management System", font=("Arial", 20, "bold"))
        title_label.pack(pady=(50, 20))
        
        subtitle_label = tk.Label(self.auth_frame, text="Admin Authentication", font=("Arial", 14))
        subtitle_label.pack(pady=(0, 50))
        
        login_btn = tk.Button(self.auth_frame, text="Login", command=self.show_login_screen,
                             font=("Arial", 14), bg="#4CAF50", fg="white", width=20, height=2)
        login_btn.pack(pady=10)
        
        register_btn = tk.Button(self.auth_frame, text="Register", command=self.show_register_screen,
                               font=("Arial", 14), bg="#2196F3", fg="white", width=20, height=2)
        register_btn.pack(pady=10)
        
        exit_btn = tk.Button(self.auth_frame, text="Exit", command=self.root.destroy,
                           font=("Arial", 12), bg="#f44336", fg="white", width=10)
        exit_btn.pack(pady=(40, 0))
        
        self.auth_frame.pack(fill=tk.BOTH, expand=True)
        
    def show_login_screen(self):
        """Show login screen"""
        self.hide_all_frames()
        self.clear_frame(self.login_frame)
        
        title_label = tk.Label(self.login_frame, text="Admin Login", font=("Arial", 18, "bold"))
        title_label.pack(pady=(40, 30))
        
        # Username
        username_frame = tk.Frame(self.login_frame)
        username_frame.pack(fill=tk.X, padx=100, pady=10)
        tk.Label(username_frame, text="Username:", font=("Arial", 12), width=10, anchor='w').pack(side=tk.LEFT)
        self.login_username = tk.Entry(username_frame, font=("Arial", 12))
        self.login_username.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Password
        password_frame = tk.Frame(self.login_frame)
        password_frame.pack(fill=tk.X, padx=100, pady=10)
        tk.Label(password_frame, text="Password:", font=("Arial", 12), width=10, anchor='w').pack(side=tk.LEFT)
        self.login_password = tk.Entry(password_frame, font=("Arial", 12), show="*")
        self.login_password.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Buttons
        btn_frame = tk.Frame(self.login_frame)
        btn_frame.pack(fill=tk.X, padx=100, pady=(30, 0))
        
        back_btn = tk.Button(btn_frame, text="Back", command=self.show_auth_screen,
                           font=("Arial", 12), bg="#607D8B", fg="white", width=10)
        back_btn.pack(side=tk.LEFT)
        
        login_btn = tk.Button(btn_frame, text="Login", command=self.do_login,
                            font=("Arial", 12), bg="#4CAF50", fg="white", width=10)
        login_btn.pack(side=tk.RIGHT)
        
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        
    def show_register_screen(self):
        """Show registration screen"""
        self.hide_all_frames()
        self.clear_frame(self.register_frame)
        
        title_label = tk.Label(self.register_frame, text="Admin Registration", font=("Arial", 18, "bold"))
        title_label.pack(pady=(40, 30))
        
        # Username
        username_frame = tk.Frame(self.register_frame)
        username_frame.pack(fill=tk.X, padx=100, pady=10)
        tk.Label(username_frame, text="Username:", font=("Arial", 12), width=10, anchor='w').pack(side=tk.LEFT)
        self.reg_username = tk.Entry(username_frame, font=("Arial", 12))
        self.reg_username.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Password
        password_frame = tk.Frame(self.register_frame)
        password_frame.pack(fill=tk.X, padx=100, pady=10)
        tk.Label(password_frame, text="Password:", font=("Arial", 12), width=10, anchor='w').pack(side=tk.LEFT)
        self.reg_password = tk.Entry(password_frame, font=("Arial", 12), show="*")
        self.reg_password.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Confirm Password
        confirm_frame = tk.Frame(self.register_frame)
        confirm_frame.pack(fill=tk.X, padx=100, pady=10)
        tk.Label(confirm_frame, text="Confirm:", font=("Arial", 12), width=10, anchor='w').pack(side=tk.LEFT)
        self.reg_confirm = tk.Entry(confirm_frame, font=("Arial", 12), show="*")
        self.reg_confirm.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Buttons
        btn_frame = tk.Frame(self.register_frame)
        btn_frame.pack(fill=tk.X, padx=100, pady=(30, 0))
        
        back_btn = tk.Button(btn_frame, text="Back", command=self.show_auth_screen,
                           font=("Arial", 12), bg="#607D8B", fg="white", width=10)
        back_btn.pack(side=tk.LEFT)
        
        register_btn = tk.Button(btn_frame, text="Register", command=self.do_register,
                               font=("Arial", 12), bg="#2196F3", fg="white", width=10)
        register_btn.pack(side=tk.RIGHT)
        
        self.register_frame.pack(fill=tk.BOTH, expand=True)
    
    def do_login(self):
        """Process login"""
        username = self.login_username.get().strip()
        password = self.login_password.get()
        
        if not username or not password:
            messagebox.showwarning("Input Error", "Username and password cannot be empty.")
            return
        
        admin_data = self.load_admin_data()
        
        if username in admin_data and admin_data[username] == self.hash_password(password):
            self.current_user = username
            messagebox.showinfo("Success", f"Welcome, {username}!")
            self.setup_choice_screen()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
            
    def do_register(self):
        """Process registration"""
        username = self.reg_username.get().strip()
        password = self.reg_password.get()
        confirm = self.reg_confirm.get()
        
        if not username or not password:
            messagebox.showwarning("Input Error", "Username and password cannot be empty.")
            return
            
        if password != confirm:
            messagebox.showwarning("Input Error", "Passwords do not match.")
            return
            
        admin_data = self.load_admin_data()
        
        if username in admin_data:
            messagebox.showwarning("Registration Error", "Username already exists.")
            return
            
        admin_data[username] = self.hash_password(password)
        self.save_admin_data(admin_data)
        
        messagebox.showinfo("Success", "Registration successful! Please login.")
        self.show_login_screen()
            
    def setup_choice_screen(self):
        """Set up the main menu screen after successful login"""
        self.hide_all_frames()
        self.clear_frame(self.main_frame)
        
        # Header with logout
        header_frame = tk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(header_frame, text=f"Welcome, {self.current_user}", font=("Arial", 12)).pack(side=tk.LEFT)
        
        logout_btn = tk.Button(header_frame, text="Logout", command=self.logout,
                             font=("Arial", 10), bg="#f44336", fg="white")
        logout_btn.pack(side=tk.RIGHT)
        
        # Main options
        choice_label = tk.Label(self.main_frame, text="What would you like to do?", font=("Arial", 16))
        choice_label.pack(pady=20)
        
        send_btn = tk.Button(self.main_frame, text="Send a Notice", command=self.show_send_screen, 
                            font=("Arial", 14), bg="#4CAF50", fg="white", width=20, height=2)
        send_btn.pack(pady=10)
        
        delete_btn = tk.Button(self.main_frame, text="Delete Notices", command=self.show_delete_screen, 
                              font=("Arial", 14), bg="#f44336", fg="white", width=20, height=2)
        delete_btn.pack(pady=10)
        
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
    def logout(self):
        """Logout user and return to auth screen"""
        self.current_user = None
        self.show_auth_screen()

    def back_to_main(self):
        """Go back to main menu from send/delete screens"""
        self.hide_all_frames()
        self.setup_choice_screen()  # Re-use the choice screen setup

    def send_notice(self):
        title_text = self.title_entry.get().strip()
        notice_text = self.notice_entry.get("1.0", tk.END).strip()
        label_text = self.label_entry.get().strip() or "general"  # Default to "general"

        if not title_text or not notice_text:
            messagebox.showwarning("Input Error", "Title and notice cannot be empty.")
            return

        try:
            response = requests.put(
                f"{BACKEND_URL}/notice",
                json={"title": title_text, "notice": notice_text, "label": label_text}
            )
            if response.status_code == 200:
                messagebox.showinfo("Success", "Notice sent successfully!")
                self.title_entry.delete(0, tk.END)
                self.notice_entry.delete("1.0", tk.END)
                self.label_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", f"Failed to send notice. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Request Error", f"An error occurred: {e}")


    def show_send_screen(self):
        self.hide_all_frames()
        self.clear_frame(self.send_frame)
        
        # Header with back button and username
        header_frame = tk.Frame(self.send_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(header_frame, text=f"Logged in as: {self.current_user}", font=("Arial", 10)).pack(side=tk.LEFT)
        
        tk.Label(self.send_frame, text="Send a New Notice", font=("Arial", 16)).pack(pady=10)
        
        title_frame = tk.Frame(self.send_frame)
        title_frame.pack(fill=tk.X, pady=5)
        tk.Label(title_frame, text="Title:", font=("Arial", 12)).pack(side=tk.LEFT)
        self.title_entry = tk.Entry(title_frame, font=("Arial", 12), width=40)
        self.title_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        label_frame = tk.Frame(self.send_frame)
        label_frame.pack(fill=tk.X, pady=5)
        tk.Label(label_frame, text="Label:", font=("Arial", 12)).pack(side=tk.LEFT)
        self.label_entry = tk.Entry(label_frame, font=("Arial", 12), width=40)
        self.label_entry.insert(0, "general")
        self.label_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        tk.Label(self.send_frame, text="Notice Content:", font=("Arial", 12)).pack(anchor=tk.W, pady=(10,5))
        self.notice_entry = tk.Text(self.send_frame, height=10, width=60, font=("Arial", 12))
        self.notice_entry.pack(fill=tk.BOTH, expand=True, pady=5)
        
        btn_frame = tk.Frame(self.send_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        back_btn = tk.Button(btn_frame, text="Back", command=self.back_to_main, 
                           font=("Arial", 12), bg="#607D8B", fg="white")
        back_btn.pack(side=tk.LEFT, padx=5)
        
        submit_btn = tk.Button(btn_frame, text="Send Notice", command=self.send_notice, 
                              font=("Arial", 12), bg="#4CAF50", fg="white")
        submit_btn.pack(side=tk.RIGHT, padx=5)
        
        self.send_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def fetch_notices(self):
        try:
            response = requests.get(f"{BACKEND_URL}/notices")
            if response.status_code == 200:
                self.notices = response.json()
                return True
            else:
                messagebox.showerror("Error", f"Failed to fetch notices. Status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Request Error", f"An error occurred: {e}")
            return False

    def toggle_selection(self, event):
        item = self.notices_tree.identify_row(event.y)
        if item:
            if item in self.selected_items:
                self.notices_tree.item(item, tags=())
                self.selected_items.remove(item)
            else:
                self.notices_tree.item(item, tags=('selected',))
                self.selected_items.append(item)

    def filter_notices(self, event=None):
        search_text = self.search_entry.get().lower()

        # clear out the tree
        for item in self.notices_tree.get_children():
            self.notices_tree.delete(item)
        self.selected_items = []

        # re-populate
        for notice in self.notices:
            title = notice.get('title', '').lower()
            date  = notice.get('dateAdded', '')
            if not search_text or search_text in title:
                self.notices_tree.insert(
                    "", tk.END,
                    values=(notice['title'], date)
                )

    def delete_selected_notices(self):
        if not self.selected_items:
            messagebox.showinfo("Info", "No notices selected for deletion.")
            return
        
        selected_titles = []
        for item_id in self.selected_items:
            item_values = self.notices_tree.item(item_id, 'values')
            selected_titles.append(item_values[0])
        
        try:
            response = requests.delete(f"{BACKEND_URL}/notices", json={"titles": selected_titles})
            
            if response.status_code == 200:
                messagebox.showinfo("Success", f"Successfully deleted {len(self.selected_items)} notice(s).")
                if self.fetch_notices():
                    self.filter_notices()
                    self.selected_items = []
            else:
                messagebox.showerror("Error", f"Failed to delete notices. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Request Error", f"An error occurred: {e}")

    def show_delete_screen(self):
        self.hide_all_frames()
        self.clear_frame(self.delete_frame)
        
        # Header with username
        header_frame = tk.Frame(self.delete_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(header_frame, text=f"Logged in as: {self.current_user}", font=("Arial", 10)).pack(side=tk.LEFT)
        
        top_frame = tk.Frame(self.delete_frame)
        top_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(top_frame, text="Delete Notices", font=("Arial", 16)).pack(side=tk.LEFT)
        
        # Search field
        search_frame = tk.Frame(self.delete_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(search_frame, text="Search by title:", font=("Arial", 12)).pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, font=("Arial", 12), width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self.filter_notices)
        
        notices_frame = tk.Frame(self.delete_frame)
        notices_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tree_frame = tk.Frame(notices_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ("title", "date")
        self.notices_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", 
                                        yscrollcommand=tree_scroll.set, selectmode="extended")
        
        self.notices_tree.heading("title", text="Title")
        self.notices_tree.heading("date", text="Date Added")
        
        self.notices_tree.column("title", width=350, stretch=True)
        self.notices_tree.column("date", width=150, stretch=False)
        
        self.notices_tree.tag_configure('selected', background='#d1d1d1')
        self.notices_tree.bind("<ButtonRelease-1>", self.toggle_selection)
        
        self.notices_tree.pack(fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.notices_tree.yview)
        
        btn_frame = tk.Frame(self.delete_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        back_btn = tk.Button(btn_frame, text="Back", command=self.back_to_main, 
                           font=("Arial", 12), bg="#607D8B", fg="white")
        back_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = tk.Button(btn_frame, text="Delete Selected", command=self.delete_selected_notices, 
                             font=("Arial", 12), bg="#f44336", fg="white")
        delete_btn.pack(side=tk.RIGHT, padx=5)
        
        if self.fetch_notices():
            self.filter_notices()
        
        self.delete_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = NoticeApp(root)
    root.mainloop()