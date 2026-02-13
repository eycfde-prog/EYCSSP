import easyocr
import cv2
import numpy as np
import requests
import re
from difflib import SequenceMatcher

class DXProcessor:
    def __init__(self):
        self.reader = easyocr.Reader(['en'], gpu=False)

    def apply_filters(self, image):
        """تحسين جودة الصورة باستخدام الفلاتر المتقدمة"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # استخدام Adaptive Thresholding للتعامل مع الإضاءة المتغيرة في تصوير الطلاب
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY, 11, 2)
        return thresh

    def download_public_image(self, url):
        try:
            if 'drive.google.com' in url:
                file_id = url.split('/')[-2] if '/view' in url else url.split('id=')[-1]
                download_url = f'https://drive.google.com/uc?export=download&id={file_id}'
            else:
                download_url = url
            response = requests.get(download_url, timeout=15)
            if response.status_code == 200:
                image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        except Exception as e:
            print(f"❌ Download Error: {e}")
        return None

    def grade_dictation(self, student_text, model_text):
        """
        منطق التصحيح:
        1. قبول الإجابة فقط إذا تم اكتشاف > 50% من الكلمات.
        2. الدرجة من 100 بناءً على التطابق.
        """
        clean_student = re.sub(r'[^a-zA-Z\s]', ' ', student_text.lower())
        s_words = clean_student.split()
        m_words = model_text.split('|') # الكلمات النموذجية مفصولة بـ |
        
        if not m_words: return 0, "No Config"
        
        matched_count = 0
        used_indices = set()

        for m_word in m_words:
            for i, s_word in enumerate(s_words):
                if i in used_indices: continue
                # نسبة مرنة للطالب (60%) لأنها لغة ثانية وخط يد
                ratio = SequenceMatcher(None, m_word.strip(), s_word).ratio()
                if ratio >= 0.60:
                    matched_count += 1
                    used_indices.add(i)
                    break
        
        match_percentage = (matched_count / len(m_words))
        
        # شرط الذكاء الاصطناعي: الرفض إذا كانت الصورة غير واضحة (أقل من 50%)
        if match_percentage < 0.50:
            return -1, "Blurry or Incomplete: Please rewrite clearly and re-upload."
            
        final_grade = round(match_percentage * 100)
        return final_grade, student_text

    def process_dx(self, image_url, model_keywords):
        image = self.download_public_image(image_url)
        if image is None: return 0, "Download Failed"
            
        processed_image = self.apply_filters(image)
        results = self.reader.readtext(processed_image, detail=0)
        student_text = " ".join(results)
        
        grade, status = self.grade_dictation(student_text, model_keywords)
        return grade, status
