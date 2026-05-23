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
from datetime import datetime
import pytz

class TraumaTrackerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Trauma Tracker")
        self.root.geometry("700x500")

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

        self.concussion_label = ttk.Label(root, text="Concussion Status: No Data", font=("Arial", 12), foreground="blue")
        self.concussion_label.pack(pady=10)

        # Table for timestamps
        self.timestamp_table = ttk.Treeview(root, columns=("#1"), show="headings")
        self.timestamp_table.heading("#1", text="Concussion Timestamps")
        self.timestamp_table.pack(pady=5)

        # Serial Variables
        self.serial_port = None
        self.running = False
        self.data = []  # Store accelerometer data
        self.timestamps = []  # Store timestamps of concussion hits
        self.thread = None  # Keep track of the reading thread
        self.concussion_detected = False  # Flag to indicate concussion event

        # Matplotlib Figure (Embedded)
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.ax.set_title("Accelerometer Data")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Acceleration")
        self.line, = self.ax.plot([], [], 'r-', label="Acceleration")
        self.ax.legend()

        # Embed Matplotlib plot in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(pady=10)

        # Animation for live plotting
        self.ani = animation.FuncAnimation(self.fig, self.update_plot, interval=500, cache_frame_data=False)

    def get_serial_ports(self):
        """Gets a list of available serial ports."""
        ports = serial.tools.list_ports.comports()
        return [str(port).split(" ")[0] for port in ports]

    def connect_serial(self):
        """Connects to the selected serial port."""
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
        """Starts the thread for reading serial data."""
        if self.serial_port:
            self.running = True
            self.thread = threading.Thread(target=self.read_data, daemon=True)
            self.thread.start()
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_label.config(text="Reading Data", foreground="blue")

    def stop_reading(self):
        """Stops data collection but retains graph data."""
        self.running = False  # Stop reading data
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Stopped", foreground="black")

    def read_data(self):
        """Reads and processes data from the serial port."""
        est = pytz.timezone('US/Eastern')
        while self.running:
            try:
                if self.serial_port.in_waiting:
                    line = self.serial_port.readline().decode('utf-8').strip()
                    print(f"Raw Data: {line}")

                    # Extract accelerometer data
                    segments = line.split("*")
                    acc_data = None
                    for segment in segments:
                        if segment.startswith("$ACC"):
                            acc_data = segment
                            break

                    if acc_data:
                        try:
                            _, x, y, z = acc_data.split(",")
                            x, y, z = float(x), float(y), float(z)
                            acc_magnitude = np.sqrt(x**2 + y**2 + z**2)
                            self.data.append(acc_magnitude)  # Store all data persistently

                            # Check for concussion threshold (3g)
                            if abs(acc_magnitude) > 3:
                                self.concussion_label.config(text="Concussion Status: Potential Concussion Hit!", foreground="red")
                                self.concussion_detected = True
                                timestamp = datetime.now(est).strftime('%Y-%m-%d %H:%M:%S EST')
                                self.timestamps.append(timestamp)
                                self.timestamp_table.insert("", "end", values=(timestamp,))

                        except ValueError:
                            print("Invalid Data Format")
                            pass

            except Exception as e:
                print(f"Error Reading Data: {e}")
                self.status_label.config(text=f"Error Reading Data", foreground="red")

            time.sleep(0.05)

    def update_plot(self, frame):
        """Updates the Matplotlib plot dynamically."""
        self.line.set_data(range(len(self.data)), self.data)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    def on_close(self):
        """Handles cleanup when the user closes the window."""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TraumaTrackerUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
