import os
import re
import time
import webbrowser
import requests
import speech_recognition as sr
import pyttsx3
import pygame
from dotenv import load_dotenv
from gtts import gTTS
from google import genai
from google.genai import types


# CONFIGURATION

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

MODEL_NAME = "gemini-3.8-flash"

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing. Check your .env file."
    )

client = genai.Client(api_key=GEMINI_API_KEY)

recognizer = sr.Recognizer()

# Speech recognition settings
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8
recognizer.non_speaking_duration = 0.5

# Load the music library safely
try:
    import musicLibrary
    MUSIC_LIBRARY = musicLibrary.music
except (ImportError, AttributeError) as error:
    print("Music library could not be loaded:", error)
    MUSIC_LIBRARY = {}



# TEXT-TO-SPEECH

def speak(text):
    """Speak text aloud and fall back to offline speech if needed."""

    if not text:
        return

    text = str(text).strip()

    if not text:
        return

    # Always display the response in the terminal
    print("\nPhantom:", text)

    # Prefer online, natural-sounding speech
    try:
        filename = "phantom_temp.mp3"

        tts = gTTS(text=text, lang="en")
        tts.save(filename)

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(20)

        pygame.mixer.music.unload()

        if os.path.exists(filename):
            os.remove(filename)

        return

    except Exception as error:
        print("Online speech error:", repr(error))

        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        except Exception:
            pass

        try:
            if os.path.exists("phantom_temp.mp3"):
                os.remove("phantom_temp.mp3")
        except OSError:
            pass

    # Offline fallback
    try:
        offline_engine = pyttsx3.init()
        offline_engine.say(text)
        offline_engine.runAndWait()
        offline_engine.stop()

    except Exception as error:
        print("Offline speech error:", repr(error))


# GEMINI AI

SYSTEM_INSTRUCTION = """
You are Phantom, a helpful personal AI voice assistant.

Rules:
1. You are Phantom, a helpful voice assistant.
2. Answer directly in simple English.
3. Keep answers concise, usually 2-5 sentences.
"""




def aiProcess(command):
    """Send the user's command to Gemini and return its answer."""

    command = command.strip()

    if not command:
        return "I didn't hear a question. Please try again."

    try:
        print("Sending question to Gemini...")

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=command,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.5,
                max_output_tokens=300,
            ),
        )

        answer = response.text

        if answer and answer.strip():
            return answer.strip()

        print("Gemini returned no text.")
        return (
            "I couldn't generate an answer. "
            "Please try asking in a different way."
        )

    except Exception as error:
        # Show the real error so you can diagnose it
        print("\n========== GEMINI ERROR ==========")
        print(repr(error))
        print("==================================\n")

        error_message = str(error).lower()

        if "api key" in error_message or "api_key" in error_message:
            return (
                "There may be a problem with my Gemini API key. "
                "Please check the key in your environment file."
            )

        if "429" in error_message or "resource_exhausted" in error_message:
            return (
                "My AI request limit may have been reached. "
                "Please check your Gemini API quota and try again later."
            )

        if "403" in error_message or "permission" in error_message:
            return (
                "I may not have permission to use this Gemini model. "
                "Please check your API key and project settings."
            )

        if "404" in error_message or "not found" in error_message:
            return (
                "The requested AI model may be unavailable. "
                "Check the model name and API access."
            )

        if "timeout" in error_message or "timed out" in error_message:
            return (
                "The AI request took too long. "
                "Please check your internet connection and try again."
            )

        return (
            "I couldn't get an answer from Gemini. "
            "Please check the terminal for the exact error."
        )



# NEWS

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



# WEBSITE COMMANDS

WEBSITES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "facebook": "https://www.facebook.com",
    "linkedin": "https://www.linkedin.com",
    "instagram": "https://www.instagram.com",
    "github": "https://github.com",
    "chatgpt": "https://chatgpt.com",
}


def open_website(command):
    """Open a supported website when the command matches."""

    command = command.lower().strip()

    match = re.fullmatch(
        r"(?:open|launch|go to)\s+(.+?)(?:\s+website)?[.!]?",
        command,
    )

    if not match:
        return False

    site = match.group(1).strip()

    if site in WEBSITES:
        webbrowser.open(WEBSITES[site])
        speak(f"Opening {site}.")
        return True

    return False


# MUSIC COMMANDS

