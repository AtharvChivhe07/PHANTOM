import os
import time
import webbrowser
import threading
from datetime import datetime

import ollama
import pyttsx3
import speech_recognition as sr
import requests
from dotenv import load_dotenv


# ==========================================================
# 1. CONFIGURATION
# ==========================================================

load_dotenv()

ASSISTANT_NAME = "Phantom"
OLLAMA_MODEL = "llama3.2:3b"

# Keep your existing NewsAPI configuration.
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")


# ==========================================================
# 2. FAST OFFLINE SPEECH ENGINE
# ==========================================================

print("Initializing Phantom speech engine...")

try:
    speech_engine = pyttsx3.init()

    # Configure speech once, not on every response.
    speech_engine.setProperty("rate", 185)
    speech_engine.setProperty("volume", 1.0)

    voices = speech_engine.getProperty("voices")

    if voices:
        # Use the default available voice.
        speech_engine.setProperty("voice", voices[0].id)

    SPEECH_AVAILABLE = True

except Exception as e:
    print("Speech initialization error:", e)
    speech_engine = None
    SPEECH_AVAILABLE = False


# Prevent two speech requests from running simultaneously.
speech_lock = threading.Lock()


def speak(text):
    """Print and speak a response using offline speech."""

    if text is None:
        return

    text = str(text).strip()

    if not text:
        return

    print(f"\n{ASSISTANT_NAME}: {text}")

    if not SPEECH_AVAILABLE:
        return

    try:
        with speech_lock:
            speech_engine.say(text)
            speech_engine.runAndWait()

    except Exception as e:
        print("Speech error:", e)


# ==========================================================
# 3. OLLAMA AI PROCESSING
# ==========================================================

conversation_history = []

SYSTEM_PROMPT = """
You are Phantom, a helpful personal AI assistant.

Your responsibilities:
- Answer general knowledge questions.
- Explain programming and Python clearly.
- Help with studies, technology, science, and everyday tasks.
- Answer follow-up questions using the conversation history.
- Be honest when you do not know something.
- Use simple English unless the user requests another language.
- Keep simple answers concise.
- Provide code examples when helpful.
- Never claim to have performed an action you did not perform.
- You are running locally through Ollama.
- You cannot automatically access live news or the internet.
  External tools must be used for those tasks.
"""


def aiProcess(command):
    """Generate an answer using the local Ollama model."""

    global conversation_history

    command = command.strip()

    if not command:
        return "Please tell me what you need."

    try:
        print("Phantom: Thinking...")

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        messages.extend(conversation_history)

        messages.append({
            "role": "user",
            "content": command
        })

        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=messages,
            options={
                "temperature": 0.5
            }
        )

        answer = response["message"]["content"].strip()

        if not answer:
            return "I couldn't generate an answer. Please try again."

        # Save the conversation for relevant follow-up questions.
        conversation_history.append({
            "role": "user",
            "content": command
        })

        conversation_history.append({
            "role": "assistant",
            "content": answer
        })

        # Keep recent history to control memory and response time.
        conversation_history = conversation_history[-10:]

        return answer

    except Exception as e:
        print("Ollama AI error:", repr(e))

        return (
            "I couldn't connect to my AI model. "
            "Please check that Ollama is running "
            "and the selected model is installed."
        )


# ==========================================================
# 4. SPEECH RECOGNITION
# ==========================================================

recognizer = sr.Recognizer()

# Avoid unnecessarily long pauses before recognizing speech.
recognizer.pause_threshold = 0.7
recognizer.non_speaking_duration = 0.4
recognizer.dynamic_energy_threshold = True


def takeCommand():
    """Listen to the microphone and return recognized speech."""

    try:
        with sr.Microphone() as source:

            print("Listening...")

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=12
            )

        command = recognizer.recognize_google(
            audio,
            language="en-IN"
        )

        command = command.strip()

        print("Recognized speech:", command)

        return command.lower()

    except sr.WaitTimeoutError:
        return ""

    except sr.UnknownValueError:
        print("Phantom: Sorry, I couldn't understand.")
        return ""

    except sr.RequestError as e:
        print("Speech recognition service error:", e)
        return ""

    except Exception as e:
        print("Microphone error:", repr(e))
        return ""


# ==========================================================
# 5. KEEP YOUR EXISTING NEWS FUNCTION HERE
# ==========================================================

