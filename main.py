import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from google import genai


# =========================
# الإعدادات
# =========================

gemini_api_key = os.environ["GEMINI_API_KEY"]
page_id = os.environ["FB_PAGE_ID"]
page_access_token = os.environ["FB_PAGE_ACCESS_TOKEN"]
football_api_key = os.environ["API_FOOTBALL_KEY"]

client = genai.Client(api_key=gemini_api_key)


# =========================
# توقيت الجزائر
# =========================

algeria_time = datetime.now(ZoneInfo("Africa/Algiers"))
hour = algeria_time.hour
today = algeria_time.strftime("%Y-%m-%d")

print("ALGERIA TIME:", algeria_time.strftime("%Y-%m-%d %H:%M:%S"))
print("DATE:", today)


# =========================
# جلب مباريات اليوم
# =========================

football_response = requests.get(
    "https://v3.football.api-sports.io/fixtures",
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
    print("FOOTBALL API ERROR:", football_response.text)
    raise Exception("Football API error")

football_data = football_response.json()

fixtures = football_data.get("response", [])

print("NUMBER OF FIXTURES:", len(fixtures))


# =========================
# تجهيز بيانات المباريات
# =========================

matches_text = ""

for fixture in fixtures[:30]:
    league = fixture["league"]["name"]

    home_team = fixture["teams"]["home"]["name"]
    away_team = fixture["teams"]["away"]["name"]

    match_time = fixture["fixture"]["date"]

    matches_text += (
        f"- البطولة: {league}\n"
        f"  المباراة: {home_team} ضد {away_team}\n"
        f"  الموعد: {match_time}\n\n"
    )


if not matches_text:
    matches_text = "لا توجد مباريات متاحة في بيانات API-Football لهذا اليوم."


print("MATCH DATA:")
print(matches_text)


# =========================
# تحديد نوع المنشور
# =========================

if 11 <= hour < 15:

    post_type = """
اكتب منشورًا عن أبرز مباريات كرة القدم المقررة اليوم.
اختر المباريات الأكثر أهمية من البيانات المتاحة.
"""

elif 15 <= hour < 20:

    post_type = """
اكتب منشورًا عن المباريات التي تستحق المتابعة خلال الفترة القادمة.
ركز على أبرز المواجهات الموجودة في البيانات.
"""

else:

    post_type = """
اكتب منشورًا كرويًا مناسبًا لفترة المساء.
إذا كانت هناك مباريات انتهت وكانت بيانات النتائج متاحة، يمكنك الإشارة إليها.
وإلا فاكتب عن أبرز مباراة أو مواجهة موجودة في البيانات.
"""


# =========================
# تعليمات Gemini
# =========================

prompt = f"""
أنت محرر رياضي يدير صفحة كرة قدم على فيسبوك.

{post_type}

بيانات المباريات التي حصلنا عليها من مصدر خارجي:

{matches_text}

قواعد الكتابة:

- اكتب باللغة العربية الفصحى المعاصرة فقط.
- ممنوع استخدام اللهجات العربية العامية.
- اجعل الأسلوب طبيعيًا وبشريًا وكأنه مكتوب من صحفي أو مشجع حقيقي لكرة القدم.
- لا تجعل النص يبدو كإجابة من روبوت أو نموذج ذكاء اصطناعي.
- تجنب العبارات النمطية مثل:
  "في عالم كرة القدم"
  "لا شك أن"
  "مما لا شك فيه"
  "يعد من أبرز"
  "في إطار"
  "يشكل محطة مهمة".
- لا تستخدم أسلوبًا أكاديميًا أو رسميًا بشكل مبالغ فيه.
- لا تكرر نفس أسلوب بداية المنشورات السابقة.
- لا تجعل المنشور طويلًا.
- اجعل المنشور مناسبًا لفيسبوك.
- استخدم المعلومات الموجودة في البيانات فقط.
- لا تخترع أي مباراة أو نتيجة أو موعد أو لاعب أو معلومة.
- إذا لم تكن هناك معلومات كافية، اكتب منشورًا عامًا بدل اختلاق المعلومات.
- لا تذكر أنك ذكاء اصطناعي.
- لا تقل "وفقًا للبيانات".
- لا تستخدم عددًا كبيرًا من الرموز التعبيرية.
- لا تضع أكثر من 2 أو 3 رموز تعبيرية عند الحاجة.
- لا تضع قائمة طويلة من الهاشتاغات.
- استخدم من 0 إلى 3 هاشتاغات فقط عند الحاجة.

أخرج المنشور فقط، دون شرح أو مقدمات.
"""


# =========================
# توليد المنشور
# =========================

print("MODEL USED: gemini-3.6-flash")

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt
)

message = response.text.strip()

print("GENERATED POST:")
print(message)


# =========================
# نشر المنشور على Facebook
# =========================

facebook_url = f"https://graph.facebook.com/v26.0/{page_id}/feed"

facebook_response = requests.post(
    facebook_url,
    data={
        "message": message,
        "access_token": page_access_token,
    },
    timeout=30
)

print("FACEBOOK STATUS:", facebook_response.status_code)
print("FACEBOOK RESPONSE:", facebook_response.json())

if facebook_response.status_code >= 400:
    raise Exception("Facebook API error")

print("POST PUBLISHED SUCCESSFULLY")
