import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from google import genai


# =========================
# المفاتيح
# =========================

gemini_api_key = os.environ["GEMINI_API_KEY"]
page_id = os.environ["FB_PAGE_ID"]
page_access_token = os.environ["FB_PAGE_ACCESS_TOKEN"]
football_api_key = os.environ["API_FOOTBALL_KEY"]

 
# =========================
# Gemini
# =========================

client = genai.Client(api_key=gemini_api_key)


# =========================
# توقيت الجزائر
# =========================

algeria_time = datetime.now(ZoneInfo("Africa/Algiers"))

hour = algeria_time.hour
today = algeria_time.strftime("%Y-%m-%d")

print("================================")
print("ALGERIA TIME:", algeria_time)
print("DATE:", today)
print("================================")


# =========================
# API-Football
# =========================

football_url = "https://v3.football.api-sports.io/fixtures"

football_response = requests.get(
    football_url,
    headers={
        "x-apisports-key": football_api_key
    },
    params={
        "date": today
    },
    timeout=30
)

print("FOOTBALL API STATUS:", football_response.status_code)

if football_response.status_code != 200:
    print("FOOTBALL API ERROR:")
    print(football_response.text)
    raise Exception("Football API error")


football_data = football_response.json()

fixtures = football_data.get("response", [])

print("NUMBER OF FIXTURES:", len(fixtures))


# =========================
# تجهيز المباريات
# =========================

matches = []

for fixture in fixtures[:30]:

    league = fixture["league"]["name"]

    home_team = fixture["teams"]["home"]["name"]
    away_team = fixture["teams"]["away"]["name"]

    match_date = fixture["fixture"]["date"]

    matches.append(
        f"""
البطولة: {league}
المباراة: {home_team} ضد {away_team}
الموعد: {match_date}
"""
    )


if matches:
    matches_text = "\n".join(matches)
else:
    matches_text = "لا توجد مباريات متاحة اليوم."


print("================================")
print("MATCH DATA:")
print(matches_text)
print("================================")


# =========================
# نوع المنشور
# =========================

if 11 <= hour < 15:

    post_type = """
اكتب منشورًا عن أبرز مباريات كرة القدم اليوم.
اختر مباراة أو مباراتين فقط من البيانات المتاحة.
"""

elif 15 <= hour < 20:

    post_type = """
اكتب منشورًا عن أبرز المباريات التي ستقام خلال الساعات القادمة.
اختر أهم مواجهة من البيانات المتاحة.
"""

else:

    post_type = """
اكتب منشورًا كرويًا مناسبًا لفترة المساء.
يمكنك الحديث عن مباراة بارزة من البيانات المتاحة.
"""


# =========================
# تعليمات Gemini
# =========================

prompt = f"""
أنت كاتب محتوى رياضي يدير صفحة كرة قدم على فيسبوك.

{post_type}

هذه هي البيانات الحقيقية التي حصلنا عليها من API-Football:

{matches_text}

اكتب منشورًا باللغة العربية الفصحى المعاصرة.

شروط مهمة جدًا:

- استخدم العربية الفصحى فقط.
- ممنوع استخدام أي لهجة عربية.
- اجعل الأسلوب طبيعيًا وبشريًا.
- اكتب كما يكتب صحفي رياضي أو مشجع حقيقي لكرة القدم.
- لا تجعل النص يبدو وكأنه مكتوب بواسطة الذكاء الاصطناعي.
- لا تستخدم عبارات محفوظة مثل:
  "في عالم كرة القدم"
  "لا شك أن"
  "مما لا شك فيه"
  "يعد من أبرز"
  "في إطار"
  "يشكل محطة مهمة".
- لا تستخدم لغة أكاديمية.
- لا تكرر نفس طريقة بداية المنشورات.
- لا تجعل المنشور طويلًا.
- لا تخترع أي مباراة أو موعد أو نتيجة.
- استخدم المعلومات الموجودة في البيانات فقط.
- لا تذكر معلومات غير موجودة في البيانات.
- لا تقل "وفقًا للبيانات".
- لا تقل إنك ذكاء اصطناعي.
- لا تستخدم أكثر من 2 رمز تعبيري.
- استخدم 0 إلى 3 هاشتاغات فقط.
- لا تضع عنوانًا منفصلًا إذا لم يكن ضروريًا.
- اجعل المنشور جذابًا ويشجع القارئ على الاهتمام بالمباراة بشكل طبيعي.

أخرج المنشور فقط.
"""


# =========================
# Gemini
# =========================

print("MODEL USED: gemini-3.6-flash")

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt
)

message = response.text.strip()

print("================================")
print("GENERATED POST:")
print(message)
print("================================")


# =========================
# Facebook
# =========================

facebook_url = f"https://graph.facebook.com/v26.0/{page_id}/feed"

facebook_response = requests.post(
    facebook_url,
    data={
        "message": message,
        "access_token": page_access_token
    },
    timeout=30
)

print("FACEBOOK STATUS:", facebook_response.status_code)

print("FACEBOOK RESPONSE:")
print(facebook_response.json())


if facebook_response.status_code >= 400:
    raise Exception("Facebook API error")


print("================================")
print("POST PUBLISHED SUCCESSFULLY")
print("================================")
