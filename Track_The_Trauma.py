import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
from collections import deque
from datetime import datetime
import sqlite3

class TraumaTrackerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Trauma Tracker")
        self.root.geometry("800x600")

        ttk.Label(root, text="Trauma Tracker", font=("Arial", 16, "bold")).pack(pady=10)
        self.status_label = ttk.Label(root, text="Status: Disconnected", font=("Arial", 12))
        self.status_label.pack(pady=5)

        self.port_var = tk.StringVar(root)
        self.port_var.set('Select COM port')
        self.ports_list = self.get_serial_ports()
        self.port_menu = ttk.Combobox(root, textvariable=self.port_var, values=self.ports_list)
        self.port_menu.pack(pady=5)

        self.connect_button = ttk.Button(root, text="Connect", command=self.connect_serial)
        self.connect_button.pack(pady=5)

        self.start_button = ttk.Button(root, text="Start", command=self.start_reading, state=tk.DISABLED)
        self.start_button.pack(pady=5)

        self.stop_button = ttk.Button(root, text="Stop", command=self.stop_reading, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.alert_label = ttk.Label(root, text="", font=("Arial", 12, "bold"), foreground="red")
        self.alert_label.pack(pady=5)

        self.serial_port = None
        self.running = False
        self.gyro_data_x = []
        self.gyro_data_y = []
        self.gyro_data_z = []
        self.thread = None

        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.ax.set_title("Gyroscope Data (X, Y, Z)")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Angular Velocity (dps)")

        self.line_x, = self.ax.plot([], [], 'r-', label="X Axis")
        self.line_y, = self.ax.plot([], [], 'g-', label="Y Axis")
        self.line_z, = self.ax.plot([], [], 'b-', label="Z Axis")
        self.ax.legend()

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(pady=10)

        self.ani = animation.FuncAnimation(self.fig, self.update_plots, interval=500, cache_frame_data=False)

        # Concussion Detection Parameters
        self.smoothing_window_size = 5
        self.impact_buffer = deque(maxlen=10)

        # Evidence-based thresholds (degrees per second)
        self.mild_threshold = 2.0       # Mild Impact: 15–20 dps
        self.moderate_threshold = 20.0   # Moderate Impact: 20–30 dps
        self.severe_threshold = 30.0     # Severe Impact: >30 dps
        # Threshold for severe impact detection

        # Table for Severe Impact Events
        self.table_frame = ttk.Frame(root)
        self.table_frame.pack(pady=10, fill="x")

        self.tree = ttk.Treeview(self.table_frame, columns=("Time", "Impact"), show="headings", height=5)
        self.tree.heading("Time", text="Timestamp")
        self.tree.heading("Impact", text="Impact Force (dps)")
        self.tree.column("Time", width=150)
        self.tree.column("Impact", width=120)
        self.tree.pack(fill="x")

        # Open log file
        self.log_file = open("impact_log.txt", "a")

    def get_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [str(port).split(" ")[0] for port in ports]

    def connect_serial(self):
        port = self.port_var.get()
        if port == 'Select COM port':
            self.status_label.config(text="Status: No Port Selected", foreground="red")
            return
        try:
            self.serial_port = serial.Serial(port, 115200, timeout=1)
            self.status_label.config(text=f"Connected to {port}", foreground="green")
            self.start_button.config(state=tk.NORMAL)
        except serial.SerialException:
            self.status_label.config(text=f"Connection Failed", foreground="red")

    def start_reading(self):
        if self.serial_port:
            self.running = True
            self.thread = threading.Thread(target=self.read_data, daemon=True)
            self.thread.start()
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_label.config(text="Reading Data", foreground="blue")

    def stop_reading(self):
        self.running = False  
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Stopped", foreground="black")
        self.log_file.close()  # Close log file

    def smooth_data(self, new_data):
        self.impact_buffer.append(new_data)
        return np.mean(list(self.impact_buffer))

    def detect_concussion(self, rx, ry, rz):
        """Detects concussion and logs it with a timestamp using realistic thresholds."""
        magnitude = np.sqrt(rx**2 + ry**2 + rz**2)
        smoothed_magnitude = self.smooth_data(magnitude)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Determine severity
        if smoothed_magnitude > self.severe_threshold:
            severity = "Severe"
            alert_text = "Severe Impact: Immediate Attention Needed!"
            alert_color = "darkred"
        elif smoothed_magnitude > self.moderate_threshold:
            severity = "Moderate"
            alert_text = "Moderate Impact: Caution!"
            alert_color = "orange"
        elif smoothed_magnitude > self.mild_threshold:
            severity = "Mild"
            alert_text = "Mild Impact: Monitor for Symptoms"
            alert_color = "yellow"
        else:
            self.alert_label.config(text="")
            return  # No impact detected

        # Update alert label
        self.alert_label.config(text=alert_text, foreground=alert_color)

        # Add entry to the table with severity
        self.tree.insert("", "end", values=(timestamp, f"{smoothed_magnitude:.2f} dps ({severity})"))

        # Print to console & log to file
        message = f"[{timestamp}] {severity} Impact Detected: {smoothed_magnitude:.2f} dps"
        print(message)
        self.log_file.write(message + "\n")

        self.add_detection_to_history(severity, smoothed_magnitude)



    def read_data(self):
        while self.running:
            try:
                if self.serial_port.in_waiting:
                    line = self.serial_port.readline().decode('utf-8').strip()

                    if "$PGYR" in line:
                        gyro_data = line.split("*")[0]  
                        gyro_values = gyro_data.split(",")  

                        if len(gyro_values) == 4:
                            _, rx, ry, rz = gyro_values
                            try:
                                rx, ry, rz = float(rx), float(ry), float(rz)
                                self.gyro_data_x.append(rx)
                                self.gyro_data_y.append(ry)
                                self.gyro_data_z.append(rz)

                                # Detect concussion with the data
                                self.detect_concussion(rx, ry, rz)

                            except ValueError:
                                print("Invalid data format, unable to convert to float")
            except Exception as e:
                print(f"Error Reading Data: {e}")
                self.status_label.config(text=f"Error Reading Data", foreground="red")

            time.sleep(0.05)

    def update_plots(self, frame):
        if self.gyro_data_x:
            self.line_x.set_data(range(len(self.gyro_data_x)), self.gyro_data_x)
        if self.gyro_data_y:
            self.line_y.set_data(range(len(self.gyro_data_y)), self.gyro_data_y)
        if self.gyro_data_z:
            self.line_z.set_data(range(len(self.gyro_data_z)), self.gyro_data_z)

        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()
        

    def add_detection_to_history(self, severity, magnitude):
        try:
            conn = sqlite3.connect("trauma_tracker.db")
            cursor = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            reasoning = f"Detected impact: {magnitude:.2f} dps"
            
            cursor.execute("""
                INSERT INTO results (timestamp, verdict, reasoning, severity, method)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, severity, reasoning, severity, "Sensor"))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"DB Logging Error: {e}")


    def on_close(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.log_file.close()
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TraumaTrackerUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
