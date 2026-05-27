#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import platform

def get_system_drives():
    drives = []
    sys_os = platform.system()
    
    if sys_os == "Windows":
        try:
            import ctypes
            bitmask = ctypes.windll.kernel32.GetLogicalDrives()
            for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                if bitmask & 1:
                    drive_path = f"{letter}:\\"
                    vol_name_buf = ctypes.create_unicode_buffer(1024)
                    try:
                        ctypes.windll.kernel32.GetVolumeInformationW(
                            ctypes.c_wchar_p(drive_path),
                            vol_name_buf, ctypes.sizeof(vol_name_buf),
                            None, None, None, None, 0
                        )
                        vol_name = vol_name_buf.value
                    except Exception:
                        vol_name = ""
                    
                    display = f"{drive_path} [{vol_name}]" if vol_name else drive_path
                    drives.append((display, drive_path))
                bitmask >>= 1
        except Exception:
            pass
    elif sys_os == "Darwin":
        drives.append(("Macintosh HD (/)", "/"))
        vol_dir = "/Volumes"
        if os.path.exists(vol_dir):
            try:
                for vol in os.listdir(vol_dir):
                    path = os.path.join(vol_dir, vol)
                    if os.path.ismount(path) or os.path.isdir(path):
                        drives.append((f"{vol} ({path})", path))
            except Exception:
                pass
    else:
        drives.append(("Root (/)", "/"))
        
    return drives

