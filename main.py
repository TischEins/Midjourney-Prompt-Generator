import os
import re
import sys
import webbrowser
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
from prompt_engine import PromptEngine

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CATEGORIES = {
    "Portrait":               "portrait",
    "Character Design":       "character_design",
    "Fantasy":                "fantasy",
    "Sci-Fi":                 "sci_fi",
    "Horror":                 "horror",
    "Surrealism":             "surrealism",
    "Food":                   "food",
    "Product Photography":    "product_photography",
    "Editorial Fashion":      "editorial_fashion",
    "Street Photography":     "street_photography",
    "Architecture":           "architecture",
    "Interior Design":        "interior_design",
    "Nature & Landscapes":    "nature_landscapes",
    "Animals & Wildlife":     "animals_wildlife",
    "Historical Scenes":      "historical_scenes",
    "Mythology & Legends":    "mythology_legends",
    "Cyberpunk":              "cyberpunk",
    "Abstract Art":           "abstract_art",
    "Vehicles & Machines":    "vehicles_machines",
    "Cinematic Storytelling": "cinematic_storytelling",
}

VERSIONS = ["--v 5.2", "--v 6", "--v 6.1", "--v 7", "--v 8.1"]

ASPECT_RATIOS = [
    "--ar 1:1", "--ar 2:3", "--ar 3:2", "--ar 4:5", "--ar 5:4",
    "--ar 16:9", "--ar 9:16", "--ar 21:9", "--ar 9:21",
]

TISCHEINS_URL = "https://tischeins.org/"

_V_PAT  = re.compile(r'--v\s+[\d.]+')
_AR_PAT = re.compile(r'--ar\s+[\d:]+')


def _asset(filename: str) -> str:
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "assets", filename)


