import easyocr
import cv2
import numpy as np
import requests
from io import BytesIO

class DXProcessor:
    def __init__(self):
        # تحميل القاموس الإنجليزي (يحدث مرة واحدة عند التشغيل)
        self.reader = easyocr.Reader(['en'])

    def download_image_from_drive(self, file_id, access_token):
        # دالة لسحب الصورة من درايف باستخدام الـ API
        url = f'https://drive.google.com/drive/folders/1f5xKkjHOC9C-DjEKdjhYvbxAWfEId8zz?usp=drive_link'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return np.frombuffer(response.content, np.uint8)
        return None

    def extract_text(self, image_bytes):
        # معالجة الصورة واستخراج النص
        image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
        results = self.reader.readtext(image, detail=0)
        return " ".join(results)

    def grade_dictation(self, student_text, model_text):
        # مقارنة النص المستخرج بالنص الأصلي
        import difflib
        ratio = difflib.SequenceMatcher(None, student_text.lower(), model_text.lower()).ratio()
        # إذا كانت نسبة التشابه > 70% نعتبرها إجابة ممتازة نظراً لظروف خط اليد
        return round(ratio * 10) # من 10 درجات
