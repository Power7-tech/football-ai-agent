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
# أولوية البطولات
# =========================

league_priority = {
    "UEFA Champions League": 100,
    "Champions League": 100,

    "Premier League": 95,
    "La Liga": 95,
    "Serie A": 95,
    "Bundesliga": 95,
    "Ligue 1": 90,

    "UEFA Europa League": 88,
    "Europa League": 88,
    "UEFA Conference League": 80,

    "Liga Profesional Argentina": 75,
    "Liga Profesional": 75,
    "MLS": 65,
    "Liga MX": 65,
    "Primera Division": 55,
    "Primera División": 55,
}


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

prepared_matches = []

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

    priority = league_priority.get(league, 40)

    prepared_matches.append({
        "priority": priority,
        "league": league,
        "home": home_team,
        "away": away_team,
        "time": match_time
    })


# =========================
# ترتيب المباريات
# =========================

prepared_matches.sort(
    key=lambda match: match["priority"],
    reverse=True
)


# =========================
# إرسال أهم المباريات فقط إلى Gemini
# =========================

top_matches = prepared_matches[:20]

matches_text = ""

for match in top_matches:

    matches_text += (
        f"- البطولة: {match['league']}\n"
        f"  المباراة: {match['home']} ضد {match['away']}\n"
        f"  الوقت بتوقيت الجزائر: {match['time']}\n\n"
    )


if not matches_text:
    matches_text = "لا توجد مباريات متاحة اليوم."


print("================================")
print("TOP MATCHES:")
print(matches_text)
print("================================")


# =========================
# تحديد نوع المنشور
# =========================

if 11 <= hour < 15:

    period_instruction = """
اختر مباراة مهمة تقام اليوم، ويفضل أن تكون في وقت مناسب للمتابعة.
"""

elif 15 <= hour < 20:

    period_instruction = """
اختر أبرز مباراة ستقام خلال الساعات القادمة.
"""

else:

    period_instruction = """
اختر أبرز مباراة في الفترة المسائية.
"""


# =========================
# تعليمات Gemini
# =========================

prompt = f"""
أنت محرر رياضي يدير صفحة كرة قدم على فيسبوك.

مهمتك اختيار مباراة واحدة فقط من القائمة وكتابة منشور قصير عنها.

{period_instruction}

هذه أهم المباريات المتاحة اليوم:

{matches_text}

قواعد اختيار المباراة:

- اختر مباراة واحدة فقط.
- أعط الأولوية للمباراة الأكثر أهمية وشهرة.
- لا تعتمد على ترتيب القائمة وحده.
- إذا وجدت مواجهة بين أندية كبيرة، أعطها أولوية.
- لا تختر مباراة من بطولة ضعيفة إذا كانت هناك مواجهة أقوى بوضوح.
- لا تخترع أي معلومة غير موجودة في البيانات.

قواعد الكتابة:

- العربية الفصحى المعاصرة فقط.
- ممنوع استخدام اللهجات.
- اكتب بأسلوب طبيعي جدًا يشبه منشورات صفحات كرة القدم الحقيقية.
- اجعل المنشور قصيرًا ومباشرًا.
- لا تكتب مقدمة عامة عن كرة القدم.
- لا تستخدم عبارات مثل:
  "في عالم كرة القدم"
  "لا شك أن"
  "مما لا شك فيه"
  "عشاق كرة القدم على موعد"
  "تتجه الأنظار"
  "في مواجهة مرتقبة"
  "موقعة نارية"
  "ملحمة كروية".
- لا تكتب معلومات عن تاريخ الفريقين أو اللاعبين إلا إذا كانت موجودة في البيانات.
- لا تخترع نتائج أو إصابات أو ترتيبًا أو إحصائيات.
- اذكر البطولة والمباراة والموعد.
- يمكنك إنهاء المنشور بسؤال قصير للمتابعين.
- استخدم رمزًا تعبيريًا واحدًا أو اثنين فقط.
- استخدم هاشتاغين كحد أقصى.
- لا تجعل المنشور يبدو وكأنه نص مولد آليًا.
- غيّر أسلوب صياغة المنشورات من مرة إلى أخرى.

مثال على الأسلوب المطلوب:

"تشيلسي وفولهام في مواجهة لندنية الليلة ضمن الدوري الإنجليزي الممتاز.
البداية عند 20:00 بتوقيت الجزائر. ⚽
من تتوقعون أن يحسم الديربي؟"

هذا المثال يوضح الأسلوب فقط، ولا تستخدم أسماءه أو معلوماته إلا إذا كانت المباراة موجودة في البيانات.

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
# النشر على Facebook
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
