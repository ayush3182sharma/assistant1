import speech_recognition as sr
import pyttsx3
import subprocess
import webbrowser
import os
import psutil
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import threading
import time
import requests
import itertools
import random
import logging
from typing import List, Tuple, Optional
import datetime
import pywhatkit
import wikipedia

# Logging Setup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# Voice Engine

class VoiceAssistant:
    def __init__(self, rate: int = 150, volume: float = 1.0, voice_index: int = 2):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)
        voices = self.engine.getProperty('voices')
        if len(voices) > voice_index:
            self.engine.setProperty('voice', voices[voice_index].id)

    def speak(self, text: str):
        logging.info(f"[Assistant]: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

voice = VoiceAssistant()


# Speech Recognition

def recognize_speech_from_mic(timeout: int = 5, phrase_time_limit: int = 8) -> str:
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            return recognizer.recognize_google(audio, language="en-IN").lower()
        except sr.UnknownValueError:
            voice.speak("Sorry, I couldn't understand.")
        except sr.RequestError:
            voice.speak("Recognition service failed.")
        except Exception as e:
            voice.speak("Microphone error.")
            logging.error(e)
    return ""


# Application Commands

APP_PATHS = {
    "spotify": "spotify.exe",
    "calculator": "Calculator.exe",
    "chrome": "chrome.exe"
}

def open_application(command: str):
    # Common websites
    sites = {
        "google": "http://www.google.com",
        "youtube": "http://www.youtube.com",
        "facebook": "http://www.facebook.com",
        "twitter": "http://www.twitter.com",
        "instagram": "http://www.instagram.com",
        "gmail": "http://mail.google.com",
        "reddit": "http://www.reddit.com",
        "github": "http://www.github.com",
        "stackoverflow": "http://stackoverflow.com",
        "linkedin": "http://www.linkedin.com",
        "amazon": "http://www.amazon.com",
        "flipkart": "http://www.flipkart.com",
        "netflix": "http://www.netflix.com",
        "hotstar": "http://www.hotstar.com",
        "wikipedia": "http://www.wikipedia.org",
        "quora": "http://www.quora.com",
        "whatsapp web": "https://web.whatsapp.com",
        "zoom": "https://zoom.us",
        "discord": "https://discord.com",
        "telegram": "https://web.telegram.org",
        "bing": "https://www.bing.com",
        "office": "https://www.office.com",
        "drive": "https://drive.google.com",
        "maps": "https://maps.google.com",
        "canva": "https://www.canva.com",
        "dropbox": "https://www.dropbox.com",
        "spotify web": "https://open.spotify.com",
        "prime video": "https://www.primevideo.com",
        "coursera": "https://www.coursera.org",
        "udemy": "https://www.udemy.com",
        "khan academy": "https://www.khanacademy.org",
        "codepen": "https://codepen.io",
        "leetcode": "https://leetcode.com",
        "hackerrank": "https://www.hackerrank.com",
        "medium": "https://medium.com",
        "news": "https://news.google.com",
        "weather": "https://weather.com",
        "irctc": "https://www.irctc.co.in",
        "railway": "https://www.indianrail.gov.in",
        "paytm": "https://paytm.com",
        "phonepe": "https://www.phonepe.com",
        "swiggy": "https://www.swiggy.com",
        "zomato": "https://www.zomato.com",
        "ola": "https://www.olacabs.com",
        "uber": "https://www.uber.com",
        "airbnb": "https://www.airbnb.com",
        "flipboard": "https://flipboard.com",
        "pinterest": "https://www.pinterest.com",
        "tumblr": "https://www.tumblr.com",
        "snapchat": "https://www.snapchat.com",
        "messenger": "https://www.messenger.com",
        "skype": "https://web.skype.com",
        "teams": "https://teams.microsoft.com",
        "meet": "https://meet.google.com",
        "classroom": "https://classroom.google.com",
        "drive": "https://drive.google.com",
        "calendar": "https://calendar.google.com",
        "notion": "https://www.notion.so",
        "todoist": "https://todoist.com",
        "trello": "https://trello.com",
        "asana": "https://asana.com",
        "slack": "https://slack.com",
        "microsoft": "https://www.microsoft.com",
        "apple": "https://www.apple.com",
        "yahoo": "https://www.yahoo.com",
        "duckduckgo": "https://duckduckgo.com",
        "bbc": "https://www.bbc.com",
        "cnn": "https://www.cnn.com",
        "ndtv": "https://www.ndtv.com",
        "times of india": "https://timesofindia.indiatimes.com",
        "espn": "https://www.espn.com",
        "cricbuzz": "https://www.cricbuzz.com",
        "cricinfo": "https://www.espncricinfo.com",
        "fifa": "https://www.fifa.com",
        "nba": "https://www.nba.com",
        "icc": "https://www.icc-cricket.com",
        "steam": "https://store.steampowered.com",
        "epic games": "https://www.epicgames.com",
        "origin": "https://www.origin.com",
        "gog": "https://www.gog.com",
        "itch": "https://itch.io",
        "roblox": "https://www.roblox.com",
        "minecraft": "https://www.minecraft.net",
        "unity": "https://unity.com",
        "unreal engine": "https://www.unrealengine.com",
        "adobe": "https://www.adobe.com",
        "photoshop": "https://www.adobe.com/products/photoshop.html",
        "illustrator": "https://www.adobe.com/products/illustrator.html",
        "xd": "https://www.adobe.com/products/xd.html",
        "figma": "https://www.figma.com",
        "github desktop": "https://desktop.github.com",
        "gitlab": "https://gitlab.com",
        "bitbucket": "https://bitbucket.org",
        "heroku": "https://www.heroku.com",
        "vercel": "https://vercel.com",
        "netlify": "https://www.netlify.com",
        "firebase": "https://firebase.google.com",
        "aws": "https://aws.amazon.com",
        "azure": "https://azure.microsoft.com",
        "gcp": "https://cloud.google.com",
        "digitalocean": "https://www.digitalocean.com",
        "vultr": "https://www.vultr.com",
        "linode": "https://www.linode.com",
        "python docs": "https://docs.python.org/3/",
        "java docs": "https://docs.oracle.com/en/java/",
        "nodejs docs": "https://nodejs.org/en/docs/",
        "react docs": "https://react.dev/",
        "angular docs": "https://angular.io/docs",
        "vue docs": "https://vuejs.org/v2/guide/",
        "flutter docs": "https://docs.flutter.dev/",
        "dart docs": "https://dart.dev/guides",
        "c++ docs": "https://en.cppreference.com/w/",
        "c# docs": "https://docs.microsoft.com/en-us/dotnet/csharp/",
        "go docs": "https://golang.org/doc/",
        "rust docs": "https://doc.rust-lang.org/",
        "php docs": "https://www.php.net/docs.php",
        "mysql docs": "https://dev.mysql.com/doc/",
        "postgres docs": "https://www.postgresql.org/docs/",
        "mongodb docs": "https://docs.mongodb.com/",
        "sqlite docs": "https://www.sqlite.org/docs.html",
        "docker docs": "https://docs.docker.com/",
        "kubernetes docs": "https://kubernetes.io/docs/",
        "tensorflow docs": "https://www.tensorflow.org/learn",
        "pytorch docs": "https://pytorch.org/docs/stable/index.html",
        "opencv docs": "https://docs.opencv.org/",
        "matplotlib docs": "https://matplotlib.org/stable/contents.html",
        "numpy docs": "https://numpy.org/doc/",
        "pandas docs": "https://pandas.pydata.org/docs/",
        "scikit-learn docs": "https://scikit-learn.org/stable/documentation.html",
        "jupyter": "https://jupyter.org",
        "colab": "https://colab.research.google.com",
        "kaggle": "https://www.kaggle.com",
        "google scholar": "https://scholar.google.com",
        "arxiv": "https://arxiv.org",
        "springer": "https://link.springer.com",
        "ieee": "https://ieeexplore.ieee.org",
        "acm": "https://dl.acm.org",
        "elsevier": "https://www.elsevier.com",
        "sciencedirect": "https://www.sciencedirect.com",
        "nature": "https://www.nature.com",
        "wiley": "https://www.wiley.com",
        "sage": "https://journals.sagepub.com",
        "pubmed": "https://pubmed.ncbi.nlm.nih.gov",
        "github gists": "https://gist.github.com",
        "pastebin": "https://pastebin.com",
        "replit": "https://replit.com",
        "glitch": "https://glitch.com",
        "jsfiddle": "https://jsfiddle.net",
        "codesandbox": "https://codesandbox.io",
        "codewars": "https://www.codewars.com",
        "edx": "https://www.edx.org",
        "pluralsight": "https://www.pluralsight.com",
        "udacity": "https://www.udacity.com",
        "datacamp": "https://www.datacamp.com",
        "brilliant": "https://brilliant.org",
        "sololearn": "https://www.sololearn.com",
        "geeksforgeeks": "https://www.geeksforgeeks.org",
        "tutorialspoint": "https://www.tutorialspoint.com",
        "w3schools": "https://www.w3schools.com",
        "programiz": "https://www.programiz.com",
        "javatpoint": "https://www.javatpoint.com",
        "freecodecamp": "https://www.freecodecamp.org",
        "hackerearth": "https://www.hackerearth.com",
        "topcoder": "https://www.topcoder.com",
        "codechef": "https://www.codechef.com",
        "atcoder": "https://atcoder.jp",
        "spoj": "https://www.spoj.com",
        "project euler": "https://projecteuler.net",
        "openai": "https://openai.com",
        "chatgpt": "https://chat.openai.com",
        "bard": "https://bard.google.com",
        "gemini": "https://gemini.google.com",
        "copilot": "https://github.com/features/copilot",
        "midjourney": "https://www.midjourney.com",
        "dalle": "https://labs.openai.com",
        "stable diffusion": "https://stablediffusionweb.com",
        "huggingface": "https://huggingface.co",
        "kivy docs": "https://kivy.org/doc/stable/",
        "tkinter docs": "https://docs.python.org/3/library/tkinter.html",
        "pygame docs": "https://www.pygame.org/docs/",
        "selenium docs": "https://www.selenium.dev/documentation/",
        "requests docs": "https://docs.python-requests.org/en/latest/",
        "beautifulsoup docs": "https://www.crummy.com/software/BeautifulSoup/bs4/doc/",
        "flask docs": "https://flask.palletsprojects.com/en/2.0.x/",
        "django docs": "https://docs.djangoproject.com/en/4.0/",
        "fastapi docs": "https://fastapi.tiangolo.com/",
        "plotly docs": "https://plotly.com/python/",
        "seaborn docs": "https://seaborn.pydata.org/",
        "pytest docs": "https://docs.pytest.org/en/7.1.x/",
        "sphinx docs": "https://www.sphinx-doc.org/en/master/",
        "pip docs": "https://pip.pypa.io/en/stable/",
        "conda docs": "https://docs.conda.io/en/latest/",
        "anaconda": "https://www.anaconda.com",
        "miniconda": "https://docs.conda.io/en/latest/miniconda.html",
        "jupyter notebook docs": "https://jupyter-notebook.readthedocs.io/en/stable/",
        "jupyterlab docs": "https://jupyterlab.readthedocs.io/en/stable/",
        "spyder": "https://www.spyder-ide.org",
        "pycharm": "https://www.jetbrains.com/pycharm/",
        "vscode": "https://code.visualstudio.com",
        "sublime text": "https://www.sublimetext.com",
        "atom": "https://atom.io",
        "notepad++": "https://notepad-plus-plus.org",
        "brackets": "http://brackets.io",
        "intellij": "https://www.jetbrains.com/idea/",
        "eclipse": "https://www.eclipse.org",
        "netbeans": "https://netbeans.apache.org",
        "android studio": "https://developer.android.com/studio",
        "xcode": "https://developer.apple.com/xcode/",
        "visual studio": "https://visualstudio.microsoft.com",
        "r studio": "https://posit.co/download/rstudio-desktop/",
        "matlab": "https://www.mathworks.com/products/matlab.html",
        "octave": "https://www.gnu.org/software/octave/",
        "scilab": "https://www.scilab.org",
        "wolfram alpha": "https://www.wolframalpha.com",
        "desmos": "https://www.desmos.com",
        "geogebra": "https://www.geogebra.org",
        "latex": "https://www.latex-project.org",
        "overleaf": "https://www.overleaf.com",
        "sharelatex": "https://www.sharelatex.com",
        "draw.io": "https://app.diagrams.net",
        "lucidchart": "https://www.lucidchart.com",
        "miro": "https://miro.com",
        "figjam": "https://www.figma.com/figjam/",
        "microsoft word": "https://www.office.com/launch/word",
        "microsoft excel": "https://www.office.com/launch/excel",
        "microsoft powerpoint": "https://www.office.com/launch/powerpoint",
        "onenote": "https://www.onenote.com",
        "outlook": "https://outlook.live.com",
        "adobe acrobat": "https://www.adobe.com/acrobat.html",
        "pdfescape": "https://www.pdfescape.com",
        "smallpdf": "https://smallpdf.com",
        "ilovepdf": "https://www.ilovepdf.com",
        "pdf24": "https://tools.pdf24.org/en/",
        "remove.bg": "https://www.remove.bg",
        "tinyjpg": "https://tinyjpg.com",
        "compressjpeg": "https://compressjpeg.com",
        "imgur": "https://imgur.com",
        "unsplash": "https://unsplash.com",
        "pexels": "https://www.pexels.com",
        "pixabay": "https://pixabay.com",
        "giphy": "https://giphy.com",
        "tenor": "https://tenor.com",
        "youtube music": "https://music.youtube.com",
        "soundcloud": "https://soundcloud.com",
        "gaana": "https://gaana.com",
        "wynk": "https://wynk.in",
        "jiosaavn": "https://www.jiosaavn.com",
        "apple music": "https://music.apple.com",
        "amazon music": "https://music.amazon.com",
        "deezer": "https://www.deezer.com",
        "pandora": "https://www.pandora.com",
        "tunein": "https://tunein.com",
        "audible": "https://www.audible.in",
        "goodreads": "https://www.goodreads.com",
        "libgen": "https://libgen.is",
        "archive": "https://archive.org",
        "project gutenberg": "https://www.gutenberg.org",
        "coursera": "https://www.coursera.org",
        "edx": "https://www.edx.org",
        "udemy": "https://www.udemy.com",
        "khan academy": "https://www.khanacademy.org",
        "brilliant": "https://brilliant.org",
        "datacamp": "https://www.datacamp.com",
        "sololearn": "https://www.sololearn.com",
        "geeksforgeeks": "https://www.geeksforgeeks.org",
        "w3schools": "https://www.w3schools.com",
        "tutorialspoint": "https://www.tutorialspoint.com",
        "programiz": "https://www.programiz.com",
        "javatpoint": "https://www.javatpoint.com",
        "freecodecamp": "https://www.freecodecamp.org",
        "hackerearth": "https://www.hackerearth.com",
        "topcoder": "https://www.topcoder.com",
        "codechef": "https://www.codechef.com",
        "atcoder": "https://atcoder.jp",
        "spoj": "https://www.spoj.com",
        "project euler": "https://projecteuler.net",
        "openai": "https://openai.com",
        "chatgpt": "https://chat.openai.com",
        "bard": "https://bard.google.com",
        "gemini": "https://gemini.google.com",
        "copilot": "https://github.com/features/copilot",
        "midjourney": "https://www.midjourney.com",
        "dalle": "https://labs.openai.com",
        "stable diffusion": "https://stablediffusionweb.com",
        "huggingface": "https://huggingface.co",
    }

    # Common Windows apps (add more as needed)
    apps = {
        "calculator": "calc.exe",
        "notepad": "notepad.exe",
        "paint": "mspaint.exe",
        "wordpad": "write.exe",
        "explorer": "explorer.exe",
        "command prompt": "cmd.exe",
        "powershell": "powershell.exe",
        "task manager": "taskmgr.exe",
        "control panel": "control.exe",
        "chrome": "chrome.exe",
        "firefox": "firefox.exe",
        "edge": "msedge.exe",
        "opera": "opera.exe",
        "vlc": "vlc.exe",
        "spotify": "spotify.exe",
        "skype": "skype.exe",
        "teams": "Teams.exe",
        "discord": "Discord.exe",
        "zoom": "Zoom.exe",
        "steam": "steam.exe",
        "outlook": "outlook.exe",
        "word": "WINWORD.EXE",
        "excel": "EXCEL.EXE",
        "powerpoint": "POWERPNT.EXE",
        "onenote": "ONENOTE.EXE",
        "adobe reader": "AcroRd32.exe",
        "photoshop": "Photoshop.exe",
        "illustrator": "Illustrator.exe",
        "xd": "XD.exe",
        "figma": "Figma.exe",
        "github desktop": "GitHubDesktop.exe",
        "pycharm": "pycharm64.exe",
        "vscode": "Code.exe",
        "sublime text": "sublime_text.exe",
        "atom": "atom.exe",
        "notepad++": "notepad++.exe",
        "brackets": "Brackets.exe",
        "intellij": "idea64.exe",
        "eclipse": "eclipse.exe",
        "netbeans": "netbeans.exe",
        "android studio": "studio64.exe",
        "xcode": "Xcode.app",
        "visual studio": "devenv.exe",
        "r studio": "rstudio.exe",
        "matlab": "matlab.exe",
        "octave": "octave.exe",
        "scilab": "scilab.exe",
        "jupyter notebook": "jupyter-notebook.exe",
        "spyder": "spyder.exe",
        "anaconda": "anaconda-navigator.exe",
        "miniconda": "miniconda.exe",
        "winamp": "winamp.exe",
        "itunes": "itunes.exe",
        "audacity": "audacity.exe",
        "obs": "obs64.exe",
        "gimp": "gimp.exe",
        "blender": "blender.exe",
        "unity": "Unity.exe",
        "unreal engine": "UE4Editor.exe",
        "docker": "Docker Desktop.exe",
        "postman": "Postman.exe",
        "putty": "putty.exe",
        "filezilla": "filezilla.exe",
        "winscp": "winscp.exe",
        "virtualbox": "VirtualBox.exe",
        "vmware": "vmware.exe",
        "microsoft store": "WinStore.App.exe",
        "calculator": "calc.exe",
        "calendar": "HxCalendarAppImm.exe",
        "camera": "WindowsCamera.exe",
        "mail": "HxMail.exe",
        "weather": "Microsoft.Msn.Weather.exe",
        "groove music": "Microsoft.ZuneMusic.exe",
        "movies & tv": "Microsoft.ZuneVideo.exe",
        "photos": "Microsoft.Photos.exe",
        "snipping tool": "SnippingTool.exe",
        "sticky notes": "StikyNot.exe",
        "magnifier": "Magnify.exe",
        "wordpad": "write.exe",
        "paint": "mspaint.exe",
        "explorer": "explorer.exe",
        "powershell": "powershell.exe",
        "task manager": "taskmgr.exe",
        "control panel": "control.exe",
    }

    # Open websites
    for site in sites:
        if f"open {site}" in command or f"go to {site}" in command or f"launch {site}" in command:
            webbrowser.open(sites[site])
            voice.speak(f"Opening {site}")
            return

    # Play on YouTube
    if "play" in command and "on youtube" in command:
        song = command.split("play")[1].split("on youtube")[0].strip()
        voice.speak(f"Playing {song} on YouTube")
        pywhatkit.playonyt(song)
        return
    elif "play" in command:
        song = command.replace("play", "").strip()
        voice.speak(f"Playing {song} on YouTube")
        pywhatkit.playonyt(song)
        return

    # Open applications
    for app in apps:
        if f"open {app}" in command or f"launch {app}" in command or f"start {app}" in command:
            try:
                subprocess.Popen([apps[app]])
                voice.speak(f"Opening {app}")
                return
            except Exception as e:
                voice.speak(f"Failed to open {app}.")
                logging.error(e)
                return

    # Fallback to APP_PATHS
    for app, path in APP_PATHS.items():
        if f"open {app}" in command:
            try:
                subprocess.Popen([path])
                voice.speak(f"Opening {app}")
                return
            except Exception as e:
                voice.speak(f"Failed to open {app}.")
                logging.error(e)
                return

    voice.speak("Sorry, I can't open that application or site.")

def close_application(command: str):
    # Close browsers and common apps
    close_map = {
        "chrome": "chrome.exe",
        "firefox": "firefox.exe",
        "edge": "msedge.exe",
        "opera": "opera.exe",
        "vlc": "vlc.exe",
        "spotify": "spotify.exe",
        "skype": "skype.exe",
        "teams": "Teams.exe",
        "discord": "Discord.exe",
        "zoom": "Zoom.exe",
        "steam": "steam.exe",
        "outlook": "outlook.exe",
        "word": "WINWORD.EXE",
        "excel": "EXCEL.EXE",
        "powerpoint": "POWERPNT.EXE",
        "onenote": "ONENOTE.EXE",
        "adobe reader": "AcroRd32.exe",
        "photoshop": "Photoshop.exe",
        "illustrator": "Illustrator.exe",
        "xd": "XD.exe",
        "figma": "Figma.exe",
        "github desktop": "GitHubDesktop.exe",
        "pycharm": "pycharm64.exe",
        "vscode": "Code.exe",
        "sublime text": "sublime_text.exe",
        "atom": "atom.exe",
        "notepad++": "notepad++.exe",
        "brackets": "Brackets.exe",
        "intellij": "idea64.exe",
        "eclipse": "eclipse.exe",
        "netbeans": "netbeans.exe",
        "android studio": "studio64.exe",
        "visual studio": "devenv.exe",
        "r studio": "rstudio.exe",
        "matlab": "matlab.exe",
        "octave": "octave.exe",
        "scilab": "scilab.exe",
        "jupyter notebook": "jupyter-notebook.exe",
        "spyder": "spyder.exe",
        "anaconda": "anaconda-navigator.exe",
        "miniconda": "miniconda.exe",
        "winamp": "winamp.exe",
        "itunes": "itunes.exe",
        "audacity": "audacity.exe",
        "obs": "obs64.exe",
        "gimp": "gimp.exe",
        "blender": "blender.exe",
        "unity": "Unity.exe",
        "unreal engine": "UE4Editor.exe",
        "docker": "Docker Desktop.exe",
        "postman": "Postman.exe",
        "putty": "putty.exe",
        "filezilla": "filezilla.exe",
        "winscp": "winscp.exe",
        "virtualbox": "VirtualBox.exe",
        "vmware": "vmware.exe",
        "microsoft store": "WinStore.App.exe",
        "calculator": "calc.exe",
        "calendar": "HxCalendarAppImm.exe",
        "camera": "WindowsCamera.exe",
        "mail": "HxMail.exe",
        "weather": "Microsoft.Msn.Weather.exe",
        "groove music": "Microsoft.ZuneMusic.exe",
        "movies & tv": "Microsoft.ZuneVideo.exe",
        "photos": "Microsoft.Photos.exe",
        "snipping tool": "SnippingTool.exe",
        "sticky notes": "StikyNot.exe",
        "magnifier": "Magnify.exe",
        "wordpad": "write.exe",
        "paint": "mspaint.exe",
        "explorer": "explorer.exe",
        "powershell": "powershell.exe",
        "task manager": "taskmgr.exe",
        "control panel": "control.exe",
        "notepad": "notepad.exe",
        "command prompt": "cmd.exe",
    }

    found = False
    for app, proc_name in close_map.items():
        if f"close {app}" in command or f"exit {app}" in command or f"stop {app}" in command:
            os.system(f"taskkill /im {proc_name} /f")
            voice.speak(f"Closed {app}")
            found = True
            break

    # Special handling for Spotify (sometimes multiple processes)
    if not found and "spotify" in command:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] and 'spotify' in proc.info['name'].lower():
                os.system(f"taskkill /pid {proc.info['pid']} /f")
                voice.speak("Closed Spotify")
                found = True

    # Fallback for browsers
    if not found and any(x in command for x in ["chrome", "youtube", "google"]):
        os.system("taskkill /im chrome.exe /f")
        voice.speak("Closed Chrome")
        found = True

    # Fallback for calculator
    found = new_func(command, found)

    if not found:
        voice.speak("I can't close that yet.")

