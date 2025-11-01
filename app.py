# app.py
import os
import re
from dotenv import load_dotenv

# load .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")  # put GEMINI_API_KEY=... in your .env

# simple banned keyword list (expand as needed)
BANNED_KEYWORDS = {"kill", "bomb", "hack", "exploit"}

def contains_banned(text):
    # whole-word, case-insensitive match
    pattern = r"\\b(" + "|".join(re.escape(w) for w in BANNED_KEYWORDS) + r")\\b"
    return re.search(pattern, text, flags=re.IGNORECASE)

def redact(text):
    pattern = r"\\b(" + "|".join(re.escape(w) for w in BANNED_KEYWORDS) + r")\\b"
    return re.sub(pattern, "[REDACTED]", text, flags=re.IGNORECASE)

def main():
    user_prompt = input("Enter your prompt: ").strip()
    # 1) Input moderation
    if contains_banned(user_prompt):
        print("Your input/output violated the moderation policy.")
        return

    # 2) System prompt (guides model behavior)
    system_prompt = (
        "You are a helpful, concise assistant. Keep replies safe and avoid disallowed content."
    )

    # 3) Call Gemini (google-genai)
    try:
        from google import genai
    except Exception as e:
        print("Missing dependency. Run: pip install -r requirements.txt")
        raise

    client = genai.Client(api_key=API_KEY) if API_KEY else genai.Client()

    # Simple approach: pass system + user prompts combined
    full_prompt = f"System: {system_prompt}\\nUser: {user_prompt}"

    # Using the text generation method (example model name)
    # Model names change over time; 'gemini-2.5-flash' is a common choice for text gen.
    resp = client.models.generate_content(model="gemini-2.5-flash", contents=full_prompt)

    # many SDK responses expose .text or .content; here we try common fields
    model_text = getattr(resp, "text", None) or getattr(resp, "content", None) or str(resp)

    # 4) Output moderation: redact banned words
    if contains_banned(model_text):
        redacted = redact(model_text)
        print("---- Moderated response (some words redacted) ----")
        print(redacted)
    else:
        print("---- Response ----")
        print(model_text)

if __name__ == "__main__":
    main()



































































































































































































































































































































































