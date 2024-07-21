import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, Menu, simpledialog, ttk
import sys
import psutil
import contextlib
from io import StringIO
import subprocess
import platform
from queue import Queue
import threading
import time
import os
import jedi
from task_visualizer import TaskVisualizer
from memory_manager import MemoryManager
from memory_visualizer import MemoryVisualizer
from find_and_replace import FindAndReplace

class PythonIDE:
    def __init__(self, master):
        self.master = master
        master.title("Python IDE")
        master.geometry("840x700")

        self.file_path = None
        self.create_widgets()

        self.task_queue = Queue()
        self.running_task = False
        self.tasks = []
        self.memory_manager = MemoryManager(1000)

    def create_widgets(self):
        # Menu Bar
        self.menu_bar = Menu(self.master)
        self.master.config(menu=self.menu_bar)

        # File Menu
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        self.file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        self.file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        self.file_menu.add_command(label="Save As", command=self.save_as_file)
        self.file_menu.add_command(label="Open Folder", command=self.open_folder)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit_program, accelerator="Ctrl+Q")
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # Tools Menu
        self.tools_menu = Menu(self.menu_bar, tearoff=0)
        self.tools_menu.add_command(label="Open Terminal", command=self.open_terminal)
        self.tools_menu.add_command(label="Task Visualization", command=self.show_task_visualization)
        self.tools_menu.add_command(label="Memory Management", command=self.show_memory_management)
        self.menu_bar.add_cascade(label="Tools", menu=self.tools_menu)

        # Buttons to simulate memory allocation and deallocation
        self.allocate_button = tk.Button(self.master, text="Allocate 100", command=self.allocate_memory)
        self.allocate_button.place(x=20, y=670)
        self.deallocate_button = tk.Button(self.master, text="Deallocate 100", command=self.deallocate_memory)
        self.deallocate_button.place(x=150, y=670)

         # System Tools Menu
        self.system_tools_menu = Menu(self.menu_bar, tearoff=0)
        self.system_tools_menu.add_command(label="View Processes", command=self.view_processes)
        self.system_tools_menu.add_command(label="Resource Usage", command=self.show_resource_usage)
        self.menu_bar.add_cascade(label="System Tools", menu=self.system_tools_menu)

        # Edit Menu
        self.edit_menu = Menu(self.menu_bar, tearoff=0)
        self.edit_menu.add_command(label="Copy", command=self.copy_text, accelerator="Ctrl+C")
        self.edit_menu.add_command(label="Cut", command=self.cut_text, accelerator="Ctrl+X")
        self.edit_menu.add_command(label="Paste", command=self.paste_text, accelerator="Ctrl+V")
        self.edit_menu.add_command(label="Select All", command=self.select_all_text, accelerator="Ctrl+A")
        self.edit_menu.add_command(label="Undo", command=self.undo_text, accelerator="Ctrl+Z")
        self.edit_menu.add_command(label="Redo", command=self.redo_text, accelerator="Ctrl+Y")
        self.edit_menu.add_command(label="Find and Replace", command=self.find_and_replace, accelerator="Ctrl+F")
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)

        editor_font = ("Courier", 12)  # Specify the font family and size

        # File Path Label
        self.file_path_label = tk.Label(self.master, text="No file selected", anchor="w", bg="lightgrey", relief="sunken")
        self.file_path_label.place(x=10, y=10, width=820, height=25)
        
        # Text Editor
        self.text_editor = scrolledtext.ScrolledText(self.master, width=61, height=13, wrap="word", font=editor_font, undo=True, highlightthickness=0)
        self.text_editor.place(x=10, y=45)
        self.text_editor.bind("<KeyRelease>", self.on_key_release)

        # Autocomplete Listbox
        self.listbox = tk.Listbox(self.master)
        self.listbox.place(x=10, y=250, width=300, height=100)
        self.listbox.bind("<Double-Button-1>", self.on_listbox_select)
        self.listbox.bind("<Escape>", self.hide_listbox)
        self.hide_listbox()

        # Output Console
        self.output_widget = scrolledtext.ScrolledText(self.master, width=61, height=10, font=editor_font, highlightthickness=0)
        self.output_widget.place(x=10, y=380)

        # File Tree
        self.tree = ttk.Treeview(self.master)
        self.tree.place(x=440, y=45, width=380, height=600)
        self.tree.heading("#0", text="Directory Structure", anchor="w")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Run Button
        self.run_button = tk.Button(self.master, text="Run", command=self.add_task, width=10)
        self.run_button.place(x=10, y=640)

        # Clear Output Button
        self.clear_output_button = tk.Button(self.master, text="Clear Output", command=self.clear_output, width=15)
        self.clear_output_button.place(x=140, y=640)

        # Keyboard Shortcuts
        self.master.bind_all("<Control-n>", self.new_file)
        self.master.bind_all("<Control-o>", self.open_file)
        self.master.bind_all("<Control-s>", self.save_file)
        self.master.bind_all("<Control-q>", self.exit_program)
        self.master.bind_all("<Control-r>", self.add_task)
        self.master.bind_all("<Control-i>", self.clear_output)
        self.master.bind_all("<Control-c>", self.copy_text)
        self.master.bind_all("<Control-x>", self.cut_text)
        self.master.bind_all("<Control-v>", self.paste_text)
        self.master.bind_all("<Control-a>", self.select_all_text)
        self.master.bind_all("<Control-z>", self.undo_text)
        self.master.bind_all("<Control-y>", self.redo_text)
        self.master.bind_all("<Control-f>", self.find_and_replace)
        self.text_editor.bind("<KeyRelease>", self.on_key_release)

    def add_task(self, event=None):
        code = self.text_editor.get("1.0", tk.END)
        self.task_queue.put(code)
        self.tasks.append((code, 'Pending'))
        if not self.running_task:
            self.run_tasks()

    def run_tasks(self):
        if not self.task_queue.empty():
            self.running_task = True
            code = self.task_queue.get()
            threading.Thread(target=self.execute_code, args=(code,)).start()
        else:
            self.running_task = False

    def execute_code(self, code):
        output_stream = StringIO()
        with contextlib.redirect_stdout(output_stream):
            try:
                exec(code)
            except Exception as e:
                output_stream.write(str(e))

        output = output_stream.getvalue()
        self.master.after(0, self.update_output, output)

        self.master.after(0, self.update_task_status, code, 'Completed')

        time.sleep(1) 
        self.run_tasks()

    def update_output(self, output):
        self.output_widget.insert(tk.END, output)
        self.output_widget.see(tk.END)

    def update_task_status(self, code, status):
        for i, task in enumerate(self.tasks):
            if task[0] == code:
                self.tasks[i] = (code, status)
                break

    def save_file(self, event=None):
        if self.file_path is None:
            self.save_as_file()
        else:
            code = self.text_editor.get("1.0", tk.END)
            with open(self.file_path, "w") as f:
                f.write(code)
            self.file_path_label.config(text=self.file_path)

    def save_as_file(self):
        code = self.text_editor.get("1.0", tk.END)
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")])
        if file_path:
            self.file_path = file_path
            with open(file_path, "w") as f:
                f.write(code)
            self.file_path_label.config(text=self.file_path)

    def open_file(self, event=None):
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            self.file_path = file_path
            with open(file_path, "r") as f:
                code = f.read()
            self.text_editor.delete("1.0", tk.END)
            self.text_editor.insert(tk.END, code)
            self.file_path_label.config(text=self.file_path)

    def new_file(self, event=None):
        self.text_editor.delete("1.0", tk.END)
        self.file_path = None
        self.file_path_label.config(text="No file selected")

    def exit_program(self, event=None):
        self.master.destroy()

    def clear_output(self, event=None):
        self.output_widget.delete("1.0", tk.END)

    def open_terminal(self):
        system_name = platform.system()
        if system_name == "Windows":
            subprocess.run("start", shell=True)
        elif system_name == "Darwin":  # macOS
            subprocess.run("open -a Terminal .", shell=True)
        elif system_name == "Linux":
            subprocess.run("gnome-terminal", shell=True)

    def show_task_visualization(self):
        if not hasattr(self, 'task_visualizer') or not self.task_visualizer.winfo_exists():
        # Pass a method reference that TaskVisualizer can call to get the latest tasks
            self.task_visualizer = TaskVisualizer(self.master, self.get_tasks)

    def get_tasks(self):
        return self.tasks

    def show_memory_management(self):
        MemoryVisualizer(self.master, self.memory_manager)

    def copy_text(self, event=None):
        try:
            self.master.clipboard_clear()
            text = self.text_editor.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.master.clipboard_append(text)
        except tk.TclError:
            pass

    def cut_text(self, event=None):
        try:
            self.copy_text()
            self.text_editor.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass

    def paste_text(self, event=None):
        try:
            text = self.master.clipboard_get()
            self.text_editor.insert(tk.INSERT, text)
        except tk.TclError:
            pass

    def select_all_text(self, event=None):
        self.text_editor.tag_add(tk.SEL, "1.0", tk.END)
        self.text_editor.mark_set(tk.INSERT, "1.0")
        self.text_editor.see(tk.INSERT)
        return "break"

    def undo_text(self, event=None):
        try:
            self.text_editor.edit_undo()
        except tk.TclError:
            pass

    def redo_text(self, event=None):
        try:
            self.text_editor.edit_redo()
        except tk.TclError:
            pass

    def find_and_replace(self, event=None):
        FindAndReplace(self.master, self.text_editor)

    def open_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.populate_tree(folder_path)

    def populate_tree(self, path, parent=""):
        self.tree.delete(*self.tree.get_children(parent))
        for p in os.listdir(path):
            abspath = os.path.join(path, p)
            oid = self.tree.insert(parent, 'end', text=p, open=False)
            if os.path.isdir(abspath):
                self.populate_tree(abspath, oid)

    def on_tree_select(self, event):
        selected_item = self.tree.selection()[0]
        file_path = self.tree.item(selected_item, "text")
        parent_iid = self.tree.parent(selected_item)
        while parent_iid:
            file_path = os.path.join(self.tree.item(parent_iid, "text"), file_path)
            parent_iid = self.tree.parent(selected_item)
        if file_path.endswith('.py') or file_path.endswith('.txt'):
            self.file_path = file_path
            with open(file_path, "r") as file:
                content = file.read()
                self.text_editor.delete("1.0", tk.END)
                self.text_editor.insert(tk.END, content)
                self.file_path_label.config(text=self.file_path)

    def show_memory_management(self):
        MemoryVisualizer(self.master, self.memory_manager)

    def allocate_memory(self):
        self.memory_manager.best_fit_allocate(100)

    def deallocate_memory(self):
        self.memory_manager.deallocate(0, 100)

    def on_key_release(self, event):
        cursor_index = self.text_editor.index(tk.INSERT)
        line, column = cursor_index.split(".")
        code = self.text_editor.get("1.0", tk.END)
        self.script = jedi.Script(code)
        completions = self.script.complete(int(line), int(column))
        self.show_completions(completions)

    def show_completions(self, completions):
        if completions:
            self.listbox.delete(0, tk.END)
            for completion in completions:
                self.listbox.insert(tk.END, completion.name)
            if not self.listbox.winfo_ismapped():
                self.listbox.place(x=10, y=250, width=300, height=100)
        else:
            self.hide_listbox()

    def on_listbox_select(self, event=None):
        if self.listbox.curselection():
            selected = self.listbox.get(self.listbox.curselection())
            cursor_position = self.text_editor.index(tk.INSERT)
            line, column = map(int, cursor_position.split('.'))
            code = self.text_editor.get("1.0", tk.END)
            script = jedi.Script(code, line, column)
            completions = script.complete()
            for completion in completions:
                if completion.name == selected:
                    insert_text = completion.complete
                    self.text_editor.insert(tk.INSERT, insert_text)
                    self.hide_listbox()
                    return

    def hide_listbox(self, event=None):
        self.listbox.place_forget()

    def view_processes(self):
        if not hasattr(self, 'process_window') or not self.process_window.winfo_exists():
            self.process_window = tk.Toplevel(self.master)
            self.process_window.title("Processes")
            self.process_window.geometry("600x400")
            self.process_listbox = tk.Listbox(self.process_window, width=80, height=20)
            self.process_listbox.pack(pady=20, fill=tk.BOTH, expand=True)
            self.keep_updating = True
            self.update_process_list_threaded()

    def fetch_process_list(self):
        return list(psutil.process_iter(['pid', 'name', 'username']))

    def update_process_list(self, processes):
        self.process_listbox.delete(0, tk.END)
        for proc in processes:
            self.process_listbox.insert(tk.END, f'PID: {proc.info["pid"]}, Name: {proc.info["name"]}, User: {proc.info["username"]}')

    def update_process_list_threaded(self):
        if self.keep_updating:
            processes = self.fetch_process_list()
            self.master.after(0, self.update_process_list, processes)
            self.process_window.after(5000, self.update_process_list_threaded)

    def on_closing_process_window(self):
        self.keep_updating = False
        self.process_window.destroy()

    # Modify how the window is closed to properly stop the update loop
    def view_processes(self):
        if not hasattr(self, 'process_window') or not self.process_window.winfo_exists():
            self.process_window = tk.Toplevel(self.master)
            self.process_window.title("Processes")
            self.process_window.geometry("600x400")
            self.process_window.protocol("WM_DELETE_WINDOW", self.on_closing_process_window)
            self.process_listbox = tk.Listbox(self.process_window, width=80, height=20)
            self.process_listbox.pack(pady=20, fill=tk.BOTH, expand=True)
            self.keep_updating = True
            self.update_process_list_threaded()

    def show_resource_usage(self):
        if not hasattr(self, 'usage_window') or not self.usage_window.winfo_exists():
            self.usage_window = tk.Toplevel(self.master)
            self.usage_window.title("Resource Usage")
            self.usage_window.geometry("300x200")
            self.cpu_label = tk.Label(self.usage_window, text="")
            self.cpu_label.pack(pady=10)
            self.memory_label = tk.Label(self.usage_window, text="")
            self.memory_label.pack(pady=10)
            self.update_resource_usage()

    def update_resource_usage(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        self.cpu_label.config(text=f"CPU Usage: {cpu_usage}%")
        self.memory_label.config(text=f"Memory Usage: {memory_usage}%")
        self.usage_window.after(5000, self.update_resource_usage)  # update every 5 seconds



def main():
    root = tk.Tk()
    app = PythonIDE(root)
    root.mainloop()

if __name__ == "__main__":
    main()
