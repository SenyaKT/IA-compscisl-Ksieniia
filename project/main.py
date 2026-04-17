"""
main.py
-------
Personal Color Analysis App — IB CS SL Internal Assessment
Uses: customtkinter, sqlite3, PIL (Pillow), shutil, os

Install requirements:
    pip install customtkinter pillow opencv-python numpy

Run: python main.py
"""

import os
import shutil
import sqlite3
import json
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk

# Import your own modules
from color_analyzer import WristColorAnalyzer
from season_engine import classify_season, get_color_combinations, SEASON_INFO

# ─────────────────────────────────────────────────────────────
# APP SETTINGS
# ─────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")          # "light" or "dark"
ctk.set_default_color_theme("blue")      # built-in theme base

UPLOADS_FOLDER = "uploads"
HISTORY_DB     = "users_history.db"
os.makedirs(UPLOADS_FOLDER, exist_ok=True)

# ─────────────────────────────────────────────────────────────
# DATABASE SETUP — stores each user's full analysis result
# ─────────────────────────────────────────────────────────────

def init_history_db():
    conn = sqlite3.connect(HISTORY_DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT,
            season_name TEXT,
            season_base TEXT,
            score       INTEGER,
            answers     TEXT,   -- stored as JSON string
            wrist_data  TEXT,   -- stored as JSON string (or NULL)
            date_time   TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_analysis(name, season_name, season_base, score, answers, wrist_data=None):
    conn = sqlite3.connect(HISTORY_DB)
    c = conn.cursor()
    c.execute("""
        INSERT INTO analyses (name, season_name, season_base, score, answers, wrist_data, date_time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        season_name,
        season_base,
        score,
        json.dumps(answers),
        json.dumps(wrist_data) if wrist_data else None,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def load_all_analyses():
    conn = sqlite3.connect(HISTORY_DB)
    c = conn.cursor()
    c.execute("SELECT * FROM analyses ORDER BY date_time DESC")
    rows = c.fetchall()
    conn.close()
    return rows

# ─────────────────────────────────────────────────────────────
# COLOR SWATCH helper — draws a small rectangle as a PIL image
# so tkinter can display it
# ─────────────────────────────────────────────────────────────

def make_swatch(hex_color: str, size=(40, 40)) -> ImageTk.PhotoImage:
    img = Image.new("RGB", size, hex_color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, size[0]-1, size[1]-1], outline="#333333", width=1)
    return ImageTk.PhotoImage(img)

# ─────────────────────────────────────────────────────────────
# MAIN APPLICATION CLASS
# ─────────────────────────────────────────────────────────────

class PersonalColorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        init_history_db()

        self.title("✦ Personal Color Analysis")
        self.geometry("900x700")
        self.resizable(True, True)
        self.configure(fg_color="#0F0F1A")   # very dark purple-black bg

        # State shared between screens
        self.user_name      = ""
        self.answers        = {}
        self.wrist_data     = None
        self.wrist_image_path = None
        self.result         = None

        # Keep a reference to all photo images (prevents garbage collection)
        self._images = []

        # Build the navigation frame on the left
        self._build_nav()

        # Container for main content
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # Show the welcome screen first
        self.show_welcome()

    # ── NAVIGATION SIDEBAR ──────────────────────────────────────────

    def _build_nav(self):
        nav = ctk.CTkFrame(self, width=180, fg_color="#1A1A2E", corner_radius=0)
        nav.pack(side="left", fill="y")
        nav.pack_propagate(False)

        # Logo / title
        ctk.CTkLabel(nav, text="✦ PERSONAL\nCOLOR", font=("Georgia", 20, "bold"),
                     text_color="#C8A4FF").pack(pady=30, padx=15)

        # Nav buttons
        nav_items = [
            ("  Home",       self.show_welcome),
            ("  Questionnaire", self.show_questionnaire),
            ("  Wrist Photo", self.show_upload),
            ("  My Results", self.show_results),
            ("  History",    self.show_history),
            ("  All Palettes", self.show_all_palettes),
        ]
        for label, cmd in nav_items:
            btn = ctk.CTkButton(
                nav, text=label, command=cmd,
                fg_color="transparent",
                text_color="#B0A0D0",
                hover_color="#2A2A4E",
                anchor="w",
                font=("Helvetica", 13),
                height=42,
                corner_radius=8,
            )
            btn.pack(fill="x", padx=10, pady=3)

        # Bottom credit
        ctk.CTkLabel(nav, text="IB CS SL IA", font=("Helvetica", 10),
                     text_color="#4A4A6A").pack(side="bottom", pady=20)

    # ── UTILITY: clear content frame ────────────────────────────────

    def _clear(self):
        for w in self.content_frame.winfo_children():
            w.destroy()
        self._images.clear()

    def _title(self, text, size=24):
        ctk.CTkLabel(
            self.content_frame, text=text,
            font=("Georgia", size, "bold"),
            text_color="#C8A4FF"
        ).pack(anchor="w", pady=(0, 4))

    def _subtitle(self, text):
        ctk.CTkLabel(
            self.content_frame, text=text,
            font=("Helvetica", 13),
            text_color="#8080AA",
            wraplength=680,
            justify="left"
        ).pack(anchor="w", pady=(0, 20))

    # ── SCREEN: WELCOME ──────────────────────────────────────────────

    def show_welcome(self):
        self._clear()

        self._title("Welcome to Personal Color Analysis", 26)
        self._subtitle(
            "Discover your seasonal color palette based on the Korean 16-tone system. "
            "Answer a few questions and optionally upload a wrist photo for a more precise result."
        )

        # Name entry
        ctk.CTkLabel(self.content_frame, text="What is your name?",
                     font=("Helvetica", 14), text_color="#C0C0E0").pack(anchor="w")
        name_entry = ctk.CTkEntry(self.content_frame, placeholder_text="Enter your name...",
                                  width=300, height=40, font=("Helvetica", 13))
        name_entry.pack(anchor="w", pady=(4, 20))

        def start():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Name required", "Please enter your name to continue.")
                return
            self.user_name = name
            self.show_questionnaire()

        ctk.CTkButton(
            self.content_frame, text="Start Analysis →",
            command=start, width=200, height=44,
            font=("Helvetica", 14, "bold"),
            fg_color="#6A3FA0", hover_color="#8A5FC0"
        ).pack(anchor="w", pady=10)

        # Info cards
        cards_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        cards_frame.pack(fill="x", pady=30)

        card_data = [
            ("📋", "Questionnaire", "Answer 8 questions about your natural coloring"),
            ("📸", "Wrist Photo", "Upload a photo for vein & skin pixel analysis"),
            ("🎨", "Your Palette", "Get 15+ matching colors + combination ideas"),
        ]
        for icon, title, desc in card_data:
            card = ctk.CTkFrame(cards_frame, fg_color="#1E1E36", corner_radius=12)
            card.pack(side="left", fill="both", expand=True, padx=8)
            ctk.CTkLabel(card, text=icon, font=("Helvetica", 30)).pack(pady=(16, 4))
            ctk.CTkLabel(card, text=title, font=("Helvetica", 13, "bold"),
                         text_color="#C8A4FF").pack()
            ctk.CTkLabel(card, text=desc, font=("Helvetica", 11),
                         text_color="#7070A0", wraplength=180).pack(pady=(4, 16))

    # ── SCREEN: QUESTIONNAIRE ────────────────────────────────────────

    def show_questionnaire(self):
        if not self.user_name:
            messagebox.showinfo("Name needed", "Please enter your name on the Home screen first.")
            self.show_welcome()
            return

        self._clear()
        self._title(f"Questionnaire — {self.user_name}")
        self._subtitle("Answer each question based on your NATURAL coloring (before any dye/tanning).")

        # Scrollable frame for questions
        scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent",
                                         label_text="", height=480)
        scroll.pack(fill="both", expand=True)

        # Question definitions
        questions = [
            ("skin_undertone", "What is your skin undertone?",
             ["warm (yellow/golden/peachy)", "cool (pink/blue/rosy)", "neutral (both/unsure)"],
             ["warm", "cool", "neutral"]),

            ("skin_depth", "How deep/dark is your natural skin tone?",
             ["light (fair/pale)", "medium", "deep (olive/dark/rich)"],
             ["light", "medium", "deep"]),

            ("hair_color", "What is your natural hair color?",
             ["blonde", "light brown", "medium brown", "dark brown", "black", "red/copper", "auburn", "grey/silver"],
             ["blonde", "light_brown", "medium_brown", "dark_brown", "black", "red", "auburn", "grey"]),

            ("eye_color", "What is your eye color?",
             ["light blue", "light grey", "green", "hazel", "medium brown", "dark brown", "black"],
             ["light_blue", "light_grey", "green", "hazel", "medium_brown", "dark_brown", "black"]),

            ("lip_color", "What is your natural lip color?",
             ["cool pink/berry", "neutral/rosy", "warm peach/coral", "warm brown/nude"],
             ["cool_pink", "neutral", "warm_peach", "warm_brown"]),

            ("vein_color", "Look at your inner wrist veins. What color are they?",
             ["blue or purple", "green", "mixed/hard to tell"],
             ["blue_purple", "green", "mixed"]),

            ("contrast_level", "What is the contrast between your skin, hair and eyes?",
             ["low (everything is similar in depth)", "medium", "high (very different — e.g. fair skin + dark hair)"],
             ["low", "medium", "high"]),

            ("skin_clarity", "How would you describe your skin's quality?",
             ["bright/clear (luminous, noticeable)", "muted/soft (blends, less striking)", "mixed"],
             ["bright", "muted", "muted"]),
        ]

        # Store StringVar for each question
        self._q_vars = {}

        for (key, question, options, values) in questions:
            # Question card
            card = ctk.CTkFrame(scroll, fg_color="#1A1A30", corner_radius=10)
            card.pack(fill="x", padx=4, pady=6)

            ctk.CTkLabel(card, text=question, font=("Helvetica", 13, "bold"),
                         text_color="#D0C0F0", anchor="w").pack(anchor="w", padx=16, pady=(12, 6))

            var = ctk.StringVar(value="")
            self._q_vars[key] = (var, values)

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(fill="x", padx=12, pady=(0, 12))

            for i, (opt_text, val) in enumerate(zip(options, values)):
                def make_cmd(v=val, variable=var, frame=btn_frame, all_vals=values):
                    def cmd():
                        variable.set(v)
                        # Update button colors
                        for child in frame.winfo_children():
                            child.configure(fg_color="#2A2A4A")
                        frame.winfo_children()[all_vals.index(v)].configure(fg_color="#6A3FA0")
                    return cmd

                btn = ctk.CTkButton(
                    btn_frame, text=opt_text,
                    command=make_cmd(),
                    fg_color="#2A2A4A", hover_color="#3A3A5A",
                    text_color="#B0A0D0", font=("Helvetica", 12),
                    height=34, corner_radius=6,
                    anchor="w"
                )
                btn.pack(fill="x", pady=2, padx=4)

        # Submit button (outside scroll)
        ctk.CTkButton(
            self.content_frame,
            text="Save & Continue to Wrist Photo →",
            command=self._submit_questionnaire,
            width=340, height=46,
            font=("Helvetica", 14, "bold"),
            fg_color="#6A3FA0", hover_color="#8A5FC0"
        ).pack(pady=14)

    def _submit_questionnaire(self):
        self.answers = {}
        missing = []
        for key, (var, values) in self._q_vars.items():
            val = var.get()
            if not val:
                missing.append(key)
            else:
                self.answers[key] = val

        if missing:
            messagebox.showwarning(
                "Incomplete",
                f"Please answer all questions.\nMissing: {', '.join(missing)}"
            )
            return

        self.show_upload()

    # ── SCREEN: WRIST UPLOAD ─────────────────────────────────────────

    def show_upload(self):
        self._clear()
        self._title("Wrist Photo Analysis (Optional)")
        self._subtitle(
            "Upload a clear photo of your inner wrist in natural daylight. "
            "The program will detect your skin tone and vein color from the image. "
            "You can skip this step and rely on your questionnaire answers only."
        )

        # Instructions card
        instr = ctk.CTkFrame(self.content_frame, fg_color="#1A2A1A", corner_radius=10)
        instr.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(instr, text="📸 Photo requirements:", font=("Helvetica", 12, "bold"),
                     text_color="#80D080").pack(anchor="w", padx=14, pady=(10, 4))
        for line in ["• Natural daylight (not artificial/flash)", "• Wrist centered in the frame",
                     "• Inner side up (veins visible)", "• JPG, JPEG, or PNG format"]:
            ctk.CTkLabel(instr, text=line, font=("Helvetica", 12),
                         text_color="#70A070").pack(anchor="w", padx=24, pady=1)
        ctk.CTkLabel(instr, text="", height=8).pack()  # spacer

        # Upload button + status
        self._upload_status = ctk.StringVar(value="No photo selected")
        self._preview_label = None

        upload_row = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        upload_row.pack(fill="x", pady=10)

        ctk.CTkButton(
            upload_row, text="📂  Choose Photo",
            command=self._choose_photo,
            width=180, height=44,
            fg_color="#2A4A2A", hover_color="#3A6A3A",
            font=("Helvetica", 13)
        ).pack(side="left")

        ctk.CTkLabel(upload_row, textvariable=self._upload_status,
                     font=("Helvetica", 12), text_color="#8080AA").pack(side="left", padx=16)

        # Preview frame
        self._preview_frame = ctk.CTkFrame(self.content_frame, fg_color="#1A1A30",
                                            corner_radius=10, width=300, height=220)
        self._preview_frame.pack(pady=10)
        self._preview_placeholder = ctk.CTkLabel(
            self._preview_frame, text="Preview will appear here",
            font=("Helvetica", 12), text_color="#5050A0"
        )
        self._preview_placeholder.pack(expand=True)

        # Results text (appears after analysis)
        self._analysis_text = ctk.CTkTextbox(self.content_frame, height=100,
                                              font=("Courier", 12), state="disabled",
                                              fg_color="#0F0F20")
        self._analysis_text.pack(fill="x", pady=8)

        # Action buttons
        btn_row = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        btn_row.pack(pady=10)

        ctk.CTkButton(
            btn_row, text="Analyse Photo",
            command=self._run_wrist_analysis,
            width=160, height=44, font=("Helvetica", 13),
            fg_color="#2A2A6A", hover_color="#3A3A8A"
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_row, text="Skip & Get My Results →",
            command=self._finalize_and_show_results,
            width=220, height=44, font=("Helvetica", 13, "bold"),
            fg_color="#6A3FA0", hover_color="#8A5FC0"
        ).pack(side="left", padx=8)

    def _choose_photo(self):
        path = filedialog.askopenfilename(
            title="Select wrist photo",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if not path:
            return

        # Copy to uploads folder
        dest = os.path.join(UPLOADS_FOLDER, os.path.basename(path))
        shutil.copy2(path, dest)
        self.wrist_image_path = dest
        self._upload_status.set(f"✓ {os.path.basename(path)}")

        # Show preview
        try:
            img = Image.open(dest)
            img.thumbnail((280, 200))
            photo = ImageTk.PhotoImage(img)
            self._images.append(photo)  # keep reference

            if self._preview_placeholder:
                self._preview_placeholder.destroy()
                self._preview_placeholder = None

            lbl = ctk.CTkLabel(self._preview_frame, image=photo, text="")
            lbl.pack(expand=True)
        except Exception as e:
            messagebox.showerror("Preview error", str(e))

    def _run_wrist_analysis(self):
        if not self.wrist_image_path:
            messagebox.showwarning("No photo", "Please select a photo first, or click Skip.")
            return

        try:
            analyzer = WristColorAnalyzer(self.wrist_image_path)
            self.wrist_data = analyzer.run_analysis()

            if "Error" in str(self.wrist_data):
                err = self.wrist_data.get("Error", "Unknown error")
                messagebox.showerror("Analysis failed", f"Could not analyse photo:\n{err}")
                self.wrist_data = None
                return

            # Display results
            r = self.wrist_data
            text = (
                f"Skin RGB:    {r.get('skin_rgb')}\n"
                f"Skin type:   {r.get('skin_type')}\n"
                f"Skin tone:   {r.get('skin_description')}\n"
                f"Vein color:  {r.get('vein_color')}\n"
                f"Undertone:   {r.get('undertone')}\n"
            )
            self._analysis_text.configure(state="normal")
            self._analysis_text.delete("1.0", "end")
            self._analysis_text.insert("1.0", text)
            self._analysis_text.configure(state="disabled")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _finalize_and_show_results(self):
        if not self.answers:
            messagebox.showwarning("No answers", "Please complete the questionnaire first.")
            self.show_questionnaire()
            return

        # Classify using both questionnaire and wrist data
        self.result = classify_season(self.answers, self.wrist_data)

        # Save to database
        save_analysis(
            name=self.user_name,
            season_name=self.result["season_name"],
            season_base=self.result["season"],
            score=self.result["score"],
            answers=self.answers,
            wrist_data=self.wrist_data
        )

        self.show_results()

    # ── SCREEN: RESULTS ──────────────────────────────────────────────

    def show_results(self):
        if not self.result:
            messagebox.showinfo("No results", "Please complete the questionnaire first.")
            self.show_questionnaire()
            return

        self._clear()
        r = self.result
        season_name = r["season_name"]
        season_base = r["season"]

        self._title(f"Your Personal Color: {season_name}", 22)
        self._subtitle(r["description"])

        # Main results card
        card = ctk.CTkFrame(self.content_frame, fg_color="#1A1A30", corner_radius=14)
        card.pack(fill="x", pady=(0, 14))

        info_row = ctk.CTkFrame(card, fg_color="transparent")
        info_row.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(info_row, text=f"Season: {season_base}",
                     font=("Helvetica", 14), text_color="#C8A4FF").pack(side="left", padx=12)
        ctk.CTkLabel(info_row, text=f"Tone: {r['tone']}",
                     font=("Helvetica", 14), text_color="#A0D0FF").pack(side="left", padx=12)
        ctk.CTkLabel(info_row, text=f"Match score: {r['score']}",
                     font=("Helvetica", 13), text_color="#7070AA").pack(side="left", padx=12)

        # Top 3 matches
        ctk.CTkLabel(card, text="Top 3 matches:",
                     font=("Helvetica", 12), text_color="#7070AA").pack(anchor="w", padx=16)
        for sname, score in r["top3"]:
            ctk.CTkLabel(card, text=f"  {sname}  ({score} pts)",
                         font=("Helvetica", 12), text_color="#A090C0").pack(anchor="w", padx=20)
        ctk.CTkLabel(card, text="", height=8).pack()  # spacer

        # Scrollable color palette
        ctk.CTkLabel(self.content_frame, text="Your Color Palette",
                     font=("Helvetica", 15, "bold"), text_color="#C8A4FF").pack(anchor="w", pady=(10, 4))

        palette_scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent",
                                                 height=160, orientation="horizontal")
        palette_scroll.pack(fill="x")

        for hex_color in r["best_colors"]:
            frame = ctk.CTkFrame(palette_scroll, fg_color="transparent")
            frame.pack(side="left", padx=4)

            swatch = make_swatch(hex_color, size=(56, 56))
            self._images.append(swatch)

            lbl = ctk.CTkLabel(frame, image=swatch, text="")
            lbl.pack()
            ctk.CTkLabel(frame, text=hex_color, font=("Courier", 9),
                         text_color="#7070A0").pack()

        # Color combinations
        combos = get_color_combinations(season_name)
        if combos:
            ctk.CTkLabel(self.content_frame, text="Suggested Outfit Combinations",
                         font=("Helvetica", 15, "bold"), text_color="#C8A4FF").pack(anchor="w", pady=(16, 6))

            for i, combo in enumerate(combos):
                combo_row = ctk.CTkFrame(self.content_frame, fg_color="#1A1A30", corner_radius=8)
                combo_row.pack(fill="x", pady=4, padx=2)

                ctk.CTkLabel(combo_row, text=f"Look {i+1}:",
                             font=("Helvetica", 12), text_color="#8080A0").pack(side="left", padx=12)

                for hex_color in combo:
                    swatch = make_swatch(hex_color, size=(40, 40))
                    self._images.append(swatch)
                    ctk.CTkLabel(combo_row, image=swatch, text="").pack(side="left", padx=4, pady=6)
                    ctk.CTkLabel(combo_row, text=hex_color, font=("Courier", 10),
                                 text_color="#A090C0").pack(side="left", padx=2)

        # Export button
        ctk.CTkButton(
            self.content_frame, text="📄  Export Report (txt)",
            command=lambda: self._export_report(r),
            width=220, height=40, font=("Helvetica", 13),
            fg_color="#2A4A4A", hover_color="#3A6A6A"
        ).pack(pady=14, anchor="w")

    def _export_report(self, r):
        name = self.user_name or "user"
        filename = f"{name}_{r['season_name'].replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt")],
            initialfile=filename,
            title="Save Report"
        )
        if not path:
            return

        lines = [
            "=" * 50,
            "PERSONAL COLOR ANALYSIS REPORT",
            "=" * 50,
            f"Name:          {self.user_name}",
            f"Date:          {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"Season:        {r['season_name']}",
            f"Base season:   {r['season']}",
            f"Tone type:     {r['tone']}",
            f"Match score:   {r['score']}",
            "",
            "DESCRIPTION:",
            r["description"],
            "",
            "TOP 3 MATCHES:",
        ]
        for s, sc in r["top3"]:
            lines.append(f"  {s}  ({sc} pts)")

        lines += ["", "YOUR QUESTIONNAIRE ANSWERS:"]
        for k, v in self.answers.items():
            lines.append(f"  {k}: {v}")

        if self.wrist_data:
            lines += ["", "WRIST PHOTO ANALYSIS:"]
            for k, v in self.wrist_data.items():
                lines.append(f"  {k}: {v}")

        lines += ["", "YOUR COLOR PALETTE:"]
        lines.append("  " + "  ".join(r["best_colors"]))

        combos = get_color_combinations(r["season_name"])
        if combos:
            lines += ["", "SUGGESTED OUTFIT COMBINATIONS:"]
            for i, combo in enumerate(combos):
                lines.append(f"  Look {i+1}: {' + '.join(combo)}")

        lines += ["", "=" * 50]

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        messagebox.showinfo("Saved!", f"Report saved to:\n{path}")

    # ── SCREEN: HISTORY ──────────────────────────────────────────────

    def show_history(self):
        self._clear()
        self._title("Past Analyses")
        self._subtitle("All previously saved color analyses, newest first.")

        rows = load_all_analyses()

        if not rows:
            ctk.CTkLabel(self.content_frame, text="No analyses saved yet.",
                         font=("Helvetica", 14), text_color="#5050A0").pack(pady=40)
            return

        scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent", height=500)
        scroll.pack(fill="both", expand=True)

        # Columns: id, name, season_name, season_base, score, answers, wrist_data, date_time
        for row in rows:
            (rid, name, season_name, season_base, score, answers_json,
             wrist_json, date_time) = row

            card = ctk.CTkFrame(scroll, fg_color="#1A1A30", corner_radius=10)
            card.pack(fill="x", pady=6, padx=4)

            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=12, pady=(10, 4))

            ctk.CTkLabel(header, text=name, font=("Helvetica", 14, "bold"),
                         text_color="#D0B0FF").pack(side="left")
            ctk.CTkLabel(header, text=date_time, font=("Helvetica", 11),
                         text_color="#5050A0").pack(side="right")

            ctk.CTkLabel(card, text=f"{season_name}  •  {season_base}  •  Score: {score}",
                         font=("Helvetica", 12), text_color="#A090C0").pack(anchor="w", padx=12)

            # Show palette swatches for this result
            if season_name in SEASON_INFO:
                colors = SEASON_INFO[season_name]["best_colors"][:8]
                swatch_row = ctk.CTkFrame(card, fg_color="transparent")
                swatch_row.pack(anchor="w", padx=12, pady=(4, 10))

                for hx in colors:
                    sw = make_swatch(hx, size=(32, 32))
                    self._images.append(sw)
                    ctk.CTkLabel(swatch_row, image=sw, text="").pack(side="left", padx=2)

    # ── SCREEN: ALL PALETTES ─────────────────────────────────────────

    def show_all_palettes(self):
        self._clear()
        self._title("All 16 Seasonal Palettes")
        self._subtitle("Browse every seasonal type and its color palette.")

        scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent", height=540)
        scroll.pack(fill="both", expand=True)

        season_groups = {
            "🌸 Spring": ["True Spring", "Light Spring", "Bright Spring", "Warm Spring"],
            "☁️ Summer": ["True Summer", "Light Summer", "Soft Summer", "Cool Summer"],
            "🍂 Autumn": ["True Autumn", "Deep Autumn", "Soft Autumn", "Warm Autumn"],
            "❄️ Winter": ["True Winter", "Deep Winter", "Bright Winter", "Cool Winter"],
        }

        for group_name, season_list in season_groups.items():
            ctk.CTkLabel(scroll, text=group_name, font=("Georgia", 16, "bold"),
                         text_color="#C8A4FF").pack(anchor="w", pady=(16, 4))

            for sname in season_list:
                info = SEASON_INFO[sname]

                card = ctk.CTkFrame(scroll, fg_color="#1A1A30", corner_radius=10)
                card.pack(fill="x", pady=4, padx=2)

                ctk.CTkLabel(card, text=sname, font=("Helvetica", 13, "bold"),
                             text_color="#D0C0F0").pack(anchor="w", padx=14, pady=(10, 2))
                ctk.CTkLabel(card, text=info["description"], font=("Helvetica", 11),
                             text_color="#8080A0", wraplength=600, justify="left").pack(anchor="w", padx=14)

                swatch_row = ctk.CTkFrame(card, fg_color="transparent")
                swatch_row.pack(anchor="w", padx=12, pady=(6, 10))

                for hx in info["best_colors"]:
                    sw = make_swatch(hx, size=(30, 30))
                    self._images.append(sw)
                    ctk.CTkLabel(swatch_row, image=sw, text="").pack(side="left", padx=2)


# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = PersonalColorApp()
    app.mainloop()
