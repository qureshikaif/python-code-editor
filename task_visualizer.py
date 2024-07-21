# task_visualizer.py
import tkinter as tk

class TaskVisualizer(tk.Toplevel):
    def __init__(self, master, task_reference):
        super().__init__(master)
        self.title("Task Visualization")
        self.geometry("400x300")
        self.task_reference = task_reference
        self.task_listbox = tk.Listbox(self, width=50, height=15)
        self.task_listbox.pack(pady=20)
        self.refresh_task_list()

    def refresh_task_list(self):
        self.task_listbox.delete(0, tk.END)
        for code, status in self.task_reference():
            self.task_listbox.insert(tk.END, f"Task: {code[:30]}... Status: {status}")
        self.after(1000, self.refresh_task_list)  # Update every 1000 milliseconds (1 second)