def resource_path(relative_path):
    """Zwraca bezwzględną ścieżkę do zasobu (działa w dev i w skompilowanym PyInstallerze)"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

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

# Paleta kolorów dla własnego renderera wykresów
COLORS = [
    "#4a90e2", "#f5a623", "#7ed321", "#d0021b", "#bd10e0",
    "#50e3c2", "#f8e71c", "#8b572a", "#417505", "#4a4a4a"
]

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
        
        self.current_files_data = []
        self.chart_type = tk.StringVar(value="pie") # 'pie' lub 'bar'
        
        self.available_drives = []
        self.last_drives_set = set()
        
        self.setup_ui()
        self.update_drives_list()
        
    def setup_ui(self):
        # Główny kontener
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- Panel kontrolny (Góra) ---
        control_frame = ttk.LabelFrame(main_frame, text="Ustawienia Skanowania", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Wybór katalogu / Dysku
        ttk.Label(control_frame, text="Katalog / Dysk:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.dir_combobox = ttk.Combobox(control_frame, textvariable=self.target_dir, width=50)
        self.dir_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.dir_combobox.bind("<<ComboboxSelected>>", self.on_drive_select)
        
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
        columns = ("#", "Rozmiar", "Nazwa Pliku", "Lokalizacja")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="none")
        self.tree.heading("#", text="Lp.", anchor=tk.CENTER)
        self.tree.heading("Rozmiar", text="Rozmiar", anchor=tk.CENTER)
        self.tree.heading("Nazwa Pliku", text="Nazwa Pliku", anchor=tk.W)
        self.tree.heading("Lokalizacja", text="Lokalizacja", anchor=tk.W)
        
        self.tree.column("#", width=40, anchor=tk.CENTER)
        self.tree.column("Rozmiar", width=80, anchor=tk.CENTER)
        self.tree.column("Nazwa Pliku", width=150, anchor=tk.W)
        self.tree.column("Lokalizacja", width=250, anchor=tk.W)
        
        # Paski przewijania dla listy
        scrollbar_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)
        
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Panel z wykresem (Własny renderer Canvas)
        self.chart_frame = ttk.Frame(results_frame)
        self.chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Kontrolki typu wykresu
        chart_controls = ttk.Frame(self.chart_frame)
        chart_controls.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(chart_controls, text="Typ wykresu:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(chart_controls, text="Kołowy", variable=self.chart_type, value="pie", command=self.draw_chart).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(chart_controls, text="Słupkowy", variable=self.chart_type, value="bar", command=self.draw_chart).pack(side=tk.LEFT, padx=5)
        
        # Płótno na którym będziemy własnoręcznie rysować wykresy
        self.canvas = tk.Canvas(self.chart_frame, bg="white", highlightthickness=1, highlightbackground="#cccccc")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Przerysowywanie wykresu przy zmianie rozmiaru okna
        self.canvas.bind("<Configure>", lambda e: self.draw_chart())
        
    def update_drives_list(self):
        current_drives = get_system_drives()
        
        # Sprawdzanie czy lista dysków się zmieniła
        current_set = set(d[0] for d in current_drives)
        if current_set != self.last_drives_set:
            self.available_drives = current_drives
            self.last_drives_set = current_set
            
            # Aktualizacja wartości w ComboBoxie
            self.dir_combobox['values'] = [d[0] for d in current_drives]
            
        # Odświeżaj listę co 2000 ms (2 sekundy) w poszukiwaniu nowych dysków/pendrive'ów
        self.root.after(2000, self.update_drives_list)
        
    def on_drive_select(self, event=None):
        selection = self.dir_combobox.get()
        # Wyciągamy rzeczywistą ścieżkę z wybranej nazwy wyświetlanej
        for display, path in self.available_drives:
            if selection == display:
                self.target_dir.set(path)
                self.dir_combobox.icursor(tk.END)
                break
        
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
        self.canvas.delete("all")
        self.current_files_data = []
        
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
        self.current_files_data = files_data
        
        # Aktualizacja tabeli
        for i, (file_path, size) in enumerate(files_data, 1):
            file_name = Path(file_path).name
            formatted_size = format_size(size)
            self.tree.insert("", tk.END, values=(i, formatted_size, file_name, file_path))
            
        # Rysowanie wykresu po raz pierwszy
        self.draw_chart()

    def draw_chart(self):
        """Główny dyspozytor rysowania wykresów na podstawie wybranego typu."""
        self.canvas.delete("all")
        if not self.current_files_data:
            return
            
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        # Tkinter na początku może zwrócić 1x1 jeśli okno nie zostało w pełni wyrenderowane
        if w < 10 or h < 10:
            self.root.after(100, self.draw_chart)
            return
            
        if self.chart_type.get() == "pie":
            self.draw_pie_chart(w, h)
        else:
            self.draw_bar_chart(w, h)
            
    def draw_pie_chart(self, w, h):
        """Własny kod renderujący wykres kołowy."""
        total_size = sum(size for _, size in self.current_files_data)
        if total_size == 0:
            return
            
        # Marginesy i wyliczenia wymiarów
        margin = 40
        legend_width = 180
        chart_w = w - legend_width
        
        cx = chart_w / 2
        cy = h / 2
        r = min(cx, cy) - margin
        
        if r <= 0:
            return
            
        start_angle = 0
        
        # Tytuł wykresu
        self.canvas.create_text(w/2, 20, text="Rozkład największych plików", font=("Arial", 12, "bold"))
        
        # Rysowanie wycinków (wedges) i legendy
        for i, (file_path, size) in enumerate(self.current_files_data):
            extent = (size / total_size) * 360
            color = COLORS[i % len(COLORS)]
            
            # Tkinter rysuje kąty odwrotnie do wskazówek zegara, co działa idealnie
            self.canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                                   start=start_angle, extent=extent,
                                   fill=color, outline="white", width=1.5)
            
            # Legenda po prawej stronie
            legend_x = chart_w + 10
            legend_y = margin + i * 25
            
            self.canvas.create_rectangle(legend_x, legend_y, legend_x + 15, legend_y + 15, fill=color, outline="black")
            
            file_name = Path(file_path).name
            if len(file_name) > 16:
                file_name = file_name[:13] + "..."
                
            pct = (size / total_size) * 100
            text = f"{file_name} ({pct:.1f}%)"
            self.canvas.create_text(legend_x + 25, legend_y + 7, text=text, anchor=tk.W, font=("Arial", 9))
            
            start_angle += extent

    def draw_bar_chart(self, w, h):
        """Własny kod renderujący poziomy wykres słupkowy."""
        margin_left = 150
        margin_right = 60
        margin_top = 50
        margin_bottom = 30
        
        chart_w = w - margin_left - margin_right
        chart_h = h - margin_top - margin_bottom
        
        if chart_w <= 0 or chart_h <= 0:
            return
            
        max_size = max(size for _, size in self.current_files_data)
        num_bars = len(self.current_files_data)
        
        bar_spacing = 10
        bar_height = (chart_h - (num_bars - 1) * bar_spacing) / num_bars
        
        self.canvas.create_text(w/2, 20, text="Rozmiary największych plików", font=("Arial", 12, "bold"))
        
        # Rysowanie osi Y
        self.canvas.create_line(margin_left, margin_top, margin_left, h - margin_bottom + 10, width=2, fill="gray")
        
        # Iterujemy bezpośrednio po posortowanej liście (największe są na początku, czyli na górze płótna Y=0)
        for i, (file_path, size) in enumerate(self.current_files_data):
            # Zachowujemy te same kolory co na wykresie kołowym
            color = COLORS[i % len(COLORS)]
            
            # Szerokość słupka (proporcjonalnie do max_size)
            bar_length = (size / max_size) * chart_w if max_size > 0 else 0
            
            y0 = margin_top + i * (bar_height + bar_spacing)
            y1 = y0 + bar_height
            x0 = margin_left
            x1 = margin_left + bar_length
            
            # Słupek
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="black")
            
            # Etykieta pliku po lewej (Oś Y)
            file_name = Path(file_path).name
            if len(file_name) > 20:
                file_name = file_name[:17] + "..."
            self.canvas.create_text(margin_left - 10, (y0 + y1) / 2, text=file_name, anchor=tk.E, font=("Arial", 9))
            
            # Etykieta rozmiaru po prawej od słupka
            formatted_size = format_size(size)
            self.canvas.create_text(x1 + 5, (y0 + y1) / 2, text=formatted_size, anchor=tk.W, font=("Arial", 8))

def main():
    root = tk.Tk()
    
    # Ustawienie ikony okna
    icon_path = resource_path("icon.png")
    if os.path.exists(icon_path):
        try:
            icon_img = tk.PhotoImage(file=icon_path)
            root.iconphoto(True, icon_img)
        except Exception:
            pass
            
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
