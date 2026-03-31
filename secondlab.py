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


def save_file(fname, items):
    """Сохранение в файл"""
    with open(fname, 'w', encoding='utf-8') as f:
        for it in items:
            f.write(f'"{it.name}" {it.price} {it.cook_time.strftime("%H:%M")} {it.color}\n')


class WorkWindow:
    def __init__(self, parent, main_win):
        self.main = main_win
        self.file = "menu.txt"
        self.items = load_file(self.file)
        
        self.root = tk.Toplevel(parent)
        self.root.title("Меню")
        self.root.geometry("750x450")
        
        # Кнопки
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)
        for txt, cmd, color in [("← Назад", self.go_back, "#607D8B"),
                                  ("Добавить", self.add, "#4CAF50"),
                                  ("Удалить", self.delete, "#f44336"),
                                  ("Загрузить", self.load, "#2196F3")]:
            tk.Button(btn_frame, text=txt, command=cmd, bg=color, fg="white",
                     width=10, font=("Arial", 9)).pack(side=tk.LEFT, padx=3)
        
        # Таблица
        self.table = ttk.Treeview(self.root, columns=("Название","Цена","Время","Цвет"), show="headings")
        for c, w in [("Название",200), ("Цена",80), ("Время",80), ("Цвет",100)]:
            self.table.heading(c, text=c)
            self.table.column(c, width=w)
        self.table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
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
        save_file(self.file, self.items)
    
    def add(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Добавить")
        dlg.geometry("300x250")
        entries = []
        for lbl in ["Название (\"...\")", "Цена", "Время (ЧЧ:ММ)", "Цвет (опц.)"]:
            tk.Label(dlg, text=lbl).pack(pady=(10,0))
            e = tk.Entry(dlg, width=30)
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
        tk.Button(dlg, text="Сохранить", command=save, bg="#4CAF50", fg="white").pack(pady=15)
    
    def delete(self):
        sel = self.table.selection()
        if not sel:
            messagebox.showwarning("", "Выберите объект")
            return
        if messagebox.askyesno("", "Удалить?"):
            idx = self.table.index(sel[0])
            del self.items[idx]
            self.refresh()
    
    def load(self):
        fname = filedialog.askopenfilename(filetypes=[("Text", "*.txt")])
        if fname:
            self.file = fname
            self.items = load_file(fname)
            self.refresh()


class HelpWindow:
    def __init__(self, parent):
        self.dlg = tk.Toplevel(parent)
        self.dlg.title("Справка")
        self.dlg.geometry("600x600")
        self.dlg.transient(parent)
        self.dlg.grab_set()
        
        # Заголовок
        tk.Label(self.dlg, text="Программа управления меню", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Информация
        info = tk.Frame(self.dlg, relief=tk.GROOVE, bd=2, bg="#f0f0f0")
        info.pack(pady=10, padx=20, fill=tk.X)
        for txt in ["Вариант: 4 (Меню)", "Бахтин Виталий"]:
            tk.Label(info, text=txt, font=("Arial", 10), bg="#f0f0f0", anchor=tk.W).pack(fill=tk.X, padx=10, pady=2)
        
        # Скриншот
        tk.Label(self.dlg, text="Внешний вид программы:", font=("Arial", 11, "bold")).pack(pady=(10,5))
        frame = tk.Frame(self.dlg, relief=tk.SUNKEN, bd=2)
        frame.pack(pady=5, padx=20)
        self.load_screenshot(frame)
        tk.Label(self.dlg, text="Рисунок 1 - Рабочее окно программы", font=("Arial", 9, "italic")).pack()
        
        # Инструкция
        tk.Label(self.dlg, text="Инструкция:", font=("Arial", 11, "bold")).pack(pady=(10,5))
        instr_frame = tk.Frame(self.dlg, relief=tk.GROOVE, bd=2)
        instr_frame.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)
        
        text = tk.Text(instr_frame, height=8, wrap=tk.WORD, font=("Arial", 10))
        scroll = tk.Scrollbar(instr_frame, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        text.insert("1.0",
            "1. Нажмите 'Работать' в главном окне\n\n"
            "2. Добавление блюда:\n"
            '   • Нажмите "Добавить"\n'
            '   • Название в кавычках: "Борщ"\n'
            '   • Цена (число > 0)\n'
            '   • Время в формате ЧЧ:ММ\n'
            '   • Цвет (необязательно)\n\n'
            "3. Удаление: выделите строку → 'Удалить'\n\n"
            "4. Загрузка файла: 'Загрузить' → выберите .txt файл\n\n"
            "5. Назад: '← Назад' или закройте окно\n\n"
            "6. Выход: 'Выход' в главном окне")
        text.config(state=tk.DISABLED)
        
        tk.Button(self.dlg, text="Закрыть", command=self.dlg.destroy,
                 bg="#4CAF50", fg="white", width=12).pack(pady=10)
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
                        fg="red").pack(padx=5, pady=5)
        except:
            tk.Label(parent, text="Ошибка загрузки скриншота", fg="red").pack()
    
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
        
        self.work = WorkWindow(self.root, self)
        self.work.root.withdraw()
        
        # Центрирование
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')
        
        # Кнопки
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(expand=True)
        for txt, cmd, color in [("Работать", self.open_work, "#2196F3"),
                                  ("Справка", self.show_help, "#FF9800"),
                                  ("Выход", self.exit_app, "#f44336")]:
            tk.Button(btn_frame, text=txt, command=cmd, bg=color, fg="white",
                     width=18, height=2, font=("Arial", 10, "bold")).pack(pady=8)
    
    def open_work(self):
        self.work.root.deiconify()
        self.work.refresh()
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
    if not os.path.exists("menu.txt"):
        with open("menu.txt", "w", encoding='utf-8') as f:
            f.write('"Борщ" 5.75 01:30 красный\n')
            f.write('"Суп" 4.50 00:45 желтый\n')
            f.write('"Пельмени" 8.25 00:20 белый\n')
    MainWindow().run()