def play_music(command):
    """Play a song from musicLibrary.py."""

    command = command.strip()

    match = re.match(
        r"^(?:play|play song)\s+(.+?)\s*$",
        command,
        flags=re.IGNORECASE,
    )

    if not match:
        return False

    song_name = match.group(1).strip().lower()

    # Try matching the complete song name first
    link = MUSIC_LIBRARY.get(song_name)

    # Otherwise, find a partial match
    if not link:
        for name, song_link in MUSIC_LIBRARY.items():
            if song_name in name.lower():
                link = song_link
                song_name = name
                break

    if not link:
        speak(
            f"I couldn't find {song_name} in your music library."
        )
        return True

    if not isinstance(link, str) or not link.startswith(
        ("https://", "http://")
    ):
        speak("The music link is invalid.")
        return True

    webbrowser.open(link)
    speak(f"Playing {song_name}.")
    return True


# COMMAND PROCESSING

def processCommand(command):
    """Process a recognized command."""

    command = command.strip()

    if not command:
        speak("I didn't hear your command. Please try again.")
        return

    print("\nYou said:", command)

    normalized = command.lower().strip()

    # Remove common wake-word prefixes if the user repeats them
    normalized = re.sub(
        r"^(?:hey\s+)?phantom[\s,.:!-]*",
        "",
        normalized,
    ).strip()

    if not normalized:
        speak("Yes Boss. What can I do for you?")
        return

    # Exit
    if normalized in {
        "exit",
        "quit",
        "stop phantom",
        "shut down phantom",
        "goodbye",
    }:
        speak("Goodbye Boss.")
        raise SystemExit

    # Website commands
    if open_website(normalized):
        return

    # Music commands
    if play_music(normalized):
        return

    # News commands
    if (
        normalized in {"news", "latest news", "read the news"}
        or "headlines" in normalized
    ):
        get_news()
        return

    # Everything else goes to Gemini
    answer = aiProcess(command)

    if answer:
        speak(answer)



# VOICE RECOGNITION

def listen_for_speech(source, timeout=8, phrase_time_limit=12):
    """
    Listen to one utterance and convert it to text.

    Returns None if speech could not be recognized.
    """

    try:
        audio = recognizer.listen(
            source,
            timeout=timeout,
            phrase_time_limit=phrase_time_limit,
        )

    except sr.WaitTimeoutError:
        print("No speech detected.")
        return None

    try:
        # Indian English recognition; change to 'en-US'
        # if that works better for your accent.
        text = recognizer.recognize_google(
            audio,
            language="en-IN",
        )

        print("Recognized speech:", text)
        return text.strip()

    except sr.UnknownValueError:
        print("Speech was unclear. Please try again.")
        return None

    except sr.RequestError as error:
        print("Speech recognition service error:", repr(error))
        speak("I cannot reach the speech recognition service.")
        return None


# MAIN LOOP

def main():
    print("=" * 45)
    print("Starting Phantom AI Assistant")
    print("=" * 45)

    speak("Initializing Phantom.")

    try:
        with sr.Microphone() as source:
            print("Calibrating microphone for background noise...")
            recognizer.adjust_for_ambient_noise(
                source,
                duration=1.5,
            )

            print("Microphone ready.")
            speak("Microphone ready. Say Phantom to activate me.")

            while True:
                try:
                    print("\nWaiting for wake word: Phantom")

                    wake_text = listen_for_speech(
                        source,
                        timeout=10,
                        phrase_time_limit=5,
                    )

                    if not wake_text:
                        continue

                    # Detect "Phantom" anywhere in the recognized phrase
                    wake_match = re.search(
                        r"\bphantom\b",
                        wake_text,
                        flags=re.IGNORECASE,
                    )

                    if not wake_match:
                        continue

                    # Support commands spoken in one sentence:
                    # "Phantom, what is Python?"
                    remaining_text = (
                        wake_text[wake_match.end():]
                        .strip(" ,.!?:;-")
                    )

                    speak("Yes Boss.")

                    if remaining_text:
                        processCommand(remaining_text)
                        continue

                    # Otherwise wait for a separate command
                    print("Phantom activated. Listening for command...")

                    command = listen_for_speech(
                        source,
                        timeout=8,
                        phrase_time_limit=15,
                    )

                    if command:
                        processCommand(command)
                    else:
                        speak("I didn't catch that. Please try again.")

                except SystemExit:
                    raise

                except Exception as error:
                    print("Command loop error:", repr(error))
                    speak("Something went wrong. I am still running.")
                    time.sleep(1)

    except OSError as error:
        print("Microphone or audio device error:", repr(error))
        print(
            "Check Windows microphone permissions, "
            "the selected input device, and your audio drivers."
        )

    except KeyboardInterrupt:
        print("\nPhantom stopped by keyboard.")

    finally:
        try:
            pygame.mixer.quit()
        except Exception:
            pass

        print("Phantom has stopped.")


if __name__ == "__main__":
    main()