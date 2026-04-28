from datetime import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re
import os
import logging
from PIL import Image, ImageTk

logging.basicConfig(filename='menu_errors.log', level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')
logger = logging.getLogger(__name__)

class ValidationError(Exception): pass
class ParseError(Exception): pass
class CommandError(Exception): pass


class MenuItem:
    def __init__(self, name, price, cook_time, color, quality=3):
        self.name = name
        self.price = price
        self.cook_time = cook_time
        self.color = color
        self.quality = quality  # качество (1-5)
        
        if not name: raise ValidationError("Пустое название")
        if price <= 0: raise ValidationError(f"Цена > 0: {price}")
        if quality < 1 or quality > 5: raise ValidationError(f"Качество должно быть 1-5: {quality}")
    
    @classmethod
    def from_str(cls, s):
        try:
            if not s or not s.strip(): raise ParseError("Пустая строка")
            # Обновлённое регулярное выражение с учётом качества
            m = re.match(r'"([^"]+)"\s+([\d.]+)\s+(\d{2}):(\d{2})(?:\s+(\w+))?(?:\s+(\d))?', s.strip())
            if not m: raise ParseError(f"Неверный формат: {s[:50]}")
            name, price, h, mn = m.group(1), float(m.group(2)), int(m.group(3)), int(m.group(4))
            if h > 23 or mn > 59: raise ParseError(f"Неверное время: {h:02d}:{mn:02d}")
            color = m.group(5) if m.group(5) else "не указан"
            quality = int(m.group(6)) if m.group(6) else 3
            logger.info(f"Загружено: {name}")
            return cls(name, price, time(h, mn), color, quality)
        except (ParseError, ValidationError) as e:
            logger.warning(f"Пропущена: '{s.strip()[:50]}' | {e}")
            raise
    
    @classmethod
    def from_csv(cls, csv_str: str):
        parts = [p.strip() for p in csv_str.split(';')]
        if len(parts) < 4:
            raise ParseError(f"Недостаточно данных: {csv_str}")
        name = parts[0].strip('"')
        price = float(parts[1])
        h, m = map(int, parts[2].split(':'))
        color = parts[3] if len(parts) > 3 else "не указан"
        quality = int(parts[4]) if len(parts) > 4 else 3
        return cls(name, price, time(h, m), color, quality)
    
    def matches(self, cond):
        cond = cond.strip()
        # name
        if cond.startswith('name =='):
            return self.name == cond.split('==')[1].strip().strip('"')
        if cond.startswith('name contains'):
            return cond.split('contains')[1].strip().strip('"') in self.name
        # price
        if cond.startswith('price <'): return self.price < float(cond.split('<')[1])
        if cond.startswith('price >'): return self.price > float(cond.split('>')[1])
        if cond.startswith('price <='): return self.price <= float(cond.split('<=')[1])
        if cond.startswith('price >='): return self.price >= float(cond.split('>=')[1])
        if cond.startswith('price =='): return abs(self.price - float(cond.split('==')[1])) < 0.001
        # cook_time
        if cond.startswith('cook_time <'):
            h, m = map(int, cond.split('<')[1].strip().split(':'))
            return self.cook_time < time(h, m)
        if cond.startswith('cook_time >'):
            h, m = map(int, cond.split('>')[1].strip().split(':'))
            return self.cook_time > time(h, m)
        if cond.startswith('cook_time =='):
            h, m = map(int, cond.split('==')[1].strip().split(':'))
            return self.cook_time == time(h, m)
        # color
        if cond.startswith('color =='):
            return self.color == cond.split('==')[1].strip()
        # quality (НОВОЕ)
        if cond.startswith('quality <'): return self.quality < int(cond.split('<')[1])
        if cond.startswith('quality >'): return self.quality > int(cond.split('>')[1])
        if cond.startswith('quality <='): return self.quality <= int(cond.split('<=')[1])
        if cond.startswith('quality >='): return self.quality >= int(cond.split('>=')[1])
        if cond.startswith('quality =='): return self.quality == int(cond.split('==')[1])
        # AND
        if ' AND ' in cond:
            left, right = cond.split(' AND ')
            return self.matches(left) and self.matches(right)
        return False
    
    def to_list(self):
        return [self.name, f"{self.price:.2f}", self.cook_time.strftime("%H:%M"), self.color, f"★{self.quality}"]
    
    def to_str(self):
        return f'"{self.name}" {self.price} {self.cook_time.strftime("%H:%M")} {self.color} {self.quality}'
    
    def to_csv(self):
        return f'{self.name};{self.price};{self.cook_time.strftime("%H:%M")};{self.color};{self.quality}'


class FileManager:
    def __init__(self, fname="menu.txt"): self.fname = fname
    def load(self):
        objs = []
        if os.path.exists(self.fname):
            with open(self.fname, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try: objs.append(MenuItem.from_str(line))
                        except: continue
        return objs
    def save(self, objs, fname=None):
        fname = fname or self.fname
        with open(fname, 'w', encoding='utf-8') as f:
            for obj in objs: f.write(obj.to_str() + '\n')


class Model:
    def __init__(self, fname="menu.txt"):
        self.fm = FileManager(fname)
        self.objects = self.fm.load()
    
    def add(self, name, price, cook_time, color="не указан", quality=3):
        obj = MenuItem(name, price, cook_time, color, quality)
        self.objects.append(obj)
        self.fm.save(self.objects)
        logger.info(f"Добавлен: {name}")
        return obj
    
    def delete(self, idx):
        if 0 <= idx < len(self.objects):
            del self.objects[idx]
            self.fm.save(self.objects)
            return True
        return False
    
    def get_all(self): return self.objects.copy()
    def load_from_file(self, items):
        self.objects = items.copy()
        self.fm.save(self.objects)


def make_button(parent, text, cmd, color, width=12):
    return tk.Button(parent, text=text, command=cmd, bg=color, fg="white", width=width, height=1, font=("Arial", 9))


def make_text_area(parent, label, height=8):
    frame = tk.LabelFrame(parent, text=label, font=("Arial", 10, "bold"))
    frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
    text = tk.Text(frame, wrap=tk.WORD, font=("Courier", 10), height=height)
    scroll = tk.Scrollbar(frame, command=text.yview)
    text.configure(yscrollcommand=scroll.set)
    text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)
    return text


class LoadDataWindow:
    def __init__(self, parent, work):
        self.work, self.current = work, None
        self.root = tk.Toplevel(parent)
        self.root.title("Загрузка данных")
        self.root.geometry("600x500")
        container = tk.Frame(self.root, padx=15, pady=15)
        container.pack(fill=tk.BOTH, expand=True)
        
        tk.Button(container, text="ЗАГРУЗИТЬ ФАЙЛ", command=self.select,
                 bg="#2196F3", fg="white", width=25, height=2, font=("Arial", 11, "bold")).pack(pady=(0, 15))
        
        self.text = make_text_area(container, "Содержимое файла", 8)
        self.text.insert(1.0, "Файл не выбран.\n\nНажмите 'ЗАГРУЗИТЬ ФАЙЛ'")
        self.text.config(state=tk.DISABLED)
        
        tk.Button(container, text="ЗАГРУЗИТЬ В ТАБЛИЦУ", command=self.process,
                 bg="#4CAF50", fg="white", width=25, height=2, font=("Arial", 12, "bold")).pack()
        
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
    
    def select(self):
        fname = filedialog.askopenfilename(filetypes=[("Text", "*.txt")])
        if fname:
            self.current = fname
            self.text.config(state=tk.NORMAL)
            self.text.delete(1.0, tk.END)
            with open(fname, 'r', encoding='utf-8') as f:
                self.text.insert(1.0, f.read())
            self.text.config(state=tk.DISABLED)
    
    def process(self):
        if not self.current:
            messagebox.showwarning("", "Сначала выберите файл!")
            return
        items = []
        with open(self.current, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try: items.append(MenuItem.from_str(line))
                    except: continue
        self.work.model.load_from_file(items)
        self.work.refresh()
        messagebox.showinfo("Готово", f"Загружено {len(items)} блюд")


class CommandsWindow:
    def __init__(self, parent, model, refresh_cb):
        self.model, self.refresh_cb, self.current = model, refresh_cb, None
        self.root = tk.Toplevel(parent)
        self.root.title("Выполнение команд")
        self.root.geometry("700x550")
        container = tk.Frame(self.root, padx=15, pady=15)
        container.pack(fill=tk.BOTH, expand=True)
        
        tk.Button(container, text="ВЫБРАТЬ ФАЙЛ КОМАНД", command=self.select,
                 bg="#2196F3", fg="white", width=25, height=2, font=("Arial", 11, "bold")).pack(pady=(0, 15))
        
        self.cmd_text = make_text_area(container, "Содержимое файла команд", 6)
        self.cmd_text.insert(1.0, "Файл не выбран")
        self.cmd_text.config(state=tk.DISABLED)
        
        tk.Button(container, text="ВЫПОЛНИТЬ КОМАНДЫ", command=self.execute,
                 bg="#4CAF50", fg="white", width=25, height=2, font=("Arial", 12, "bold")).pack(pady=(0, 15))
        
        self.result_text = make_text_area(container, "Результаты", 6)
        self.result_text.config(state=tk.DISABLED)
    
    def select(self):
        fname = filedialog.askopenfilename(filetypes=[("Text", "*.txt")])
        if fname:
            self.current = fname
            self.cmd_text.config(state=tk.NORMAL)
            self.cmd_text.delete(1.0, tk.END)
            with open(fname, 'r', encoding='utf-8') as f:
                self.cmd_text.insert(1.0, f.read())
            self.cmd_text.config(state=tk.DISABLED)
    
    def execute(self):
        if not self.current:
            messagebox.showwarning("", "Сначала выберите файл!")
            return
        
        results = []
        with open(self.current, 'r', encoding='utf-8') as f:
            for num, line in enumerate(f, 1):
                line = line.strip()
                if not line: continue
                parts = line.split(maxsplit=1)
                if len(parts) < 2:
                    results.append(f"Строка {num}: Неверный формат")
                    continue
                cmd, args = parts[0].upper(), parts[1]
                try:
                    if cmd == "ADD":
                        data = [p.strip() for p in args.split(';')]
                        quality = int(data[4]) if len(data) > 4 else 3
                        obj = MenuItem(
                            data[0].strip('"'), float(data[1]),
                            time(*map(int, data[2].split(':'))),
                            data[3] if len(data) > 3 else "не указан",
                            quality
                        )
                        self.model.add(obj.name, obj.price, obj.cook_time, obj.color, obj.quality)
                        results.append(f"Строка {num}: Добавлен: {obj.name} (⭐{obj.quality})")
                    elif cmd == "REM":
                        to_del = [i for i, o in enumerate(self.model.get_all()) if o.matches(args)]
                        for i in reversed(to_del): self.model.delete(i)
                        results.append(f"Строка {num}: Удалено {len(to_del)} объектов")
                    elif cmd == "SAVE":
                        self.model.fm.save(self.model.get_all(), args.strip())
                        results.append(f"Строка {num}: Сохранено в {args.strip()}")
                    else:
                        results.append(f"Строка {num}: Неизвестная команда: {cmd}")
                    self.refresh_cb()
                except Exception as e:
                    results.append(f"Строка {num}: {e}")
        
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, "\n".join(results))
        self.result_text.config(state=tk.DISABLED)


class WorkWindow:
    def __init__(self, parent, model, on_close):
        self.model, self.on_close = model, on_close
        self.root = tk.Toplevel(parent)
        self.root.title("Таблица")
        self.root.geometry("900x500")
        
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        for txt, cmd, color in [("← Назад", self.close, "#607D8B"), ("Добавить", self.add, "#4CAF50"),
                                  ("Удалить", self.delete, "#f44336"), ("Обновить", self.refresh, "#FF9800")]:
            make_button(btn_frame, txt, cmd, color).pack(side=tk.LEFT, padx=3)
        
        self.table = ttk.Treeview(self.root, columns=("Название","Цена","Время","Цвет","Качество"), show="headings", height=15)
        for c, w in [("Название",250), ("Цена",80), ("Время",80), ("Цвет",100), ("Качество",80)]:
            self.table.heading(c, text=c)
            self.table.column(c, width=w)
        self.table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.status = tk.Label(self.root, text="", font=("Arial", 9), fg="gray")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.refresh()
    
    def refresh(self):
        for row in self.table.get_children(): self.table.delete(row)
        for it in self.model.get_all():
            self.table.insert("", tk.END, values=it.to_list())
        self.status.config(text=f"Всего: {len(self.model.get_all())}")
    
    def add(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Добавить")
        dlg.geometry("400x400")
        entries = []
        for lbl in ["Название (\"...\")", "Цена", "Время (ЧЧ:ММ)", "Цвет", "Качество (1-5)"]:
            tk.Label(dlg, text=lbl).pack(pady=(10,0))
            e = tk.Entry(dlg, width=30)
            e.pack()
            entries.append(e)
        def save():
            try:
                n, p, t, c, q = [e.get().strip() for e in entries]
                if not (n.startswith('"') and n.endswith('"')): raise ValueError
                h, m = map(int, re.match(r'(\d{2}):(\d{2})', t).groups())
                if h > 23 or m > 59: raise ValueError
                quality = int(q) if q else 3
                if quality < 1 or quality > 5: raise ValueError
                self.model.add(n.strip('"'), float(p), time(h, m), c, quality)
                self.refresh()
                dlg.destroy()
                messagebox.showinfo("Успех", "Добавлено!")
            except: messagebox.showerror("Ошибка", "Проверьте данные")
        tk.Button(dlg, text="Сохранить", command=save, bg="#4CAF50", fg="white").pack(pady=15)
    
    def delete(self):
        sel = self.table.selection()
        if not sel: messagebox.showwarning("", "Выберите объект"); return
        if messagebox.askyesno("", "Удалить?"):
            self.model.delete(self.table.index(sel[0]))
            self.refresh()
    
    def close(self): self.root.destroy(); self.on_close()
    def show(self): self.root.deiconify(); self.refresh()
    def hide(self): self.root.withdraw()


class HelpWindow:
    def __init__(self, parent):
        self.dlg = tk.Toplevel(parent)
        self.dlg.title("Справка")
        self.dlg.geometry("600x550")
        self.dlg.transient(parent)
        self.dlg.grab_set()
        
        tk.Label(self.dlg, text="Программа управления меню", font=("Arial", 14, "bold")).pack(pady=10)
        info = tk.Frame(self.dlg, relief=tk.GROOVE, bd=2, bg="#f0f0f0")
        info.pack(pady=10, padx=20, fill=tk.X)
        for txt in ["Вариант: 4 (Меню)", "Бахтин Виталий", "Версия: 4.0 (с качеством)"]:
            tk.Label(info, text=txt, bg="#f0f0f0", anchor=tk.W).pack(fill=tk.X, padx=10, pady=2)
        
        if os.path.exists("screenshot.png"):
            try:
                img = Image.open("screenshot.png")
                img.thumbnail((500, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(self.dlg, image=photo)
                lbl.image = photo
                lbl.pack(pady=10)
            except: pass
        
        text = tk.Text(self.dlg, height=10, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        text.insert(1.0,
            "1. Нажмите 'Работать'\n\n"
            "2. Откроются 3 окна:\n"
            "   • Таблица (Добавить/Удалить)\n"
            "   • Загрузка данных\n"
            "   • Команды ADD/REM/SAVE\n\n"
            "3. Формат команд:\n"
            "   ADD название;цена;время;цвет;качество\n"
            "   REM quality > 3\n"
            "   SAVE file.txt\n\n"
            "4. Поля для условий REM:\n"
            "   name, price, cook_time, color, quality\n\n"
            "5. Качество: 1-5 (★)")
        text.config(state=tk.DISABLED)
        tk.Button(self.dlg, text="Закрыть", command=self.dlg.destroy, bg="#4CAF50", fg="white").pack(pady=10)


class MainWindow:
    def __init__(self, model):
        self.model = model
        self.root = tk.Tk()
        self.root.title("Главное окно")
        self.root.geometry("350x300")
        self.root.resizable(False, False)
        self.work = None
        
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(expand=True)
        for txt, cmd, color in [("Работать", self.open_work, "#2196F3"),
                                  ("Справка", self.show_help, "#FF9800"),
                                  ("Выход", self.exit, "#f44336")]:
            tk.Button(btn_frame, text=txt, command=cmd, bg=color, fg="white",
                     width=25, height=2, font=("Arial", 12, "bold")).pack(pady=8)
        self.center()
    
    def center(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f'{w}x{h}+{x}+{y}')
    
    def open_work(self):
        self.work = WorkWindow(self.root, self.model, self.show_main)
        self.load_data = LoadDataWindow(self.root, self.work)
        self.cmd = CommandsWindow(self.root, self.model, self.work.refresh)
        self.root.withdraw()
    
    def show_main(self):
        self.root.deiconify()
        for w in [self.work, self.load_data, self.cmd]:
            if w: w.root.destroy()
        self.work = self.load_data = self.cmd = None
    
    def show_help(self): HelpWindow(self.root)
    def exit(self):
        if messagebox.askyesno("Выход", "Вы уверены?"):
            self.root.destroy()
    def run(self): self.root.mainloop()


if __name__ == "__main__":
    if not os.path.exists("commands.txt"):
        with open("commands.txt", "w", encoding='utf-8') as f:
            f.write('ADD "Блинчики";3.50;00:15;желтый;4\n')
            f.write('ADD "Оливье";4.80;00:20;зеленый;5\n')
            f.write('REM quality < 3\n')
            f.write('SAVE saved.txt\n')
    
    if not os.path.exists("menu.txt"):
        with open("menu.txt", "w", encoding='utf-8') as f:
            f.write('"Борщ" 5.75 01:30 красный 4\n')
            f.write('"Суп" 4.50 00:45 желтый 3\n')
            f.write('"Пельмени" 8.25 00:20 белый 5\n')
    
    MainWindow(Model("menu.txt")).run()