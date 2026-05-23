# gui_pages.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import sqlite3
import time
import os

# ---------------------- Home Page ----------------------
class HomePage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f8f5fa")
        self.pack(fill="both", expand=True)


        canvas = tk.Canvas(self, bg="#f8f5fa", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)

        scrollable_frame = tk.Frame(canvas, bg="#f8f5fa")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        content_window = canvas.create_window(
            (0, 0), window=scrollable_frame, anchor="nw"
        )

        # Make scrollable frame expand to full window width
        def resize_scroll(event):
            canvas_width = event.width
            canvas.itemconfig(content_window, width=canvas_width)

        canvas.bind("<Configure>", resize_scroll)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Hero
        hero = tk.Frame(scrollable_frame, bg="#6a1b9a")
        hero.pack(fill="x", pady=(0,20))
        tk.Label(hero, text="Welcome to Trauma Tracker",
                 font=("Arial", 28, "bold"), fg="white", bg="#6a1b9a").pack(pady=30)
        tk.Label(hero,
                 text="Revolutionizing concussion detection with advanced AI and real-time analytics. Stay safe. Stay informed.",
                 font=("Arial", 14), fg="white", bg="#6a1b9a", wraplength=900, justify="center").pack()
        tk.Button(hero, text="Get Started", font=("Arial", 14, "bold"),
                  bg="#4a148c", fg="white", padx=15, pady=5).pack(pady=15)

        # Key Features
        tk.Label(scrollable_frame, text="Key Features", font=("Arial", 22, "bold"), fg="#4a148c", bg="#f8f5fa").pack(pady=10)
        features_frame = tk.Frame(scrollable_frame, bg="#f8f5fa")
        features_frame.pack(padx=20, pady=10, fill="x", expand=True)

        features = [
            ("Real-Time Detection", "Instantly analyze eye movements using AI to identify potential concussion symptoms during gameplay. Immediate alerts ensure player safety."),
            ("Data Tracking", "Effortlessly monitor concussion events over time with a simple dashboard. Secure storage and detailed reports help identify patterns."),
            ("Educational Resources", "Access comprehensive resources, expert advice, and safety guidelines to understand concussion prevention and care."),
            ("User-Friendly Interface", "Enjoy seamless navigation with an interface designed for ease of use, ensuring users of all backgrounds can access vital tools."),
        ]

        for i, (title, desc) in enumerate(features):
            f = tk.Frame(features_frame, bg="#f2edfa", padx=15, pady=15, bd=1, relief="solid")
            f.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            tk.Label(f, text=title, font=("Arial", 16, "bold"), bg="#f2edfa").pack(anchor="w", pady=(0,5))
            tk.Label(f, text=desc, font=("Arial", 12), bg="#f2edfa", wraplength=400, justify="left").pack(anchor="w")

        features_frame.grid_columnconfigure(0, weight=1)
        features_frame.grid_columnconfigure(1, weight=1)

        # Why it Matters
        why_frame = tk.Frame(scrollable_frame, bg="#f3e5f5", padx=20, pady=20)
        why_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(why_frame, text="Why It Matters ?", font=("Arial", 20, "bold"), fg="#4a148c", bg="#f3e5f5").pack(anchor="w", pady=5)
        why_text = "Concussions can lead to serious long-term cognitive and physical health issues if not properly addressed. Trauma Tracker helps identify risks by analyzing real-time data, giving athletes, coaches, and parents a crucial tool for timely intervention."
        tk.Label(why_frame, text=why_text, font=("Arial", 12), bg="#f3e5f5", wraplength=900, justify="left").pack(anchor="w")

        # Our Goal
        goal_frame = tk.Frame(scrollable_frame, bg="#f9f1f7", padx=20, pady=20)
        goal_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(goal_frame, text="Our Goal", font=("Arial", 20, "bold"), fg="#6a1b9a", bg="#f9f1f7").pack(anchor="w", pady=5)
        goal_text = "Provide athletes, coaches, and healthcare professionals with tools to detect, manage, and prevent concussions using real-time data analysis."
        tk.Label(goal_frame, text=goal_text, font=("Arial", 12), bg="#f9f1f7", wraplength=900, justify="left").pack(anchor="w")

        # FAQ
        faq_frame = tk.Frame(scrollable_frame, bg="#e6eaf8", padx=20, pady=20)
        faq_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(faq_frame, text="Frequently Asked Questions", font=("Arial", 20, "bold"), fg="#4a148c", bg="#e6eaf8").pack(anchor="w", pady=5)
        faqs = [
            ("How does Trauma Tracker detect concussions?", "Uses real-time data from sensors to analyze eye movements and impacts, identifying potential concussion risks."),
            ("Is my data secure?", "All data is encrypted and stored securely in compliance with privacy regulations."),
            ("How many children under 17 are affected by concussions?", "Approx. 2.3 million children and adolescents aged 17 and under in the U.S. have been diagnosed with a concussion or brain injury."),
        ]
        for q, a in faqs:
            faq_item = tk.Frame(faq_frame, bg="#f4f4fe", padx=10, pady=10)
            faq_item.pack(fill="x", pady=5)
            tk.Label(faq_item, text=q, font=("Arial", 14, "bold"), bg="#f4f4fe").pack(anchor="w")
            tk.Label(faq_item, text=a, font=("Arial", 12), bg="#f4f4fe", wraplength=880, justify="left").pack(anchor="w")

        # Support
        support_frame = tk.Frame(scrollable_frame, bg="#f4def8", padx=20, pady=20)
        support_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(support_frame, text="Need Help?", font=("Arial", 20, "bold"), fg="#4a148c", bg="#f4def8").pack(anchor="w", pady=5)
        support_text = "If you have any questions or need assistance, feel free to contact us."
        tk.Label(support_frame, text=support_text, font=("Arial", 12), bg="#f4def8", wraplength=900, justify="left").pack(anchor="w", pady=5)
        tk.Button(support_frame, text="Contact Support", font=("Arial", 12, "bold"), bg="#4a148c", fg="white").pack(anchor="w", pady=10)

        # Footer
        footer = tk.Frame(scrollable_frame, bg="#4f4c81", height=50)
        footer.pack(fill="x", pady=(20,0))
        tk.Label(footer, text="© 2024 Trauma Tracker. All rights reserved.", font=("Arial", 12), fg="white", bg="#4f4c81").pack(pady=10)