def new_func(command, found):
    if not found and "calculator" in command:
        os.system("taskkill /im Calculator.exe /f")
        voice.speak("Closed Calculator")
        found = True
    return found

# Coding FAQ

FAQ = {
    
  "Sanatan Dharma": "The eternal way of life rooted in universal truths. Example: Like gravity governs motion, Sanatan Dharma governs spiritual evolution.",
  "Veda": "Ancient scriptures containing divine knowledge. Example: Rigveda praises cosmic forces through hymns.",
  "Upanishad": "Philosophical texts exploring the soul and reality. Example: 'Tat Tvam Asi' means 'You are That'.",
  "Bhagavad Gita": "A dialogue between Krishna and Arjuna on duty and devotion. Example: 'Do your duty without attachment to results.'",
  "Karma": "Law of cause and effect. Example: Helping others creates good karma.",
  "Moksha": "Liberation from the cycle of birth and death. Example: A soul attaining moksha merges with the Supreme.",
  "Dharma": "Righteous duty or moral law. Example: A teacher’s dharma is to educate.",
  "Avatar": "Divine incarnation. Example: Krishna is an avatar of Vishnu.",
  "Trimurti": "Trinity of Brahma (creator), Vishnu (preserver), and Shiva (destroyer). Example: Vishnu incarnates to restore balance.",
  "Yajna": "Sacred ritual offering. Example: Agnihotra is a fire ritual performed at sunrise.",
  "Mantra": "Sacred sound or phrase. Example: 'Om Namah Shivaya' invokes Lord Shiva.",
  "Om": "Primordial sound representing universal consciousness. Example: Chanting Om calms the mind.",
  "Ashram": "Spiritual hermitage or retreat. Example: Rishi Valmiki lived in an ashram.",
  "Guru": "Spiritual teacher. Example: A guru guides the disciple toward enlightenment.",
  "Shloka": "Verse from scriptures. Example: 'Karmanye vadhikaraste' is a famous shloka from the Gita.",
  "Rishi": "Sage or seer. Example: Rishi Vasistha was a teacher of Lord Rama.",
  "Bhakti": "Devotion to the divine. Example: Meera Bai’s bhakti for Krishna was unconditional.",
  "Jnana": "Spiritual knowledge. Example: Self-realization through study and reflection.",
  "Tapas": "Spiritual discipline or austerity. Example: Sage Vishwamitra performed tapas for years.",
  "Puja": "Worship ritual. Example: Offering flowers and incense to a deity.",
  "Prasad": "Sanctified food offered to deities. Example: Ladoo given after Ganesh puja.",
  "Darshan": "Sacred sight of a deity or saint. Example: Visiting a temple for darshan.",
  "Mandir": "Temple. Example: People visit the mandir to pray and meditate.",
  "Shakti": "Divine feminine energy. Example: Durga represents fierce protective Shakti.",
  "Lakshmi": "Goddess of wealth and prosperity. Example: Worshipped during Diwali.",
  "Saraswati": "Goddess of wisdom and arts. Example: Students pray to Saraswati before exams.",
  "Durga": "Warrior goddess who defeats evil. Example: Celebrated during Navratri.",
  "Kali": "Fierce form of Shakti. Example: Symbolizes destruction of ego.",
  "Rama": "Avatar of Vishnu, hero of Ramayana. Example: Embodiment of dharma and virtue.",
  "Krishna": "Avatar of Vishnu, teacher of Gita. Example: Played flute and guided Arjuna.",
  "Hanuman": "Devotee of Rama, symbol of strength and devotion. Example: Leapt across the ocean to find Sita.",
  "Sita": "Wife of Rama, symbol of purity and devotion. Example: Endured exile with grace.",
  "Arjuna": "Warrior prince guided by Krishna. Example: Faced moral dilemma in Mahabharata.",
  "Mahabharata": "Epic describing the Kurukshetra war. Example: Contains the Bhagavad Gita.",
  "Ramayana": "Epic of Lord Rama’s life. Example: Teaches values of dharma and loyalty.",
  "Chakra": "Energy centers in the body. Example: Heart chakra governs love and compassion.",
  "Yoga": "Union of body, mind, and spirit. Example: Practicing asanas and meditation.",
  "Raja Yoga": "Path of meditation and mental discipline. Example: Focuses on inner stillness.",
  "Bhakti Yoga": "Path of devotion. Example: Singing kirtans and chanting mantras.",
  "Karma Yoga": "Path of selfless action. Example: Serving others without expecting rewards.",
  "Jnana Yoga": "Path of knowledge. Example: Studying scriptures and contemplating truth.",
  "Samsara": "Cycle of birth, death, and rebirth. Example: Moksha ends the cycle of samsara.",
  "Ahamkara": "Ego or sense of self. Example: Ahamkara creates illusion of separation.",
  "Maya": "Illusion that veils true reality. Example: Worldly attachments are part of maya.",
  "Satya": "Truthfulness. Example: Speaking truth is part of dharma.",
  "Ahimsa": "Non-violence. Example: Practicing compassion toward all beings.",
  "Tirtha": "Sacred pilgrimage site. Example: Varanasi is a famous tirtha.",
  "Samskara": "Rites of passage. Example: Naming ceremony is a samskara.",
  "Shraddha": "Faith and reverence. Example: Performing rituals for ancestors.",
  "Aarti": "Ceremonial offering of light. Example: Waving lamps before deity during puja.",
  "variable": "A variable stores data. Example: x = 5",
  "loop": "Loops repeat code. Example:\nfor i in range(5): print(i)\nwhile x < 10: x += 1",
  "function": "Define a function using def keyword. Example:\ndef greet(name):\n    print(f'Hello {name}')",
  "if statement": "Runs code on condition. Example:\nif x > 0:\n    print('Positive')",
  "list": "List holds multiple values. Example:\nnumbers = [1, 2, 3]",
  "dictionary": "A dictionary stores key-value pairs. Example:\ndata = {'a': 1, 'b': 2}",
    "class": "A class defines a blueprint for objects. Example:\nclass Dog:\n    def __init__(self, name):\n        self.name = name",
    "exception": "Exceptions handle errors. Example:\ntry:\n    x = 1/0\nexcept ZeroDivisionError:\n    print('Error!')",
    "what is python?": "Python is a popular, high-level, interpreted programming language known for its simplicity and readability.",
    "how to install python?": "Download Python from python.org and follow the installation instructions for your operating system.",
    "how to print in python?": "Use the print() function. Example:\nprint('Hello World')",
    "what is a list comprehension?": "List comprehensions provide a concise way to create lists. Example:\nsquares = [x*x for x in range(5)]",
    "how to import a module?": "Use the import statement. Example:\nimport math",
    "what is pip?": "pip is the package installer for Python. Example:\npip install package_name",
    "how to read a file in python?": "Use open() to read files. Example:\nwith open('file.txt', 'r') as f:\n    content = f.read()",
    "how to write to a file?": "Use open() with 'w' mode and write(). Example:\nwith open('file.txt', 'w') as f:\n    f.write('text')",
    "what is a lambda function?": "A lambda function is an anonymous function. Example:\nsum = lambda x, y: x + y",
    "how to handle errors?": "Use try-except blocks to handle errors. Example:\ntry:\n    int('abc')\nexcept ValueError:\n    print('Not a number')",
    "what is inheritance?": "Inheritance allows a class to inherit attributes and methods from another class. Example:\nclass Animal: pass\nclass Dog(Animal): pass",
    "what is polymorphism?": "Polymorphism allows objects of different classes to be treated as objects of a common superclass. Example:\nclass Cat: def speak(self): print('Meow')\nclass Dog: def speak(self): print('Woof')",
    "how to install numpy?": "Use pip install numpy to install the numpy package.",
    "what is a tuple?": "A tuple is an immutable sequence type. Example:\nt = (1, 2, 3)",
    "how to reverse a list?": "Use list.reverse() or list[::-1]. Example:\nnumbers = [1,2,3]; numbers.reverse()",
    "how to sort a list?": "Use list.sort() or sorted(list). Example:\nnumbers = [3,1,2]; numbers.sort()",
    "what is a set?": "A set is an unordered collection of unique elements. Example:\ns = {1, 2, 3}",
    "how to remove duplicates from a list?": "Convert the list to a set: list(set(my_list)). Example:\nunique = list(set([1,2,2,3]))",
    "what is __init__?": "__init__ is the constructor method in Python classes. Example:\nclass A:\n    def __init__(self):\n        self.x = 1",
    "how to create a virtual environment?": "Use python -m venv env to create a virtual environment.",
    "how to install packages from requirements.txt?": "Use pip install -r requirements.txt",
    "what is recursion?": "Recursion is a function calling itself to solve a problem. Example:\ndef factorial(n):\n    return 1 if n==0 else n*factorial(n-1)",
    "how to get user input?": "Use input() function. Example:\nname = input('Enter your name: ')",
    "how to check python version?": "Use python --version in the terminal.",
    "what is a decorator?": "A decorator modifies the behavior of a function. Example:\n@staticmethod\ndef foo(): pass",
    "how to use map()?": "map() applies a function to all items in an iterable. Example:\nlist(map(str, [1,2,3]))",
    "how to use filter()?": "filter() filters items in an iterable. Example:\nlist(filter(lambda x: x>0, [1,-1,2]))",
    "how to use reduce()?": "reduce() applies a rolling computation. Example:\nfrom functools import reduce\nreduce(lambda x,y: x+y, [1,2,3])",
    "what is a generator?": "A generator yields items one at a time using yield keyword. Example:\ndef gen():\n    yield 1\n    yield 2",
    "how to install pandas?": "Use pip install pandas",
    "how to merge dictionaries?": "Use {**dict1, **dict2} in Python 3.5+. Example:\nd = {**{'a':1}, **{'b':2}}",
    "how to check if a key exists in a dictionary?": "Use 'key' in dict. Example:\nif 'a' in d:",
    "how to iterate over a dictionary?": "Use for k, v in dict.items(). Example:\nfor k, v in d.items(): print(k, v)",
    "how to convert string to int?": "Use int('123'). Example:\nx = int('123')",
    "how to convert int to string?": "Use str(123). Example:\ns = str(123)",
    "how to format strings?": "Use f-strings: f'Hello {name}'. Example:\nname = 'Ayush'; print(f'Hello {name}')",
    "how to use list slicing?": "Use list[start:end:step]. Example:\nnumbers[1:4]",
    "how to install matplotlib?": "Use pip install matplotlib",
    "how to plot a graph in python?": "Use matplotlib.pyplot.plot(). Example:\nimport matplotlib.pyplot as plt\nplt.plot([1,2,3],[4,5,6])\nplt.show()",
    "how to create a class?": "Use class keyword. Example:\nclass MyClass:\n    pass",
    "how to create an object?": "Instantiate the class. Example:\nobj = MyClass()",
    "how to delete a file?": "Use os.remove('filename'). Example:\nimport os; os.remove('file.txt')",
    "how to rename a file?": "Use os.rename('old', 'new'). Example:\nos.rename('a.txt', 'b.txt')",
    "how to get current working directory?": "Use os.getcwd(). Example:\nimport os; print(os.getcwd())",
    "how to list files in a directory?": "Use os.listdir('path'). Example:\nfiles = os.listdir('.')",
    "how to check if file exists?": "Use os.path.exists('filename'). Example:\nimport os; os.path.exists('file.txt')",
    "how to use try except finally?": "try: ... except: ... finally: .... Example:\ntry:\n    x=1/0\nexcept:\n    print('Error')\nfinally:\n    print('Done')",
    "how to raise an exception?": "Use raise Exception('message'). Example:\nraise ValueError('Invalid value')",
    "how to define a constant?": "Use uppercase variable names by convention. Example:\nPI = 3.14",
    "how to use enumerate()?": "enumerate() gives index and value. Example:\nfor i, v in enumerate(['a','b']): print(i, v)",
    "how to zip lists?": "Use zip(list1, list2). Example:\nfor a, b in zip([1,2],[3,4]): print(a, b)",
    "how to unpack tuples?": "Use a, b = (1, 2). Example:\na, b = (1, 2)",
    "how to use *args and **kwargs?": "*args for variable arguments, **kwargs for keyword arguments. Example:\ndef foo(*args, **kwargs): pass",
    "how to check type of variable?": "Use type(var). Example:\ntype(123)",
    "how to convert list to string?": "Use ','.join(list). Example:\n','.join(['a','b'])",
    "how to convert string to list?": "Use list('string') or split(). Example:\nlist('abc'), 'a b c'.split()",
    "how to use random module?": "import random; random.randint(1,10). Example:\nimport random; print(random.randint(1,10))",
    "how to shuffle a list?": "Use random.shuffle(list). Example:\nimport random; random.shuffle(my_list)",
    "how to generate random number?": "Use random.randint(a, b). Example:\nrandom.randint(1,100)",
    "how to use time.sleep()?": "import time; time.sleep(seconds). Example:\nimport time; time.sleep(2)",
    "how to get current time?": "Use time.time() or datetime.datetime.now(). Example:\nimport time; print(time.time())",
    "how to use datetime module?": "import datetime; datetime.datetime.now(). Example:\nimport datetime; print(datetime.datetime.now())",
    "how to create a GUI in python?": "Use tkinter. Example:\nimport tkinter as tk\nroot = tk.Tk()\nroot.mainloop()",
}

