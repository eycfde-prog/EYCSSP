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

    def grade_dictation(self, student_text, model_text):
        """مقارنة مرنة جداً تبحث عن الكلمات حتى لو كانت وسط رموز"""
        # 1. تنظيف نص الطالب من الرموز الزائدة مع الحفاظ على المسافات
        clean_student = re.sub(r'[^a-zA-Z\s]', ' ', student_text.lower())
        s_words = clean_student.split()
        
        # 2. استخراج كلمات النموذج
        m_words = re.findall(r'\w+', model_text.lower())
        
        if not m_words: return 0
        
        matched_count = 0
        used_student_indices = set()

        # 3. استراتيجية البحث: لكل كلمة في النموذج، ابحث عن شبيه في نص الطالب
        for m_word in m_words:
            if len(m_word) <= 1: continue # تجاهل الحروف المنفردة
            
            best_match_for_this_word = False
            for i, s_word in enumerate(s_words):
                if i in used_student_indices: continue
                
                # حساب نسبة التشابه (مثلاً down vs dowa)
                ratio = SequenceMatcher(None, m_word, s_word).ratio()
                
                # إذا وجدنا تطابقاً بنسبة 65% فأكثر (مرونة عالية)
                if ratio >= 0.65:
                    matched_count += 1
                    used_student_indices.add(i)
                    best_match_for_this_word = True
                    print(f"✅ Match Found: '{m_word}' resembles '{s_word}' ({round(ratio,2)})")
                    break
        
        # حساب الدرجة النهائية من 10
        score = (matched_count / len(m_words)) * 10
        print(f"📊 Summary: Matched {matched_count} out of {len(m_words)}")
        return round(score)

    def process_dx(self, image_url, model_text):
        """الدالة الرئيسية للمحرك"""
        image = self.download_public_image(image_url)
        if image is None:
            return 0, "Download Failed"
            
        results = self.reader.readtext(image, detail=0)
        student_text = " ".join(results)
        print(f"🔍 OCR Raw Result: {student_text}")
        
        grade = self.grade_dictation(student_text, model_text)
        return grade, student_text
