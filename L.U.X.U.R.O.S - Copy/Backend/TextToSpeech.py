import asyncio
import random

import edge_tts
import pygame

from Backend.Common import AssistantVoice, DATA_DIR

SPEECH_FILE = DATA_DIR / "speech.mp3"


async def TextToAudioFile(text) -> None:
    SPEECH_FILE.unlink(missing_ok=True)
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch="+5Hz", rate="+13%")
    await communicate.save(str(SPEECH_FILE))


def TTS(Text, func=lambda r=None: True):
    """Speak `Text`. `func()` returning False stops playback early."""
    try:
        asyncio.run(TextToAudioFile(Text))

        pygame.mixer.init()
        pygame.mixer.music.load(str(SPEECH_FILE))
        pygame.mixer.music.play()

        clock = pygame.time.Clock()
        while pygame.mixer.music.get_busy():
            if func() is False:
                break
            clock.tick(10)
        return True
    except Exception as e:
        print(f"Error in TTS: {e}")
        return False
    finally:
        try:
            func(False)
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                pygame.mixer.quit()
        except Exception as e:
            print(f"Error in TTS cleanup: {e}")


def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".")

    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    if len(Data) > 4 and len(Text) >= 250:
        TTS(". ".join(Data[0:2]) + ". " + random.choice(responses), func)
    else:
        TTS(Text, func)


if __name__ == "__main__":
    while True:
        TextToSpeech(input("Enter text: "))