def answer_question(question: str):
    for key, answer in FAQ.items():
        if key in question:
            voice.speak(answer)
            return
    voice.speak("Sorry, I don't know the answer to that yet.")

# Jokes

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why did the computer show up at work late? It had a hard drive.",
    "Why do Java developers wear glasses? Because they don't see sharp.",
    "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
    "Why did the developer go broke? Because he used up all his cache.",
    "Why do Python programmers have low self-esteem? Because they're constantly comparing their self to others."
]


# Reminders

reminders: List[Tuple[float, str]] = []

def parse_time(time_part: str) -> Optional[int]:
    try:
        num = int(time_part.split()[0])
        if "minute" in time_part:
            return num * 60
        elif "second" in time_part:
            return num * 1
        elif "hour" in time_part:
            return num * 3600
    except Exception as e:
        logging.error(e)
    return None
 

def set_reminder(command: str):
    try:
        if "remind me to" in command and "in" in command:
            task = command.split("remind me to")[1].split("in")[0].strip()
            time_part = command.split("in")[1].strip()
            seconds = parse_time(time_part)
            if seconds is None:
                voice.speak("Please specify seconds, minutes, or hours.")
                return
            remind_time = time.time() + seconds
            reminders.append((remind_time, task))
            voice.speak(f"Reminder set for {task} in {seconds} seconds.")
        else:
            voice.speak("Please say, for example: remind me to drink water in 10 minutes.")
    except Exception as e:
        voice.speak("Sorry, I couldn't set the reminder.")
        logging.error(e)



