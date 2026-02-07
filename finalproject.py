import os
import logging
import requests
import pyttsx3
import tkinter as tk
from tkinter import scrolledtext, filedialog
from PIL import Image, ImageTk
import threading
import time
import psutil
import wikipedia
import speech_recognition as sr
import pywhatkit
import webbrowser
import subprocess
from typing import List, Tuple, Optional
from dotenv import load_dotenv
import plyer
from pathlib import Path
import random
import json
# ===================================================================== load questions from file
with open("questions.json", "r", encoding="utf-8") as questions_file:
    questions = json.load(questions_file)
try:
    import GPUtil
except ImportError:
    GPUtil = None
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
# =========================================== Voice 
engine = pyttsx3.init()
engine.setProperty("rate", 150)
engine.setProperty("volume", 0.9)
# =========================================Mute button
is_muted = False
def speak(text: str):
    global is_muted
    if is_muted:
        logging.info(f"[MUTED]: {text}")
        return
    logging.info(f"[Assistant]: {text}")
    engine.say(text)
    engine.runAndWait()
def toggle_mute():
    global is_muted
    is_muted = not is_muted
    mute_btn.config(
        text="🔇 Muted" if is_muted else "🔊 Unmute",
        bg="#ef4444" if is_muted else "#22c55e"
    )
    speak("Voice " + ("muted" if is_muted else "unmuted"))
# ===================================================================== API keys     
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY") or "YOUR_OPENWEATHER_KEY"
def ask_perplexity(q: str) -> str:
    if "YOUR_NEW_KEY_HERE" in str(PERPLEXITY_API_KEY) or not PERPLEXITY_API_KEY:
        return "Set PERPLEXITY_API_KEY in .env."
    try:
        r = requests.post(
            "https://api.perplexity.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "sonar",  # replace with valid model for your key
                "messages": [{"role": "user", "content": q}],
                "stream": True,
                "web_search_options": {"searchtype": "auto"},
            },
            timeout=15,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logging.error(e)
        return "Perplexity API error."
def get_weather(current_city="Delhi") -> str:  # Default to Delhi for India
    if "YOUR_OPENWEATHER_KEY" in WEATHER_API_KEY:
        return "Weather unavailable"
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={current_city}&appid={WEATHER_API_KEY}&units=metric"
        d = requests.get(url, timeout=10).json()
        return f"{d['main']['temp']}°C, {d['weather'][0]['description']}"
    except Exception as e:
        logging.error(e)
        return "Weather unavailable"
def recognize_speech(timeout=5) -> str:
    r = sr.Recognizer()
    try:
        with sr.Microphone() as src:
            r.adjust_for_ambient_noise(src, duration=0.3)
            audio = r.listen(src, timeout=timeout, phrase_time_limit=8)
            return r.recognize_google(audio, language="en-IN").lower()
    except Exception as e:
        logging.error(e)
        return ""
# =============================================================== App open / close 
def open_app(name: str):
    urls = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "spotify": "https://open.spotify.com",
        "chrome": "https://www.google.com/chrome/",
    }
    if name == "chrome":
        target = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        try:
            subprocess.Popen(target, shell=True)
            speak("Opening Chrome")
        except Exception as e:
            logging.error(e)
            speak("Failed to open Chrome")
        return
    url = urls.get(name)
    if not url:
        speak(f"Cannot open {name}")
        return
    try:
        webbrowser.open(url)
        speak(f"Opening {name}")
    except Exception as e:
        logging.error(e)
        speak(f"Failed to open {name}")
