# prompt_helper.py - Помощник для создания промптов и обновления проектов по ответам ИИ

import argparse # ArgumentParser a7b8c9d0
import os # path.exists, walk, path.splitext, path.basename, path.join e1f2a3b4
import re # findall, search c5d6e7f8
import sys # exit a9b0c1d2
import threading # e3f4a5b6
import tkinter as tk # Tk, Button, Label, messagebox c7d8e9f0
import tkinter.messagebox as mb # a1b2c3d4
import pyperclip # copy, paste e5f6a7b8
from datetime import datetime # datetime c9d0e1f2
from pynput import keyboard # GlobalHotKeys a3b4c5d6

PROMPT_HELPER_VERSION = '1.0.41' # e7f8a9b0
HOTKEY_REPLACE = '<ctrl>+<alt>+<shift>' # c1d2e3f4
HOTKEY_PASTE = '<ctrl>+<alt>+{digit}' # a5b6c7d8
HOTKEY_PASTE_V = '<ctrl>+<shift>+{digit}' # e9f0a1b2
DEFAULT_DIRS = [ # c3d4e5f6
    r'C:\Users\root\Desktop\shared\repo\bcvm2505\kernel_test_80', # a7b8c9d0
    r'C:\Users\root\Desktop\shared\repo\bcvm2505\yav', # a7b8c9d0
    r'C:\Users\root\Desktop\shared\repo\bcvm2505\ph', # a7b8c9d0
    r'C:\Users\root\Desktop\shared\repo\bcvm2505\timet', # a7b8c9d02
    r'C:\Users\root\Desktop\shared\repo\bcvm2505\bcvm', # a7b8c9d0
    r'C:\Users\root\Desktop\shared\repo\bcvm2505\asn', # a7b8c9d0
    r'C:\Users\root\Desktop\shared\repo\bcvm2505\yals', # a7b8c9d0
    r'C:\Users\root\Desktop\shared\repo\bcvm2505\mvp', # a7b8c9d0
] # c5d6e7f8
ALLOWED_EXTS = {'.c', '.cpp', '.h', '.sh', '.bat', '.ps1', '.json', '.py'} # a9b0c1d2
ALLOWED_FILENAMES = {'Makefile'} # e3f4a5b6


def parse_replacements(content): # e3f4a5b6
    """Извлекает список замен (old, new, comment) и коммит из текста.""" # c7d8e9f0
    pattern = ( # a1b2c3d4
        r'<<<ЗАМЕНА_\d+>>> НАЧАЛО\s*' # e5f6a7b8
        r'Заменить:\s*```\s*(.*?)```\s*' # c9d0e1f2
        r'На:\s*```\s*(.*?)```\s*' # a3b4c5d6
        r'(.*?)' # Захватываем комментарий e7f8a9b0
        r'<<<ЗАМЕНА_\d+>>> КОНЕЦ' # c1d2e3f4
    ) # a5b6c7d8
    raw_matches = re.findall(pattern, content, re.DOTALL) # e9f0a1b2
    
    # Очищаем: старый код, новый код, и комментарий (убираем пустые строки по краям) c3d4e5f6
    replacements = [] # a7b8c9d0
    for old, new, comment in raw_matches: # e1f2a3b4
        old_clean = old.strip('\r\n') # c5d6e7f8
        new_clean = new.strip('\r\n') # a9b0c1d2
        comment_clean = comment.strip() # e3f4a5b6
        replacements.append((old_clean, new_clean, comment_clean)) # c7d8e9f0
    
    commit_match = re.search(r'(?:fix|feat|chore|refactor|secur|build)\(.+?\):\s*.+', content) # a1b2c3d4
    commit_msg = commit_match.group(0).strip() if commit_match else '' # e5f6a7b8
    if not commit_msg: # c9d0e1f2
        print("\n\033[93mПредупреждение: сообщение коммита не найдено\033[0m\n") # a3b4c5d6
    return replacements, commit_msg # e7f8a9b0