# ---------------------- Detect Page ----------------------
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import traceback
import os
import time
import cv2
import sqlite3

from detect_pupil import run_pupil_detection_dual  # your backend

class DetectPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f8f5fa")
        self.pack(fill="both", expand=True)

        # Scrollable Canvas
        canvas = tk.Canvas(self, bg="#f8f5fa", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f8f5fa")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        content_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(content_window, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Hero
        hero = tk.Frame(scrollable_frame, bg="#6a1b9a")
        hero.pack(fill="x", pady=(0,20))
        tk.Label(hero, text="Pupil Detection Test", font=("Arial", 28, "bold"), fg="white", bg="#6a1b9a").pack(pady=25)
        tk.Label(hero, text="Run real-time pupil dilation analysis using AI vision.",
                 font=("Arial", 14), fg="white", bg="#6a1b9a", wraplength=900, justify="center").pack()

        # Controls Card
        controls_card = tk.Frame(scrollable_frame, bg="#f2edfa", padx=20, pady=20, bd=1, relief="solid")
        controls_card.pack(padx=30, pady=15, fill="x")
        tk.Label(controls_card, text="AI Detection Controls", font=("Arial", 18, "bold"),
                 bg="#f2edfa", fg="#4a148c").pack(anchor="w", pady=5)
        instructions = (
            "Instructions:\n"
            "1. Make sure your camera is connected.\n"
            "2. Click 'Start Detection' to begin the pupil analysis.\n"
            "3. The AI will analyze eye movements and report potential concussion symptoms.\n"
            "4. Results will be displayed below in the 'Detection Results' section."
        )
        tk.Label(controls_card, text=instructions, font=("Arial", 12), bg="#f2edfa", justify="left", wraplength=700).pack(anchor="w", pady=(0,10))

        inner = tk.Frame(controls_card, bg="#f2edfa")
        inner.pack(anchor="w", pady=10)
        self.show_overlay_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(inner, text="Show live overlay", variable=self.show_overlay_var).pack(side="left", padx=10)
        ttk.Button(inner, text="Start Detection", command=self.start_detection_thread).pack(side="left", padx=10)
        self.status_label = tk.Label(controls_card, text="Status: Waiting...", font=("Arial", 12),
                                     bg="#f2edfa", wraplength=600, justify="left")
        self.status_label.pack(anchor="w", pady=10)

        # Results Card
        results_card = tk.Frame(scrollable_frame, bg="#f3e5f5", padx=20, pady=20, bd=1, relief="solid")
        results_card.pack(padx=30, pady=15, fill="both", expand=True)
        tk.Label(results_card, text="Detection Results", font=("Arial", 18, "bold"),
                 bg="#f3e5f5", fg="#4a148c").pack(anchor="w", pady=5)
        results_frame = tk.Frame(results_card)
        results_frame.pack(fill="both", expand=True, pady=5)
        self.results_box = tk.Text(results_frame, height=12, wrap="word", bg="ivory", font=("Arial", 12))
        scrollbar2 = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_box.yview)
        self.results_box.configure(yscrollcommand=scrollbar2.set)
        self.results_box.pack(side="left", fill="both", expand=True)
        scrollbar2.pack(side="right", fill="y")
        self.results_box.insert("1.0", "Results will appear here after the test.\n")
        self.results_box.config(state="disabled")
        ttk.Button(results_card, text="Export Last Raw Data...", command=self.export_last_raw).pack(pady=10)

        # Threading
        self._detection_thread = None
        self._stop_event = threading.Event()
        self._last_details = None
        self.bind("<Destroy>", lambda e: self._cleanup())

        # Cleanup on destroy
        self.bind("<Destroy>", lambda e: self._cleanup())

    # --- Detection Thread ---
    def start_detection_thread(self):
        if self._detection_thread and self._detection_thread.is_alive():
            self.status_label.config(text="Detection already running...")
            return

        self._stop_event.clear()
        self._set_results_text("Running dual-eye PLR test. Please face the camera.\n")
        self.status_label.config(text="Detecting...")

        def worker():
            try:
                verdict, reason, details = run_pupil_detection_dual(
                    MIN_READINGS=100,
                    MAX_READINGS=300,
                    camera_index=0,
                    show_window=self.show_overlay_var.get(),
                )
                self._last_details = details
                report_text = self._format_report(verdict, reason, details)
                self.after(0, lambda: self._display_results_and_status(report_text, verdict, reason))
                self._save_to_history(verdict, reason)
            except Exception as e:
                tb = traceback.format_exc()
                self.after(0, lambda: self._set_results_text(f"Error: {e}\n{tb}"))
                self.after(0, lambda: self.status_label.config(text="Error during detection."))

        self._detection_thread = threading.Thread(target=worker, daemon=True)
        self._detection_thread.start()

    # --- Format Report ---
    def _format_report(self, verdict, reason, details):
        lines = [f"VERDICT: {verdict}", f"Reason: {reason}", ""]
        lines.append(f"Confidence: {details.get('confidence_score', 'N/A')}")
        lines.append(f"Saved CSV: {details.get('saved_csv', 'None')}\n")

        for side in ["left", "right"]:
            m = details.get(side)
            if m:
                lines.append(f"{side.capitalize()} Eye Metrics:")
                lines.append(f" - Max diameter: {m['max_diameter']:.1f} px")
                lines.append(f" - Min diameter: {m['min_diameter']:.1f} px")
                lines.append(f" - Constriction: {m['constriction_percent']:.1f}%")
                lines.append(f" - T75: {m['t75'] if m['t75'] is not None else 'N/A'} s")
                lines.append(f" - Samples: {m['n_samples']}\n")
            else:
                lines.append(f"{side.capitalize()} Eye: No reliable data\n")

        flags = details.get("flags", [])
        if flags:
            lines.append("Flags / Observations:")
            for f in flags:
                lines.append(f" - {f}")
            lines.append("")

        return "\n".join(lines)

    # --- Display Results ---
    def _display_results_and_status(self, report_text, verdict, reason):
        self.status_label.config(text=f"{verdict} — {reason}")
        self._set_results_text(report_text)

    def _set_results_text(self, text):
        self.results_box.config(state="normal")
        self.results_box.delete("1.0", tk.END)
        self.results_box.insert("1.0", text)
        self.results_box.config(state="disabled")

    # --- Save to History ---
    def _save_to_history(self, verdict, reason):
        """Saves the detection result to the database."""
        severity = "Mild" if verdict.lower() == "concussed" else "None"
        method = "Pupil"
        
        try:
            conn = sqlite3.connect("trauma_tracker.db")
            c = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Insert into DB with all 5 columns
            c.execute(
                "INSERT INTO results (timestamp, verdict, reasoning, severity, method) VALUES (?, ?, ?, ?, ?)",
                (timestamp, verdict, reason, severity, method)
            )
            conn.commit()
            conn.close()
                    
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not log history: {e}")

    


    # --- Export Last Raw ---
    def export_last_raw(self):
        if not self._last_details or "raw" not in self._last_details:
            messagebox.showinfo("Export", "No raw data available.")
            return

        default_path = self._last_details.get("saved_csv")
        initialdir = os.path.dirname(default_path) if default_path and os.path.exists(default_path) else "."
        initialfile = os.path.basename(default_path) if default_path else "plr_raw_export.csv"

        save_path = filedialog.asksaveasfilename(
            title="Save PLR raw CSV",
            defaultextension=".csv",
            initialdir=initialdir,
            initialfile=initialfile,
            filetypes=[("CSV files", "*.csv")]
        )
        if not save_path:
            return

        try:
            if default_path and os.path.exists(default_path):
                with open(default_path, "rb") as src, open(save_path, "wb") as dst:
                    dst.write(src.read())
            else:
                raw = self._last_details["raw"]
                left, right = raw.get("left", {}), raw.get("right", {})
                times = sorted(set(left.get("times", []) + right.get("times", [])))
                with open(save_path, "w") as f:
                    f.write("time,left_diameter,right_diameter\n")
                    for t in times:
                        ld = f"{left['diams'][left['times'].index(t)]:.3f}" if t in left.get("times", []) else ""
                        rd = f"{right['diams'][right['times'].index(t)]:.3f}" if t in right.get("times", []) else ""
                        f.write(f"{t:.4f},{ld},{rd}\n")
            messagebox.showinfo("Export", f"Saved raw data to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save file: {e}")

    # --- Cleanup ---
    def _cleanup(self):
        if self._detection_thread and self._detection_thread.is_alive():
            self._stop_event.set()
            self._detection_thread.join(timeout=2.0)
        cv2.destroyAllWindows()
