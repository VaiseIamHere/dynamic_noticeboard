import tkinter as tk
from tkinter import ttk
import requests

BACKEND_URL = "http://localhost:5000"

class NoticeBoardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notice Board")
        self.root.geometry("800x600")

        self.auto_refresh = True
        self.open_notices_count = 0

        self.is_newest_first = True

        self.notice_data = []
        self.displayed_notices = []

        self.setup_ui()
        self.fetch_data()

    def setup_ui(self):
        tk.Label(self.root, text="Notice Board", font=("Arial", 24, "bold"), fg="blue").pack(pady=10)

        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=5, fill="x", padx=20)

        search_frame = tk.Frame(top_frame)
        search_frame.pack(side="left")
        
        tk.Label(search_frame, text="Search:", font=("Arial", 12)).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_notices)
        tk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side="left", padx=5)

        sort_frame = tk.Frame(top_frame)
        sort_frame.pack(side="right")
        
        tk.Label(sort_frame, text="Sort:", font=("Arial", 12)).pack(side="left", padx=(0, 5))

        self.newest_btn = tk.Button(
            sort_frame, 
            text="Newest", 
            bg="#4CAF50" if self.is_newest_first else "#f0f0f0",
            fg="white" if self.is_newest_first else "black",
            command=lambda: self.update_sort_order(True)
        )
        self.newest_btn.pack(side="left", padx=2)
        
        self.oldest_btn = tk.Button(
            sort_frame, 
            text="Oldest", 
            bg="#f0f0f0" if self.is_newest_first else "#4CAF50",
            fg="black" if self.is_newest_first else "white",
            command=lambda: self.update_sort_order(False)
        )
        self.oldest_btn.pack(side="left", padx=2)

        self.canvas = tk.Canvas(self.root)
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=(20, 0))
        self.scrollbar.pack(side="right", fill="y")

        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind("<Configure>", self.resize_canvas)

    def update_sort_order(self, is_newest):
        if is_newest:
            self.newest_btn.config(bg="#4CAF50", fg="white")
            self.oldest_btn.config(bg="#f0f0f0", fg="black")
        else:
            self.newest_btn.config(bg="#f0f0f0", fg="black")
            self.oldest_btn.config(bg="#4CAF50", fg="white")
        
        self.is_newest_first = is_newest
        
        self.sort_notices()
        self.refresh_display()

    def resize_canvas(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def fetch_data(self):
        if self.auto_refresh:
            try:
                response = requests.get(f"{BACKEND_URL}/notices")
                notices_json = response.json()
                
                self.notice_data = notices_json
                
                if not self.is_newest_first:
                    self.notice_data.reverse()
                
                self.filter_notices()
                
            except Exception as e:
                print("Error fetching data:", e)
                self.notice_data = [["Unable to fetch notices", "", "N/A"]]
                self.filter_notices()

        self.root.after(10000, self.fetch_data)

    def sort_notices(self):
        if not self.is_newest_first:
            self.notice_data.reverse()
        
        if self.displayed_notices:
            if not self.is_newest_first:
                self.displayed_notices.reverse()

    def filter_notices(self, *args):
        term = self.search_var.get().lower()
        self.displayed_notices = [n for n in self.notice_data if term in n[0].lower()]
        self.refresh_display()

    def refresh_display(self):
        for w in self.scrollable_frame.winfo_children():
            w.destroy()

        for idx, (title, content, date) in enumerate(self.displayed_notices):
            row = tk.Frame(self.scrollable_frame, bd=1, relief="solid", padx=5, pady=5)
            row.pack(fill="x", pady=5)

            header = tk.Frame(row)
            header.pack(fill="x")
            header.grid_columnconfigure(1, weight=1)

            tk.Label(header, text=f"{idx+1}.", font=("Arial", 11, "bold"))\
                .grid(row=0, column=0, sticky="w", padx=5)
            tk.Label(header, text=title, font=("Arial", 11))\
                .grid(row=0, column=1, sticky="w")
            tk.Label(header, text=date, font=("Arial", 11))\
                .grid(row=0, column=2, sticky="w", padx=10)

            content_frame = tk.Frame(row)
            tk.Label(content_frame, text=content, wraplength=700, justify="left", font=("Arial", 11))\
                .pack(anchor="w", padx=10, pady=5)
            content_frame.pack_forget()

            btn = tk.Button(header, text="Open", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
            btn.grid(row=0, column=3, sticky="e", padx=5)

            def toggle(e=None, c=content_frame, b=btn):
                if c.winfo_ismapped():
                    c.pack_forget()
                    b.config(text="Open")
                    self.open_notices_count -= 1
                    if self.open_notices_count == 0:
                        self.auto_refresh = True
                else:
                    c.pack(fill="x")
                    b.config(text="Collapse")
                    self.open_notices_count += 1
                    if self.open_notices_count == 1:
                        self.auto_refresh = False

            btn.config(command=toggle)

if __name__ == "__main__":
    root = tk.Tk()
    NoticeBoardApp(root)
    root.mainloop()