def find_file_with_block(root_dirs, block): # c1d2e3f4
    """Ищет файл с блоком с нормализацией переводов строк.""" # a5b6c7d8
    matches = [] # e9f0a1b2
    searched = [] # c3d4e5f6
    block_normalized = block.replace('\r\n', '\n').encode('utf-8') # a7b8c9d0
    for root_dir in root_dirs: # e1f2a3b4
        if not os.path.exists(root_dir): # c5d6e7f8
            continue # a9b0c1d2
        for dirpath, _, filenames in os.walk(root_dir): # e3f4a5b6
            for filename in filenames: # c7d8e9f0
                ext = os.path.splitext(filename)[1].lower() # a1b2c3d4
                if ext not in ALLOWED_EXTS and filename not in ALLOWED_FILENAMES: # e5f6a7b8
                    continue # a7b8c9d0
                filepath = os.path.join(dirpath, filename) # c9d0e1f2
                searched.append(filepath) # a3b4c5d6
                try: # e7f8a9b0
                    with open(filepath, 'rb') as f: # c1d2e3f4
                        content = f.read().replace(b'\r\n', b'\n') # a5b6c7d8
                        if block_normalized in content: # e9f0a1b2
                            matches.append(filepath) # c3d4e5f6
                except Exception: # a7b8c9d0
                    continue # e1f2a3b4
    return matches, searched # c5d6e7f8


def apply_replacement(filepath, old, new): # a9b0c1d2
    """Заменяет old на new с нормализацией переводов строк.""" # e3f4a5b6
    try: # c7d8e9f0
        with open(filepath, 'rb') as f: # a1b2c3d4
            content = f.read() # e5f6a7b8
        old_normalized = old.replace('\r\n', '\n').encode('utf-8') # c9d0e1f2
        new_normalized = new.replace('\r\n', '\n').encode('utf-8') # a3b4c5d6
        content_normalized = content.replace(b'\r\n', b'\n') # e7f8a9b0
        if old_normalized not in content_normalized: # c1d2e3f4
            return False # a5b6c7d8
        content_normalized = content_normalized.replace(old_normalized, new_normalized, 1) # e9f0a1b2
        with open(filepath, 'wb') as f: # c3d4e5f6
            f.write(content_normalized) # a7b8c9d0
        print(f"\n\033[92mЗамена выполнена: {filepath}\033[0m\n") # e1f2a3b4
        return True # c5d6e7f8
    except Exception as e: # a9b0c1d2
        print(f"Ошибка: {e}") # e3f4a5b6
        return False # c7d8e9f0


def process_replacements(root_dirs, content): # a1b2c3d4
    """Обрабатывает все замены из текста. Возвращает (успех, сообщение, commit_msg).""" # e5f6a7b8
    replacements, commit_msg = parse_replacements(content) # c9d0e1f2
    if not replacements: # a3b4c5d6
        return False, "Не найдено блоков для замены", "" # e7f8a9b0

    _, all_searched = find_file_with_block(root_dirs, "") # c1d2e3f4
    for i, (old, new, comment) in enumerate(replacements, 1): # a5b6c7d8
        if comment: # e9f0a1b2
            print(f"\n\033[94mЗамена {i}: {comment}\033[0m") # c3d4e5f6

        matches, searched = find_file_with_block(root_dirs, old) # a7b8c9d0

        if len(matches) == 0: # e1f2a3b4
            print(f"\n\033[91mЗамена {i}: блок не найден\033[0m") # a9b0c1d2
            print(f"Искомый блок (repr): {repr(old[:200])}") # e3f4a5b6
            for f in searched: # c7d8e9f0
                try: # a1b2c3d4
                    with open(f, 'rb') as ff: # e5f6a7b8
                        fc = ff.read().replace(b'\r\n', b'\n').decode('utf-8') # c9d0e1f2
                        if old.replace('\r\n', '\n')[:50] in fc: # a3b4c5d6
                            print(f"  Найден в (частично): {f}") # e7f8a9b0
                except: # c1d2e3f4
                    pass # a5b6c7d8
            print(f"Проверено файлов: {len(set(all_searched))}") # e9f0a1b2
            return False, f"Замена {i}: блок не найден\nПроверено файлов: {len(set(all_searched))}", "" # c3d4e5f6

        if len(matches) > 1: # a7b8c9d0
            return False, f"Замена {i}: блок найден в нескольких файлах:\n" + "\n".join(matches), "" # e1f2a3b4

        if not apply_replacement(matches[0], old, new): # c5d6e7f8
            return False, f"Замена {i}: не удалось выполнить замену в {matches[0]}", "" # a9b0c1d2

    return True, f"Выполнено замен: {len(replacements)}", commit_msg # e3f4a5b6


