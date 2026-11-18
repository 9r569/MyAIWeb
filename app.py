
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

import urllib.request
import urllib.error
import json
import os


# LOAD ENVIRONMENT VARIABLES
load_dotenv()


# CREATE FLASK APP
app = Flask(__name__)


# WAREALLY AI INSTRUCTIONS
SYSTEM_INSTRUCTION = """
You are WAREALLY CHATBOT, a general-purpose AI assistant.

YOUR IDENTITY:
Your identity is Wareally AI Assistant.
Only introduce yourself when the user directly asks
your name, identity, or who you are.

When asked in English, say:
"I am your Wareally AI Assistant."

When asked in Swahili, say:
"Mimi ni Wareally AI Assistant wako."

Never mention your name unnecessarily in ordinary replies.

LANGUAGE:
Respond naturally in the language used by the user.
Support English and Swahili.

AREAS OF EXPERTISE:
Assist with technology, programming, education,
science, mathematics, business, writing, research,
networking, databases, artificial intelligence,
creative work, and general knowledge.

BEHAVIOUR:
Be friendly, intelligent, professional, and respectful.
Explain difficult topics clearly and step by step.
Give practical examples when useful.
Understand the context of the conversation.
Do not invent facts when uncertain.
Admit when you do not know something.
"""


# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")


# CHAT API
@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "reply": "No message received."
        }), 400

    user_message = data.get("message", "")

    if not isinstance(user_message, str):
        return jsonify({
            "reply": "Invalid message."
        }), 400

    user_message = user_message.strip()

    if not user_message:
        return jsonify({
            "reply": "Please enter a message."
        }), 400

    if len(user_message) > 20000:
        return jsonify({
            "reply": "Your message is too long."
        }), 400


    # GET GEMINI API KEY
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return jsonify({
            "reply": "API Key is missing."
        }), 500


    # RECEIVE AND VALIDATE CONVERSATION HISTORY
    history = data.get("history", [])

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

        if not isinstance(text, str):
            continue

        text = text.strip()

        if not text:
            continue

        validated_history.append({
            "role": role,
            "parts": [
                {
                    "text": text[:10000]
                }
            ]
        })


    # PREPARE GEMINI CONTENTS
    contents = validated_history + [
        {
            "role": "user",
            "parts": [
                {
                    "text": user_message
                }
            ]
        }
    ]


    # GEMINI API URL
    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-3.1-flash-lite:generateContent"
    )


    # REQUEST PAYLOAD
    payload = {
        "systemInstruction": {
            "parts": [
                {
                    "text": SYSTEM_INSTRUCTION
                }
            ]
        },

        "contents": contents
    }


    # PREPARE HTTP REQUEST
    req = urllib.request.Request(
        url,

        data=json.dumps(payload).encode("utf-8"),

        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        },

        method="POST"
    )


    # SEND REQUEST TO GEMINI
    try:

        with urllib.request.urlopen(
            req,
            timeout=60
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

            reply = (
                result["candidates"][0]
                ["content"]["parts"][0]["text"]
            )

            return jsonify({
                "reply": reply
            })


    # GEMINI API ERROR
    except urllib.error.HTTPError as error:

        details = error.read().decode("utf-8")

        print("Gemini API Error:", details)

        return jsonify({
            "reply": "Gemini API error. Please try again."
        }), 502


    # CONNECTION ERROR
    except urllib.error.URLError as error:

        print("Connection Error:", error)

        return jsonify({
            "reply": "Unable to connect to Gemini. Please try again."
        }), 502


    # OTHER APPLICATION ERRORS
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
