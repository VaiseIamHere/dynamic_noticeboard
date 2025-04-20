import tkinter as tk
from tkinter import messagebox, ttk
import requests

BACKEND_URL = "http://localhost:5000"

class NoticeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notice Management System")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.setup_choice_screen()

        self.send_frame = tk.Frame(root)
        self.delete_frame = tk.Frame(root)

        self.notices = []
        self.selected_items = []

    def setup_choice_screen(self):
        choice_label = tk.Label(self.main_frame, text="What would you like to do?", font=("Arial", 16))
        choice_label.pack(pady=20)
        
        send_btn = tk.Button(self.main_frame, text="Send a Notice", command=self.show_send_screen, 
                            font=("Arial", 14), bg="#4CAF50", fg="white", width=20, height=2)
        send_btn.pack(pady=10)
        
        delete_btn = tk.Button(self.main_frame, text="Delete Notices", command=self.show_delete_screen, 
                              font=("Arial", 14), bg="#f44336", fg="white", width=20, height=2)
        delete_btn.pack(pady=10)

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def back_to_main(self):
        self.send_frame.pack_forget()
        self.delete_frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def send_notice(self):
        title_text = self.title_entry.get().strip()
        notice_text = self.notice_entry.get("1.0", tk.END).strip()
        
        if not title_text or not notice_text:
            messagebox.showwarning("Input Error", "Title and notice cannot be empty.")
            return
        
        try:
            response = requests.put(f"{BACKEND_URL}/notice", json={"title": title_text, "notice": notice_text})
            if response.status_code == 200:
                messagebox.showinfo("Success", "Notice sent successfully!")
                self.title_entry.delete(0, tk.END)
                self.notice_entry.delete("1.0", tk.END)
            else:
                messagebox.showerror("Error", f"Failed to send notice. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Request Error", f"An error occurred: {e}")

    def show_send_screen(self):
        self.main_frame.pack_forget()
        self.delete_frame.pack_forget()
        
        self.clear_frame(self.send_frame)
        
        tk.Label(self.send_frame, text="Send a New Notice", font=("Arial", 16)).pack(pady=10)
        
        title_frame = tk.Frame(self.send_frame)
        title_frame.pack(fill=tk.X, pady=5)
        tk.Label(title_frame, text="Title:", font=("Arial", 12)).pack(side=tk.LEFT)
        self.title_entry = tk.Entry(title_frame, font=("Arial", 12), width=40)
        self.title_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

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
        
        for item in self.notices_tree.get_children():
            self.notices_tree.delete(item)
        
        self.selected_items = []

        for notice in self.notices:
            title = notice[0].lower()
            
            if search_text == "" or search_text in title:
                item = self.notices_tree.insert("", tk.END, values=(notice[0], notice[2]))

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
        self.main_frame.pack_forget()
        self.send_frame.pack_forget()
        
        self.clear_frame(self.delete_frame)
        
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
