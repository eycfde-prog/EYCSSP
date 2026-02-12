import easyocr
import cv2
import numpy as np
import requests

class DXProcessor:
    def __init__(self):
        # تحميل القاموس مرة واحدة
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

    def process_dx(self, image_url, model_text):
        """تحويل الصورة لنص ومقارنته بالنموذج"""
        image = self.download_public_image(image_url)
        if image is None:
            return 0, "Download Failed"
            
        results = self.reader.readtext(image, detail=0)
        student_text = " ".join(results)
        print(f"🔍 OCR Result: {student_text}")
        
        import difflib
        ratio = difflib.SequenceMatcher(None, student_text.lower().strip(), model_text.lower().strip()).ratio()
        
        # إذا كانت النسبة أعلى من 70% نعتبرها درجة كاملة (لأن الـ OCR قد يخطئ قليلاً)
        if ratio > 0.70:
            return 10, student_text
        return round(ratio * 10), student_text