import shutil
def close_app(name: str):
    """
       Try to close the default browser and Spotify reliably on Windows."""
    browser_exes = ["chrome.exe", "msedge.exe", "brave.exe", "firefox.exe"]
    if name in ("google", "youtube"):
        for exe in browser_exes:
            try:
                subprocess.run(
                    f'taskkill /F /T /IM "{exe}"',
                    shell=True,
                    capture_output=True,
                    text=True
                )
            except Exception as e:
                logging.error(e)
        speak(f"Close the tabs manually (if running).")
        return
    if name == "spotify":
        exe = "Spotify.exe"
    elif name == "chrome":
        exe = "chrome.exe"
    else:
        speak(f"Cannot close {name}")
        return
    try:
        result = subprocess.run(
            f'taskkill /F /T /IM "{exe}"',
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            speak(f"Closed {name}")
        else:
            logging.error(result.stderr)
            speak(f"{name} is not running.")
    except Exception as e:
        logging.error(e)
        speak(f"Close the tabs manually (if running).")
# =============================================================== Reminders     
reminders: List[Tuple[float, str]] = []
def parse_time(part: str) -> Optional[int]:
    try:
        num = int(part.split()[-2])
        if "minute" in part:
            return num * 60
        if "second" in part:
            return num
        if "hour" in part:
            return num * 3600
    except Exception:
        return None
def set_reminder(cmd: str):
    if "remind me to" in cmd and "in" in cmd:
        task = cmd.split("remind me to")[1].split("in")[0].strip()
        tpart = cmd.split("in")[1].strip()
        sec = parse_time(tpart)
        if sec:
            reminders.append((time.time() + sec, task))
            speak(f"Reminder set for {task}")
        else:
            speak("Say time in seconds, minutes, or hours.")
def check_reminders():
    while True:
        now = time.time()
        for r in reminders[:]:
            if now >= r[0]:
                speak(f"Reminder: {r[1]}")
                plyer.notification.notify(title="Reminder", message=r[1], timeout=5)
                reminders.remove(r)
        time.sleep(1)
# =============================================================== System info 
def get_battery() -> str:
    try:
        b = psutil.sensors_battery()
        if b:
            return f"{b.percent:.0f}%{' ⚡' if b.power_plugged else ''}"
        return "N/A"
    except Exception as e:
        logging.error(e)
        return "N/A"
def get_cpu_ram_disk_text() -> str:
    vm = psutil.virtual_memory()
    cpu = psutil.cpu_percent()
    ram_pct = vm.percent
    disk = psutil.disk_usage("/").percent
    return f"🧠 CPU: {cpu:.1f}%   |   💾 RAM: {ram_pct:.1f}%   |   💽 Disk: {disk:.1f}%"
# =============================================================== Theme system 
THEMES = {
    "dark": {
        "bg": "#000000",
        "fg": "#00ffcc",
        "panel": "#000000",
        "button": "#1f2937",
        "button_fg": "#e5e7eb",
        "accent": "#22c55e",
        "status": "#00ffff",
    },
    "light": {
        "bg": "#f5f5f5",
        "fg": "#111827",
        "panel": "#ffffff",
        "button": "#e5e7eb",
        "button_fg": "#111827",
        "accent": "#16a34a",
        "status": "#0ea5e9",
    },
}
current_theme = "dark"
def apply_theme(theme_name: str, root, widgets: list[tk.Widget],
                status_widgets: list[tk.Label]):
    global current_theme
    current_theme = theme_name
    t = THEMES[theme_name]
    root.configure(bg=t["bg"])
    for w in widgets:
        try:
            if isinstance(w, tk.Button):
                w.configure(bg=t["button"], fg=t["button_fg"],
                            activebackground=t["button"])
            elif isinstance(w, (tk.Frame, tk.Label, scrolledtext.ScrolledText)):
                w.configure(bg=t["panel"])
                if "fg" in w.configure():
                    w.configure(fg=t["fg"])
        except Exception as e:
            logging.error(f"Theme apply error: {e}")
    for lbl in status_widgets:
        try:
            lbl.configure(bg=t["panel"], fg=t["status"])
        except Exception as e:
            logging.error(f"Status theme error: {e}")
# =============================================================== typewriter helper 
def typewriter_insert(widget: scrolledtext.ScrolledText, text: str, prefix: str = "Assistant: "):
    widget.config(state=tk.NORMAL)
    widget.insert(tk.END, prefix)
    widget.config(state=tk.DISABLED)
    def writer(i=0):
        if i >= len(text):
            widget.config(state=tk.NORMAL)
            widget.insert(tk.END, "\n")
            widget.see(tk.END)
            widget.config(state=tk.DISABLED)
            return
        widget.config(state=tk.NORMAL)
        widget.insert(tk.END, text[i])
        widget.see(tk.END)
        widget.config(state=tk.DISABLED)
        widget.after(15, writer, i + 1)
    writer()
# =============================================================== Command handler 
def handle_command(cmd: str, box: scrolledtext.ScrolledText):
    if not cmd:
        return
    box.config(state=tk.NORMAL)
    box.insert(tk.END, f"You: {cmd}\n")
    box.see(tk.END)
    box.config(state=tk.DISABLED)
    c = cmd.lower()
    if "remind" in c:
        set_reminder(c)
    elif "joke" in c:
        reply = "Why did the programmer quit? Because he didn't get arrays of pay!"
        speak(reply)
        typewriter_insert(box, reply)
    elif "weather" in c:
        ans = get_weather()
        speak(ans)
        typewriter_insert(box, ans)
    elif "battery" in c:
        ans = get_battery()
        speak(ans)
        typewriter_insert(box, ans)
    elif "open " in c:
        open_app(c.split("open ")[1].split()[0])
    elif "close " in c:
        close_app(c.split("close ")[1].split()[0])
    elif "mute" in c:
        toggle_mute()
    else:
        print("User command:", repr(c))
        print("Available keys:", list(questions.keys()))
        if c in questions:
            print("Matched in JSON")
            ans = questions[c]
        else:
            print("Not in JSON, calling API")
            ans = ask_perplexity(c)
        # -=========-----------===============-----------------------====-- JSON first, then API fallback --------
        if c in questions:
            ans = questions[c]
        else:
            ans = ask_perplexity(c)
        speak(ans[:120])
        typewriter_insert(box, ans)
# -------------------------------------------------------------------------------------- GUI
def run_gui():
    global current_theme, mute_btn

    root = tk.Tk()
    root.title("Lock Assistant Pro")
    root.geometry("1200x720")
    root.configure(bg="#000000")

    # --------------------------------------------------------------------------------------desktop-style wallpaper from Pictures
    wallpaper_label = tk.Label(root)
    wallpaper_label.place(x=0, y=0, relwidth=1, relheight=1)

    def pick_pictures_wallpaper() -> Optional[Path]:
        pics = Path.home() / "Pictures"
        candidates = []
        for ext in ("*.jpg", "*.jpeg", "*.png", "*.bmp"):
            candidates.extend(pics.glob(ext))
        return candidates[0] if candidates else None
    def set_wallpaper(path: Path | None):
        if not path:
            return
        try:
            img = Image.open(path)
            w, h = root.winfo_screenwidth(), root.winfo_screenheight()
            img = img.resize((w, h), Image.LANCZOS)
            root.wallpaper_image = ImageTk.PhotoImage(img)
            wallpaper_label.configure(image=root.wallpaper_image)
        except Exception as e:
            logging.error(f"Wallpaper error: {e}")
    set_wallpaper(pick_pictures_wallpaper())
    overlay = tk.Frame(root, bg="#000000")
    overlay.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.98, relheight=0.96)
    # --------------------------------------------------------------------------------------header
    header = tk.Frame(overlay, bg="#000000")
    header.pack(fill=tk.X, pady=(8, 2))
    title = tk.Label(header, text="🤖 Lock Assistant Pro",
                     font=("Arial", 22, "bold"), bg="#000000", fg="#22c55e")
    title.pack(anchor="w")
    subtitle = tk.Label(header,
                        text="Voice AI · App Control · System Monitor · Wallpapers",
                        font=("Arial", 10), bg="#000000", fg="#9ca3af")
    subtitle.pack(anchor="w")
    # --------------------------------------------------------------------------------------command panel
    hints_frame = tk.Frame(overlay, bg="#000000")
    hints_visible = tk.BooleanVar(value=True)

    hints_label = tk.Label(
        hints_frame,
        text="Tips:  \"open youtube\" · \"set reminder\" · \"battery\" · \"weather\" · \"play song name\" · \"mute\"",
        font=("Arial", 9),
        bg="#000000",
        fg="#00ffcc"
    )
    hints_label.pack(anchor="w", padx=4)
    hints_frame.pack(fill=tk.X, pady=(0, 4))

    # --------------------------------------------------------------------------------------toggle_hints
    hints_btn = None
    def toggle_hints():
        nonlocal hints_btn
        if hints_visible.get():
            hints_frame.forget()
            hints_visible.set(False)
            hints_btn.config(text="Show Tips")
        else:
            hints_frame.pack(fill=tk.X, pady=(0, 4))
            hints_visible.set(True)
            hints_btn.config(text="Hide Tips")

    # --------------------------------------------------------------------------------------chat
    chat = scrolledtext.ScrolledText(
        overlay, height=12, bg="#000000", fg="#00ffcc",
        font=("Consolas", 10), relief="flat",
        insertbackground="#22c55e", highlightthickness=1,
        highlightbackground="#00ffcc"
    )
    chat.pack(fill=tk.BOTH, expand=True, pady=(4, 6))

    # --------------------------------------------------------------------------------------input row
    input_row = tk.Frame(overlay, bg="#000000")
    input_row.pack(fill=tk.X, pady=(0, 8))

    entry = tk.Entry(input_row, font=("Arial", 11),
                     bg="#111111", fg="#e5e7eb",
                     insertbackground="#22c55e", relief="flat")
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8), ipady=4)

    def submit():
        txt = entry.get().strip()
        if txt:
            threading.Thread(target=lambda: handle_command(txt, chat), daemon=True).start()
            entry.delete(0, tk.END)
    entry.bind("<Return>", lambda e: submit())
    btn_style = {"font": ("Arial", 10, "bold"), "relief": "flat", "bd": 0}

    def voice_cmd():
        def listen():
            text = recognize_speech()
            if not text:
                speak("I did not catch that. Please try again.")
                return
            handle_command(text, chat)
        threading.Thread(target=listen, daemon=True).start()
    voice_btn = tk.Button(input_row, text="🎙 Voice", command=voice_cmd,
                          bg="#2563eb", fg="white", width=10, **btn_style)
    voice_btn.pack(side=tk.LEFT, padx=2)
    send_btn = tk.Button(input_row, text="Send", command=submit,
                         bg="#22c55e", fg="#020617", width=10, **btn_style)
    send_btn.pack(side=tk.LEFT, padx=2)

    # --------------------------------------------------------------------------------------mute button
    mute_btn = tk.Button(input_row, text="🔊 Unmute", command=toggle_mute,
                         bg="#22c55e", fg="#020617", width=10, **btn_style)
    mute_btn.pack(side=tk.LEFT, padx=2)

    # --------------------------------------------------------------------------------------app buttons
    apps_frame = tk.Frame(overlay, bg="#000000")
    apps_frame.pack(pady=(0, 4))

    open_buttons = []
    close_buttons = []

    for i, name in enumerate(["google", "youtube", "spotify", "chrome"]):
        b = tk.Button(apps_frame, text=name.title(),
                      command=lambda n=name: open_app(n),
                      bg="#1f2937", fg="#e5e7eb", width=15, **btn_style)
        b.grid(row=0, column=i, padx=4, pady=2)
        open_buttons.append(b)

    for i, name in enumerate(["google", "youtube", "spotify", "chrome"]):
        b = tk.Button(apps_frame, text=f"Close {name.title()}",
                      command=lambda n=name: close_app(n),
                      bg="#b91c1c", fg="#f9fafb", width=15, **btn_style)
        b.grid(row=1, column=i, padx=4, pady=2)
        close_buttons.append(b)

    # --------------------------------------------------------------------------------------profile preset buttons
    presets_frame = tk.Frame(overlay, bg="#000000")
    presets_frame.pack(pady=(2, 6))
    all_widgets_init = []
    status_widgets_init = []

    def apply_preset(mode: str):
        if mode == "study":
            subtitle.config(text="Study Mode · Focus on docs and coding")
            apply_theme("dark", root, all_widgets_init, status_widgets_init)
        elif mode == "gaming":
            subtitle.config(text="Gaming Mode · Quick access to YouTube and Spotify")
            apply_theme("dark", root, all_widgets_init, status_widgets_init)
            title.config(fg="#ff4b81")
        elif mode == "work":
            subtitle.config(text="Work Mode · Google · Docs · Meetings")
            apply_theme("light", root, all_widgets_init, status_widgets_init)

    study_btn = tk.Button(presets_frame, text="Study Mode",
                          command=lambda: apply_preset("study"),
                          bg="#1f2937", fg="#e5e7eb", width=10, **btn_style)
    study_btn.pack(side=tk.LEFT, padx=3)

    gaming_btn = tk.Button(presets_frame, text="Gaming Mode",
                           command=lambda: apply_preset("gaming"),
                           bg="#1f2937", fg="#e5e7eb", width=12, **btn_style)
    gaming_btn.pack(side=tk.LEFT, padx=3)

    work_btn = tk.Button(presets_frame, text="Work Mode",
                         command=lambda: apply_preset("work"),
                         bg="#1f2937", fg="#e5e7eb", width=10, **btn_style)
    work_btn.pack(side=tk.LEFT, padx=3)

    # compact status block
    status_block = tk.Frame(overlay, bg="#000000")
    status_block.pack(pady=(4, 8))

    time_lbl = tk.Label(status_block, bg="#000000", fg="#00ffff",
                        font=("Arial", 12, "bold"))
    time_lbl.pack()

    weather_lbl = tk.Label(status_block, bg="#000000", fg="#00ffff",
                           font=("Arial", 11))
    weather_lbl.pack()

    sys_lbl = tk.Label(status_block, bg="#000000", fg="#00ffff",
                       font=("Arial", 11))
    sys_lbl.pack()

    def update_status():
        while True:
            time_lbl.config(text=f"🕒 {time.strftime('%H:%M:%S')}   🔋 {get_battery()}")
            weather_lbl.config(text=f"☁ {get_weather()}")
            sys_lbl.config(text=get_cpu_ram_disk_text())
            time.sleep(2)

    threading.Thread(target=update_status, daemon=True).start()

    # --------------------------------------------------------------------------------------mini music control
    music_frame = tk.Frame(overlay, bg="#000000")
    music_frame.pack(fill=tk.X, pady=(0, 6))

    song_entry = tk.Entry(music_frame, font=("Arial", 10),
                          bg="#111111", fg="#e5e7eb",
                          insertbackground="#22c55e", relief="flat")
    song_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6), ipady=2)

    def play_song():
        song = song_entry.get().strip()
        if not song:
            speak("Please type a song name.")
            return
        try:
            pywhatkit.playonyt(song)
            speak(f"Playing {song} on YouTube.")
        except Exception as e:
            logging.error(e)
            speak("Could not play song.")

    def stop_music():
        close_app("chrome")  
        speak("Stopped music.")

    play_btn = tk.Button(music_frame, text="Play Song",
                         command=play_song,
                         bg="#22c55e", fg="#020617", width=10, **btn_style)
    play_btn.pack(side=tk.LEFT, padx=3)

    stop_btn = tk.Button(music_frame, text="Stop Music",
                         command=stop_music,
                         bg="#b91c1c", fg="#f9fafb", width=10, **btn_style)
    stop_btn.pack(side=tk.LEFT, padx=3)

    # -------------------------------------------------------------------------------------bottom controls
    controls = tk.Frame(overlay, bg="#000000")
    controls.pack(fill=tk.X, pady=(0, 6))

    def next_wp():
        set_wallpaper(pick_pictures_wallpaper())

    def add_wp():
        path = filedialog.askopenfilename(
            title="Select Wallpaper",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        if path:
            set_wallpaper(Path(path))

    next_btn = tk.Button(controls, text="Next Wallpaper", command=next_wp,
                         bg="#374151", fg="#e5e7eb", width=16, **btn_style)
    next_btn.pack(side=tk.LEFT, padx=4)
    add_btn = tk.Button(controls, text="Add Wallpaper", command=add_wp,
                        bg="#f59e0b", fg="#111827", width=16, **btn_style)
    add_btn.pack(side=tk.LEFT, padx=4)

    exit_btn = tk.Button(controls, text="Exit", command=root.destroy,
                         bg="#ef4444", fg="#f9fafb", width=10, **btn_style)
    exit_btn.pack(side=tk.RIGHT, padx=4)

    # --------------------------------------------------------------------------------------theme toggle
    def toggle_theme():
        new_theme = "light" if current_theme == "dark" else "dark"
        all_widgets = [
            overlay, header, title, subtitle,
            hints_frame, hints_label,
            chat, input_row, entry,
            apps_frame, status_block,
            music_frame,
            presets_frame,
            controls,
            voice_btn, send_btn, mute_btn,
            *open_buttons, *close_buttons,
            study_btn, gaming_btn, work_btn,
            play_btn, stop_btn,
            next_btn, add_btn, exit_btn,
            toggle_btn, hints_btn,
        ]
        status_widgets = [time_lbl, weather_lbl, sys_lbl]
        apply_theme(new_theme, root, all_widgets, status_widgets)

    toggle_btn = tk.Button(controls, text="Toggle Theme",
                           command=toggle_theme,
                           bg="#6b7280", fg="#e5e7eb", width=12, **btn_style)
    # -----------------------------------------------------------------------Now assign the actual button to hints_btn
    hints_btn = tk.Button(controls, text="Hide Tips",
                          command=toggle_hints,
                          bg="#1f2937", fg="#e5e7eb", width=10, **btn_style)
    hints_btn.pack(side=tk.RIGHT, padx=4)
    hints_btn = tk.Button(controls, text="Hide Tips",
                          command=toggle_hints,
                          bg="#1f2937", fg="#e5e7eb", width=10, **btn_style)
    hints_btn.pack(side=tk.RIGHT, padx=4)

    # -------------------------------------------------------------------------------------initial theme
    all_widgets_init = [
        overlay, header, title, subtitle,
        hints_frame, hints_label,
        chat, input_row, entry,
        apps_frame, status_block,
        music_frame,
        presets_frame,
        controls,
        voice_btn, send_btn, mute_btn,
        *open_buttons, *close_buttons,
        study_btn, gaming_btn, work_btn,
        play_btn, stop_btn,
        next_btn, add_btn, exit_btn,
        toggle_btn, hints_btn,
    ]
    status_widgets_init = [time_lbl, weather_lbl, sys_lbl]
    apply_theme("dark", root, all_widgets_init, status_widgets_init)

    threading.Thread(target=check_reminders, daemon=True).start()

    #-----------------------------------------------------------------------------------welcome line
    welcomes = [
        "Lock Assistant loaded. Ready for work, Ayush.",
        "Welcome back, Ayush. Time to ship some code.",
        "Systems online. What are we doing today?",
        "Assistant ready. DSA, projects, or gaming?"
    ]
    msg = random.choice(welcomes)
    typewriter_insert(chat, msg)

    root.mainloop()


#---------------------------------------------------------------------------------------------------Main



if __name__ == "__main__":
    speak("Lock Assistant is starting.")
    try:
        run_gui()
    finally:
        speak("  Goodbye..")
    