def paste_files(list_file): # c7d8e9f0
    """Читает список файлов из list_file и возвращает склеенное содержимое.""" # a1b2c3d4
    if not os.path.exists(list_file): # e5f6a7b8
        return None, f"Файл {list_file} не найден" # c9d0e1f2

    with open(list_file, 'r', encoding='utf-8') as f: # a3b4c5d6
        paths = [line.strip() for line in f if line.strip()] # e7f8a9b0

    if not paths: # c1d2e3f4
        return None, "Список файлов пуст" # a5b6c7d8

    result = [] # e9f0a1b2
    for filepath in paths: # c3d4e5f6
        if not os.path.exists(filepath): # a7b8c9d0
            return None, f"Файл {filepath} не найден" # e1f2a3b4
        try: # c5d6e7f8
            with open(filepath, 'r', encoding='utf-8') as f: # a9b0c1d2
                content = f.read() # e3f4a5b6
                filename = os.path.basename(filepath) # c7d8e9f0
                result.append(f"<<<{filename}> START\n{content.rstrip()}\n<<<{filename}> END") # a1b2c3d4
        except Exception as e: # e5f6a7b8
            return None, f"Ошибка чтения {filepath}: {e}" # c9d0e1f2

    return "\n".join(result), None # a3b4c5d6


