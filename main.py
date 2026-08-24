import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from google import genai

gemini_api_key = os.environ["GEMINI_API_KEY"]
page_id = os.environ["FB_PAGE_ID"]
page_access_token = os.environ["FB_PAGE_ACCESS_TOKEN"]

client = genai.Client(api_key=gemini_api_key)

# توقيت الجزائر
algeria_time = datetime.now(ZoneInfo("Africa/Algiers"))
hour = algeria_time.hour

# أسلوب الكتابة المشترك
style_rules = """
اكتب بأسلوب بشري طبيعي، وكأنك صحفي أو مشجع لكرة القدم يكتب منشورًا لصفحة فيسبوك.

قواعد الأسلوب:
- استخدم العربية الفصحى المعاصرة، وليس أي لهجة عامية.
- اجعل اللغة طبيعية وسلسة وغير متكلفة.
- لا تستخدم أسلوبًا أكاديميًا أو رسميًا أكثر من اللازم.
- لا تستخدم عبارات نمطية توحي بأن النص مولّد بالذكاء الاصطناعي، مثل:
  "في عالم كرة القدم"، "لا شك أن"، "مما لا شك فيه"،
  "يُعد من أبرز"، "في إطار"، "يشكل محطة مهمة".
- لا تبدأ المنشور دائمًا بالطريقة نفسها.
- غيّر بنية الجمل وطولها من منشور إلى آخر.
- تجنب التكرار في الكلمات والتعبيرات.
- لا تشرح الموضوع بطريقة مدرسية.
- لا تضع عنوانًا منفصلًا إلا إذا كان ذلك مفيدًا فعلًا.
- لا تفرط في استخدام علامات التعجب.
- لا تضع عددًا كبيرًا من الرموز التعبيرية.
- اجعل المنشور يبدو وكأنه كُتب في لحظته من شخص يتابع كرة القدم.
- لا تقل إنك ذكاء اصطناعي، ولا تتحدث عن طريقة توليد النص.
- لا تخترع أخبارًا أو نتائج أو مواعيد أو أرقامًا.
- إذا لم تكن متأكدًا من معلومة، فلا تذكرها باعتبارها حقيقة.
"""

if 11 <= hour < 15:
    prompt = style_rules + """
اكتب منشورًا قصيرًا عن كرة القدم يناسب فترة الظهيرة.

يمكن أن يتناول أبرز ما ينتظر جماهير كرة القدم خلال اليوم، لكن لا تذكر مباريات أو مواعيد محددة إلا إذا كانت المعلومات مؤكدة.

اجعل المنشور جذابًا ويشجع القارئ على التفاعل، من دون طرح سؤال مصطنع في نهايته.
"""

elif 15 <= hour < 20:
    prompt = style_rules + """
اكتب منشورًا قصيرًا عن أجواء كرة القدم قبل مباريات المساء.

ركز على الحماس والترقب وما يجعل مباريات كرة القدم ممتعة للجماهير، من دون اختلاق أخبار أو مواعيد أو نتائج.

اجعل النص يبدو كمنشور كتبه مشجع لكرة القدم في لحظته.
"""

else:
    prompt = style_rules + """
اكتب منشورًا قصيرًا عن كرة القدم مناسبًا لفترة المساء.

يمكن أن يتناول لاعبًا، فريقًا، موقفًا كرويًا، تكتيكًا، أو لحظة تاريخية معروفة.

اختر فكرة واحدة فقط وقدمها بطريقة طبيعية وممتعة، دون تحويل المنشور إلى مقال طويل.
"""

print("ALGERIA TIME:", algeria_time.strftime("%Y-%m-%d %H:%M:%S"))
print("MODEL USED:", "gemini-3.6-flash")

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
