from groq import Groq

from Backend.Common import (
    Assistantname, GroqModel, HISTORY_LIMIT, Username,
    AnswerModifier, LoadChatLog, RealtimeInformation, RequireEnv, SaveChatLog,
)

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [{"role": "system", "content": System}]

_client = None


def GroqClient():
    global _client
    if _client is None:
        _client = Groq(api_key=RequireEnv("GroqAPIKey"))
    return _client


def StreamCompletion(messages, max_tokens=1024):
    extra = {}
    if GroqModel.startswith("openai/gpt-oss"):
        # Reasoning model: keep thinking short so voice replies stay fast.
        extra["reasoning_effort"] = "low"
    completion = GroqClient().chat.completions.create(
        model=GroqModel,
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.7,
        top_p=1,
        stream=True,
        **extra,
    )
    Answer = ""
    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content
    return Answer.replace("</s>", "").strip()


def ChatBot(Query):
    messages = LoadChatLog()
    messages.append({"role": "user", "content": Query})
    try:
        Answer = StreamCompletion(
            SystemChatBot
            + [{"role": "system", "content": RealtimeInformation()}]
            + messages[-HISTORY_LIMIT:]
        )
    except Exception as e:
        print(f"ChatBot error: {e}")
        return "Sorry, I couldn't reach the language model. Please check your API key and connection."

    messages.append({"role": "assistant", "content": Answer})
    SaveChatLog(messages)
    return AnswerModifier(Answer)


if __name__ == "__main__":
    while True:
        print(ChatBot(input("Enter Your Question: ")))