def check_reminders():
    while True:
        now = time.time()
        for r in reminders[:]:
            remind_time, task = r
            if now >= remind_time:
                voice.speak(f"Reminder: {task}")
                reminders.remove(r)
        time.sleep(1)

# Help

def show_help():
    help_text = (
        "Here are some things you can say:\n"
        "- open google/youtube/spotify/calculator/chrome\n"
        "- play [song] on youtube\n"
        "- close chrome/youtube/google/spotify/calculator\n"
        "- coding/python/codding [ask a coding question]\n"
        "- tell me a joke\n"
        "- remind me to [task] in [seconds/minutes/hours]\n"
        "- help\n"
        "- hello/hi/नमस्ते"
    )
    voice.speak(help_text)

# Command Handler

def handle_command(command: str):
    command = command.strip().lower()
    if not command:
        return
    if "open" in command or "play" in command:
        open_application(command)
    elif "close" in command:
        close_application(command)
    elif any(x in command for x in ["coding", "python", "codding"]):
        voice.speak("What's your coding question?")
        q = recognize_speech_from_mic()
        if q:
            answer_coding_question(q)
    elif "joke" in command:
        joke = random.choice(JOKES)
        voice.speak(joke)
    elif "remind me" in command:
        set_reminder(command)
    elif "help" in command:
        show_help()
    elif any(x in command for x in ["hello", "hi", "नमस्ते"]):
        voice.speak("Namaste Ayush! I'm ready to assist you.")
        for word in command.split():
            if word.istitle():
                city = word
        weather_info = get_weather(city)
        voice.speak(f"Weather in {city}: {weather_info}")
    elif "time" in command:
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        voice.speak(f"The current time is {current_time}")
    elif "date" in command:
        date = datetime.date.today().strftime('%B %d, %Y')
        voice.speak(f"Today's date is {date}")
    elif "who is" in command:
        person = command.replace('who is', '').strip()
        try:
            info = wikipedia.summary(person, sentences=1)
            voice.speak(info)
        except Exception:
            voice.speak("Sorry, I couldn't find information about that person.")
    elif "exit" in command or "bye" in command:
        voice.speak("Goodbye!")
        exit()
    else:
        voice.speak("I didn't understand that command.")


