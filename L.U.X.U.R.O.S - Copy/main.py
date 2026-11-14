import os
import threading
import traceback
from asyncio import run
from time import sleep

from Backend.Automation import Automation
from Backend.Chatbot import ChatBot
from Backend.Common import (
    Assistantname, Username,
    AnswerModifier, GetAssistantStatus, GetMicrophoneStatus, LoadChatLog, QueryModifier,
    SetAssistantStatus, SetMicrophoneStatus, ShowTextToScreen, TempDirectoryPath,
)
from Backend.ImageGeneration import GenerateImage
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.SpeakToText import Shutdown, SpeechRecognition
from Backend.TextToSpeech import TextToSpeech
from Frontend.GUI import GraphicalUserInterface

DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may I help you?'''

Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]


def ChatLogIntegration():
    """Write the saved chat log, formatted for display, to Database.data."""
    lines = []
    for entry in LoadChatLog():
        if entry.get("role") == "user":
            lines.append(f"{Username} : {entry['content']}")
        elif entry.get("role") == "assistant":
            lines.append(f"{Assistantname} : {entry['content']}")
    TempDirectoryPath("Database.data").write_text(AnswerModifier("\n".join(lines)), encoding="utf-8")


def ShowChatsOnGUI():
    history = TempDirectoryPath("Database.data").read_text(encoding="utf-8")
    ShowTextToScreen(history if history.strip() else DefaultMessage)


def InitialExecution():
    SetMicrophoneStatus("False")
    SetAssistantStatus("Available ...")
    ShowTextToScreen("")
    ChatLogIntegration()
    ShowChatsOnGUI()


def Answer(Text):
    ShowTextToScreen(f"{Assistantname} : {Text}")
    SetAssistantStatus("Answering ...")
    # Switching the mic off in the GUI interrupts playback.
    TextToSpeech(Text, func=lambda r=None: GetMicrophoneStatus() == "True")


def MainExecution():
    SetAssistantStatus("Listening ...")
    Query = SpeechRecognition()
    if not Query:
        return False

    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking ...")
    Decision = FirstLayerDMM(Query)
    print(f"\nDecision : {Decision}\n")

    General = [" ".join(i.split()[1:]) for i in Decision if i.startswith("general")]
    Realtime = [" ".join(i.split()[1:]) for i in Decision if i.startswith("realtime")]
    MergedQuery = " and ".join(General + Realtime)

    if any(q.startswith(func) for q in Decision for func in Functions):
        run(Automation(list(Decision)))

    for q in Decision:
        if q.startswith("generate image"):
            threading.Thread(target=GenerateImage, args=(q,), daemon=True).start()

    if Realtime:
        SetAssistantStatus("Searching ...")
        Answer(RealtimeSearchEngine(QueryModifier(MergedQuery)))
    elif General:
        Answer(ChatBot(QueryModifier(MergedQuery)))

    if "exit" in Decision:
        Answer("Okay, bye!")
        SetMicrophoneStatus("False")
        Shutdown()
        os._exit(0)
    return True


def FirstThread():
    while True:
        if GetMicrophoneStatus() == "True":
            try:
                MainExecution()
            except Exception as e:
                # Stop listening so a persistent failure (missing key, no Chrome, ...)
                # doesn't retry in a loop; the error stays on screen until the mic is used again.
                traceback.print_exc()
                SetMicrophoneStatus("False")
                SetAssistantStatus(f"Error: {e}")
        else:
            status = GetAssistantStatus()
            if not status.startswith(("Available ...", "Error")):
                SetAssistantStatus("Available ...")
            sleep(0.1)


if __name__ == "__main__":
    InitialExecution()
    threading.Thread(target=FirstThread, daemon=True).start()
    GraphicalUserInterface()
