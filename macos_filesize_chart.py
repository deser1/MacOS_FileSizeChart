#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

# --- Automatyczna instalacja zależności ---
def _check_dependencies():
    try:
        import matplotlib
    except ImportError:
        print("Brak biblioteki 'matplotlib'. Trwa automatyczna instalacja, proszę czekać...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib>=3.5.0"])
            print("Instalacja zależności zakończona sukcesem.")
        except Exception as e:
            print(f"Nie udało się automatycznie zainstalować zależności: {e}")
            print("Zainstaluj je ręcznie poleceniem: pip3 install matplotlib")
            sys.exit(1)

_check_dependencies()

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib

# Konfiguracja backendu matplotlib dla Tkinter
matplotlib.use("TkAgg")

def get_file_size(file_path):
    try:
        return os.path.getsize(file_path)
    except (OSError, FileNotFoundError, PermissionError):
        return 0

def format_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

class FileSizeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MacOS Analizator Przestrzeni Dyskowej")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Zmienne
        self.target_dir = tk.StringVar(value=os.path.expanduser("~"))
        self.num_files = tk.IntVar(value=10)
        self.is_scanning = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Główny kontener
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- Panel kontrolny (Góra) ---
        control_frame = ttk.LabelFrame(main_frame, text="Ustawienia Skanowania", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Wybór katalogu
        ttk.Label(control_frame, text="Katalog:").grid(row=0, column=0, sticky=tk.W, pady=5)
        dir_entry = ttk.Entry(control_frame, textvariable=self.target_dir, width=50)
        dir_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        browse_btn = ttk.Button(control_frame, text="Przeglądaj...", command=self.browse_directory)
        browse_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Liczba plików
        ttk.Label(control_frame, text="Liczba plików:").grid(row=1, column=0, sticky=tk.W, pady=5)
        num_spinbox = ttk.Spinbox(control_frame, from_=1, to=100, textvariable=self.num_files, width=10)
        num_spinbox.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Przycisk skanowania
        self.scan_btn = ttk.Button(control_frame, text="Rozpocznij Skanowanie", command=self.start_scan)
        self.scan_btn.grid(row=1, column=2, padx=5, pady=5)
        
        # Status
        self.status_var = tk.StringVar(value="Gotowy do skanowania.")
        status_label = ttk.Label(control_frame, textvariable=self.status_var, foreground="gray")
        status_label.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        control_frame.columnconfigure(1, weight=1)
        
        # --- Obszar Wyników (Dół) ---
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Panel boczny z listą plików
        list_frame = ttk.Frame(results_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=(0, 10))
        
        ttk.Label(list_frame, text="Szczegóły Plików:").pack(anchor=tk.W, pady=(0, 5))
        
        # Treeview dla listy plików
        columns = ("#", "Rozmiar", "Nazwa Pliku")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="none")
        self.tree.heading("#", text="Lp.", anchor=tk.CENTER)
        self.tree.heading("Rozmiar", text="Rozmiar", anchor=tk.CENTER)
        self.tree.heading("Nazwa Pliku", text="Nazwa Pliku", anchor=tk.W)
        
        self.tree.column("#", width=40, anchor=tk.CENTER)
        self.tree.column("Rozmiar", width=80, anchor=tk.CENTER)
        self.tree.column("Nazwa Pliku", width=250, anchor=tk.W)
        
        # Pasek przewijania dla listy
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Panel z wykresem
        self.chart_frame = ttk.Frame(results_frame)
        self.chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.figure = plt.Figure(figsize=(6, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=self.target_dir.get(), title="Wybierz katalog do skanowania")
        if directory:
            self.target_dir.set(directory)
            
    def start_scan(self):
        if self.is_scanning:
            return
            
        directory = self.target_dir.get()
        if not os.path.isdir(directory):
            messagebox.showerror("Błąd", "Wybrany katalog nie istnieje!")
            return
            
        self.is_scanning = True
        self.scan_btn.config(state=tk.DISABLED)
        self.status_var.set(f"Skanowanie katalogu: {directory}... Proszę czekać (może to chwilę potrwać).")
        
        # Wyczyść poprzednie wyniki
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.figure.clear()
        self.canvas.draw()
        
        # Uruchom skanowanie w osobnym wątku, aby nie blokować GUI
        thread = threading.Thread(target=self.scan_directory_thread, args=(directory, self.num_files.get()))
        thread.daemon = True
        thread.start()
        
    def scan_directory_thread(self, directory, num_files):
        files_with_sizes = []
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    if not os.path.islink(file_path):
                        size = get_file_size(file_path)
                        if size > 0:
                            files_with_sizes.append((file_path, size))
                            
            files_with_sizes.sort(key=lambda x: x[1], reverse=True)
            largest_files = files_with_sizes[:num_files]
            
            # Zaktualizuj GUI w głównym wątku
            self.root.after(0, self.update_results, largest_files)
        except Exception as e:
            self.root.after(0, self.handle_scan_error, str(e))
            
    def handle_scan_error(self, error_msg):
        self.is_scanning = False
        self.scan_btn.config(state=tk.NORMAL)
        self.status_var.set("Wystąpił błąd podczas skanowania.")
        messagebox.showerror("Błąd Skanowania", f"Wystąpił błąd:\n{error_msg}")

    def update_results(self, files_data):
        self.is_scanning = False
        self.scan_btn.config(state=tk.NORMAL)
        
        if not files_data:
            self.status_var.set("Zakończono. Nie znaleziono żadnych plików.")
            return
            
        self.status_var.set(f"Zakończono. Znaleziono {len(files_data)} największych plików.")
        
        # Aktualizacja tabeli
        labels = []
        sizes = []
        
        for i, (file_path, size) in enumerate(files_data, 1):
            file_name = Path(file_path).name
            formatted_size = format_size(size)
            
            # Wstaw do tabeli
            self.tree.insert("", tk.END, values=(i, formatted_size, file_name))
            
            # Dane do wykresu
            labels.append(f"{file_name}\n({formatted_size})")
            sizes.append(size)
            
        # Aktualizacja wykresu kołowego
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140,
               wedgeprops={'edgecolor': 'white'})
        ax.set_title("Największe pliki", pad=20, fontweight='bold')
        ax.axis('equal')
        
        self.figure.tight_layout()
        self.canvas.draw()

def main():
    root = tk.Tk()
    
    # Próba ustawienia ładniejszego motywu na MacOS
    try:
        from tkinter import ttk
        style = ttk.Style()
        if 'aqua' in style.theme_names():
            style.theme_use('aqua') # Natywny wygląd MacOS
    except Exception:
        pass
        
    app = FileSizeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
