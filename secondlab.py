from dataclasses import dataclass
from datetime import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re
import os
from PIL import Image, ImageTk

@dataclass
class MenuItem:
    name: str
    price: float
    cook_time: time
    color: str


def parse_item(line: str):
    """Парсит строку в объект MenuItem"""
    m = re.match(r'"([^"]+)"\s+([\d.]+)\s+(\d{2}):(\d{2})(?:\s+(\w+))?', line.strip())
    if not m:
        return None
    return MenuItem(m.group(1), float(m.group(2)), 
                   time(int(m.group(3)), int(m.group(4))),
                   m.group(5) if m.group(5) else "не указан")


def load_file(fname):
    """Загрузка из файла"""
    items = []
    if os.path.exists(fname):
        with open(fname, 'r', encoding='utf-8') as f:
            for line in f:
                item = parse_item(line.strip())
                if item:
                    items.append(item)
    return items


class TableWindow:
    """Основное окно с таблицей"""
    def __init__(self, parent, main_win):
        self.main = main_win
        self.items = []
        self.current_file = None
        
        self.root = tk.Toplevel(parent)
        self.root.title("Меню - таблица")
        self.root.geometry("800x550")
        
        # Верхняя панель с кнопками
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5, fill=tk.X)
        
        tk.Button(btn_frame, text="← Назад", command=self.go_back,
                 bg="#607D8B", fg="white", width=12, height=1, font=("Arial", 9)).pack(side=tk.LEFT, padx=3)
        
        tk.Button(btn_frame, text="Добавить", command=self.add_item,
                 bg="#4CAF50", fg="white", width=12, height=1, font=("Arial", 9)).pack(side=tk.LEFT, padx=3)
        
        tk.Button(btn_frame, text="Удалить", command=self.delete_item,
                 bg="#f44336", fg="white", width=12, height=1, font=("Arial", 9)).pack(side=tk.LEFT, padx=3)
        
        tk.Button(btn_frame, text="Сохранить", command=self.save_to_file,
                 bg="#FF9800", fg="white", width=12, height=1, font=("Arial", 9)).pack(side=tk.LEFT, padx=3)
        
        # Таблица
        self.table = ttk.Treeview(self.root, columns=("Название","Цена","Время","Цвет"), show="headings")
        for c, w in [("Название",350), ("Цена",100), ("Время",100), ("Цвет",150)]:
            self.table.heading(c, text=c)
            self.table.column(c, width=w)
        self.table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Статусная строка
        self.status_label = tk.Label(self.root, text="Таблица пуста", font=("Arial", 9), fg="gray")
        self.status_label.pack(pady=5)
        
        self.root.protocol("WM_DELETE_WINDOW", self.go_back)
        self.refresh()
    
    def go_back(self):
        self.root.withdraw()
        self.main.show()
    
    def refresh(self):
        for row in self.table.get_children():
            self.table.delete(row)
        for it in self.items:
            self.table.insert("", tk.END, values=(it.name, f"{it.price:.2f}", 
                              it.cook_time.strftime("%H:%M"), it.color))
        self.status_label.config(text=f"Всего блюд: {len(self.items)}")
    
    def add_item(self):
        """Диалог добавления блюда"""
        dlg = tk.Toplevel(self.root)
        dlg.title("Добавить блюдо")
        dlg.geometry("350x300")
        dlg.resizable(False, False)
        
        entries = []
        labels = ["Название (\"...\")", "Цена", "Время (ЧЧ:ММ)", "Цвет (опц.)"]
        
        for lbl in labels:
            tk.Label(dlg, text=lbl).pack(pady=(10,0))
            e = tk.Entry(dlg, width=35)
            e.pack()
            entries.append(e)
        
        def save():
            try:
                name, price, tm, color = [e.get().strip() for e in entries]
                if not name or not price or not tm:
                    raise ValueError
                if not name.startswith('"') or not name.endswith('"'):
                    raise ValueError
                line = f'{name} {price} {tm}' + (f' {color}' if color else '')
                item = parse_item(line)
                if item:
                    self.items.append(item)
                    self.refresh()
                    dlg.destroy()
                else:
                    messagebox.showerror("Ошибка", "Неверный формат")
            except:
                messagebox.showerror("Ошибка", "Проверьте данные")
        
        tk.Button(dlg, text="Сохранить", command=save, bg="#4CAF50", fg="white", width=15, height=1).pack(pady=15)
    
    def delete_item(self):
        """Удаляет выделенный элемент"""
        sel = self.table.selection()
        if not sel:
            messagebox.showwarning("", "Выберите объект для удаления")
            return
        if messagebox.askyesno("", "Удалить выбранное блюдо?"):
            idx = self.table.index(sel[0])
            del self.items[idx]
            self.refresh()
    
    def save_to_file(self):
        """Сохраняет текущую таблицу в файл"""
        if not self.items:
            messagebox.showwarning("", "Нет данных для сохранения")
            return
        
        fname = filedialog.asksaveasfilename(
            title="Сохранить файл",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if fname:
            with open(fname, 'w', encoding='utf-8') as f:
                for it in self.items:
                    f.write(f'"{it.name}" {it.price} {it.cook_time.strftime("%H:%M")} {it.color}\n')
            messagebox.showinfo("Успех", f"Сохранено {len(self.items)} блюд")
    
    def load_items_from_file(self, items, filename):
        """Загружает данные из файла в таблицу"""
        self.items = items.copy()
        self.current_file = filename
        self.refresh()


class LoadWindow:
    """Дополнительное окно для загрузки файла"""
    def __init__(self, parent, table_window):
        self.table_window = table_window
        self.current_file = None
        
        self.root = tk.Toplevel(parent)
        self.root.title("Загрузка файла")
        self.root.geometry("600x500")
        self.root.minsize(550, 450)  # Минимальный размер
        
        # Основной контейнер с отступами
        main_container = tk.Frame(self.root, padx=15, pady=15)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Кнопка "Загрузить файл"
        tk.Button(main_container, text="📂 ЗАГРУЗИТЬ ФАЙЛ", command=self.select_file,
                 bg="#2196F3", fg="white", width=25, height=2, 
                 font=("Arial", 11, "bold")).pack(pady=(0, 15))
        
        # Окошко с содержимым файла
        info_frame = tk.LabelFrame(main_container, text="Содержимое файла", font=("Arial", 10, "bold"))
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Создаём фрейм для текста и скролла
        text_frame = tk.Frame(info_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.file_text = tk.Text(text_frame, wrap=tk.WORD, font=("Courier", 10))
        scroll = tk.Scrollbar(text_frame, command=self.file_text.yview)
        self.file_text.configure(yscrollcommand=scroll.set)
        self.file_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопка "Обработать"
        tk.Button(main_container, text="✅ ОБРАБОТАТЬ", command=self.process_file,
                 bg="#4CAF50", fg="white", width=25, height=2, 
                 font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        # Текст-подсказка
        self.file_text.insert(1.0, "Файл не выбран.\n\nНажмите 'ЗАГРУЗИТЬ ФАЙЛ' для выбора файла .txt")
        self.file_text.config(state=tk.DISABLED)
        
        # Центрируем окно после создания всех виджетов
        self.root.update_idletasks()
        self.center_window()
    
    def center_window(self):
        """Центрирует окно на экране"""
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')
    
    def select_file(self):
        """Выбор файла"""
        fname = filedialog.askopenfilename(
            title="Выберите файл с данными",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if fname:
            self.current_file = fname
            self.show_file_content()
            messagebox.showinfo("Информация", f"Выбран файл: {os.path.basename(fname)}\n\nНажмите 'ОБРАБОТАТЬ' для загрузки данных в таблицу")
    
    def show_file_content(self):
        """Показывает содержимое файла в текстовом поле"""
        self.file_text.config(state=tk.NORMAL)
        self.file_text.delete(1.0, tk.END)
        
        if self.current_file and os.path.exists(self.current_file):
            with open(self.current_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.file_text.insert(1.0, content)
        else:
            self.file_text.insert(1.0, f"Файл {self.current_file} не найден")
        
        self.file_text.config(state=tk.DISABLED)
    
    def process_file(self):
        """Обрабатывает файл: загружает данные в таблицу"""
        if not self.current_file:
            messagebox.showwarning("Предупреждение", "Сначала выберите файл с помощью кнопки 'ЗАГРУЗИТЬ ФАЙЛ'")
            return
        
        if not os.path.exists(self.current_file):
            messagebox.showerror("Ошибка", f"Файл {self.current_file} не существует")
            return
        
        items = load_file(self.current_file)
        self.table_window.load_items_from_file(items, self.current_file)
        messagebox.showinfo("Готово", f"Загружено {len(items)} блюд в таблицу")


class HelpWindow:
    """Окно справки"""
    def __init__(self, parent):
        self.dlg = tk.Toplevel(parent)
        self.dlg.title("Справка")
        self.dlg.geometry("650x650")
        self.dlg.transient(parent)
        self.dlg.grab_set()
        
        tk.Label(self.dlg, text="Программа управления меню", font=("Arial", 16, "bold")).pack(pady=15)
        
        info = tk.Frame(self.dlg, relief=tk.GROOVE, bd=2, bg="#f0f0f0")
        info.pack(pady=10, padx=20, fill=tk.X)
        for txt in ["Вариант: 4 (Меню)", "Бахтин Виталий"]:
            tk.Label(info, text=txt, font=("Arial", 11), bg="#f0f0f0", anchor=tk.W).pack(fill=tk.X, padx=10, pady=2)
        
        tk.Label(self.dlg, text="Внешний вид программы:", font=("Arial", 12, "bold")).pack(pady=(15,5))
        frame = tk.Frame(self.dlg, relief=tk.SUNKEN, bd=2)
        frame.pack(pady=5, padx=20)
        self.load_screenshot(frame)
        tk.Label(self.dlg, text="Рисунок 1 - Рабочее окно программы", font=("Arial", 10, "italic")).pack()
        
        tk.Label(self.dlg, text="Инструкция:", font=("Arial", 12, "bold")).pack(pady=(15,5))
        instr_frame = tk.Frame(self.dlg, relief=tk.GROOVE, bd=2)
        instr_frame.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)
        
        text = tk.Text(instr_frame, height=10, wrap=tk.WORD, font=("Arial", 10))
        scroll = tk.Scrollbar(instr_frame, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        text.insert("1.0",
            "1. Нажмите 'Работать' в главном окне\n\n"
            "2. Откроются ДВА окна параллельно:\n"
            "   • Окно с таблицей (кнопки: Добавить, Удалить, Сохранить, Назад)\n"
            "   • Окно загрузки файла\n\n"
            "3. Загрузка файла:\n"
            "   • В окне загрузки нажмите 'ЗАГРУЗИТЬ ФАЙЛ'\n"
            "   • Выберите .txt файл\n"
            "   • Содержимое появится в окошке\n"
            "   • Нажмите 'ОБРАБОТАТЬ'\n"
            "   • Данные появятся в таблице\n\n"
            "4. Добавление вручную:\n"
            "   • Нажмите 'Добавить' в окне таблицы\n"
            "   • Заполните поля\n\n"
            "5. Удаление: выделите строку → 'Удалить'\n\n"
            "6. Сохранение: нажмите 'Сохранить' → выберите файл\n\n"
            "7. Возврат: '← Назад' → главное меню")
        text.config(state=tk.DISABLED)
        
        tk.Button(self.dlg, text="Закрыть", command=self.dlg.destroy,
                 bg="#4CAF50", fg="white", width=15, height=1, font=("Arial", 11, "bold")).pack(pady=15)
        self.center()
    
    def load_screenshot(self, parent):
        try:
            if os.path.exists("screenshot.png"):
                img = Image.open("screenshot.png")
                img.thumbnail((500, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(parent, image=photo)
                lbl.image = photo
                lbl.pack(padx=5, pady=5)
            else:
                tk.Label(parent, text="Скриншот не найден\n(файл screenshot.png)", 
                        fg="red", font=("Arial", 10)).pack(padx=5, pady=5)
        except:
            tk.Label(parent, text="Ошибка загрузки скриншота", fg="red", font=("Arial", 10)).pack()
    
    def center(self):
        self.dlg.update_idletasks()
        w, h = self.dlg.winfo_width(), self.dlg.winfo_height()
        x = (self.dlg.winfo_screenwidth() // 2) - (w // 2)
        y = (self.dlg.winfo_screenheight() // 2) - (h // 2)
        self.dlg.geometry(f'{w}x{h}+{x}+{y}')


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Главное окно")
        self.root.geometry("350x300")
        self.root.resizable(False, False)
        
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')
        
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(expand=True)
        
        tk.Button(btn_frame, text="Работать", command=self.open_work,
                 bg="#2196F3", fg="white", width=18, height=2, 
                 font=("Arial", 11, "bold")).pack(pady=8)
        
        tk.Button(btn_frame, text="Справка", command=self.show_help,
                 bg="#FF9800", fg="white", width=18, height=2, 
                 font=("Arial", 11, "bold")).pack(pady=8)
        
        tk.Button(btn_frame, text="Выход", command=self.exit_app,
                 bg="#f44336", fg="white", width=18, height=2, 
                 font=("Arial", 11, "bold")).pack(pady=8)
    
    def open_work(self):
        """Открывает ДВА окна параллельно"""
        self.table_window = TableWindow(self.root, self)
        self.load_window = LoadWindow(self.root, self.table_window)
        self.root.withdraw()
    
    def show(self):
        self.root.deiconify()
    
    def show_help(self):
        HelpWindow(self.root)
    
    def exit_app(self):
        if messagebox.askyesno("Выход", "Точно хотите выйти?"):
            self.root.destroy()
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    MainWindow().run()