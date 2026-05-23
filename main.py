# main.py
import tkinter as tk
from GUI import HomePage, DetectPage, SensorDetectPage, HistoryPage, SafetyPage
import sqlite3

DB_PATH = "trauma_tracker.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create table with all required columns if it doesn't exist
    c.execute("""
    CREATE TABLE IF NOT EXISTS results (
        timestamp TEXT,
        verdict TEXT,
        reasoning TEXT,
        severity TEXT,
        method TEXT
    )
    """)

    # Add missing columns if table already exists but is old
    c.execute("PRAGMA table_info(results)")
    columns = [info[1] for info in c.fetchall()]
    if "reasoning" not in columns:
        c.execute("ALTER TABLE results ADD COLUMN reasoning TEXT")
    if "severity" not in columns:
        c.execute("ALTER TABLE results ADD COLUMN severity TEXT")

    conn.commit()
    conn.close()


class TraumaTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Trauma Tracker")
        self.geometry("900x700")
        self.configure(bg="#f8f5fa")
        self.resizable(True, True)

        # Header / Navbar
        self.header = tk.Frame(self, bg="#6a1b9a", height=60)
        self.header.pack(fill="x", side="top")
        self.nav_buttons = {}
        for name, page in [("Home", HomePage), ("Detect Pupil", DetectPage),
                           ("Detect Sensor", SensorDetectPage), ("History", HistoryPage), ("Learn More", SafetyPage)]:
            btn = tk.Button(self.header, text=name, bg="#6a1b9a", fg="white",
                            font=("Arial", 12, "bold"),
                            bd=0, relief="flat",
                            command=lambda p=page: self.show_page(p))
            btn.pack(side="left", padx=15, pady=12)
            self.nav_buttons[name] = btn

        # Container for pages
        self.container = tk.Frame(self, bg="#f8f5fa")
        self.container.pack(fill="both", expand=True)

        # Pages
        self.pages = {}
        for P in (HomePage, DetectPage, HistoryPage, SensorDetectPage, SafetyPage):
            page = P(self.container)
            self.pages[P] = page
            page.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_page(HomePage)

    def show_page(self, page_class):
        page = self.pages[page_class]
        page.tkraise()


if __name__ == "__main__":
    init_db()  # Initialize DB before starting the app
    app = TraumaTrackerApp()
    app.mainloop()