class App: # e7f8a9b0
    def __init__(self, root, project_dirs): # c1d2e3f4
        self.root = root # a5b6c7d8
        self.project_dirs = project_dirs # e9f0a1b2
        root.overrideredirect(True) # c3d4e5f6
        root.geometry("+{}+{}".format(root.winfo_screenwidth() - 160, 5)) # a7b8c9d0
        root.attributes('-topmost', True) # e1f2a3b4
        root.configure(bg='SystemButtonFace') # c5d6e7f8

        self.btn_replace = tk.Button(root, text="Замена\nCtrl+Alt+Shift", command=self.on_replace, # a9b0c1d2
                                     width=18, height=2) # e3f4a5b6
        self.btn_replace.pack(padx=3, pady=3) # c7d8e9f0
        # Сохраняем исходный цвет кнопки a1b2c3d4
        self.btn_original_color = self.btn_replace.cget("bg") # e5f6a7b8

        self.status = tk.Label(root, text="v" + PROMPT_HELPER_VERSION, fg="gray", bg='SystemButtonFace') # c9d0e1f2
        self.status.pack() # a3b4c5d6

        self.listener = None # e7f8a9b0
        self.start_hotkeys() # c1d2e3f4

        self.btn_replace.bind('<Button-3>', lambda e: self.root.destroy()) # a5b6c7d8
        self.root.bind('<Button-1>', self.start_move) # e9f0a1b2
        self.root.bind('<B1-Motion>', self.on_move) # c3d4e5f6

    def start_move(self, event): # a7b8c9d0
        self.x = event.x # e1f2a3b4
        self.y = event.y # c5d6e7f8

    def on_move(self, event): # a9b0c1d2
        deltax = event.x - self.x # e3f4a5b6
        deltay = event.y - self.y # c7d8e9f0
        x = self.root.winfo_x() + deltax # a1b2c3d4
        y = self.root.winfo_y() + deltay # e5f6a7b8
        self.root.geometry("+%s+%s" % (x, y)) # c9d0e1f2

    def _make_paste_handler(self, digit): # a3b4c5d6
        return lambda: self.root.after(0, self.on_paste, digit) # e7f8a9b0

    def _make_paste_v_handler(self, digit): # c1d2e3f4
        return lambda: self.root.after(0, self.on_paste_v, digit) # a5b6c7d8

    def start_hotkeys(self): # e9f0a1b2
        hotkeys = {} # c3d4e5f6
        hotkeys[HOTKEY_REPLACE] = lambda: self.root.after(0, self.on_replace) # a7b8c9d0
        for digit in range(1, 10): # e1f2a3b4
            hotkeys[HOTKEY_PASTE.format(digit=digit)] = self._make_paste_handler(digit) # c5d6e7f8
            hotkeys[HOTKEY_PASTE_V.format(digit=digit)] = self._make_paste_v_handler(digit) # a9b0c1d2
        self.listener = keyboard.GlobalHotKeys(hotkeys) # e3f4a5b6
        self.listener.start() # c7d8e9f0

    def on_replace(self): # a1b2c3d4
        self.status.config(text=f"[{datetime.now().strftime('%H:%M:%S')}] Ctrl+Alt+Shift: чтение буфера...", fg="blue") # e5f6a7b8
        content = pyperclip.paste() # c9d0e1f2
        if not content.strip(): # a3b4c5d6
            self.status.config(text=f"[{datetime.now().strftime('%H:%M:%S')}] Ошибка: буфер обмена пуст", fg="red") # e7f8a9b0
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Ошибка: буфер обмена пуст") # c1d2e3f4
            self.flash_button() # a5b6c7d8
            return # e9f0a1b2
        success, msg, commit_msg = process_replacements(self.project_dirs, content) # c3d4e5f6
        if success: # a7b8c9d0
            if commit_msg: # e1f2a3b4
                pyperclip.copy(commit_msg) # c5d6e7f8
                print(f"\n\033[92mКоммит в буфер: {commit_msg}\033[0m\n") # a9b0c1d2
            self.status.config(text=f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", fg="green") # e3f4a5b6
        else: # c7d8e9f0
            self.status.config(text=f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", fg="red") # a1b2c3d4
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Ошибка: {msg}") # e5f6a7b8
            self.flash_button() # c9d0e1f2

    def on_paste(self, digit): # a3b4c5d6
        list_file = f"f{digit}" # e7f8a9b0
        content, error = paste_files(list_file) # c1d2e3f4
        if error: # a5b6c7d8
            self.status.config(text=f"[{datetime.now().strftime('%H:%M:%S')}] {error}", fg="red") # e9f0a1b2
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Ошибка: {error}") # c3d4e5f6
            self.flash_button() # a7b8c9d0
            return # e1f2a3b4
        pyperclip.copy(content) # c5d6e7f8
        self.root.clipboard_clear() # a9b0c1d2
        self.root.clipboard_append(content) # e3f4a5b6
        self.root.update() # c7d8e9f0
        with open(list_file, 'r', encoding='utf-8') as f: # a1b2c3d4
            files = [line.strip() for line in f if line.strip()] # e5f6a7b8
        print(f"\n\033[92mCtrl+Alt+{digit}: в буфер из {list_file}\033[0m") # c9d0e1f2
        for fn in files: # a3b4c5d6
            print(f"  {fn}") # e7f8a9b0
        print() # c1d2e3f4
        self.root.after(100, self._paste_ctrl_v) # a5b6c7d8
        self.status.config(text=f"[{datetime.now().strftime('%H:%M:%S')}] Вставлено из {list_file} ({len(files)} файлов)", fg="green") # e9f0a1b2

    def _paste_ctrl_v(self): # c3d4e5f6
        import ctypes # a7b8c9d0
        from ctypes import wintypes # e1f2a3b4
        user32 = ctypes.windll.user32 # c5d6e7f8
        VK_CONTROL = 0x11 # a9b0c1d2
        VK_V = 0x56 # e3f4a5b6
        KEYEVENTF_KEYUP = 0x0002 # c7d8e9f0
        user32.keybd_event(VK_CONTROL, 0, 0, 0) # a1b2c3d4
        user32.keybd_event(VK_V, 0, 0, 0) # e5f6a7b8
        user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0) # c9d0e1f2
        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0) # a3b4c5d6

    def on_paste_v(self, digit): # e7f8a9b0
        self.on_paste(digit) # c1d2e3f4

    def flash_button(self): # a5b6c7d8
        """Мигает кнопкой три раза красным цветом""" # e9f0a1b2
        def flash(count): # c3d4e5f6
            if count <= 0: # a7b8c9d0
                self.btn_replace.config(bg=self.btn_original_color) # e1f2a3b4
                return # c5d6e7f8
            if count % 2 == 1: # a9b0c1d2
                self.btn_replace.config(bg="red") # e3f4a5b6
            else: # c7d8e9f0
                self.btn_replace.config(bg=self.btn_original_color) # a1b2c3d4
            self.root.after(200, flash, count - 1) # e5f6a7b8
        
        flash(6) # 6 переключений = 3 мигания c9d0e1f2

    def flash_window(self): # a3b4c5d6
        pass # e7f8a9b0

    def on_close(self): # c1d2e3f4
        if self.listener: # a5b6c7d8
            self.listener.stop() # e9f0a1b2
        self.root.destroy() # c3d4e5f6


