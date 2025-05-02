import pandas as pd
import matplotlib.pyplot as plt
import configparser
import sys
import glob # Добавлен импорт glob

from tkinter import Tk, Toplevel, Button, Label
from tkinter.filedialog import askopenfilename
from tkinter import StringVar
from tkinter import messagebox
from tkinter import ttk

import os
import numpy as np
import tkinter as tk # Импорт tk для основного окна

def custom_message_box(parent, callback_open_png, callback_open_folder, callback_close):
    def on_open_png():
        callback_open_png()
        #top.destroy()
    
    def on_open_folder():
        callback_open_folder()
        #top.destroy()
    
    def on_close():
        callback_close()
        top.destroy()

    top = Toplevel(parent)
    top.title("HRRP v0.5.0 - Готово")
    top.geometry("500x260")

    current_directory = os.path.dirname(__file__)
    parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
    icon_path = os.path.join(parent_directory, '.gitpics', 'hrrp.ico')

    try:
        top.iconbitmap(icon_path)
        top.wm_iconbitmap(icon_path)
    except Exception as e:
        print(f"Внимание: Не удалось загрузить иконку для диалога: {e}")

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

    # Создаем наш собственный стиль кнопки для диалога
    style.configure("HRRP.TButton", 
                   font=("Segoe UI", 10, "bold"), 
                   padding=10)
    
    style.map("HRRP.TButton",
             background=[("active", colors["secondary"]),
                         ("!disabled", colors["primary"]),
                         ("disabled", "#bdc3c7")],
             foreground=[("active", colors["text_light"]),
                         ("!disabled", colors["text_light"]),
                         ("disabled", "#7f8c8d")])

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

    # Стилизованные кнопки с нашим новым стилем
    view_btn = ttk.Button(button_frame, text="Показать график",
                         command=on_open_png, style="HRRP.TButton", width=16)
    view_btn.pack(side='left', padx=8)

    folder_btn = ttk.Button(button_frame, text="Открыть папку",
                           command=on_open_folder, style="HRRP.TButton", width=16)
    folder_btn.pack(side='left', padx=8)

    exit_btn = ttk.Button(button_frame, text="Выйти",
                         command=on_close, style="HRRP.TButton", width=16)
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

