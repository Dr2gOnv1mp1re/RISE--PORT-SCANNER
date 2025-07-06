import tkinter as tk
from tkinter import scrolledtext
import socket
import threading

def scan_ports():
    result_box.delete(1.0, tk.END)
    target = entry_target.get().strip()
    try:
        ip = socket.gethostbyname(target)
    except socket.gaierror:
        result_box.insert(tk.END, "Invalid target.\n")
        return

    try:
        start_port = int(entry_start.get())
        end_port = int(entry_end.get())
        if start_port < 1 or end_port > 65535 or start_port > end_port:
            raise ValueError
    except ValueError:
        result_box.insert(tk.END, "Invalid port range.\n")
        return

    result_box.insert(tk.END, f"Scanning {target} ({ip}) ports {start_port} to {end_port}...\n")
    scan_button.config(state=tk.DISABLED)
    threading.Thread(target=threaded_scan, args=(ip, start_port, end_port), daemon=True).start()

def threaded_scan(target, start_port, end_port):
    open_ports = []
    for port in range(start_port, end_port + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((target, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        except Exception:
            pass
        # Update progress in the main thread
        if port % 50 == 0 or port == end_port:
            root.after(0, lambda p=port: result_box.insert(tk.END, f"Scanned up to port {p}\n"))
    # Show open ports in the main thread
    def show_results():
        if open_ports:
            for port in open_ports:
                result_box.insert(tk.END, f"[OPEN] Port {port}\n")
        else:
            result_box.insert(tk.END, "No open ports found.\n")
        result_box.insert(tk.END, "Scan complete.\n")
        scan_button.config(state=tk.NORMAL)
    root.after(0, show_results)

# GUI setup
root = tk.Tk()
root.title("Port Scanner")
root.geometry("500x400")

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Target (IP or domain):").grid(row=0, column=0, sticky="e")
entry_target = tk.Entry(frame, width=30)
entry_target.grid(row=0, column=1, padx=5, pady=2)
entry_target.insert(0, "localhost")

tk.Label(frame, text="Start port:").grid(row=1, column=0, sticky="e")
entry_start = tk.Entry(frame, width=10)
entry_start.grid(row=1, column=1, sticky="w", padx=5, pady=2)
entry_start.insert(0, "1")

tk.Label(frame, text="End port:").grid(row=2, column=0, sticky="e")
entry_end = tk.Entry(frame, width=10)
entry_end.grid(row=2, column=1, sticky="w", padx=5, pady=2)
entry_end.insert(0, "1024")

scan_button = tk.Button(root, text="Scan", command=scan_ports, font=("Arial", 12))
scan_button.pack(pady=5)

result_box = scrolledtext.ScrolledText(root, width=60, height=15, font=("Consolas", 10))
result_box.pack(padx=10, pady=10)

root.mainloop()