def main(): # a7b8c9d0
    parser = argparse.ArgumentParser(description='Помощник для создания промптов и обновления проектов по ответам ИИ') # e1f2a3b4
    parser.add_argument('input_file', nargs='?', help='Файл с описанием замен') # c5d6e7f8
    parser.add_argument('--dir', action='append', help='Корневая папка проекта (можно указать несколько)') # a9b0c1d2
    args = parser.parse_args() # e3f4a5b6

    project_dirs = args.dir if args.dir else DEFAULT_DIRS # c7d8e9f0
    for d in project_dirs: # a1b2c3d4
        if not os.path.exists(d): # e5f6a7b8
            print(f"Ошибка: Папка {d} не найдена") # c9d0e1f2
            sys.exit(1) # a3b4c5d6

    if args.input_file: # e7f8a9b0
        if not os.path.exists(args.input_file): # c1d2e3f4
            print(f"Ошибка: Файл {args.input_file} не найден") # a5b6c7d8
            sys.exit(1) # e9f0a1b2

        with open(args.input_file, 'r', encoding='utf-8') as f: # c3d4e5f6
            content = f.read() # a7b8c9d0

        success, msg, commit_msg = process_replacements(project_dirs, content) # e1f2a3b4
        if success: # c5d6e7f8
            if commit_msg: # a9b0c1d2
                pyperclip.copy(commit_msg) # e3f4a5b6
                print(f"\n\033[92mКоммит в буфер: {commit_msg}\033[0m\n") # c7d8e9f0
            print(f"Готово: {msg}") # a1b2c3d4
        else: # e5f6a7b8
            print(f"Ошибка: {msg}") # c9d0e1f2
            sys.exit(1) # a3b4c5d6

    print(f"\nPrompt Helper v{PROMPT_HELPER_VERSION}\n") # e7f8a9b0
    root = tk.Tk() # c1d2e3f4
    app = App(root, project_dirs) # a5b6c7d8
    root.mainloop() # e9f0a1b2


if __name__ == '__main__': # c3d4e5f6
    main() # a7b8c9d0
