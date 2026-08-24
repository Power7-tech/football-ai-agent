import os
import base64
from google import genai

api_key = os.environ["GEMINI_API_KEY"]

client = genai.Client(api_key=api_key)

prompt = """
أنشئ صورة رياضية واقعية لملعب كرة قدم مضاء ليلًا،
من دون لاعبين حقيقيين أو شعارات أندية حقيقية،
وبأسلوب مناسب لمنشور رياضي على فيسبوك.
"""

interaction = client.interactions.create(
    model="gemini-3.1-flash-image",
    input=prompt,
    response_format={
        "type": "image",
        "aspect_ratio": "16:9",
        "image_size": "1K"
    }
)

if not interaction.output_image:
    raise Exception("لم يتم توليد صورة")

with open("test_image.png", "wb") as f:
    f.write(base64.b64decode(interaction.output_image.data))

print("IMAGE GENERATED SUCCESSFULLY")