# Weather & System Stats

def get_weather(city: str = "Hamirpur") -> str:
    api = "your_openweather_api_key"
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api}&units=metric"
        data = requests.get(url, timeout=5).json()
        temp = data['main']['temp']
        desc = data['weather'][0]['description']
        return f"{temp}°C, {desc.capitalize()}"
    except Exception as e:
        logging.error(e)
        return "Weather unavailable"

def get_battery_status() -> str:
    try:
        battery = psutil.sensors_battery()
        if battery:
            return f"🔋 {battery.percent}% {'(Charging)' if battery.power_plugged else ''}"
        else:
            return "🔋 N/A"
    except Exception as e:
        logging.error(e)
        return "🔋 N/A" 

def update_widgets(clock, weather, stats, battery_label):
    def refresh():
        while True:
            try:
                clock.config(text="🕒 " + time.strftime("%H:%M"))
                weather.config(text="☁️ " + get_weather())
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                stats.config(text=f"🧠 CPU: {cpu}% | RAM: {ram}% | Disk: {psutil.disk_usage('/').percent}%")
                battery_label.config(text=get_battery_status())
            except Exception as e:
                logging.error(e)
            time.sleep(5)
    threading.Thread(target=refresh, daemon=True).start()

# Wallpaper Switching

wallpapers = itertools.cycle(["wallpaper1.gif", "wallpaper2.gif", "wallpaper3.gif"])
current_frames: List[ImageTk.PhotoImage] = []

