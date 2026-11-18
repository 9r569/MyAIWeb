from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

import urllib.request
import urllib.error
import json
import os


# Load environment variables
load_dotenv()


# Create Flask application
app = Flask(__name__)


# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")


# CHAT API
@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    if not data:
        return jsonify({
            "reply": "No message received."
        }), 400

    user_message = data.get("message", "").strip()
     
history = data.get("history", [])

# Validate conversation history
if not isinstance(history, list):
    history = []

history = history[-20:]

validated_history = []

for item in history:

    if not isinstance(item, dict):
        continue

    role = item.get("role")
    parts = item.get("parts")

    if role not in ("user", "model"):
        continue

    if not isinstance(parts, list) or not parts:
        continue

    if not isinstance(parts[0], dict):
        continue

    text = parts[0].get("text")

    if isinstance(text, str) and text.strip():

        validated_history.append({
            "role": role,
            "parts": [
                {"text": text[:10000]}
            ]
        })


    if not user_message:
        return jsonify({
            "reply": "Please enter a message."
        }), 400

    # Get Gemini API Key
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return jsonify({
            "reply": "API Key is missing."
        }), 500


    # Gemini API URL
    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-3.1-flash-lite:generateContent"
    )


    # WAREALLY AI IDENTITY AND INSTRUCTIONS
           
payload = {

    "systemInstruction": {
        "parts": [
            {
                "text": (
                    "You are WAREALLY CHATBOT, a general-purpose AI assistant. "
                    "Your identity is Wareally AI Assistant. "

                    "Only introduce yourself when the user directly asks "
                    "your name, identity, or who you are. "

                    "When asked, say: "
                    "'I am your Wareally AI Assistant.' "

                    "In Swahili, say: "
                    "'Mimi ni Wareally AI Assistant wako.' "

                    "Never mention your name unnecessarily. "

                    "Respond naturally in the language used by the user. "
                    "Support English and Swahili. "

                    "Assist with technology, programming, education, "
                    "science, mathematics, business, writing, research, "
                    "networking, databases, artificial intelligence, "
                    "creative work, and general knowledge. "

                    "Be friendly, intelligent, professional, and respectful. "
                    "Explain difficult topics clearly and step by step. "
                    "Do not invent facts when uncertain."
                )
            }
        ]
    },

    "contents": validated_history + [
        {
            "role": "user",
            "parts": [
                {
                    "text": user_message
                }
            ]
        }
    ]
}


    # Prepare API Request
    req = urllib.request.Request(
        url,

        data=json.dumps(payload).encode("utf-8"),

        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        },

        method="POST"
    )


    # Send Request to Gemini
    try:

        with urllib.request.urlopen(req, timeout=60) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

            reply = result["candidates"][0]["content"]["parts"][0]["text"]

            return jsonify({
                "reply": reply
            })


    # Handle Gemini API Errors
    except urllib.error.HTTPError as error:

        details = error.read().decode("utf-8")

        print("Gemini API Error:", details)

        return jsonify({
            "reply": "Gemini API error. Check Terminal for details."
        }), 502


    # Handle Other Errors
    except Exception as error:

        print("Application Error:", error)

        return jsonify({
            "reply": "Something went wrong. Please try again."
        }), 500


# RUN APPLICATION
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
