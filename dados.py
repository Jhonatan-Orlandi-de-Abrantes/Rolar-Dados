import tkinter as tk
from tkinter import ttk
import random, json, os, io, urllib.request, tempfile, pygame
from PIL import Image, ImageTk
from datetime import datetime

GITHUB_BASE = "https://raw.githubusercontent.com/Jhonatan-Orlandi-de-Abrantes/Rolar-Dados/main/assets"

IMAGE_URLS = {
    "D20": f"{GITHUB_BASE}/imagens/d20.png",
    "D12": f"{GITHUB_BASE}/imagens/d12.png",
    "D10": f"{GITHUB_BASE}/imagens/d10.png",
    "D8": f"{GITHUB_BASE}/imagens/d8.png",
    "D6": f"{GITHUB_BASE}/imagens/d6.png",
    "D4": f"{GITHUB_BASE}/imagens/d4.png",
}

SOUND_URL = f"{GITHUB_BASE}/som/roll.wav"

DICE_TYPES = {
    "D20": 20,
    "D12": 12,
    "D10": 10,
    "D8": 8,
    "D6": 6,
    "D4": 4
}

def get_data_dir():
    base = os.getenv("APPDATA") or os.path.expanduser("~")
    path = os.path.join(base, "DiceRoller")
    os.makedirs(path, exist_ok=True)
    return path

DATA_DIR = get_data_dir()
HISTORY_FILE = os.path.join(DATA_DIR, "historico.json")

pygame.mixer.init()

def load_remote_sound(url):
    with urllib.request.urlopen(url) as response:
        data = response.read()

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp.write(data)
    temp.close()

    return pygame.mixer.Sound(temp.name)

ROLL_SOUND = load_remote_sound(SOUND_URL)

class DiceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dice Roller")
        self.geometry("900x600")

        self.history = self.load_history()
        self.dice_imagens = {}

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True)

        self.roll_tab = ttk.Frame(self.tabs)
        self.sum_tab = ttk.Frame(self.tabs)

        self.tabs.add(self.roll_tab, text="Rolagem")
        self.tabs.add(self.sum_tab, text="Soma de Dados")

        self.create_roll_tab()
        self.create_sum_tab()

    def load_history(self):
        if not os.path.exists(HISTORY_FILE):
            return []
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                return json.loads(content) if content else []
        except json.JSONDecodeError:
            return []

    def save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=4, ensure_ascii=False)

    def add_history(self, dice, modifier, final_value, all_results):
        entry = {
            "datetime": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "dice": dice,
            "modifier": modifier,
            "result": final_value,
            "rolls": all_results
        }
        self.history.append(entry)
        self.history_box.insert(0, f"{entry['datetime']} | {dice} | {final_value}")
        self.save_history()

    def clear_history(self):
        self.history = []
        self.history_box.delete(0, tk.END)
        self.save_history()

    def roll_dice(self, sides, modifier):
        rolls = max(1, abs(modifier)) if modifier != 0 else 1
        results = [random.randint(1, sides) for _ in range(rolls)]

        if modifier > 0:
            return max(results), results
        elif modifier < 0:
            return min(results), results
        else:
            return results[0], results

    def load_remote_image(self, url):
        with urllib.request.urlopen(url) as response:
            data = response.read()
        image = Image.open(io.BytesIO(data)).resize((100, 100))
        return ImageTk.PhotoImage(image)

    def create_roll_tab(self):
        control = ttk.Frame(self.roll_tab)
        control.pack(pady=10)

        ttk.Label(control, text="Vantagem / Desvantagem:").pack(side="left")
        self.mod_entry = ttk.Entry(control, width=5)
        self.mod_entry.insert(0, "0")
        self.mod_entry.pack(side="left", padx=5)

        ttk.Button(
            control,
            text="Limpar Histórico",
            command=self.clear_history
        ).pack(side="right", padx=10)

        dice_frame = ttk.Frame(self.roll_tab)
        dice_frame.pack(pady=20)

        for dice, sides in DICE_TYPES.items():
            img = self.load_remote_image(IMAGE_URLS[dice])
            self.dice_imagens[dice] = img

            btn = tk.Button(
                dice_frame,
                image=img,
                command=lambda d=dice, s=sides: self.roll_single(d, s),
                borderwidth=0
            )
            btn.pack(side="left", padx=10)

        self.result_label = ttk.Label(self.roll_tab, text="Resultado: -", font=("Arial", 16))
        self.result_label.pack(pady=10)

        history_frame = ttk.LabelFrame(self.roll_tab, text="Histórico")
        history_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.history_box = tk.Listbox(history_frame)
        self.history_box.pack(fill="both", expand=True)

        for h in reversed(self.history):
            self.history_box.insert(
                tk.END,
                f"{h['datetime']} | {h['dice']} | {h['result']}"
            )

    def roll_single(self, dice, sides):
        try:
            modifier = int(self.mod_entry.get())
        except ValueError:
            modifier = 0

        ROLL_SOUND.play()

        final, all_results = self.roll_dice(sides, modifier)
        self.result_label.config(
            text=f"{dice}: {final} | Rolagens: {all_results}"
        )

        self.add_history(dice, modifier, final, all_results)

    def create_sum_tab(self):
        self.sum_vars = {}

        frame = ttk.Frame(self.sum_tab)
        frame.pack(pady=20)

        for dice in DICE_TYPES:
            var = tk.IntVar(value=0)
            self.sum_vars[dice] = var

            row = ttk.Frame(frame)
            row.pack(anchor="w", pady=3)

            ttk.Label(row, text=dice, width=5).pack(side="left")
            ttk.Spinbox(row, from_=0, to=20, width=5, textvariable=var).pack(side="left")

        ttk.Button(self.sum_tab, text="Rolar Soma", command=self.roll_sum).pack(pady=10)

        self.sum_result = ttk.Label(self.sum_tab, text="Soma Total: -", font=("Arial", 16))
        self.sum_result.pack()

    def roll_sum(self):
        total = 0
        details = []

        ROLL_SOUND.play()

        for dice, count_var in self.sum_vars.items():
            sides = DICE_TYPES[dice]
            for _ in range(count_var.get()):
                roll = random.randint(1, sides)
                total += roll
                details.append(f"{dice}:{roll}")

        self.sum_result.config(
            text=f"Soma Total: {total}\n{', '.join(details)}"
        )

if __name__ == "__main__":
    app = DiceApp()
    app.mainloop()