def _load_logo(size: int = 44):
    svg_path = _asset("tischlogo.svg")
    if not os.path.exists(svg_path):
        return None
    try:
        import cairosvg
        from PIL import Image, ImageTk
        import io
        data = cairosvg.svg2png(url=svg_path, output_width=size, output_height=size)
        return ImageTk.PhotoImage(Image.open(io.BytesIO(data)))
    except Exception:
        pass
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM
        from PIL import Image, ImageTk
        import io
        drw = svg2rlg(svg_path)
        if drw and drw.width:
            s = size / max(drw.width, drw.height)
            drw.width = drw.height = size
            drw.transform = (s, 0, 0, s, 0, 0)
            data = renderPM.drawToString(drw, fmt="PNG")
            return ImageTk.PhotoImage(Image.open(io.BytesIO(data)))
    except Exception:
        pass
    return None


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.engine = PromptEngine()
        self.current_prompt = ""
        self._logo_img = None

        self.title("TischEins Midjourney Prompt Generator")
        self.geometry("860x620")
        self.minsize(760, 540)
        self._build_ui()

    # ── Layout ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_main_panel()

    def _build_main_panel(self):
        panel = ctk.CTkFrame(self, corner_radius=12)
        panel.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(3, weight=1)

        # ── Title ──
        ctk.CTkLabel(
            panel,
            text="TischEins Midjourney Prompt Generator",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, pady=(22, 12))

        # ── Controls: Category + Version + AR ──
        ctrl = ctk.CTkFrame(panel, fg_color="transparent")
        ctrl.grid(row=1, column=0, pady=(0, 16))

        ctk.CTkLabel(ctrl, text="Category:", font=ctk.CTkFont(size=13)).grid(
            row=0, column=0, padx=(0, 6)
        )
        self.category_menu = ctk.CTkOptionMenu(
            ctrl,
            values=list(CATEGORIES.keys()),
            width=210,
            font=ctk.CTkFont(size=13),
            dropdown_font=ctk.CTkFont(size=12),
        )
        self.category_menu.set("Portrait")
        self.category_menu.grid(row=0, column=1, padx=(0, 22))

        ctk.CTkLabel(ctrl, text="Version:", font=ctk.CTkFont(size=13)).grid(
            row=0, column=2, padx=(0, 6)
        )
        self.version_menu = ctk.CTkOptionMenu(
            ctrl,
            values=VERSIONS,
            width=120,
            font=ctk.CTkFont(size=13),
            dropdown_font=ctk.CTkFont(size=12),
        )
        self.version_menu.set("--v 6.1")
        self.version_menu.grid(row=0, column=3, padx=(0, 22))

        ctk.CTkLabel(ctrl, text="Aspect Ratio:", font=ctk.CTkFont(size=13)).grid(
            row=0, column=4, padx=(0, 6)
        )
        self.ar_menu = ctk.CTkOptionMenu(
            ctrl,
            values=ASPECT_RATIOS,
            width=130,
            font=ctk.CTkFont(size=13),
            dropdown_font=ctk.CTkFont(size=12),
        )
        self.ar_menu.set("--ar 16:9")
        self.ar_menu.grid(row=0, column=5)

        # ── Generate button ──
        self.gen_btn = ctk.CTkButton(
            panel,
            text="⚡  Generate Prompt",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=62,
            corner_radius=31,
            command=self._generate,
        )
        self.gen_btn.grid(row=2, column=0, padx=50, pady=(0, 16), sticky="ew")

        # ── Prompt textbox ──
        self.prompt_box = ctk.CTkTextbox(
            panel,
            font=ctk.CTkFont(family="Consolas", size=13),
            wrap="word",
        )
        self.prompt_box.grid(row=3, column=0, padx=20, pady=(0, 12), sticky="nsew")
        self.prompt_box.configure(state="disabled")

        # ── Action buttons ──
        bar = ctk.CTkFrame(panel, fg_color="transparent")
        bar.grid(row=4, column=0, pady=(0, 10))

        self.copy_btn = ctk.CTkButton(
            bar, text="Copy to Clipboard", width=170, command=self._copy
        )
        self.copy_btn.grid(row=0, column=0, padx=8)

        ctk.CTkButton(
            bar,
            text="Blacklist this Prompt",
            width=170,
            fg_color="#444",
            hover_color="#333",
            command=self._blacklist,
        ).grid(row=0, column=1, padx=8)

        ctk.CTkButton(
            bar,
            text="Save as TXT",
            width=130,
            fg_color="#444",
            hover_color="#333",
            command=self._save_as_txt,
        ).grid(row=0, column=2, padx=8)

        # ── Bottom bar: status left, logo right ──
        bottom = ctk.CTkFrame(panel, fg_color="transparent")
        bottom.grid(row=5, column=0, padx=20, pady=(0, 14), sticky="ew")
        bottom.grid_columnconfigure(0, weight=1)

        self.status_var = tk.StringVar(
            value="Select a category and generate your first prompt."
        )
        ctk.CTkLabel(
            bottom,
            textvariable=self.status_var,
            text_color="gray50",
            font=ctk.CTkFont(size=11),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            bottom,
            text="Made with ♥ | 100% Free",
            text_color="gray45",
            font=ctk.CTkFont(size=11),
        ).grid(row=0, column=1, sticky="e", padx=(0, 12))

        self._add_logo(bottom)

    def _add_logo(self, parent):
        img = _load_logo(44)
        if img:
            self._logo_img = img
            logo_btn = ctk.CTkButton(
                parent,
                image=img,
                text="",
                width=44,
                height=44,
                fg_color="transparent",
                hover_color="#222",
                command=lambda: webbrowser.open(TISCHEINS_URL),
            )
        else:
            logo_btn = ctk.CTkButton(
                parent,
                text="↑ VISIT TISCHEINS",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="transparent",
                hover_color="#1a1a1a",
                text_color="gray55",
                width=150,
                command=lambda: webbrowser.open(TISCHEINS_URL),
            )
        logo_btn.grid(row=0, column=2, sticky="e")

    # ── Actions ─────────────────────────────────────────────────────────────

    def _generate(self):
        cat_key = CATEGORIES.get(self.category_menu.get())
        if not cat_key:
            return
        raw = self.engine.generate(cat_key)
        if not raw:
            messagebox.showwarning(
                "Hinweis",
                "Alle möglichen Prompts sind auf der Blacklist.\n"
                "Bitte starte die App neu.",
            )
            return
        final = self._override_params(raw, self.version_menu.get(), self.ar_menu.get())
        self.current_prompt = final
        self._set_prompt_text(final)
        self.status_var.set(f"Kategorie: {self.category_menu.get()}")

    @staticmethod
    def _override_params(prompt: str, version: str, ar: str) -> str:
        prompt = _V_PAT.sub("", prompt)
        prompt = _AR_PAT.sub("", prompt)
        prompt = " ".join(prompt.split())
        return f"{prompt} {ar} {version}"

    def _copy(self):
        if not self.current_prompt:
            return
        self.clipboard_clear()
        self.clipboard_append(self.current_prompt)
        self.copy_btn.configure(text="✓  Copied!")
        self.after(1800, lambda: self.copy_btn.configure(text="Copy to Clipboard"))

    def _blacklist(self):
        if not self.current_prompt:
            return
        self.engine.add_to_blacklist(self.current_prompt)
        self.status_var.set(
            f"Blacklisted · {len(self.engine.blacklist)} Prompts gesperrt"
        )

    def _save_as_txt(self):
        if not self.current_prompt:
            messagebox.showinfo("Hinweis", "Bitte zuerst einen Prompt generieren.")
            return
        path = filedialog.asksaveasfilename(
            title="Prompt speichern",
            defaultextension=".txt",
            filetypes=[("Textdatei", "*.txt"), ("Alle Dateien", "*.*")],
            initialfile="midjourney_prompt.txt",
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.current_prompt)
        self.status_var.set(f"Gespeichert: {os.path.basename(path)}")

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _set_prompt_text(self, text: str):
        self.prompt_box.configure(state="normal")
        self.prompt_box.delete("1.0", "end")
        self.prompt_box.insert("1.0", text)
        self.prompt_box.configure(state="disabled")


if __name__ == "__main__":
    app = App()
    app.mainloop()
