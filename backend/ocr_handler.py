import easyocr
import cv2
import numpy as np
import requests
import re
from difflib import SequenceMatcher

class DXProcessor:
    def __init__(self):
        # تحميل القاموس (سيتم تحميله مرة واحدة في بيئة GitHub)
        self.reader = easyocr.Reader(['en'], gpu=False)

    def download_public_image(self, url):
        """تحميل الصورة من رابط جوجل درايف العام"""
        try:
            if 'drive.google.com' in url:
                file_id = url.split('/')[-2] if '/view' in url else url.split('id=')[-1]
                download_url = f'https://drive.google.com/uc?export=download&id={file_id}'
            else:
                download_url = url
            response = requests.get(download_url, timeout=10)
            if response.status_code == 200:
                image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        except Exception as e:
            print(f"❌ Image Download Error: {e}")
        return None

import easyocr
import cv2
import numpy as np
import requests
import re
from difflib import SequenceMatcher

class DXProcessor:
    def __init__(self):
        # تحميل القاموس مرة واحدة
        self.reader = easyocr.Reader(['en'], gpu=False)

    def apply_filters(self, image):
        """تحسين جودة الصورة باستخدام الفلاتر"""
        # 1. تحويل الصورة للرمادي (Grayscale)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 2. زيادة التباين وتحويلها لأبيض وأسود حاد (Thresholding)
        # نستخدم تقنية Otsu للتعامل مع الإضاءة غير المستوية
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 3. إزالة النقاط الصغيرة (Noise Reduction)
        kernel = np.ones((1, 1), np.uint8)
        processed_img = cv2.dilate(thresh, kernel, iterations=1)
        processed_img = cv2.erode(processed_img, kernel, iterations=1)
        
        return processed_img

    def download_public_image(self, url):
        """تحميل الصورة من رابط جوجل درايف العام"""
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
            print(f"❌ Image Download Error: {e}")
        return None

    def grade_dictation(self, student_text, model_text):
        """مقارنة مرنة جداً للكلمات"""
        clean_student = re.sub(r'[^a-zA-Z\s]', ' ', student_text.lower())
        s_words = clean_student.split()
        m_words = re.findall(r'\w+', model_text.lower())
        
        if not m_words: return 0
        
        matched_count = 0
        used_indices = set()

        for m_word in m_words:
            if len(m_word) <= 1: continue
            for i, s_word in enumerate(s_words):
                if i in used_indices: continue
                ratio = SequenceMatcher(None, m_word, s_word).ratio()
                if ratio >= 0.65:
                    matched_count += 1
                    used_indices.add(i)
                    print(f"✅ Match: '{m_word}' -> '{s_word}' ({round(ratio,2)})")
                    break
        
        score = (matched_count / len(m_words)) * 10
        return round(score)

    def process_dx(self, image_url, model_text):
        """الدالة الرئيسية بعد إضافة الفلترة"""
        image = self.download_public_image(image_url)
        if image is None:
            return 0, "Download Failed"
            
        # تطبيق الفلتر قبل القراءة
        processed_image = self.apply_filters(image)
        
        # القراءة من الصورة المعالجة
        results = self.reader.readtext(processed_image, detail=0)
        student_text = " ".join(results)
        print(f"🔍 OCR Post-Filter: {student_text}")
        
        grade = self.grade_dictation(student_text, model_text)
        return grade, student_text
