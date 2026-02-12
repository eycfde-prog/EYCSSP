import easyocr
import cv2
import numpy as np
import requests
import re
from difflib import SequenceMatcher

class DXProcessor:
    def __init__(self):
        # تحميل القاموس الإنجليزي
        self.reader = easyocr.Reader(['en'], gpu=False)

    def download_public_image(self, url):
        """تحميل الصورة من جوجل درايف العام"""
        try:
            if 'drive.google.com' in url:
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
        """مقارنة مرنة جداً تعتمد على وجود الكلمات الأساسية"""
        # 1. تنظيف النص المستخرج من أي رموز غريبة
        clean_student = re.sub(r'[^a-zA-Z\s]', '', student_text.lower())
        s_words = clean_student.split()
        
        # 2. تنظيف نص النموذج
        clean_model = re.sub(r'[^a-zA-Z\s]', '', model_text.lower())
        m_words = clean_model.split()
        
        if not m_words: return 0
        
        matched_count = 0
        used_indices = set()

        # 3. البحث عن الكلمات المتشابهة
        for m_word in m_words:
            if len(m_word) < 2: continue
            for i, s_word in enumerate(s_words):
                if i in used_indices: continue
                ratio = SequenceMatcher(None, m_word, s_word).ratio()
                if ratio >= 0.70:
                    matched_count += 1
                    used_indices.add(i)
                    break 

        score = (matched_count / len(m_words)) * 10
        print(f"📊 Final Matches: {matched_count}/{len(m_words)}")
        return round(score)

    def process_dx(self, image_url, model_text):
        """تحويل الصورة لنص ومقارنته بالنموذج"""
        image = self.download_public_image(image_url)
        if image is None:
            return 0, "Download Failed"
            
        results = self.reader.readtext(image, detail=0)
        student_text = " ".join(results)
        print(f"🔍 OCR Raw Result: {student_text}")
        
        grade = self.grade_dictation(student_text, model_text)
        return grade, student_text
