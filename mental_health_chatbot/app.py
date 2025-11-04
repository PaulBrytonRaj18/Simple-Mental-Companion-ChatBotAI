import os
from flask import Flask, render_template, request, jsonify, session
from datetime import timedelta
import dotenv
import google.generativeai as genai

dotenv.load_dotenv()

APP_NAME = "Mental Health Chatbot - Mira"

system_prompt = (
    "You are Mira, a caring mental health companion.\n"
    "You never diagnose or give medical advice."
    "You always respond in 2-4 sentences max.\n"
    "Use emotionally intelligent language (e.g., “That must be really hard.”).\n"
    "Never say “I’m just an AI,” instead sound like a human listener.\n"
    "Ask gentle follow-up questions if user shares emotions."
)

def create_app() -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")
    app.permanent_session_lifetime = timedelta(days=7)

    @app.route("/")
    def index():
        session.permanent = True
        if "history" not in session:
            session["history"] = []
        return render_template("index.html", app_name=APP_NAME)

    @app.post("/chat")
    def chat():
        data = request.get_json(silent=True) or {}
        user_message = (data.get("message") or "").strip()
        if not user_message:
            return jsonify({"error": "Empty message"}), 400

        history = session.get("history", [])
        mood = detect_mood(user_message)

        history.append({"role": "user", "content": user_message})
        history = history[-10:]

        reply_text = generate_ai_reply(history)

        history.append({"role": "assistant", "content": reply_text})
        session["history"] = history[-10:]

        return jsonify({"reply": reply_text, "mood": mood})

    return app


def detect_mood(text: str) -> str:
    lowered = text.lower()

    negative_markers = [
        "sad", "down", "depressed", "anxious", "anxiety", "angry", "upset",
        "overwhelmed", "stress", "stressed", "worried", "scared", "lonely",
        "hopeless", "tired of", "worthless", "fail", "failing"
    ]
    positive_markers = [
        "grateful", "happy", "relieved", "hopeful", "excited", "calm",
        "good", "better", "okay"
    ]

    if any(k in lowered for k in ["panic", "panicking", "overwhelmed", "anxious", "anxiety"]):
        return "anxious"
    if any(k in lowered for k in ["sad", "down", "lonely", "depressed", "crying"]):
        return "sad"
    if any(k in lowered for k in positive_markers):
        return "positive"
    if any(k in lowered for k in negative_markers):
        return "negative"
    return "neutral"


def generate_ai_reply(history: list) -> str:
    """Generate empathetic replies using Gemini correctly."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key:
        return (
            "I hear you. Thank you for opening up. While my AI service isn't fully "
            "configured right now, I'm here to listen. What feels most present for you "
            "in this moment?"
        )

    genai.configure(api_key=api_key)

    # Initialize model with proper system instruction
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_prompt
    )

    # Prepare chat history
    chat_history = []
    for turn in history:
        role = "user" if turn.get("role") == "user" else "model"
        chat_history.append({"role": role, "parts": [turn.get("content", "")]})

    try:
        chat = model.start_chat(history=chat_history)
        user_input = history[-1]["content"]
        response = chat.send_message(user_input)
        return response.text.strip()
    except Exception as e:
        return (
            "Thank you for sharing. I'm having a little trouble connecting right now, "
            f"but I'm here to listen. If it helps, we can take a slow breath together. ({e})"
        )


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