def load_wallpaper(name: str) -> List[ImageTk.PhotoImage]:
    try:
        img = Image.open(name)
        return [ImageTk.PhotoImage(f.convert("RGBA")) for f in ImageSequence.Iterator(img)]
    except Exception as e:
        logging.error(e)
        return []

def switch_wallpaper(bg_label):
    global current_frames
    online_wallpapers = [
        "https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif",
        "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
        "https://media.giphy.com/media/xT9IgG50Fb7Mi0prBC/giphy.gif",
        "https://media.giphy.com/media/26ufdipQqU2lhNA4g/giphy.gif"
    ]
    next_wallpaper = next(wallpapers)
    if random.random() < 0.5:
        next_wallpaper = random.choice(online_wallpapers)
    if next_wallpaper.startswith("http"):
        try:
            response = requests.get(next_wallpaper, stream=True, timeout=10)
            response.raise_for_status()
            with open("temp_wallpaper.gif", "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            current_frames = load_wallpaper("temp_wallpaper.gif")
        except Exception as e:
            logging.error(e)
            current_frames = []
    else:
        current_frames = load_wallpaper(next_wallpaper)
    if current_frames:
        animate_bg(bg_label)

def animate_bg(label, i=0):
    if current_frames:
        label.config(image=current_frames[i])
        label.after(100, animate_bg, label, (i + 1) % len(current_frames))


# Fade-in Startup

def fade_in(root):
    alpha = 0.0
    while alpha < 1.0:
        root.attributes("-alpha", alpha)
        alpha += 0.05
        root.update()
        time.sleep(0.02)

# Theme Toggle

def toggle_theme(root, overlay, labels, entry, btns, battery_label):
    if root["bg"] == "#222222":
        root.config(bg="#f0f0f0")
        overlay.config(bg="#ffffff")
        for l in labels:
            l.config(bg="#ffffff", fg="#222222")
        entry.config(bg="#ffffff", fg="#222222")
        for child in btns.winfo_children():
            child.config(bg="#e0e0e0", fg="#222222")
        battery_label.config(bg="#ffffff", fg="#222222")
    else:
        root.config(bg="#222222")
        overlay.config(bg="#2c2f33")
        for l in labels:
            l.config(bg="#2c2f33", fg="#00ffff")
        entry.config(bg="#2c2f33", fg="#00ffff")
        for child in btns.winfo_children():
            child.config(bg="#00ffff", fg="#000")
        battery_label.config(bg="#2c2f33", fg="#00ffff")


# GUI

def run_gui():
    root = tk.Tk()
    root.title("🔒 Lock Assistant")
    root.geometry("760x560")
    root.attributes("-alpha", 0.0)
    root.config(bg="#0E0E0E")

    # Background animation
    bg_label = tk.Label(root)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    switch_wallpaper(bg_label)

    threading.Thread(target=fade_in, args=(root,), daemon=True).start()
    threading.Thread(target=check_reminders, daemon=True).start()

    overlay = tk.Frame(root, bg="#2c2f33", bd=4, relief="groove")
    overlay.place(relx=0.5, rely=0.5, anchor="center", width=550, height=500)

    title_label = tk.Label(overlay, text="🤖 Lock Assistant", font=("Helvetica", 20, "bold"), fg="#00ffff", bg="#2c2f33")
    subtitle_label = tk.Label(overlay, text="Your Bilingual Voice-Powered Companion", font=("Helvetica", 12), fg="#ffffff", bg="#2c2f33")
    prompt_label = tk.Label(overlay, text="Type a command:", font=("Helvetica", 11), fg="#dddddd", bg="#2c2f33")
    title_label.pack(pady=10)
    subtitle_label.pack()
    prompt_label.pack(pady=8)

    entry = tk.Entry(overlay, width=45, font=("Helvetica", 11), bg="#2c2f33", fg="#00ffff")
    entry.pack()

    def on_submit():
        cmd = entry.get().lower()
        if cmd:
            handle_command(cmd)
            entry.delete(0, tk.END)

    btns = tk.Frame(overlay, bg="#2c2f33")
    btns.pack(pady=10)
    tk.Button(btns, text="💡 Submit", command=on_submit, bg="#00ffff", fg="#000", font=("Helvetica", 10, "bold"), width=22).grid(row=0, column=0, padx=6)
    root.bind('<Return>', lambda event: on_submit())
    tk.Button(btns, text="🎙️ Voice Command", command=lambda: handle_command(recognize_speech_from_mic()), bg="#007acc", fg="#fff", font=("Helvetica", 10, "bold"), width=22).grid(row=0, column=1, padx=6)
    tk.Button(overlay, text="❌ Exit", command=root.quit, bg="#ff5555", fg="#fff", font=("Helvetica", 10), width=40).pack(pady=10)

    theme_btn = tk.Button(overlay, text="🌗 Toggle Theme", font=("Helvetica", 10), width=40, bg="#222222", fg="#00ffff")
    theme_btn.pack(pady=5)

    clock = tk.Label(overlay, font=("Helvetica", 13), fg="#00ffff", bg="#2c2f33")
    clock.pack(pady=8)
    weather = tk.Label(overlay, font=("Helvetica", 13), fg="#00ffff", bg="#2c2f33")
    weather.pack(pady=8)
    stats = tk.Label(overlay, font=("Helvetica", 13), fg="#00ffff", bg="#2c2f33")
    stats.pack(pady=8)
    battery_label = tk.Label(overlay, font=("Helvetica", 13), fg="#00ffff", bg="#2c2f33")
    battery_label.pack(pady=8)
    update_widgets(clock, weather, stats, battery_label)

    labels = [title_label, subtitle_label, prompt_label, clock, weather, stats, battery_label]
    theme_btn.config(command=lambda: toggle_theme(root, overlay, labels, entry, btns, battery_label))

    root.mainloop()  

if __name__ == "__main__":
    speak_text =(
        "Hello Ayush! I'm your voice assistant. "
        "You can ask me to open applications, play music, tell jokes, set reminders, "
        "check the weather, and much more. Just say 'help' to see what I can do."
    )
    voice.speak(speak_text)
    try:
        run_gui()
    except KeyboardInterrupt:
        logging.info("Exiting...")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        voice.speak("An error occurred while starting the assistant.")
    finally:
        logging.info("Assistant has been shut down.")
        voice.speak("Goodbye! See you next time.")
        exit(0)
        
    
        
        
        
        
        