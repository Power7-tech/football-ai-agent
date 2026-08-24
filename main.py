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

client = genai.Client(api_key=gemini_api_key)


# =========================
# توقيت الجزائر
# =========================

algeria_tz = ZoneInfo("Africa/Algiers")
algeria_time = datetime.now(algeria_tz)

hour = algeria_time.hour
today = algeria_time.strftime("%Y-%m-%d")

print("================================")
print("ALGERIA TIME:", algeria_time.strftime("%Y-%m-%d %H:%M:%S"))
print("DATE:", today)
print("================================")


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

for fixture in fixtures:

    league = fixture["league"]["name"]

    home_team = fixture["teams"]["home"]["name"]
    away_team = fixture["teams"]["away"]["name"]

    utc_date = fixture["fixture"]["date"]

    try:
        match_datetime = datetime.fromisoformat(
            utc_date.replace("Z", "+00:00")
        )

        local_datetime = match_datetime.astimezone(algeria_tz)

        match_time = local_datetime.strftime("%H:%M")

    except Exception:
        match_time = utc_date

    matches.append(
        f"- البطولة: {league}\n"
        f"  المباراة: {home_team} ضد {away_team}\n"
        f"  الوقت بتوقيت الجزائر: {match_time}\n"
    )


if not matches:
    matches_text = "لا توجد مباريات متاحة اليوم."

else:
    matches_text = "\n".join(matches)


print("================================")
print("MATCH DATA:")
print(matches_text)
print("================================")


# =========================
# تحديد الفترة
# =========================

if 11 <= hour < 15:

    period_instruction = """
ركز على مباراة مهمة تقام اليوم، ويفضل أن تكون من بطولة معروفة.
"""

elif 15 <= hour < 20:

    period_instruction = """
ركز على أقرب مباراة مهمة تستحق المتابعة خلال الساعات القادمة.
"""

else:

    period_instruction = """
ركز على أبرز مباراة في الفترة المسائية.
"""


# =========================
# Prompt
# =========================

prompt = f"""
أنت محرر رياضي يدير صفحة كرة قدم على فيسبوك.

مهمتك اختيار مباراة واحدة فقط من القائمة وكتابة منشور قصير عنها.

{period_instruction}

قائمة مباريات اليوم:

{matches_text}

قواعد مهمة:

- اختر مباراة واحدة فقط.
- أعط الأولوية للمباريات بين الأندية المعروفة أو المباريات الكبيرة.
- لا تختر مباراة عشوائية من البطولات الأقل أهمية إذا كانت هناك مواجهة أقوى في القائمة.
- استخدم اسم البطولة واسم الفريقين والموعد فقط إذا كانت المعلومات موجودة.
- لا تخترع أي معلومة.
- لا تتحدث عن نتيجة المباراة إلا إذا كانت النتيجة موجودة بوضوح في البيانات.
- اكتب بالعربية الفصحى المعاصرة.
- ممنوع استخدام اللهجات.
- اجعل الأسلوب طبيعيًا جدًا، كأنه منشور كتبه شخص يتابع كرة القدم فعلًا.
- لا تستخدم أسلوبًا صحفيًا رسميًا مبالغًا فيه.
- لا تستخدم مقدمات عامة.
- لا تبدأ بعبارات مثل:
  "في عالم كرة القدم"
  "لا شك أن"
  "مما لا شك فيه"
  "عشاق كرة القدم على موعد"
  "تتجه الأنظار"
  "في مواجهة مرتقبة"
  "يعد من أبرز"
  "يشكل محطة مهمة".
- لا تستخدم عبارات مبالغًا فيها مثل:
  "موقعة نارية"
  "قمة كروية تاريخية"
  "ملحمة كروية".
- لا تكرر نفس طريقة الكتابة في كل منشور.
- لا تجعل المنشور يبدو وكأنه نص مولد آليًا.
- اجعل المنشور بين 2 و4 أسطر تقريبًا.
- يمكن طرح سؤال بسيط في النهاية لزيادة التفاعل.
- استخدم رمزًا تعبيريًا واحدًا أو اثنين فقط عند الحاجة.
- استخدم هاشتاغين كحد أقصى.
- لا تذكر أنك ذكاء اصطناعي.
- لا تقل "وفقًا للبيانات".
- أخرج المنشور فقط دون شرح.

يجب أن يكون المنشور قريبًا من أسلوب منشور طبيعي على صفحة رياضية، وليس مقالًا صحفيًا.
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
