
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import urllib.request
import urllib.error
import json
import os

load_dotenv()

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    if not data:
        return jsonify({"reply": "No message received."}), 400

    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please enter a message."}), 400

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return jsonify({"reply": "API Key is missing."}), 500

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": user_message}
                ]
            }
        ]
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        },
        method="POST"
    )

    try:

        with urllib.request.urlopen(req, timeout=60) as response:

            result = json.loads(response.read().decode("utf-8"))

            reply = result["candidates"][0]["content"]["parts"][0]["text"]

            return jsonify({"reply": reply})

    except urllib.error.HTTPError as error:

        details = error.read().decode("utf-8")
        print("Gemini API Error:", details)

        return jsonify({
            "reply": "Gemini API error. Check Terminal for details."
        }), 502

    except Exception as error:

        print("Application Error:", error)

        return jsonify({
            "reply": "Something went wrong. Please try again."
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
