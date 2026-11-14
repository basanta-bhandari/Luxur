from googlesearch import search

from Backend.Chatbot import StreamCompletion
from Backend.Common import (
    Assistantname, HISTORY_LIMIT, Username,
    AnswerModifier, LoadChatLog, RealtimeInformation, SaveChatLog,
)

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello! How can I assist you today?"},
]


def GoogleSearch(query):
    try:
        results = list(search(query, advanced=True, num_results=5))
    except Exception as e:
        print(f"Google search failed: {e}")
        results = []

    Answer = f"The search results for '{query}' are:\n[start]\n"
    for i in results:
        Answer += f"Title: {i.title}\nURL: {i.url}\nDescription: {i.description}\n\n"
    if not results:
        Answer += "No search results were found.\n"
    Answer += "[end]"
    return Answer


def RealtimeSearchEngine(prompt):
    messages = LoadChatLog()
    messages.append({"role": "user", "content": prompt})
    try:
        Answer = StreamCompletion(
            SystemChatBot
            + [{"role": "system", "content": GoogleSearch(prompt)},
               {"role": "system", "content": RealtimeInformation()}]
            + messages[-HISTORY_LIMIT:],
            max_tokens=2048,
        )
    except Exception as e:
        print(f"RealtimeSearchEngine error: {e}")
        return "Sorry, I couldn't complete the search. Please check your API key and connection."

    messages.append({"role": "assistant", "content": Answer})
    SaveChatLog(messages)
    return AnswerModifier(Answer)


if __name__ == "__main__":
    while True:
        print(RealtimeSearchEngine(input("Enter your query: ")))
