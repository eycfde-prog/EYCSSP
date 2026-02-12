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

import re
from difflib import SequenceMatcher

def grade_dictation(self, student_text, model_text):
    """
    مقارنة مرنة تعتمد على الكلمات المفتاحية مع التحقق من تشابه الحروف لتجاوز أخطاء الـ OCR
    """
    s_words = re.findall(r'\w+', student_text.lower())
    m_words = re.findall(r'\w+', model_text.lower())
    
    if not m_words:
        return 0
    
    matched_count = 0
    temp_s_words = list(s_words)

    for m_word in m_words:
        best_ratio = 0
        best_index = -1
        
        for i, s_word in enumerate(temp_s_words):
            # حساب نسبة التشابه بين الكلمتين
            ratio = SequenceMatcher(None, m_word, s_word).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_index = i
        
        # السماح بوجود خطأ حرف واحد (عادة النسبة > 0.8 تعني اختلاف حرف في كلمات متوسطة الطول)
        if best_ratio >= 0.8:
            matched_count += 1
            if best_index != -1:
                temp_s_words.pop(best_index)

    score = (matched_count / len(m_words)) * 100
    return round(score, 2)
