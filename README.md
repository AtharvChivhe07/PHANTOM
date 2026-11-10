# 👻 Phantom – AI Voice Assistant

**Phantom** is a Python-based personal AI voice assistant designed to make computer interactions easier through voice commands and AI-powered conversations.

It uses speech recognition to listen to user commands, Google Gemini AI to generate intelligent responses, and text-to-speech technology to communicate with users.

## 🚀 Features

- **Wake Word Detection:** Activates when the user says "Phantom".
- **Voice Recognition:** Listens to and processes voice commands.
- **AI-Powered Responses:** Uses Google Gemini Gen AI to answer questions.
- **Text-to-Speech:** Converts AI responses into spoken audio.
- **Web Automation:** Opens websites such as Google, YouTube and ChatGPT.
- **News Feature:** Provides news-related information.
- **Voice Interaction:** Allows users to interact without constantly typing.

## 🛠️ Technologies Used

- Python
- Google Gemini API (Gen AI)
- SpeechRecognition
- PyAudio
- pyttsx3
- gTTS
- Pygame
- Python-dotenv

## 📁 Project Structure

```text
Phantom/
│
├── main.py
├── news.py
├── requirements.txt
├── README.md
├── .gitignore
└── .env
```

*Note: `.env` is used locally for storing API keys and must never be uploaded to GitHub.*

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Open the project directory

```bash
cd Phantom
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

For Windows:

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure your API key

Create a `.env` file in the project directory and add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

Never share or upload your actual API key.

### 7. Run Phantom

```bash
python main.py
```

## 🎯 Project Objective

The main objective of Phantom is to explore Python programming, artificial intelligence, speech recognition, voice automation and API integration by developing a personal voice assistant.

## 🔮 Future Improvements

- Add more intelligent voice commands.
- Improve speech recognition accuracy.
- Add more computer automation features.
- Improve response speed.
- Introduce a graphical user interface (GUI).
- Expand AI capabilities.

## 👨‍💻 Developer

Developed as a personal Python learning project to explore AI-powered voice assistants and automation.

**Built with Python ❤️**