# --- Новый HRRPApp класс ---
class HRRPApp(tk.Tk):
    def __init__(self, UniqueID):
        super().__init__()
        self.UniqueID = UniqueID
        self.csv_file_path = None
        self.fds_dir = "Unknown"

        # --- Настройка GUI ---
        self.title(f"HRRP v0.5.0 - ID: {self.UniqueID}")

        # Цвета (упрощенные)
        self.colors = {
            "primary": "#3498db",
            "secondary": "#2ecc71",
            "bg_light": "#f5f5f5",
            "text_dark": "#34495e",
            "success": "#27ae60",
            "warning": "#f39c12",
            "error": "#c0392b",
            "text_light": "#ecf0f1"
        }
        self.configure(bg=self.colors["bg_light"])
        self.geometry("500x180")
        self.minsize(450, 150)

        # Иконка
        current_directory = os.path.dirname(__file__)
        parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
        icon_path = os.path.join(parent_directory, '.gitpics', 'hrrp.ico')
        try:
            self.iconbitmap(icon_path)
            self.wm_iconbitmap(icon_path)
        except Exception as e:
            print(f"Warning: Could not load icon: {e}")

        # Стиль
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TFrame", background=self.colors["bg_light"])
        self.style.configure("TLabel", background=self.colors["bg_light"], font=("Segoe UI", 10))
        
        # Создаем собственные стили кнопок с явными цветами для всех состояний
        self.style.configure("HRRP.TButton", 
                            font=("Segoe UI", 10, "bold"), 
                            padding=10)
        
        # Важно: Установите цвета для всех состояний, включая отключенные
        self.style.map("HRRP.TButton",
                      background=[("active", self.colors["secondary"]),
                                  ("!disabled", self.colors["primary"]),
                                  ("disabled", "#bdc3c7")],
                      foreground=[("active", self.colors["text_light"]),
                                  ("!disabled", self.colors["text_light"]),
                                  ("disabled", "#7f8c8d")])
        
        self.style.configure("Status.TLabel", font=("Segoe UI", 10, "bold"))

        # Основной фрейм
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Лейбл статуса
        self.status_label = ttk.Label(main_frame, text="Инициализация...", style="Status.TLabel", wraplength=450)
        self.status_label.pack(pady=(0, 15))

        # Фрейм кнопок
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        # Кнопки
        self.select_file_btn = ttk.Button(button_frame, text="Выбрать CSV файл", command=self.select_file, width=20, style="HRRP.TButton")
        self.select_file_btn.pack(side=tk.LEFT, padx=(0, 10), expand=True)

        self.calculate_btn = ttk.Button(button_frame, text="Рассчитать", command=self.start_calculation, 
                                      state="disabled", width=20, style="HRRP.TButton")
        self.calculate_btn.pack(side=tk.LEFT, padx=(10, 0), expand=True)
        
        # --- Проверка INI и CSV ---
        self._check_ini_and_csv()

        # Центрирование окна
        self.center_window()

    def _on_calculate_btn_state_change(self, state):
        """Обновление стиля кнопки на основе состояния"""
        # Нет необходимости изменять стили, ttk будет обрабатывать их через style.map
        pass
    
    def _check_ini_and_csv(self):
        config = configparser.ConfigParser()
        current_directory = os.path.dirname(__file__)
        parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
        inis_path = os.path.join(parent_directory, 'inis')
        ini_file_path = os.path.join(inis_path, f'filePath_{self.UniqueID}.ini')

        ini_found = False
        csv_found = False
        status_text = ""
        status_color = self.colors["text_dark"] # Default

        if os.path.isfile(ini_file_path):
            ini_found = True
            try:
                config.read(ini_file_path, encoding='utf-16')
                if 'filePath' in config and 'filePath' in config['filePath']:
                    fds_file_path = config['filePath']['filePath']
                    self.fds_dir = os.path.dirname(fds_file_path)
                    fds_basename = os.path.splitext(os.path.basename(fds_file_path))[0]

                    base_part = fds_basename
                    postfixes = ['_nfs_tout', '_tout_nfs', '_nfs', '_tout']
                    for postfix in postfixes:
                        if base_part.endswith(postfix):
                            base_part = base_part[:-len(postfix)]
                            break

                    csv_filename_pattern = f"{base_part}*_hrr.csv"
                    csv_file_path_pattern = os.path.join(self.fds_dir, csv_filename_pattern)
                    found_files = glob.glob(csv_file_path_pattern)

                    if found_files:
                        found_files.sort()
                        self.csv_file_path = found_files[0]
                        csv_found = True
                        print(f"Найден CSV файл по шаблону '{csv_filename_pattern}': {self.csv_file_path}")
                    else:
                        print(f"Не удалось найти файл по шаблону '{csv_filename_pattern}' в {self.fds_dir}")
                        self.csv_file_path = None
                else:
                    print(f"Ошибка: Не найдена секция [filePath] или ключ 'filePath' в {ini_file_path}")
                    self.csv_file_path = None
            except Exception as e:
                print(f"Ошибка чтения INI: {e}")
                self.csv_file_path = None
        else:
            print(f"Предупреждение: INI файл не найден по пути: {ini_file_path}")
            self.csv_file_path = None

        # Update GUI based on check results
        if ini_found and csv_found:
            status_text = f"Найден INI и CSV файл: {os.path.basename(self.csv_file_path)}"
            status_color = self.colors["success"]
            self.calculate_btn.config(state="normal")
        elif ini_found and not csv_found:
            status_text = "Найден INI, но CSV файл не найден. Выберите файл вручную."
            status_color = self.colors["warning"]
            self.calculate_btn.config(state="disabled")
        else: # INI not found
            status_text = "INI файл не найден. Выберите CSV файл вручную."
            status_color = self.colors["warning"]
            self.calculate_btn.config(state="disabled")

        self.status_label.config(text=status_text, foreground=status_color)

    def select_file(self):
        initial_dir = self.fds_dir if self.fds_dir != "Unknown" else os.getcwd()
        selected_path = askopenfilename(
            title="Выберите файл *_hrr.csv",
            initialdir=initial_dir,
            filetypes=[("CSV файлы", "*_hrr.csv"), ("Все файлы", "*.*")]
        )
        if selected_path:
            self.csv_file_path = selected_path
            status_text = f"Выбран файл: {os.path.basename(self.csv_file_path)}"
            self.status_label.config(text=status_text, foreground=self.colors["success"])
            self.calculate_btn.config(state="normal")
            print(f"Выбран файл вручную: {self.csv_file_path}")
        else:
            # Сохраняем предыдущий статус, если выбор был отменен
            if not self.csv_file_path: # Показываем предупреждение только если не был выбран файл
                self.status_label.config(text="Выбор файла отменен. Выберите CSV файл вручную.", foreground=self.colors["warning"])
                self.calculate_btn.config(state="disabled")
            print("Выбор файла отменен.")

    def start_calculation(self):
        if not self.csv_file_path:
            messagebox.showerror("Ошибка", "Не выбран CSV файл для расчета.")
            return

        print("Запуск расчета...")
        self.withdraw() # Скрываем начальное GUI
        # Вызываем фактическую функцию обработки здесь, передавая экземпляр приложения
        run_processing(self, self.csv_file_path, self.UniqueID)
        # Удалите преждевременное завершение, позвольте run_processing обрабатывать жизненный цикл приложения
        # self.quit()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

