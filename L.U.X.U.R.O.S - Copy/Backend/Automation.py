from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

classes = [
    "zCubwf",
    "hgKElc",
    "LTKOO sY7ric",
    "Z0LcW",
    "gsrt vk_bk FzvWSb YwPhnf",
    "pclqee",
    "tw-Data-text tw-text-small tw-ta",
    "IZ6rdc",
    "O5Ur6d LTKOO",
    "vlzY6d",
    "webanswers-webanswers_table__webanswers-table",
    "dDoNo ikb4Bb gsrt",
    "sXLaOe",
    "LWkfKe",
    "VQF4g",
    "qv3Wpe",
    "kno-rdesc",
    "SPZz6b"
]

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
client = Groq(api_key=GroqAPIKey)
professional_resonse= [
    "Your stafisfaction is my priority bitch feel free to reach dont hide like coward, I am here to help you with any questions or concerns you may have.",
    "I am here to provide you with the best possible assistance, so please don't hesitate to reach out to me with any questions or concerns you may have."
]

messages = []

SystemChatBot= [{ "role": "system", "content": f"Hello, I am {os.environ.get('Username')}, You are a very accurate and advanced AI chatbot named {os.environ.get('Assistantname')} which has real-time up-to-date information from the internet. *** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.*** *** Just answer the question from the provided data in a professional way. ***"}]

def GoogleSearch(Topic):
    search(Topic)
    return True

def Content(Topic):
    def OpenNotepad(file_path):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, file_path])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None,
        )
        Answer = ""

        for chunk in completion:
            if "choices" in chunk:
                for choice in chunk["choices"]:
                    if getattr(choice.delta, "content", None):
                        Answer += choice.delta.content
                Answer = Answer.replace("</s>", "")
                messages.append({"role": "assistant", "content": f"{Answer}"})
                return Answer

        return ""

    cleaned_topic = Topic.replace("Content", "")
    ContentByAI = ContentWriterAI(cleaned_topic)

    file_path = rf"Data\{cleaned_topic.lower().replace(' ', '')}.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    OpenNotepad(file_path)
    return True


def YoutubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webopen(Url4Search)
    return True


def PlayYoutube(query):
    playonyt(query)
    return True


def OpenApp(app, sess=requests.Session()):
    try:
        appopen(app, match_closest=True, output=True, throw_errors=True)
        return True
    except:
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find.all('a', {'jsname': 'UWckNb '})
            return [link.get('href') for link in links]

        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {'User-Agent': useragent}
            response = sess.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
            else:
                return None
        html= search_google(app)
        if html:
            links = extract_links(html)
            webopen(link)
        return True

def CloseApp(app):
    if CloseApp(app):
        if "chrome" in app:
            pass
        else:
            try:
                close(app, match_closest=True, output=True, throw_errors=True)
                return True
            except:
                return False


def System(command):
    def mute():
        keyboard.press_and_release('volume mute')
    def unmute():
        keyboard.press_and_release('volume mute')
    def volumeup():
        keyboard.press_and_release('volume up')
    def volumedown():
        keyboard.press_and_release('volume down')

    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volumeup":
        volumeup()
    elif command == "volumedown":
        volumedown()
    return True

async def TranslateAnsExecute(commands: list[str]):
    funcs= []
    for command in commands:
        if command.startswith("open "):
            if "open it" in command:
                pass
            if "open file" in command:
                pass
            else:
                fun= asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)

        elif command.startswith("general "):
            pass
        elif command.startswith("realtime "):
            pass
        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)
        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)
        elif command.startswith("content "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("content "))
            funcs.append(fun)     
        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(YoutubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)
        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)
        else:
            print(f"[red]Unknown command: {command}[/red]")
    results=await asyncio.gather(*funcs)
    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result

async def Automation(commands: list[str]):
    async for result in TranslateAnsExecute(commands):
        pass
    return True
