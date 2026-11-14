"""Desktop automation: open/close apps, web & YouTube search, content writing, volume.

Windows is the supported platform. The `not IS_WINDOWS` branches are a minimal
Linux shim so the app can be smoke-tested on Linux; they are not maintained.
"""
import asyncio
import re
import shutil
import subprocess
import webbrowser
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup
from rich import print

from Backend.Chatbot import StreamCompletion
from Backend.Common import DATA_DIR, IS_WINDOWS, Assistantname, Username

if IS_WINDOWS:
    import keyboard
    from AppOpener import close as appclose, open as appopen

useragent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
             "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

ContentWriterSystem = [{
    "role": "system",
    "content": f"Hello, I am {Username}. You are {Assistantname}, a content writer. "
               "You write content such as letters, code, applications, essays, notes, songs and poems. "
               "Write the requested content directly, with proper grammar and formatting.",
}]


def OpenInEditor(path):
    """Open a text file in Notepad (or the default app on Linux)."""
    if IS_WINDOWS:
        subprocess.Popen(["notepad.exe", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def GoogleSearch(Topic):
    webbrowser.open(f"https://www.google.com/search?q={quote_plus(Topic)}")
    return True


def Content(Topic):
    Topic = Topic.strip()
    try:
        ContentByAI = StreamCompletion(
            ContentWriterSystem + [{"role": "user", "content": Topic}], max_tokens=2048
        )
    except Exception as e:
        print(f"[red]Content writer failed: {e}[/red]")
        return False

    safe_name = re.sub(r"[^a-z0-9]+", "_", Topic.lower()).strip("_")[:60] or "content"
    file_path = DATA_DIR / f"{safe_name}.txt"
    file_path.write_text(ContentByAI, encoding="utf-8")
    OpenInEditor(file_path)
    return True


def YoutubeSearch(Topic):
    webbrowser.open(f"https://www.youtube.com/results?search_query={quote_plus(Topic)}")
    return True


def PlayYoutube(query):
    """Open the first YouTube result for `query`, or the results page if none is found."""
    url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
    try:
        html = requests.get(url, headers={"User-Agent": useragent}, timeout=10).text
        match = re.search(r'"videoId":"([\w-]{11})"', html) or re.search(r"watch\?v=([\w-]{11})", html)
        if match:
            url = f"https://www.youtube.com/watch?v={match.group(1)}"
    except requests.RequestException as e:
        print(f"[yellow]YouTube lookup failed, opening search page: {e}[/yellow]")
    webbrowser.open(url)
    return True


def OpenWebsiteFor(app):
    """Fallback when no installed app matches: open the top Google result for it."""
    try:
        html = requests.get(f"https://www.google.com/search?q={quote_plus(app)}",
                            headers={"User-Agent": useragent}, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        links = [a.get("href") for a in soup.find_all("a", {"jsname": "UWckNb"}) if a.get("href")]
        if links:
            webbrowser.open(links[0])
            return True
    except requests.RequestException as e:
        print(f"[yellow]Google lookup failed: {e}[/yellow]")
    return GoogleSearch(app)


def OpenApp(app):
    if IS_WINDOWS:
        try:
            appopen(app, match_closest=True, output=True, throw_errors=True)
            return True
        except Exception:
            return OpenWebsiteFor(app)

    executable = shutil.which(app.lower().replace(" ", "-")) or shutil.which(app.lower().replace(" ", ""))
    if executable:
        subprocess.Popen([executable], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)
        return True
    return OpenWebsiteFor(app)


def CloseApp(app):
    try:
        if IS_WINDOWS:
            appclose(app, match_closest=True, output=True, throw_errors=True)
        else:
            subprocess.run(["pkill", "-i", "-x", app.lower().replace(" ", "")], check=False)
        return True
    except Exception as e:
        print(f"[red]Could not close {app}: {e}[/red]")
        return False


def System(command):
    command = command.strip().lower().replace(" ", "")
    if IS_WINDOWS:
        keys = {"mute": "volume mute", "unmute": "volume mute",
                "volumeup": "volume up", "volumedown": "volume down"}
        if command in keys:
            keyboard.press_and_release(keys[command])
            return True
    else:
        sink = "@DEFAULT_SINK@"
        args = {"mute": ["set-sink-mute", sink, "1"], "unmute": ["set-sink-mute", sink, "0"],
                "volumeup": ["set-sink-volume", sink, "+10%"], "volumedown": ["set-sink-volume", sink, "-10%"]}
        if command in args and shutil.which("pactl"):
            subprocess.run(["pactl", *args[command]], check=False)
            return True
    print(f"[red]Unknown system command: {command}[/red]")
    return False


# Prefix -> handler. Order matters: longer prefixes that overlap must come first.
HANDLERS = [
    ("google search ", GoogleSearch),
    ("youtube search ", YoutubeSearch),
    ("open ", OpenApp),
    ("close ", CloseApp),
    ("play ", PlayYoutube),
    ("content ", Content),
    ("system ", System),
]

# Categories the decision model can return that are handled elsewhere (or not yet).
NOT_AUTOMATION = ("general", "realtime", "generate image", "reminder", "exit")


async def TranslateAndExecute(commands: list[str]):
    funcs = []
    for command in commands:
        if command.startswith(NOT_AUTOMATION):
            continue
        if command in ("open it", "open file") or command.startswith("open file "):
            continue
        for prefix, handler in HANDLERS:
            if command.startswith(prefix):
                funcs.append(asyncio.to_thread(handler, command.removeprefix(prefix)))
                break
        else:
            print(f"[red]Unknown command: {command}[/red]")

    for result in await asyncio.gather(*funcs, return_exceptions=True):
        if isinstance(result, Exception):
            print(f"[red]Automation error: {result}[/red]")
        yield result


async def Automation(commands: list[str]):
    async for _ in TranslateAndExecute(commands):
        pass
    return True
