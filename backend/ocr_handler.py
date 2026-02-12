import easyocr
import cv2
import numpy as np
import requests
import re
import difflib

class DXProcessor:
    def __init__(self):
        # تحميل القاموس الإنجليزي
        self.reader = easyocr.Reader(['en'], gpu=False)

    def download_public_image(self, url):
        """تحميل الصورة من جوجل درايف العام"""
        try:
            if 'drive.google.com' in url:
                # استخراج الـ ID للتحميل المباشر
                file_id = url.split('/')[-2] if '/view' in url else url.split('id=')[-1]
                download_url = f'https://drive.google.com/uc?export=download&id={file_id}'
            else:
                download_url = url
                
            response = requests.get(download_url)
            if response.status_code == 200:
                image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        except Exception as e:
            print(f"❌ Image Download Error: {e}")
        return None

   def grade_dictation(self, student_text, model_text):
        """مقارنة مرنة تعتمد على الكلمات المفتاحية لتجاوز أخطاء الـ OCR البسيطة"""
        # الرد النموذجي المدمج
        model_text = """
        R-down-down. up - semi
        circle and slash down.
        r. down and up with
        curve. between 2 Lines.
        S-curve up - slash
        """
        
        # تنظيف النصوص من الرموز وتحويلها لكلمات
        s_words = set(re.findall(r'\w+', student_text.lower()))
        m_words = set(re.findall(r'\w+', model_text.lower()))
        
        if not m_words:
            return 0

        # حساب النسبة المئوية للكلمات الصحيحة
        matches = s_words.intersection(m_words)
        score = (len(matches) / len(m_words)) * 100
        return round(score, 2)
        
        # حساب كم كلمة نموذجية ظهرت في نتيجة الـ OCR
        matches = s_words.intersection(m_words)
        score_ratio = len(matches) / len(m_words)
        
        print(f"📊 Words Matched: {len(matches)}/{len(m_words)}")
        
        # إذا كانت النسبة أعلى من 60% نعتبرها درجة كاملة (10/10)
        if score_ratio >= 0.6:
            return 10
        # غير ذلك نحسب النسبة من 10
        return round(score_ratio * 10)

    def process_dx(self, image_url, model_text):
        """تحويل الصورة لنص ومقارنته بالنموذج"""
        image = self.download_public_image(image_url)
        if image is None:
            return 0, "Download Failed"
            
        # استخراج النص من الصورة
        results = self.reader.readtext(image, detail=0)
        student_text = " ".join(results)
        print(f"🔍 OCR Raw Result: {student_text}")
        
        # استخدام دالة التصحيح المرنة
        grade = self.grade_dictation(student_text, model_text)
        
        return grade, student_text