def get_news():
    """Fetch and read the latest available Indian headlines."""

    if not NEWS_API_KEY:
        speak(
            "The news API key is missing. "
            "Please add NEWS_API_KEY to your environment file."
        )
        return

    try:
        speak("Getting the latest news.")

        url = "https://newsapi.org/v2/top-headlines"

        response = requests.get(
            url,
            params={
                "country": "in",
                "apiKey": NEWS_API_KEY,
                "pageSize": 5,
            },
            timeout=15,
        )

        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            print("News API response:", data)
            speak("The news service returned an error.")
            return

        articles = data.get("articles", [])

        if not articles:
            speak("Sorry, I couldn't find any news headlines.")
            return

        for index, article in enumerate(articles, start=1):
            title = article.get("title")

            if not title:
                continue

            # Remove the publisher suffix sometimes added by NewsAPI
            title = title.split(" - ")[0]

            speak(f"Headline {index}. {title}")

    except requests.exceptions.Timeout:
        speak("The news request timed out. Please try again.")

    except requests.exceptions.RequestException as error:
        print("News network error:", repr(error))
        speak("I couldn't connect to the news service.")

    except Exception as error:
        print("News error:", repr(error))
        speak("Something went wrong while getting the news.")



# ==========================================================
# 6. COMMAND HANDLER
# ==========================================================

def handle_command(command):
    """Handle direct commands or send questions to Ollama."""

    command = command.lower().strip()

    if not command:
        return

    # ---------------- NEWS ----------------

    if any(phrase in command for phrase in [
        "tell me news",
        "latest news",
        "read the news",
        "what is the news",
        "news headlines",
        "news"
    ]):
        print("Phantom: News command detected.")

        try:
            get_news()
        except NameError:
            speak(
                "The news function has not been added yet. "
                "Please add your existing news code."
            )
        except Exception as e:
            print("News error:", repr(e))
            speak("Sorry, I couldn't retrieve the news.")

        return

    # ---------------- TIME ----------------

    if "what time" in command or "current time" in command:
        current_time = datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}.")
        return

    # ---------------- DATE ----------------

    if "what is the date" in command or "today's date" in command:
        current_date = datetime.now().strftime("%d %B %Y")
        speak(f"Today's date is {current_date}.")
        return

    # ---------------- WEBSITES ----------------

    if "open youtube" in command:
        speak("Opening YouTube.")
        webbrowser.open("https://www.youtube.com")
        return

    if "open google" in command:
        speak("Opening Google.")
        webbrowser.open("https://www.google.com")
        return

    if "open chatgpt" in command:
        speak("Opening ChatGPT.")
        webbrowser.open("https://chatgpt.com")
        return

    if "open github" in command:
        speak("Opening GitHub.")
        webbrowser.open("https://github.com")
        return

    # ---------------- EXIT ----------------

    if command in [
        "stop phantom",
        "exit phantom",
        "shutdown phantom",
        "quit phantom"
    ]:
        speak("Shutting down Phantom. Goodbye!")
        raise SystemExit

    # ---------------- GENERAL AI ----------------

    # Every other question goes to Ollama.
    answer = aiProcess(command)

    speak(answer)


# ==========================================================
# 7. MAIN ASSISTANT LOOP
# ==========================================================

def main():

    print("=" * 50)
    print("Initializing Phantom...")
    print("AI model:", OLLAMA_MODEL)
    print("=" * 50)

    # Verify Ollama is available before starting.
    try:
        ollama.list()
        print("Ollama connection successful.")

    except Exception as e:
        print("Cannot connect to Ollama:", repr(e))

        print(
            "Start Ollama and check that the model is installed."
        )

        return

    # Verify the selected model exists.
    try:
        model_list = ollama.list()

        installed_models = [
            model.model
            for model in model_list.models
        ]

        if not any(
            name.split(":")[0] == OLLAMA_MODEL.split(":")[0]
            and (
                ":" not in OLLAMA_MODEL
                or name.endswith(":" + OLLAMA_MODEL.split(":")[-1])
            )
            for name in installed_models
        ):
            print("Required model not found:", OLLAMA_MODEL)
            print("Installed models:", installed_models)
            print("Run: ollama pull " + OLLAMA_MODEL)
            return

    except Exception as e:
        print("Model verification error:", repr(e))
        return

    speak("Phantom is ready. Say Phantom to activate me.")

    while True:

        try:
            print("\nWaiting for wake word: Phantom")

            heard = takeCommand()

            if not heard:
                continue

            # Wait until the wake word is recognized.
            if ASSISTANT_NAME.lower() not in heard:
                continue

            speak("Yes, Boss.")

            # Allow commands in the same sentence:
            # "Phantom, what is Python?"
            command = heard.replace(
                ASSISTANT_NAME.lower(), ""
            ).strip(" ,.!?")

            if command:
                print("You said:", command)
                handle_command(command)

            else:
                # Wake word alone: listen for the next command.
                print("Phantom activated. Listening for command...")

                command = takeCommand()

                if command:
                    print("You said:", command)
                    handle_command(command)

        except SystemExit:
            break

        except KeyboardInterrupt:
            print("\nPhantom stopped.")
            break

        except Exception as e:
            print("Unexpected Phantom error:", repr(e))
            speak("Something went wrong. Please try again.")

            time.sleep(0.5)

    print("Phantom has stopped.")


# ==========================================================
# 8. START PHANTOM
# ==========================================================

if __name__ == "__main__":
    main()