from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()

for m in ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash"]:
    try:
        r = client.models.generate_content(model=m, contents="Say OK")
        print(m, "->", r.text.strip())
    except Exception as e:
        print(m, "-> FAILED:", str(e)[:80])