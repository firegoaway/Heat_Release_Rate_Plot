import pandas as pd
import matplotlib.pyplot as plt
import configparser
import sys

from tkinter import Tk, Toplevel, Button, Label
from tkinter.filedialog import askopenfilename
from tkinter import StringVar
from tkinter import messagebox
from tkinter import ttk

import os
import numpy as np
import tkinter as tk # Import tk for main window Frame

def custom_message_box(callback_open_png, callback_open_folder, callback_close):
    def on_open_png():
        callback_open_png()
        #top.destroy()
    
    def on_open_folder():
        callback_open_folder()
        #top.destroy()
    
    def on_close():
        callback_close()
        top.destroy()

    top = Toplevel()
    top.title("HRRP v0.4.0 - Готово")
    top.geometry("500x260")

    current_directory = os.path.dirname(__file__)
    parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
    icon_path = os.path.join(parent_directory, '.gitpics', 'hrrp.ico')

    try:
        top.iconbitmap(icon_path)
        top.wm_iconbitmap(icon_path)
    except Exception as e:
        print(f"Warning: Could not load icon for dialog: {e}")

    # Словарь цветов для стилизации (taken from PCTT)
    colors = {
        "primary": "#3498db",       # Основной цвет (синий)
        "secondary": "#2ecc71",     # Вторичный цвет (зеленый)
        "accent": "#e74c3c",        # Акцентный цвет (красный)
        "bg_light": "#f5f5f5",      # Светлый фон
        "bg_dark": "#2c3e50",       # Темный фон
        "text_light": "#ecf0f1",    # Светлый текст
        "text_dark": "#34495e",     # Темный текст
        "success": "#27ae60",       # Цвет успеха
    }

    # Создаем стили для диалога
    style = ttk.Style()
    style.configure("Success.TLabel",
                   font=("Segoe UI", 14, "bold"),
                   foreground=colors["success"],
                   background=colors["bg_light"])

    style.configure("Message.TLabel",
                   font=("Segoe UI", 11),
                   foreground=colors["text_dark"],
                   background=colors["bg_light"])

    style.configure("Dialog.TButton",
                   font=("Segoe UI", 10, "bold"),
                   padding=10)

    style.map("Dialog.TButton",
             background=[("active", colors["secondary"]),
                         ("!active", colors["primary"])],
             foreground=[("active", colors["text_light"]),
                         ("!active", colors["text_light"])])

    # Стилизация диалога результатов
    top_frame = ttk.Frame(top, padding="20", style="TFrame")
    top_frame.pack(fill=tk.BOTH, expand=True)

    # Иконка успеха (эмодзи или текстовый символ)
    success_icon = ttk.Label(top_frame, text="✓", font=("Segoe UI", 36, "bold"),
                           foreground=colors["success"], background=colors["bg_light"])
    success_icon.pack(pady=(0, 5))

    # Заголовок с сообщением об успехе (Modified for HRRP)
    label = ttk.Label(top_frame, text="График мощности пожара построен!",
                     style="Success.TLabel")
    label.pack(pady=(0, 15))

    # Дополнительное сообщение (Modified for HRRP)
    message = ttk.Label(top_frame,
                       text="Результаты сохранены. Выберите следующее действие:",
                       style="Message.TLabel", wraplength=450)
    message.pack(pady=(0, 20))

    # Кнопки в отдельном фрейме
    button_frame = ttk.Frame(top_frame, style="TFrame")
    button_frame.pack(pady=5)

    # Стилизованные кнопки
    view_btn = ttk.Button(button_frame, text="Показать график",
                         command=on_open_png, style="Dialog.TButton", width=16)
    view_btn.pack(side='left', padx=8)

    folder_btn = ttk.Button(button_frame, text="Открыть папку",
                           command=on_open_folder, style="Dialog.TButton", width=16)
    folder_btn.pack(side='left', padx=8)

    exit_btn = ttk.Button(button_frame, text="Выйти",
                         command=on_close, style="Dialog.TButton", width=16)
    exit_btn.pack(side='left', padx=8)

    # Центрирование окна
    top.update_idletasks()
    width = top.winfo_width()
    height = top.winfo_height()
    x = (top.winfo_screenwidth() // 2) - (width // 2)
    y = (top.winfo_screenheight() // 2) - (height // 2)
    top.geometry(f'{width}x{height}+{x}+{y}')

    # Делаем диалог модальным
    top.transient()  # Поверх других окон
    top.grab_set()  # Модальное окно
    top.protocol("WM_DELETE_WINDOW", on_close)  # Закрытие окна

    # Фокусируем кнопку просмотра графика по умолчанию
    view_btn.focus_set()

def addToClipBoard(text):
    command = 'echo ' + text.strip() + '| clip'
    os.system(command)

def main():
    # --- Get UniqueID from command line arguments ---
    UniqueID = "Unknown"
    if len(sys.argv) > 1:
        try:
            UniqueID = int(sys.argv[1])
            print(f"Process ID received: {UniqueID}")
        except ValueError:
            print(f"Warning: Invalid Process ID received '{sys.argv[1]}'. Using '{UniqueID}'.")
    else:
        print("No Process ID received. Using '{UniqueID}'.")
    # --- End Get UniqueID ---

    # --- Determine CSV file path from INI ---
    config = configparser.ConfigParser()
    current_directory = os.path.dirname(__file__)
    parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
    inis_path = os.path.join(parent_directory, 'inis') # Go up one more level for inis
    ini_file_path = os.path.join(inis_path, f'filePath_{UniqueID}.ini')

    fds_file_path = None
    csv_file_path = None

    if os.path.isfile(ini_file_path):
        try:
            config.read(ini_file_path, encoding='utf-16')
            if 'filePath' in config and 'filePath' in config['filePath']:
                fds_file_path = config['filePath']['filePath']
                fds_dir = os.path.dirname(fds_file_path)
                fds_basename = os.path.splitext(os.path.basename(fds_file_path))[0] # e.g., '21cd5693_tout' or '21cd5693'

                # Pattern 1: Use the fds_basename as is and append _hrr.csv
                csv_filename_pattern1 = f"{fds_basename}_hrr.csv" # e.g., 21cd5693_tout_hrr.csv
                csv_file_path_pattern1 = os.path.join(fds_dir, csv_filename_pattern1)

                # Pattern 2: If fds_basename ends with _tout, remove it before appending _hrr.csv
                fds_basename_without_tout = fds_basename
                if fds_basename.endswith('_tout'):
                    fds_basename_without_tout = fds_basename[:-len('_tout')] # Remove _tout -> e.g., 21cd5693

                csv_filename_pattern2 = f"{fds_basename_without_tout}_hrr.csv" # e.g., 21cd5693_hrr.csv
                csv_file_path_pattern2 = os.path.join(fds_dir, csv_filename_pattern2)

                # Check existence, prioritizing pattern 1 (direct match with _tout if present)
                if os.path.isfile(csv_file_path_pattern1):
                    csv_file_path = csv_file_path_pattern1
                    print(f"Found CSV file (Pattern 1): {csv_file_path}")
                elif os.path.isfile(csv_file_path_pattern2):
                    csv_file_path = csv_file_path_pattern2
                    print(f"Found CSV file (Pattern 2): {csv_file_path}")
                else:
                    csv_file_path = None # Ensure it's None if neither is found
                    print(f"Could not find {csv_filename_pattern1} or {csv_filename_pattern2} in {fds_dir}")

            else:
                messagebox.showerror("Ошибка INI", f"Не найдена секция [filePath] или ключ 'filePath' в {ini_file_path}")
                return
        except Exception as e:
            messagebox.showerror("Ошибка чтения INI", f"Не удалось прочитать файл {ini_file_path}: {e}")
            return
    else:
        messagebox.showerror("Ошибка INI", f"INI файл не найден по пути: {ini_file_path}")
        return

    if not csv_file_path: # Check if csv_file_path is None after attempts
        # Need to reconstruct potential names for the error message
        # Get base info from config again, as fds_file_path might be None
        fds_dir_for_error = "Unknown"
        expected_name1 = "Unknown"
        expected_name2 = "Unknown"
        if 'filePath' in config and 'filePath' in config['filePath']:
            try:
                config_fds_path = config['filePath']['filePath']
                fds_dir_for_error = os.path.dirname(config_fds_path)
                fds_basename_for_error = os.path.splitext(os.path.basename(config_fds_path))[0]
                expected_name1 = f"{fds_basename_for_error}_hrr.csv"
                
                fds_basename_without_tout_for_error = fds_basename_for_error
                if fds_basename_for_error.endswith('_tout'):
                    fds_basename_without_tout_for_error = fds_basename_for_error[:-len('_tout')]
                expected_name2 = f"{fds_basename_without_tout_for_error}_hrr.csv"
            except Exception:
                 pass # Keep unknowns if error reconstructing path

        messagebox.showerror("Ошибка CSV", f"CSV файл не найден в директории: {fds_dir_for_error}\nОжидаемые имена: \n- {expected_name1}\n- {expected_name2}\nПроверьте имя файла и его расположение.")
        return
    # --- End Determine CSV file path ---

    # --- GUI Setup ---
    root = tk.Tk() # Use tk.Tk for the main window
    root.title(f"HRRP v0.4.0 - ID: {UniqueID}")

    # Define color scheme (simplified version from PCTT)
    colors = {
        "primary": "#3498db",
        "secondary": "#2ecc71",
        "bg_light": "#f5f5f5",
        "text_dark": "#34495e",
        "success": "#27ae60",
        "error": "#c0392b"
    }
    root.configure(bg=colors["bg_light"])
    root.geometry("400x150") # Adjusted size

    # Icon
    icon_path = os.path.join(parent_directory, '.gitpics', 'hrrp.ico')
    try:
        root.iconbitmap(icon_path)
        root.wm_iconbitmap(icon_path)
    except Exception as e:
        print(f"Warning: Could not load icon: {e}")

    # Style configuration
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TFrame", background=colors["bg_light"])
    style.configure("TLabel", background=colors["bg_light"], font=("Segoe UI", 10))
    style.configure("TProgressbar", troughcolor=colors["bg_light"], background=colors["secondary"])
    style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), foreground=colors["primary"])

    # Main frame
    main_frame = ttk.Frame(root, padding="15")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Header
    header_label = ttk.Label(main_frame, text="Обработка файла HRR...", style="Header.TLabel")
    header_label.pack(pady=(0, 10))

    # Progress Bar
    root.progress = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate", length=350)
    root.progress.pack(pady=5)

    # Progress Label
    root.progress_label = ttk.Label(main_frame, text="Инициализация...", wraplength=350)
    root.progress_label.pack(pady=5)
    # --- End GUI Setup ---

    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    root.update_idletasks() # Make sure window is positioned before processing

    # --- Start Processing ---
    root.progress_label.config(text=f"Чтение файла: {os.path.basename(csv_file_path)}")
    root.progress['value'] = 5
    root.update_idletasks()

    data = pd.read_csv(csv_file_path, skiprows=1)

    # Удаляем начальные и конечные вайтспейсы из столбцов
    data.columns = data.columns.str.strip()

    root.progress['maximum'] = 100
    root.progress['value'] = 10
    root.progress_label.config(text=f"Обработка заголовков...")
    root.update_idletasks()

    # Создаем путь для _output
    dir_name = os.path.dirname(csv_file_path)
    base_name = os.path.basename(csv_file_path)
    output_file_path = os.path.join(dir_name, f"{os.path.splitext(base_name)[0]}_output.csv")

    root.progress['value'] = 15
    root.progress_label.config(text=f"Создание пути для _output...")
    root.update_idletasks()

    # Сохраняем новый _output
    data.to_csv(output_file_path, index=False)

    root.progress['value'] = 20
    root.progress_label.config(text=f"Сохранение _output файла...")
    root.update_idletasks()

    try:
        time_col = data['Time'] # Renamed for clarity
        hrr_col = data['HRR']  # Renamed for clarity
    except KeyError as e:
        root.progress_label.config(text=f"Ошибка: Отсутствуют колонки 'Time' или 'HRR'", foreground=colors["error"])
        messagebox.showerror("Ошибка данных", f"Ошибка: {e}, убедитесь, что CSV файл содержит колонки 'Time' и 'HRR'")
        root.destroy()
        return

    root.progress['value'] = 40
    root.progress_label.config(text=f"Сбор данных для графика...")
    root.update_idletasks()

    # Обозначаем пути для сохранения картинок
    output_folder_path = os.path.normpath(os.path.join(os.path.dirname(csv_file_path), '..', '..', '..'))
    second_folder_name = os.path.basename(os.path.normpath(os.path.join(os.path.dirname(csv_file_path), '..')))
    output_file_name = f"hrrp_{second_folder_name}_plot.png"
    save_path = os.path.join(output_folder_path, output_file_name)

    root.progress['value'] = 60
    root.progress_label.config(text=f"Определение пути для сохранения графика...")
    root.update_idletasks()

    # Рисуем график
    plt.figure(figsize=(8, 5))
    plt.plot(time_col, hrr_col, color='red', linewidth=0.5)
    plt.scatter(time_col, hrr_col, color='black', s=1)
    plt.xlabel('Время (сек)')
    plt.ylabel('Мощность пожара (кВт)')
    plt.title('График мощности пожара', fontsize=12)
    # plt.legend() # Legend is often unnecessary if only one line is plotted
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    root.progress['value'] = 75
    root.progress_label.config(text=f"Построение графика...")
    root.update_idletasks()

    # Вносим имя сценария в буфер обмена
    addToClipBoard(second_folder_name)

    root.progress['value'] = 80
    root.progress_label.config(text=f"Копирование имени сценария в буфер...")
    root.update_idletasks()

    # Сохраняем график в изображение, GUI не отображаем
    plt.savefig(save_path, bbox_inches='tight', format='png')  # Можно добавить dpi=300 для большего разрешения картинок
    plt.close()  # Закрываем инстанс, освобождаем память

    root.progress['value'] = 100
    root.progress_label.config(text=f"Сохранение графика...", foreground=colors["success"])
    root.update_idletasks()

    # Скрываем окно прогресса перед показом диалога
    root.withdraw()

    # --- End Processing ---

    def OpenPNG():
        os.startfile(save_path)

    def OpenPNGfolder():
        os.startfile(output_folder_path)

    def Close():
        root.quit()  # Закрываем основное окно tkinter

    # Schedule the custom message box to appear after withdrawing the main window
    root.withdraw()
    root.after(0, lambda: custom_message_box(OpenPNG, OpenPNGfolder, Close))

    root.mainloop() # Start the main event loop

if __name__ == "__main__":
    main()
