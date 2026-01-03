import tkinter as tk
from tkinter import ttk
import random
from datetime import datetime

# ---------------- CONFIG ---------------- #

DICE_TYPES = {
    "D20": 20,
    "D12": 12,
    "D10": 10,
    "D8": 8,
    "D6": 6,
    "D4": 4
}

# ---------------- APP ---------------- #

class DiceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dice Roller")
        self.geometry("900x600")

        self.history = []

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True)

        self.roll_tab = ttk.Frame(self.tabs)
        self.sum_tab = ttk.Frame(self.tabs)

        self.tabs.add(self.roll_tab, text="Rolagem")
        self.tabs.add(self.sum_tab, text="Soma de Dados")

        self.create_roll_tab()
        self.create_sum_tab()

    # ---------- UTIL ---------- #

    def roll_dice(self, sides, modifier):
        modifier = int(modifier)
        rolls = max(1, abs(modifier)) if modifier != 0 else 1
        results = [random.randint(1, sides) for _ in range(rolls)]

        if modifier > 0:
            return max(results), results
        elif modifier < 0:
            return min(results), results
        else:
            return results[0], results

    def add_history(self, dice, modifier, final_value):
        entry = f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | {dice} | Mod: {modifier} | Resultado: {final_value}"
        self.history.append(entry)
        self.history_box.insert(tk.END, entry)

    # ---------- ROLAGEM TAB ---------- #

    def create_roll_tab(self):
        top_frame = ttk.Frame(self.roll_tab)
        top_frame.pack(pady=10)

        ttk.Label(top_frame, text="Vantagem / Desvantagem (-X / +X):").pack(side="left")
        self.modifier_entry = ttk.Entry(top_frame, width=5)
        self.modifier_entry.insert(0, "0")
        self.modifier_entry.pack(side="left", padx=5)

        dice_frame = ttk.Frame(self.roll_tab)
        dice_frame.pack(pady=20)

        for dice, sides in DICE_TYPES.items():
            btn = tk.Button(
                dice_frame,
                text=f"{dice}\n({sides})",
                width=10,
                height=4,
                command=lambda d=dice, s=sides: self.roll_single(d, s)
            )
            btn.pack(side="left", padx=10)

        result_frame = ttk.Frame(self.roll_tab)
        result_frame.pack(pady=10)

        self.result_label = ttk.Label(result_frame, text="Resultado: -", font=("Arial", 16))
        self.result_label.pack()

        history_frame = ttk.LabelFrame(self.roll_tab, text="Histórico")
        history_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.history_box = tk.Listbox(history_frame)
        self.history_box.pack(fill="both", expand=True)

    def roll_single(self, dice, sides):
        try:
            modifier = int(self.modifier_entry.get())
        except ValueError:
            modifier = 0

        final, all_results = self.roll_dice(sides, modifier)
        self.result_label.config(text=f"{dice}: {final}  (Rolagens: {all_results})")
        self.add_history(dice, modifier, final)

    # ---------- SOMA TAB ---------- #

    def create_sum_tab(self):
        self.sum_vars = {}

        frame = ttk.Frame(self.sum_tab)
        frame.pack(pady=20)

        for dice in DICE_TYPES:
            var = tk.IntVar(value=0)
            self.sum_vars[dice] = var

            row = ttk.Frame(frame)
            row.pack(anchor="w", pady=2)

            ttk.Label(row, text=dice, width=5).pack(side="left")
            ttk.Spinbox(row, from_=0, to=20, width=5, textvariable=var).pack(side="left")

        ttk.Button(
            self.sum_tab,
            text="Rolar Soma",
            command=self.roll_sum
        ).pack(pady=10)

        self.sum_result_label = ttk.Label(self.sum_tab, text="Soma Total: -", font=("Arial", 16))
        self.sum_result_label.pack()

    def roll_sum(self):
        total = 0
        details = []

        for dice, count_var in self.sum_vars.items():
            count = count_var.get()
            sides = DICE_TYPES[dice]

            for _ in range(count):
                roll = random.randint(1, sides)
                total += roll
                details.append(f"{dice}:{roll}")

        self.sum_result_label.config(
            text=f"Soma Total: {total}\nDetalhes: {' | '.join(details)}"
        )

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app = DiceApp()
    app.mainloop()