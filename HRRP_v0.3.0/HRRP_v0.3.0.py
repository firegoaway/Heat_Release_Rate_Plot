import pandas as pd
import matplotlib.pyplot as plt

from tkinter import Tk, Toplevel, Button, Label
from tkinter.filedialog import askopenfilename
from tkinter import StringVar
from tkinter import messagebox
from tkinter import ttk

import os
import numpy as np

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
    top.title("HRRP v0.3.0")
    top.geometry("400x100")
    
    current_directory = os.path.dirname(__file__)
    parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
    icon_path = os.path.join(parent_directory, '.gitpics', 'hrrp.ico')
    
    top.iconbitmap(icon_path)
    top.wm_iconbitmap(icon_path)
    
    top.overrideredirect(False)  # Скрываем стандартную рамку

    label = Label(top, text="Выберите действие", padx=10, pady=10)
    label.pack(pady=(10, 0))
    
    button_frame = ttk.Frame(top)
    button_frame.pack(pady=10)
    
    Button(button_frame, text="Показать график мощности пожара", command=on_open_png).pack(side='left', padx=5)
    Button(button_frame, text="Открыть папку с графиком", command=on_open_folder).pack(side='left', padx=5)
    Button(button_frame, text="Выйти", command=on_close).pack(side='left', padx=5)
    
    top.update_idletasks()
    width = top.winfo_width()
    height = top.winfo_height()
    x = (top.winfo_screenwidth() // 2) - (width // 2)
    y = (top.winfo_screenheight() // 2) - (height // 2)
    top.geometry(f'{width}x{height}+{x}+{y}')

    top.transient()  # Поверх других окон
    top.grab_set()  # Модальное окно
    top.protocol("WM_DELETE_WINDOW", on_close)  # Закрытие окна

def addToClipBoard(text):
    command = 'echo ' + text.strip() + '| clip'
    os.system(command)

def main():
    current_directory = os.path.dirname(__file__)
    parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
    icon_path = os.path.join(parent_directory, '.gitpics', 'hrrp.ico')
    
    root = Tk()
    root.title("HRRP v0.3.0")
    root.iconbitmap(icon_path)
    root.wm_iconbitmap(icon_path)
    # root.withdraw() # Вырубаем GUI
    
    # Прогресс бар
    root.progress = ttk.Progressbar(root, orient="horizontal", mode="determinate", length = 200)
    root.progress.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
    root.progress_label = ttk.Label(root, text="")
    root.progress_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    file_path = askopenfilename(title="Выберите _hrr.csv файл", filetypes=[("Файлы формата CSV", "*.csv")])
    
    if not file_path:
        print("Ничего не выбрано")
        return

    data = pd.read_csv(file_path, skiprows=1)

    # Удаляем начальные и конечные вайтспейсы из столбцов
    data.columns = data.columns.str.strip()
    
    root.progress['maximum'] = 100
    root.progress['value'] = 10
    root.progress_label.config(text=f"Удаляем начальные и конечные вайтспейсы из столбцов..")
    root.update_idletasks()

    # Создаем путь для _output
    dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    output_file_path = os.path.join(dir_name, f"{os.path.splitext(base_name)[0]}_output.csv")
    
    root.progress['value'] = 15
    root.progress_label.config(text=f"Создаем путь для _output...")
    root.update_idletasks()
    
    # Сохраняем новый _output
    data.to_csv(output_file_path, index=False)
    
    root.progress['value'] = 20
    root.progress_label.config(text=f"Сохраняем новый _output....")
    root.update_idletasks()
    
    try:
        time = data['Time']
        hrr = data['HRR']
    except KeyError as e:
        print(f"Ошибка: {e}, убедитесь, что CSV файл содержит колонки 'Time' и 'HRR'")
        return
        
    root.progress['value'] = 40
    root.progress_label.config(text=f"Собираем значения мощности пожара.....")
    root.update_idletasks()

    # Обозначаем пути для сохранения картинок
    output_folder_path = os.path.normpath(os.path.join(os.path.dirname(file_path), '..', '..', '..'))
    second_folder_name = os.path.basename(os.path.normpath(os.path.join(os.path.dirname(file_path), '..')))
    output_file_name = f"hrrp_{second_folder_name}_plot.png"
    save_path = os.path.join(output_folder_path, output_file_name)
    
    root.progress['value'] = 60
    root.progress_label.config(text=f"Обозначаем пути для сохранения картинок......")
    root.update_idletasks()

    # Рисуем график
    plt.figure(figsize=(8, 5))
    plt.plot(time, hrr, color='red', linewidth=0.5)
    plt.scatter(time, hrr, color='black', s=1)
    plt.xlabel('Время (сек)')
    plt.ylabel('Мощность пожара (кВт)')
    plt.title('График мощности пожара', fontsize=12)
    plt.legend()
    """
    x_ticks = np.arange(min(time), max(time) + 20, 20)
    y_ticks = np.arange(min(hrr), max(hrr) + 100, 100)

    plt.xticks(x_ticks)
    plt.yticks(y_ticks)
    """
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    root.progress['value'] = 75
    root.progress_label.config(text=f"Рисуем график.......")
    root.update_idletasks()
    
    # Вносим имя сценария в буфер обмена
    addToClipBoard(second_folder_name)
    
    root.progress['value'] = 80
    root.progress_label.config(text=f"Вносим имя сценария в буфер обмена........")
    root.update_idletasks()
    
    # Сохраняем график в изображение, GUI не отображаем
    plt.savefig(save_path, bbox_inches='tight', format='png')  # Можно добавить dpi=300 для большего разрешения картинок
    plt.close()  # Закрываем инстанс, освобождаем память
    
    root.withdraw() # Вырубаем GUI
    
    root.progress['value'] = 100
    root.progress_label.config(text=f"Сохраняем график в изображение.........")
    root.update_idletasks()
    
    def OpenPNG():
        os.startfile(save_path)

    def OpenPNGfolder():
        os.startfile(output_folder_path)

    def Close():
        root.quit()  # Закрываем основное окно tkinter

    custom_message_box(OpenPNG, OpenPNGfolder, Close)
    
    root.mainloop()

if __name__ == "__main__":
    main()
