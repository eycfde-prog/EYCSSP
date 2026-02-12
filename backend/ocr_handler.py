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
        """مقارنة مرنة لتجاوز أخطاء الـ OCR"""
        s_words = re.findall(r'\w+', student_text.lower())
        m_words = re.findall(r'\w+', model_text.lower())
        if not m_words: return 0
        
        matched_count = 0
        temp_s_words = list(s_words)
        for m_word in m_words:
            best_ratio = 0
            best_index = -1
            for i, s_word in enumerate(temp_s_words):
                ratio = SequenceMatcher(None, m_word, s_word).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_index = i
            if best_ratio >= 0.75: # خفضنا النسبة قليلاً لتكون أكثر مرونة
                matched_count += 1
                if best_index != -1: temp_s_words.pop(best_index)
        
        score = (matched_count / len(m_words)) * 10
        return round(score)

    def process_dx(self, image_url, model_text):
        """هذه هي الدالة التي كان يفتقدها المحرك"""
        image = self.download_public_image(image_url)
        if image is None:
            return 0, "Download Failed"
            
        results = self.reader.readtext(image, detail=0)
        student_text = " ".join(results)
        print(f"🔍 OCR Raw Result: {student_text}")
        
        grade = self.grade_dictation(student_text, model_text)
        return grade, student_text
