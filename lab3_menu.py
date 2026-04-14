from datetime import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re
import os
import logging
from typing import List, Optional
from PIL import Image, ImageTk

# Настройка логирования
logging.basicConfig(filename='menu_errors.log', level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')
logger = logging.getLogger(__name__)

class ValidationError(Exception): pass
class ParseError(Exception): pass

class MenuItem:
    def __init__(self, name: str, price: float, cook_time: time, color: str):
        self.name = name
        self.price = price
        self.cook_time = cook_time
        self.color = color
        if not name: raise ValidationError("Пустое название")
        if price <= 0: raise ValidationError(f"Цена должна быть > 0: {price}")
    
    @classmethod
    def from_str(cls, s):
        try:
            if not s or not s.strip(): raise ParseError("Пустая строка")
            m = re.match(r'"([^"]+)"\s+([\d.]+)\s+(\d{2}):(\d{2})(?:\s+(\w+))?', s.strip())
            if not m: raise ParseError(f"Неверный формат: {s[:50]}")
            name = m.group(1)
            price = float(m.group(2))
            h, mn = int(m.group(3)), int(m.group(4))
            if h > 23 or mn > 59: raise ParseError(f"Неверное время: {h:02d}:{mn:02d}")
            color = m.group(5) if m.group(5) else "не указан"
            logger.info(f"✅ Загружено: {name}")
            return cls(name, price, time(h, mn), color)
        except (ParseError, ValidationError) as e:
            logger.warning(f"❌ Пропущена: '{s.strip()[:50]}' | {e}")
            raise
    
    def to_list(self): return [self.name, f"{self.price:.2f}", self.cook_time.strftime("%H:%M"), self.color]
    def to_str(self): return f'"{self.name}" {self.price} {self.cook_time.strftime("%H:%M")} {self.color}'

class FileManager:
    def __init__(self, filename="menu.txt"): self.filename = filename
    def load(self):
        objects = []
        if not os.path.exists(self.filename): return objects
        with open(self.filename, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try: objects.append(MenuItem.from_str(line))
                    except: continue
        return objects
    def save(self, objects):
        with open(self.filename, 'w', encoding='utf-8') as f:
            for obj in objects: f.write(obj.to_str() + '\n')

class Model:
    def __init__(self, filename="menu.txt"): 
        self.fm = FileManager(filename)
        self.objects = self.fm.load()
    
    def add(self, name, price, cook_time, color="не указан"):
        obj = MenuItem(name, price, cook_time, color)
        self.objects.append(obj)
        self.fm.save(self.objects)
        logger.info(f"Добавлен: {name}")
        return obj
    
    def delete(self, index):
        if 0 <= index < len(self.objects):
            del self.objects[index]
            self.fm.save(self.objects)
            return True
        return False
    
    def get_all(self): return self.objects.copy()
    def get(self, index): return self.objects[index] if 0 <= index < len(self.objects) else None
    def load_items_from_file(self, items):
        """Загружает данные из файла (заменяет текущие)"""
        self.objects = items.copy()
        self.fm.save(self.objects)
        logger.info(f"Загружено {len(items)} объектов из файла")

class WorkWindow:
    def __init__(self, parent, model, on_close):
        self.model = model
        self.on_close = on_close
        self.root = tk.Toplevel(parent)
        self.root.title("Управление меню - таблица")
        self.root.geometry("800x500")
        self.create_widgets()
        self.refresh()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="← Назад", command=self.on_closing,
                 bg="#607D8B", fg="white", width=12, height=1, font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Добавить", command=self.add,
                 bg="#4CAF50", fg="white", width=12, height=1, font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Удалить", command=self.delete,
                 bg="#f44336", fg="white", width=12, height=1, font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Обновить", command=self.refresh,
                 bg="#FF9800", fg="white", width=12, height=1, font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.table = ttk.Treeview(table_frame, columns=("Название","Цена","Время","Цвет"), show="headings", height=15)
        
        self.table.heading("Название", text="Название")
        self.table.heading("Цена", text="Цена (руб.)")
        self.table.heading("Время", text="Время")
        self.table.heading("Цвет", text="Цвет")
        
        self.table.column("Название", width=300)
        self.table.column("Цена", width=100)
        self.table.column("Время", width=100)
        self.table.column("Цвет", width=150)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.status_label = tk.Label(self.root, text="", font=("Arial", 9), fg="gray", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def refresh(self):
        for row in self.table.get_children(): self.table.delete(row)
        for it in self.model.get_all():
            self.table.insert("", tk.END, values=it.to_list())
        self.status_label.config(text=f"Всего блюд: {len(self.model.get_all())}")
    
    def add(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Добавить блюдо")
        dlg.geometry("350x300")
        dlg.resizable(False, False)
        
        entries = []
        for lbl in ["Название (\"...\")", "Цена", "Время (ЧЧ:ММ)", "Цвет (опц.)"]:
            tk.Label(dlg, text=lbl).pack(pady=(10,0))
            e = tk.Entry(dlg, width=30)
            e.pack()
            entries.append(e)
        
        def save():
            try:
                name, price, tm, color = [e.get().strip() for e in entries]
                if not name or not price or not tm: raise ValueError
                if not (name.startswith('"') and name.endswith('"')): raise ValueError
                m = re.match(r'(\d{2}):(\d{2})', tm)
                if not m: raise ValueError
                h, mn = int(m.group(1)), int(m.group(2))
                if h > 23 or mn > 59: raise ValueError
                self.model.add(name.strip('"'), float(price), time(h, mn), color)
                self.refresh()
                dlg.destroy()
                messagebox.showinfo("Успех", "Блюдо добавлено!")
            except: messagebox.showerror("Ошибка", "Проверьте данные")
        
        tk.Button(dlg, text="Сохранить", command=save, bg="#4CAF50", fg="white").pack(pady=15)
    
    def delete(self):
        sel = self.table.selection()
        if not sel: messagebox.showwarning("", "Выберите блюдо для удаления"); return
        if messagebox.askyesno("", "Удалить выбранное блюдо?"):
            self.model.delete(self.table.index(sel[0]))
            self.refresh()
    
    def load_from_file(self, items):
        """Загружает данные из файла в таблицу"""
        self.model.load_items_from_file(items)
        self.refresh()
    
    def on_closing(self): 
        self.root.destroy()
        self.on_close()
    
    def show(self): 
        self.root.deiconify()
        self.refresh()
    
    def hide(self): 
        self.root.withdraw()


class LoadWindow:
    """Окно загрузки файла (открывается параллельно с таблицей)"""
    def __init__(self, parent, work_window):
        self.work_window = work_window
        self.current_file = None
        
        self.root = tk.Toplevel(parent)
        self.root.title("Загрузка файла")
        self.root.geometry("600x500")
        self.root.minsize(550, 450)
        
        main_container = tk.Frame(self.root, padx=15, pady=15)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        tk.Button(main_container, text="ЗАГРУЗИТЬ ФАЙЛ", command=self.select_file,
                 bg="#2196F3", fg="white", width=25, height=2, 
                 font=("Arial", 11, "bold")).pack(pady=(0, 15))
        
        info_frame = tk.LabelFrame(main_container, text="Содержимое файла", font=("Arial", 10, "bold"))
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        text_frame = tk.Frame(info_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.file_text = tk.Text(text_frame, wrap=tk.WORD, font=("Courier", 10))
        scroll = tk.Scrollbar(text_frame, command=self.file_text.yview)
        self.file_text.configure(yscrollcommand=scroll.set)
        self.file_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Button(main_container, text="ОБРАБОТАТЬ", command=self.process_file,
                 bg="#4CAF50", fg="white", width=25, height=2, 
                 font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        self.file_text.insert(1.0, "Файл не выбран.\n\nНажмите 'ЗАГРУЗИТЬ ФАЙЛ' для выбора файла .txt")
        self.file_text.config(state=tk.DISABLED)
        
        self.root.update_idletasks()
        self.center_window()
        
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)
    
    def center_window(self):
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')
    
    def select_file(self):
        fname = filedialog.askopenfilename(
            title="Выберите файл с данными",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if fname:
            self.current_file = fname
            self.show_file_content()
            messagebox.showinfo("Информация", f"Выбран файл: {os.path.basename(fname)}\n\nНажмите 'ОБРАБОТАТЬ' для загрузки данных в таблицу")
    
    def show_file_content(self):
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
        if not self.current_file:
            messagebox.showwarning("Предупреждение", "Сначала выберите файл с помощью кнопки 'ЗАГРУЗИТЬ ФАЙЛ'")
            return
        
        if not os.path.exists(self.current_file):
            messagebox.showerror("Ошибка", f"Файл {self.current_file} не существует")
            return
        
        items = []
        with open(self.current_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        item = MenuItem.from_str(line)
                        items.append(item)
                    except:
                        continue
        
        self.work_window.load_from_file(items)
        messagebox.showinfo("Готово", f"Загружено {len(items)} блюд в таблицу")
    
    def close_window(self):
        if self.root:
            self.root.destroy()
    
    def destroy(self):
        self.close_window()


class HelpWindow:
    def __init__(self, parent):
        self.dlg = tk.Toplevel(parent)
        self.dlg.title("Справка")
        self.dlg.geometry("650x650")
        self.dlg.transient(parent)
        self.dlg.grab_set()
        
        tk.Label(self.dlg, text="Программа управления меню", font=("Arial", 16, "bold")).pack(pady=15)
        
        info = tk.Frame(self.dlg, relief=tk.GROOVE, bd=2, bg="#f0f0f0")
        info.pack(pady=10, padx=20, fill=tk.X)
        for txt in ["Вариант: 4 (Меню)", "Бахтин Виталий", "Версия: 3.0 (с логированием)"]:
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
            "   • Окно с таблицей (кнопки: Добавить, Удалить, Обновить, Назад)\n"
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
            "6. Выход: 'Выход' в главном окне")
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
    def __init__(self, model):
        self.model = model
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
                 width=25, height=2, bg="#2196F3", fg="white", font=("Arial", 12, "bold")).pack(pady=10)
        
        tk.Button(btn_frame, text="Справка", command=self.show_help,
                 width=25, height=2, bg="#FF9800", fg="white", font=("Arial", 12, "bold")).pack(pady=10)
        
        tk.Button(btn_frame, text="Выход", command=self.exit_app,
                 width=25, height=2, bg="#f44336", fg="white", font=("Arial", 12, "bold")).pack(pady=10)
        
        self.work_window = None
        self.load_window = None
    
    def open_work(self):
        """Открывает ДВА окна параллельно: таблицу и загрузку файла"""
        self.work_window = WorkWindow(self.root, self.model, self.show_main)
        self.load_window = LoadWindow(self.root, self.work_window)
        self.root.withdraw()
    
    def show_main(self):
        """Показывает главное окно и закрывает рабочие окна"""
        self.root.deiconify()
        if self.work_window:
            self.work_window.root.destroy()
            self.work_window = None
        if self.load_window:
            self.load_window.destroy()
            self.load_window = None
    
    def show_help(self):
        HelpWindow(self.root)
    
    def exit_app(self):
        if messagebox.askyesno("Выход", "Вы уверены?"):
            self.root.destroy()
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    if not os.path.exists("menu.txt"):
        with open("menu.txt", "w", encoding='utf-8') as f:
            f.write('"Борщ" 5.75 01:30 красный\n')
            f.write('"Суп" 4.50 00:45 желтый\n')
            f.write('"Пельмени" 8.25 00:20 белый\n')
            f.write('Борщ 5.75 01:30\n')
            f.write('"Суп" -4.50 00:45\n')
            f.write('"Ошибка" 8.25 25:61\n')
    
    model = Model("menu.txt")
    MainWindow(model).run()