# --- End HRRPApp Class ---

# --- Core Processing Logic ---
def run_processing(app, csv_file_path, UniqueID):
    # --- Настройка GUI Прогресса --- (Adapted from original main)
    # Создаем Toplevel вместо Tk() для окна прогресса
    root_progress = tk.Toplevel(app)
    root_progress.withdraw() # Скрываем окно прогресса
    root_progress.title(f"HRRP v0.5.0 - Обработка ID: {UniqueID}")

    # Используем те же цвета
    root_progress.configure(bg=app.colors["bg_light"])
    root_progress.geometry("400x150") # Подстройте размер по необходимости

    # Иконка (путь должен быть доступен)
    current_directory = os.path.dirname(__file__)
    parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
    icon_path = os.path.join(parent_directory, '.gitpics', 'hrrp.ico')
    try:
        root_progress.iconbitmap(icon_path)
        root_progress.wm_iconbitmap(icon_path)
    except Exception as e:
        print(f"Warning: Could not load progress icon: {e}")

    # Настройка стиля (можно переиспользовать стиль из App или создать новый)
    style = ttk.Style(root_progress) # Pass the root window to the style
    style.theme_use('clam')
    style.configure("Progress.TFrame", background=app.colors["bg_light"])
    style.configure("Progress.TLabel", background=app.colors["bg_light"], font=("Segoe UI", 10))
    # Настройка стиля горизонтальной полосы прогресса по умолчанию
    style.configure("Horizontal.TProgressbar", troughcolor=app.colors["bg_light"], background=app.colors["secondary"])
    style.configure("Header.Progress.TLabel", font=("Segoe UI", 12, "bold"), foreground=app.colors["primary"])

    # Основной фрейм прогресса
    main_frame = ttk.Frame(root_progress, padding="15", style="Progress.TFrame")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Заголовок
    header_label = ttk.Label(main_frame, text="Обработка файла HRR...", style="Header.Progress.TLabel")
    header_label.pack(pady=(0, 10))

    # Полоса прогресса - удалите аргумент custom style
    progress_bar = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate", length=350)
    progress_bar.pack(pady=5)

    # Лейбл прогресса
    progress_label = ttk.Label(main_frame, text="Инициализация...", wraplength=350, style="Progress.TLabel")
    progress_label.pack(pady=5)

    # Центрирование окна прогресса
    root_progress.update_idletasks()
    width = root_progress.winfo_width()
    height = root_progress.winfo_height()
    x = (root_progress.winfo_screenwidth() // 2) - (width // 2)
    y = (root_progress.winfo_screenheight() // 2) - (height // 2)
    root_progress.geometry(f'{width}x{height}+{x}+{y}')
    root_progress.deiconify() # Показываем окно прогресса
    root_progress.update_idletasks()

    try:
        # --- Начало обработки --- (Логика из main)
        progress_label.config(text=f"Чтение файла: {os.path.basename(csv_file_path)}")
        progress_bar['value'] = 5
        root_progress.update_idletasks()

        data = pd.read_csv(csv_file_path, skiprows=1)

        data.columns = data.columns.str.strip()

        progress_bar['maximum'] = 100
        progress_bar['value'] = 10
        progress_label.config(text=f"Обработка заголовков...")
        root_progress.update_idletasks()

        dir_name = os.path.dirname(csv_file_path)
        base_name = os.path.basename(csv_file_path)
        output_file_path = os.path.join(dir_name, f"{os.path.splitext(base_name)[0]}_output.csv")

        progress_bar['value'] = 15
        progress_label.config(text=f"Создание пути для _output...")
        root_progress.update_idletasks()

        data.to_csv(output_file_path, index=False)

        progress_bar['value'] = 20
        progress_label.config(text=f"Сохранение _output файла...")
        root_progress.update_idletasks()

        try:
            if 'Time' in data.columns:
                time_col_name = 'Time'
            elif 'FDS_HRR_Time' in data.columns:
                time_col_name = 'FDS_HRR_Time'
            else:
                raise KeyError("Не найдена колонка времени ('Time' или 'FDS_HRR_Time')")

            if 'HRR' not in data.columns:
                raise KeyError("Не найдена колонка мощности ('HRR')")

            time_col = data[time_col_name]
            hrr_col = data['HRR']
        except KeyError as e:
            error_message = f"Ошибка: {e}, убедитесь, что CSV файл содержит необходимую колонку времени ('Time' или 'FDS_HRR_Time') и колонку мощности ('HRR')"
            progress_label.config(text=error_message, foreground=app.colors["error"])
            messagebox.showerror("Ошибка данных", error_message)
            root_progress.destroy()
            return

        progress_bar['value'] = 40
        progress_label.config(text=f"Сбор данных для графика...")
        root_progress.update_idletasks()

        output_folder_path = os.path.normpath(os.path.join(os.path.dirname(csv_file_path), '..', '..', '..'))
        second_folder_name = os.path.basename(os.path.normpath(os.path.join(os.path.dirname(csv_file_path), '..')))
        output_file_name = f"hrrp_{second_folder_name}_plot.png"
        save_path = os.path.join(output_folder_path, output_file_name)

        progress_bar['value'] = 60
        progress_label.config(text=f"Определение пути для сохранения графика...")
        root_progress.update_idletasks()

        plt.figure(figsize=(8, 5))
        plt.plot(time_col, hrr_col, color='red', linewidth=0.5)
        plt.scatter(time_col, hrr_col, color='black', s=1)
        plt.xlabel('Время (сек)')
        plt.ylabel('Мощность пожара (кВт)')
        plt.title('График мощности пожара', fontsize=12)
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)

        progress_bar['value'] = 75
        progress_label.config(text=f"Построение графика...")
        root_progress.update_idletasks()

        addToClipBoard(second_folder_name)

        progress_bar['value'] = 80
        progress_label.config(text=f"Копирование имени сценария в буфер...")
        root_progress.update_idletasks()

        plt.savefig(save_path, bbox_inches='tight', format='png')
        plt.close()

        progress_bar['value'] = 100
        progress_label.config(text=f"Сохранение графика...", foreground=app.colors["success"])
        root_progress.update_idletasks()

        root_progress.withdraw() # Скрываем окно прогресса

        # --- Показ диалога завершения --- (Adapted from original main)
        def OpenPNG():
            os.startfile(save_path)

        def OpenPNGfolder():
            os.startfile(output_folder_path)

        def CloseApp():
            # Нам нужен способ правильно завершить жизненный цикл приложения
            # На данный момент мы уничтожаем root_progress.
            #root_progress.quit() # Заверщает главный цикл hidden progress root's mainloop, если он запущен
            root_progress.destroy()
            # sys.exit() # Выход из всего скрипта
            # Вместо sys.exit(), убедитесь, что все циклы Tkinter завершены.
            # Главный цикл HRRPApp был завершен ранее через withdraw/quit. Цикл progress завершится, когда его окно будет уничтожено.
            # ends when its window is destroyed.
            # Вызовите app.destroy() для завершения главного цикла приложения
            app.destroy()

        # Используй root_progress в качестве родителя для диалога
        # Нет необходимости для root_progress.mainloop() как app.mainloop() запущен
        root_progress.after(0, lambda: custom_message_box(root_progress, OpenPNG, OpenPNGfolder, CloseApp))
        # root_progress.mainloop()

    except Exception as e:
        messagebox.showerror("Ошибка обработки", f"Произошла ошибка: {e}")
        if root_progress.winfo_exists():
             root_progress.destroy()
        # Также уничтожаем главную программу, если возникает ошибка во время обработки
        if app.winfo_exists():
             app.destroy()

# --- Конец основной логики обработки ---

def main():
    # --- Получение UniqueID из аргументов командной строки ---
    UniqueID = "Unknown"
    if len(sys.argv) > 1:
        try:
            UniqueID = int(sys.argv[1])
            print(f"Получен ID процесса: {UniqueID}")
        except ValueError:
            print(f"Внимание: Получен недопустимый ID процесса '{sys.argv[1]}'. Используется '{UniqueID}'.")
    else:
        print(f"Не получен ID процесса. Используется '{UniqueID}'.")
    # --- Конец получения UniqueID ---

    # --- Запуск нового приложения ---
    app = HRRPApp(UniqueID)
    app.mainloop()

if __name__ == "__main__":
    main()
