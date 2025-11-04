# Mental Health Chatbot (Mira)

A gentle, empathetic AI companion named Mira that chats with users about their feelings. Built with Flask and the Gemini API.

## Features
- Warm, non-judgmental responses with a safety note for crisis situations
- Clean, calming UI with chat history
- Typing indicator ("Mira is thinking…")
- Simple mood detection on each input
- Maintains the last 10 messages for context

## Tech Stack
- Backend: Flask (Python)
- Frontend: HTML, CSS, JS (vanilla)
- AI: Google Gemini via `google-genai`

## Setup
1. Clone this repository and move into the folder.
2. Create a virtual environment (optional but recommended).
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set your environment variables (at minimum, your Gemini API key). You can put these in a `.env` file in the project root (auto-loaded):
   ```env
   GOOGLE_API_KEY=YOUR_API_KEY
   GEMINI_MODEL=gemini-2.5-flash
   FLASK_SECRET_KEY=change-me
   ```
   Or set them manually:
   - On macOS/Linux:
     ```bash
     export GOOGLE_API_KEY=YOUR_API_KEY
     export GEMINI_MODEL=gemini-2.5-flash   # optional, defaults to this
     export FLASK_SECRET_KEY=change-me      # optional
     ```
   - On Windows (PowerShell):
     ```powershell
     setx GOOGLE_API_KEY "YOUR_API_KEY"
     setx GEMINI_MODEL "gemini-2.5-flash"
     setx FLASK_SECRET_KEY "change-me"
     ```

## Run Locally
```bash
python app.py
```
Visit `http://localhost:5000` in your browser.

## Deploy
- Render/Replit: Configure a Python web service, set `GOOGLE_API_KEY` (and optional `GEMINI_MODEL`, `FLASK_SECRET_KEY`) in environment. Set start command to `python app.py`.
- The app binds to `0.0.0.0` and respects the `PORT` environment variable when present.

## Notes
- Mira is supportive and not a medical professional. For crisis situations, encourage contacting a trusted person or local helpline.
- The code uses the `google-genai` Python SDK. Ensure your API key has access to the selected Gemini model.