#----------------------- Sensor Detect ---------------------

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sqlite3
from datetime import datetime

class SensorDetectPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="thistle")
        self.pack(fill="both", expand=True)

        # --- Scrollable Layout ---
        canvas = tk.Canvas(self, bg="#f8f5fa", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f8f5fa")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        content_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(content_window, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Header ---
        hero = tk.Frame(scrollable_frame, bg="#6a1b9a")
        hero.pack(fill="x", pady=(0, 20))
        tk.Label(hero, text="Sensor Data Collection", font=("Arial", 28, "bold"), fg="white", bg="#6a1b9a").pack(pady=25)
        tk.Label(hero,
                 text="Capture motion and impact data using your connected sensors to identify potential trauma events.",
                 font=("Arial", 14), fg="white", bg="#6a1b9a", wraplength=900, justify="center").pack(pady=(0, 20))

        # --- Controls Card ---
        controls_card = tk.Frame(scrollable_frame, bg="#f2edfa", padx=20, pady=20, bd=1, relief="solid")
        controls_card.pack(padx=30, pady=15, fill="x")

        tk.Label(controls_card, text="Sensor Data Capture", font=("Arial", 18, "bold"),
                 bg="#f2edfa", fg="#4a148c").pack(anchor="w", pady=5)

        self.status_label = tk.Label(controls_card, text="Status: Waiting...", font=("Arial", 12),
                                     bg="#f2edfa", fg="black")
        self.status_label.pack(anchor="w", pady=8)

        ttk.Button(controls_card, text="Start Sensor Test", command=self.run_script_1).pack(pady=10)

    def run_script_1(self):
        self.status_label.config(text="Running trauma tracking script...")
        self.update_idletasks()
        try:
            subprocess.run(['python', 'Track_The_Trauma.py'], check=True)
            self.status_label.config(text="✅ Sensor test completed successfully!")
            self.add_to_history(verdict="Completed", severity="N/A", method="Sensor")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Script Error", f"An error occurred:\n{e}")
            self.status_label.config(text="❌ Error during sensor test.")

# ---------------------- History Page ----------------------
DB_PATH = "trauma_tracker.db"

class HistoryPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f8f5fa")
        
         # Scrollable Canvas
        canvas = tk.Canvas(self, bg="#f8f5fa", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f8f5fa")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        content_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(content_window, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Hero Section
        hero = tk.Frame(scrollable_frame, bg="#6a1b9a")
        hero.pack(fill="x", pady=(0, 20))
        tk.Label(hero, text="Concussion History", font=("Arial", 28, "bold"),
                 fg="white", bg="#6a1b9a").pack(pady=25)
        tk.Label(hero, text="Review past test results.", font=("Arial", 14),
                 fg="white", bg="#6a1b9a", wraplength=900, justify="center").pack()

        # History Card
        history_card = tk.Frame(scrollable_frame, bg="#f3e5f5", padx=20, pady=20, bd=1, relief="solid")
        history_card.pack(padx=30, pady=15, fill="both", expand=True)

        tk.Label(history_card, text="History Records", font=("Arial", 18, "bold"),
                 bg="#f3e5f5", fg="#4a148c").pack(anchor="w", pady=5)

        # Treeview Table
        columns = ("timestamp", "verdict", "reasoning", "severity", "method")
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#fdfdfd",
                        foreground="#000000",
                        rowheight=25,
                        fieldbackground="#fdfdfd",
                        font=("Arial", 12))
        style.configure("Treeview.Heading",
                        font=("Arial", 12, "bold"),
                        background="#4a148c",
                        foreground="white",
                        padding=(10,5))
        style.map("Treeview", background=[("selected", "#9575cd")],
                              foreground=[("selected", "white")])

        self.tree = ttk.Treeview(history_card, columns=columns, show="headings", height=15)
        self.tree.pack(fill="both", expand=True, pady=10)

        # Define headings and column widths
        self.tree.heading("timestamp", text="Timestamp")
        self.tree.heading("verdict", text="Verdict")
        self.tree.heading("reasoning", text="Reasoning")
        self.tree.heading("severity", text="Severity")
        self.tree.heading("method", text="Method")

        self.tree.column("timestamp", width=150, anchor="w")
        self.tree.column("verdict", width=120, anchor="w")
        self.tree.column("reasoning", width=300, anchor="w")
        self.tree.column("severity", width=100, anchor="w")
        self.tree.column("method", width=150, anchor="w")

        # Add vertical scrollbar for Treeview
        tree_scrollbar = ttk.Scrollbar(history_card, orient="vertical", command=self.tree.yview)
        tree_scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=tree_scrollbar.set)

        # Tag for striped rows
        self.tree.tag_configure('oddrow', background="#fdfdfd")
        self.tree.tag_configure('evenrow', background="#e8def8")

        # Refresh Button
        ttk.Button(history_card, text="Refresh History", command=self.load_history).pack(pady=5)

        # Initial load
        self.load_history()

        # Hover effect
        self.tree.bind("<Motion>", self.on_hover)

    def load_history(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Ensure all columns exist
        c.execute("PRAGMA table_info(results)")
        columns = [info[1] for info in c.fetchall()]
        for col in ["reasoning", "severity", "method"]:
            if col not in columns:
                c.execute(f"ALTER TABLE results ADD COLUMN {col} TEXT")
        conn.commit()

        # Fetch all 5 columns
        c.execute("SELECT timestamp, verdict, reasoning, severity, method FROM results ORDER BY timestamp DESC")
        rows = c.fetchall()
        conn.close()

        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Insert new rows with alternating colors
        for index, row in enumerate(rows):
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=row, tags=(tag,))

    def on_hover(self, event):
        """Highlight row under mouse cursor."""
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
class SafetyPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f8f5fa")
        
         # Scrollable Canvas
        canvas = tk.Canvas(self, bg="#f8f5fa", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f8f5fa")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        content_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(content_window, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Hero Section
        hero = tk.Frame(scrollable_frame, bg="#6a1b9a")
        hero.pack(fill="x", pady=(0,20))
        tk.Label(hero, text="Concussion Safety & Education", font=("Arial", 28, "bold"),
                 fg="white", bg="#6a1b9a").pack(pady=25)
        tk.Label(hero, text="Learn about concussions, prevention, and how to stay safe.",
                 font=("Arial", 14), fg="white", bg="#6a1b9a", wraplength=900, justify="center").pack()

        # Safety/Info Cards
        sections = [
            ("What is a Concussion?",
             "A concussion is a type of traumatic brain injury caused by a bump, blow, or jolt to the head. "
             "It can temporarily affect brain function and may cause headaches, dizziness, confusion, or memory problems."),

            ("Common Symptoms",
             "- Headache or pressure in the head\n"
             "- Confusion or feeling dazed\n"
             "- Nausea or vomiting\n"
             "- Balance problems or dizziness\n"
             "- Sensitivity to light or noise\n"
             "- Sleep disturbances or fatigue\n"
             "- Memory or concentration difficulties"),

            ("Prevention Tips",
             "- Wear appropriate safety gear during sports or activities (helmets, mouthguards).\n"
             "- Follow rules and proper techniques for safe play.\n"
             "- Ensure safe environments at home, school, and work.\n"
             "- Never ignore a head injury or push through symptoms."),

            ("When to Seek Medical Help",
             "- Loss of consciousness, even briefly\n"
             "- Persistent or worsening headache\n"
             "- Repeated vomiting or nausea\n"
             "- Seizures or unusual behavior\n"
             "- Vision or balance problems\n"
             "- Confusion, agitation, or unusual drowsiness"),

            ("Recovery & Return to Activity",
             "Recovery from a concussion varies by individual. Follow your doctor’s guidance, gradually return "
             "to physical and mental activities, and avoid situations that could cause another head injury during recovery."),

            ("Educational Resources",
             "For more information, visit reputable sources:\n"
             "- Centers for Disease Control and Prevention (CDC)\n"
             "- Brain Injury Association of America\n"
             "- National Institute of Neurological Disorders and Stroke (NINDS)")
        ]

        for title, content in sections:
            card = tk.Frame(scrollable_frame, bg="#f3e5f5", padx=20, pady=15, bd=1, relief="solid")
            card.pack(fill="x", padx=30, pady=10)

            tk.Label(card, text=title, font=("Arial", 18, "bold"), fg="#4a148c", bg="#f3e5f5").pack(anchor="w", pady=(0,5))
            tk.Label(card, text=content, font=("Arial", 12), bg="#f3e5f5", wraplength=900, justify="left").pack(anchor="w")

        # Footer
        footer = tk.Frame(scrollable_frame, bg="#6a1b9a")
        footer.pack(fill="x", pady=(20,0))
        tk.Label(footer, text="Stay Safe & Protect Your Brain", font=("Arial", 14, "bold"),
                 fg="white", bg="#6a1b9a").pack(pady=15)