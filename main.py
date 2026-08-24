import os
import requests
from google import genai

gemini_api_key = os.environ["GEMINI_API_KEY"]
page_id = os.environ["FB_PAGE_ID"]
page_access_token = os.environ["FB_PAGE_ACCESS_TOKEN"]

client = genai.Client(api_key=gemini_api_key)

prompt = """
اكتب منشورًا قصيرًا وجذابًا عن كرة القدم لصفحة فيسبوك.
اجعله باللغة العربية، بأسلوب حماسي، ومن دون اختلاق أخبار أو نتائج.
"""

response = client.models.generate_content(
   model="gemini-3.6-flash",
    contents=prompt
)

message = response.text.strip()

url = f"https://graph.facebook.com/v26.0/{page_id}/feed"

result = requests.post(
    url,
    data={
        "message": message,
        "access_token": page_access_token,
    },
)

print(result.json())

if result.status_code >= 400:
    raise Exception("Facebook API error")
