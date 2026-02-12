import easyocr
import cv2
import numpy as np
import requests

class DXProcessor:
    def __init__(self):
        # تحميل القاموس (سيتم تحميله في سيرفر GitHub عند أول تشغيل)
        self.reader = easyocr.Reader(['en'], gpu=False)

    def download_public_image(self, url):
        """تحميل الصورة من رابط عام (Public Drive Link)"""
        try:
            # تحويل رابط المعاينة إلى رابط تحميل مباشر
            if 'drive.google.com' in url:
                file_id = url.split('/')[-2] if '/view' in url else url.split('id=')[-1]
                download_url = f'https://drive.google.com/uc?export=download&id={file_id}'
            else:
                download_url = url
                
            response = requests.get(download_url)
            if response.status_code == 200:
                # تحويل البيانات لصورة يفهمها OpenCV
                image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        except Exception as e:
            print(f"❌ Error downloading image: {e}")
        return None

    def process_dx(self, image_url, model_text):
        """الدالة الرئيسية لتشغيل الـ OCR والتصحيح"""
        image = self.download_public_image(image_url)
        if image is None:
            return 0, "Could not download image"
            
        # استخراج النص
        results = self.reader.readtext(image, detail=0)
        student_text = " ".join(results)
        print(f"🔍 Extracted Text: {student_text}")
        
        # التصحيح
        import difflib
        ratio = difflib.SequenceMatcher(None, student_text.lower(), model_text.lower()).ratio()
        
        # حساب الدرجة من 10 (مثلاً)
        grade = round(ratio * 10)
        return grade, student_text
