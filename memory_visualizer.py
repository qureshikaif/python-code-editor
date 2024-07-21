import tkinter as tk

class MemoryVisualizer(tk.Toplevel):
    def __init__(self, master, memory_manager):
        super().__init__(master)
        self.title("Memory Management Visualization")
        self.geometry("400x400")

        self.memory_manager = memory_manager

        self.canvas = tk.Canvas(self, width=380, height=300, bg="white")
        self.canvas.pack(pady=20)

        self.update_canvas()

    def update_canvas(self):
        self.canvas.delete("all")
        y = 10
        for start, size in self.memory_manager.blocks:
            self.canvas.create_rectangle(10, y, 10 + size * 0.3, y + 20, outline="black", fill="lightgrey")
            self.canvas.create_text(15, y + 10, anchor="w", text=f"Block {start}-{start+size}", font=("Courier", 10))
            y += 30
        self.after(1000, self.update_canvas) 
