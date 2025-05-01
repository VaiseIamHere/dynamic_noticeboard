import tkinter as tk
from tkinter import ttk
import requests

BACKEND_URL = "https://noticeboard-backend-kmwd.onrender.com"
# BACKEND_URL = "http://localhost:5000"

class NoticeBoardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notice Board")
        self.root.geometry("800x600")
        self.page_size = 10
        self.current_page = 0

        self.auto_refresh = True
        self.open_notices_count = 0

        self.is_newest_first = True
        self.selected_labels = []
        self.all_labels = set()
        self.label_filter_listbox = None
        self.label_vars = {}

        self.notice_data = []
        self.displayed_notices = []

        self.setup_ui()
        self.fetch_data()

    def setup_ui(self):
        tk.Label(self.root, text="Notice Board", font=("Arial", 24, "bold"), fg="blue").pack(pady=10)

        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=5, fill="x", padx=20)

        # SEARCH + LABEL FILTER (VERTICAL STACK OF HORIZONTAL ROWS)
        search_frame = tk.Frame(top_frame)
        search_frame.pack(side="left", anchor="w")

        # Search row
        search_row = tk.Frame(search_frame)
        search_row.pack(anchor="w", pady=(0, 5))
        tk.Label(search_row, text="Search:", font=("Arial", 12)).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_notices)
        tk.Entry(search_row, textvariable=self.search_var, width=30).pack(side="left", padx=(5, 0))

        # Label filter row
        label_row = tk.Frame(search_frame)
        label_row.pack(anchor="w")
        tk.Label(label_row, text="Labels:", font=("Arial", 12)).pack(side="left")
        self.label_filter_var = tk.StringVar()
        self.label_filter_var.trace_add("write", self.filter_notices)
        tk.Entry(label_row, textvariable=self.label_filter_var, width=30).pack(side="left", padx=(5, 0))


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


    def toggle_dropdown(self):
        if self.dropdown_menu and tk.Toplevel.winfo_exists(self.dropdown_menu):
            self.dropdown_menu.destroy()
            return

        self.dropdown_menu = tk.Toplevel(self.root)
        self.dropdown_menu.wm_overrideredirect(True)

        # Position dropdown just below the button
        x = self.dropdown_button.winfo_rootx()
        y = self.dropdown_button.winfo_rooty() + self.dropdown_button.winfo_height()
        self.dropdown_menu.geometry(f"+{x}+{y}")

        # Add checkbuttons for each label
        for label in sorted(self.all_labels):
            if label not in self.label_vars:
                self.label_vars[label] = tk.BooleanVar()

            cb = tk.Checkbutton(
                self.dropdown_menu,
                text=label,
                variable=self.label_vars[label],
                command=self.filter_notices,
                anchor="w"
            )
            cb.pack(fill="x", anchor="w")

    def update_sort_order(self, is_newest):
        self.current_page = 0
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

                # Ensure response is a list of dictionaries
                if not isinstance(notices_json, list) or not all(isinstance(n, dict) for n in notices_json):
                    raise ValueError("Invalid response format")

                self.notice_data = notices_json

                # Extract unique labels
                self.all_labels = set()
                for notice in self.notice_data:
                    self.all_labels.update(notice.get("labels", []))

                # Rebuild label_vars if labels changed
                new_labels = set()
                for notice in self.notice_data:
                    new_labels.update(notice.get("labels", []))

                if new_labels != self.all_labels:
                    self.all_labels = new_labels
                    self.label_vars.clear()
                    for label in sorted(self.all_labels):
                        self.label_vars[label] = tk.BooleanVar()


                if not self.is_newest_first:
                    self.notice_data.reverse()

                self.filter_notices()

            except Exception as e:
                print("Error fetching data:", e)
                self.notice_data = [{
                    "title": "Unable to fetch notices",
                    "notice": str(e),
                    "dateAdded": "N/A",
                    "labels": ["error"]
                }]
                self.filter_notices()

        self.root.after(10000, self.fetch_data)

    def sort_notices(self):
        if not self.is_newest_first:
            self.notice_data.reverse()
        
        if self.displayed_notices:
            if not self.is_newest_first:
                self.displayed_notices.reverse()

    def filter_notices(self, *args):
        self.current_page = 0
        term = self.search_var.get().lower()

        # Get label input and convert to set of cleaned lowercase labels
        label_input = self.label_filter_var.get()
        label_substrings = [lbl.strip().lower() for lbl in label_input.split(",") if lbl.strip()]

        def matches(notice):
            title = notice.get("title", "").lower()
            labels = set(lbl.lower() for lbl in notice.get("labels", []))
            matches_term = term in title
            matches_label = not label_substrings or any(
                any(sub in label for label in labels)
                for sub in label_substrings
            )
            return matches_term and matches_label

        self.displayed_notices = [n for n in self.notice_data if matches(n)]
        self.sort_notices()
        self.refresh_display()


    def refresh_display(self):
        for w in self.scrollable_frame.winfo_children():
            w.destroy()

        start_idx = self.current_page * self.page_size
        end_idx = start_idx + self.page_size
        notices_to_show = self.displayed_notices[start_idx:end_idx]

        for idx, notice in enumerate(notices_to_show, start=start_idx + 1):
            title = notice.get("title", "")
            content = notice.get("notice", "")
            date = notice.get("dateAdded", "")
            labels = notice.get("labels", [])

            row = tk.Frame(self.scrollable_frame, bd=1, relief="solid", padx=5, pady=5)
            row.pack(fill="x", pady=5)

            header = tk.Frame(row)
            header.pack(fill="x")
            header.grid_columnconfigure(1, weight=1)

            tk.Label(header, text=f"{idx}.", font=("Arial", 11, "bold"))\
                .grid(row=0, column=0, sticky="w", padx=5)
            tk.Label(header, text=title, font=("Arial", 11))\
                .grid(row=0, column=1, sticky="w")
            tk.Label(header, text=date, font=("Arial", 11))\
                .grid(row=0, column=2, sticky="w", padx=10)

            content_frame = tk.Frame(row)

            tk.Label(content_frame, text="Labels: " + ", ".join(labels), font=("Arial", 10, "italic"), fg="gray")\
                .pack(anchor="w", padx=10, pady=(0, 5))
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

        # Pagination controls
        nav_frame = tk.Frame(self.scrollable_frame)
        nav_frame.pack(pady=10)

        prev_btn = tk.Button(nav_frame, text="Previous", command=self.prev_page)
        prev_btn.pack(side="left", padx=10)
        if self.current_page == 0:
            prev_btn.config(state="disabled")

        next_btn = tk.Button(nav_frame, text="Next", command=self.next_page)
        next_btn.pack(side="left", padx=10)
        if end_idx >= len(self.displayed_notices):
            next_btn.config(state="disabled")

        total_pages = max(1, (len(self.displayed_notices) - 1) // self.page_size + 1)
        page_label = tk.Label(nav_frame, text=f"Page {self.current_page + 1} of {total_pages}")
        page_label.pack(side="left", padx=20)


    def next_page(self):
        if (self.current_page + 1) * self.page_size < len(self.displayed_notices):
            self.current_page += 1
            self.refresh_display()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.refresh_display()


if __name__ == "__main__":
    root = tk.Tk()
    NoticeBoardApp(root)
    root.mainloop()
