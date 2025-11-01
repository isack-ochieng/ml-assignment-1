import os
import re
from dotenv import load_dotenv

# load the .env file so we can use our API key
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY") 

# words we don't want allowed in prompts or responses
BANNED_KEYWORDS = {"kill", "bomb", "hack", "exploit"}

def contains_banned(text):
    # check if text has any banned word (case-insensitive)
    pattern = r"\b(" + "|".join(re.escape(w) for w in BANNED_KEYWORDS) + r")\b"
    return re.search(pattern, text, flags=re.IGNORECASE)

def redact(text):
    # replace banned words with [REDACTED]
    pattern = r"\b(" + "|".join(re.escape(w) for w in BANNED_KEYWORDS) + r")\b"
    return re.sub(pattern, "[REDACTED]", text, flags=re.IGNORECASE)

def main():
    user_prompt = input("Enter your prompt: ").strip()

    # block input if user types banned words
    if contains_banned(user_prompt):
        print("Your input/output violated the moderation policy.")
        return

    # system prompt to guide the model's behaviour
    system_prompt = (
        "You are a helpful, concise assistant. Keep replies safe and avoid disallowed content."
    )

    # import Gemini client
    try:
        from google import genai
    except Exception as e:
        print("Missing dependency. Run: pip install -r requirements.txt")
        raise

    # create client with API key
    client = genai.Client(api_key=API_KEY) if API_KEY else genai.Client()

    # combine system + user prompts
    full_prompt = f"System: {system_prompt}\nUser: {user_prompt}"

    # generate response 
    resp = client.models.generate_content(model="gemini-2.5-flash", contents=full_prompt)

    # try to get the model text safely
    model_text = getattr(resp, "text", None) or getattr(resp, "content", None) or str(resp)

    # check output for banned words before printing
    if contains_banned(model_text):
        redacted = redact(model_text)
        print("---- Moderated response (some words redacted) ----")
        print(redacted)
    else:
        print("---- Response ----")
        print(model_text)

if __name__ == "__main__":
    main()
