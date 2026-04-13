import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

for m in client.models.list():
    if "embedContent" in [a for a in getattr(m, "supported_generation_methods", [])]:
        print("EMBED MODEL:", m.name)

# Also let's print all models just in case
print("All base models:")
for m in client.models.list():
    if not m.name.startswith("tunedModels"):
        print(m.name)
