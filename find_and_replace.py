# find_and_replace.py
import tkinter as tk

class FindAndReplace(tk.Toplevel):
    def __init__(self, master, text_widget):
        super().__init__(master)
        self.text_widget = text_widget
        self.title("Find and Replace")
        self.geometry("300x150")

        self.find_label = tk.Label(self, text="Find:")
        self.find_label.pack(pady=5)
        self.find_entry = tk.Entry(self, width=30)
        self.find_entry.pack(pady=5)

        self.replace_label = tk.Label(self, text="Replace:")
        self.replace_label.pack(pady=5)
        self.replace_entry = tk.Entry(self, width=30)
        self.replace_entry.pack(pady=5)

        self.replace_button = tk.Button(self, text="Replace", command=self.replace_text)
        self.replace_button.pack(pady=10)

    def replace_text(self):
        find_text = self.find_entry.get()
        replace_text = self.replace_entry.get()
        content = self.text_widget.get("1.0", tk.END)
        new_content = content.replace(find_text, replace_text)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(tk.END, new_content)
