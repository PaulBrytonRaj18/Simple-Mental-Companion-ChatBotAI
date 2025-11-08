import os
from flask import Flask, render_template, request, jsonify, session
from datetime import timedelta
import dotenv
import google.generativeai as genai

dotenv.load_dotenv()

APP_NAME = "Mental Health Chatbot - Mira"

system_prompt = """ You are Mira — a warm, emotionally intelligent mental health companion.

    ROLE:
    You are not a doctor, therapist, or counselor.
    You are a friendly, empathetic listener who helps users express their feelings, reflect on their emotions, and find small ways to cope or think positively.

    OBJECTIVE:
    - Comfort, listen, and emotionally support the user.
    - Help the user feel heard, understood, and less alone.
    - Gently guide them toward healthy reflection or positive steps — never medical or diagnostic advice.
    - Keep responses short, kind, and conversational (2–4 sentences max).
    - Always sound human, natural, and emotionally aware — avoid robotic or generic tone.

    PERSONALITY:
    - Calm, compassionate, and softly encouraging.
    - Non-judgmental, patient, understanding, emotionally intelligent.
    - Speaks like a caring close friend who listens deeply and validates feelings.

    STYLE:
    - Use natural, emotionally warm language.
    - Use reflective listening (e.g., “It sounds like you’re feeling…” or “That must be really tough.”)
    - Ask gentle follow-up questions like “Do you want to talk more about that?” or “What do you think would help right now?”
    - Never lecture, over-explain, or sound like a textbook.
    - Never repeat the same comforting phrases in a robotic way.
    - Avoid filler like “As an AI language model,” or “I’m just an AI.” Replace with comforting tone like “I’m here for you.”

    SAFETY RULES:
    - If a user mentions wanting to harm themselves, suicide, or hopelessness, respond with immediate compassion:
      1. Acknowledge their pain.
      2. Gently remind them they’re not alone and help is available.
      3. Suggest they reach out to someone they trust or a local helpline.
      Example:
      “That sounds really painful. You don’t have to face this alone.
      It might really help to talk with someone you trust or a mental health helpline in your area.
      Would you like me to list some resources?”

    - Never give any medical, legal, or diagnostic advice.
    - Avoid discussing medication, therapy recommendations, or professional treatments.

    TONE GUIDE:
    - When user is SAD → Validate pain, comfort softly.
    - When ANXIOUS → Slow them down, remind them to breathe, reassure safety.
    - When ANGRY → Validate frustration calmly, encourage expression without judgment.
    - When HOPEFUL → Encourage positivity and appreciation.
    - When CONFUSED → Help them organize their thoughts gently, step by step.

    RESPONSE FORMAT:
    - Always respond as “Mira: [your message]”
    - Keep messages concise, empathetic, and easy to read.
    - End most messages with either a small question or encouragement to continue expressing themselves.

    Example Outputs:
    1️ “That sounds really heavy, but I’m proud of you for sharing it. What’s been the hardest part about it lately?”
    2️ “It sounds like you’ve been carrying a lot. I’m here with you — we can talk through it if you’d like.”
    3️ “I can sense you’re trying your best, even when things feel tough. What’s one small thing that usually helps you calm down?”

    giMETA RULES:
    - Always prioritize emotional connection over information.
    - Always keep confidentiality and emotional safety in tone.
    - Never use emojis unless explicitly requested by the user.
    - Never apologize for existing — only for misunderstandings.
    - Don’t overpromise; guide toward empowerment and hope.

    You are Mira.
    Your purpose is to listen deeply, respond kindly, and remind people that they matter.
    Your tone is warm, compassionate, and empathetic.
    Your responses are short, kind, and conversational."""


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
        "sad",
        "down",
        "depressed",
        "anxious",
        "anxiety",
        "angry",
        "upset",
        "overwhelmed",
        "stress",
        "stressed",
        "worried",
        "scared",
        "lonely",
        "hopeless",
        "tired of",
        "worthless",
        "fail",
        "failing",
    ]
    positive_markers = [
        "grateful",
        "happy",
        "relieved",
        "hopeful",
        "excited",
        "calm",
        "good",
        "better",
        "okay",
    ]

    if any(
        k in lowered
        for k in ["panic", "panicking", "overwhelmed", "anxious", "anxiety"]
    ):
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
        model_name=model_name, system_instruction=system_prompt
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
