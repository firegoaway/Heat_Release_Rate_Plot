import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os
import numpy as np

def addToClipBoard(text):
    command = 'echo ' + text.strip() + '| clip'
    os.system(command)

def main():
    root = Tk()
    root.title("HRRP v0.2.0")
    root.iconbitmap('.gitpics\\hrrp.ico')
    root.wm_iconbitmap('.gitpics\\hrrp.ico')
    # root.withdraw()

    file_path = askopenfilename(title="Выберите _hrr.csv файл", filetypes=[("Файлы формата CSV", "*.csv")])
    
    if not file_path:
        print("Ничего не выбрано")
        return

    data = pd.read_csv(file_path, skiprows=1)

    # Удаляем начальные и конечные вайтспейсы из столбцов
    data.columns = data.columns.str.strip()

    # Создаем путь для _output
    dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    output_file_path = os.path.join(dir_name, f"{os.path.splitext(base_name)[0]}_output.csv")
    
    # Сохраняем новый _output
    data.to_csv(output_file_path, index=False)
    
    try:
        time = data['Time']
        hrr = data['HRR']
    except KeyError as e:
        print(f"Ошибка: {e}, убедитесь, что CSV файл содержит колонки 'Time' и 'HRR'")
        return

    # Обозначаем пути для сохранения картинок
    output_folder_path = os.path.normpath(os.path.join(os.path.dirname(file_path), '..', '..', '..'))
    second_folder_name = os.path.basename(os.path.normpath(os.path.join(os.path.dirname(file_path), '..')))
    output_file_name = f"hrrp_{second_folder_name}_plot.png"
    save_path = os.path.join(output_folder_path, output_file_name)

    # Рисуем график
    plt.figure(figsize=(8, 5))
    plt.plot(time, hrr, color='red', linewidth=0.5)
    plt.scatter(time, hrr, color='black', s=1)
    plt.xlabel('Время (сек)')
    plt.ylabel('Мощность пожара (кВт)')
    plt.title('График мощности пожара', fontsize=12)
    plt.legend()
    
    x_ticks = np.arange(min(time), max(time) + 20, 20)
    y_ticks = np.arange(min(hrr), max(hrr) + 100, 100)

    plt.xticks(x_ticks)
    plt.yticks(y_ticks)
    
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    addToClipBoard(second_folder_name)
    
    # Сохраняем график в изображение, GUI не отображаем
    plt.savefig(save_path, bbox_inches='tight', format='png')  # Можно добавить dpi=300 для большего разрешения картинок
    plt.close()  # Закрываем инстанс, освобождаем память

if __name__ == "__main__":
    main()
