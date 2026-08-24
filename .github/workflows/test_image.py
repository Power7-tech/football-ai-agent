import os
from google import genai

api_key = os.environ["GEMINI_API_KEY"]

client = genai.Client(api_key=api_key)

print("================================")
print("TESTING GEMINI IMAGE GENERATION")
print("================================")

response = client.models.generate_content(
    model="gemini-3.1-flash-image",
    contents="Create a realistic football stadium at night, suitable for a football news Facebook post."
)

print("================================")
print("IMAGE GENERATION REQUEST COMPLETED")
print("================================")

print(response)
