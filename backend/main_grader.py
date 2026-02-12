import os
import json
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
import difflib

# 1. إعداد الاتصال بجوجل شيت (باستخدام السر الذي وضعته)
def get_sheets_service():
    info = json.loads(os.environ.get('GCP_SERVICE_ACCOUNT_KEY'))
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    return build('sheets', 'v4', credentials=creds)

# 2. منطق تصحيح الكلمات (نشاط AS, GS, LS) - يسمح بخطأ بسيط
def fuzzy_grade(student_answer, model_answers, max_points=5):
    # تحويل الإجابات لقائمة
    student_list = [a.strip().lower() for a in student_answer.split(',')]
    model_list = [m.strip().lower() for m in model_answers]
    
    correct_count = 0
    for i, s_ans in enumerate(student_list):
        if i < len(model_list):
            # نسبة التشابه (0.8 تعني تطابق بنسبة 80%)
            ratio = difflib.SequenceMatcher(None, s_ans, model_list[i]).ratio()
            if ratio >= 0.85: 
                correct_count += 1
                
    score = (correct_count / len(model_list)) * max_points
    return round(score)

# 3. محرك الأتمتة الرئيسي
def process_submissions():
def process_submissions():
    # قراءة البيانات المرسلة من GitHub Action
    raw_data = os.environ.get('SUBMISSION_DATA')
    if not raw_data:
        print("No data received.")
        return

    data = json.loads(raw_data)
    print(f"Processing submission for: {data.get('email')}")
    
    # هنا سيتم استدعاء دوال التصحيح بناءً على actCode
    if data.get('actCode') == 'AS':
        # مثال لتشغيل التصحيح (سنقوم بربطه بالـ JSON لاحقاً)
        print(f"Correcting AS Activity. Student Answer: {data.get('answer')}")

if __name__ == "__main__":
    process_submissions()

if __name__ == "__main__":
    print("Grader Engine is Ready...")

from ocr_handler import DXProcessor

# تهيئة معالج الصور
dx_engine = DXProcessor()

def handle_dx_activity(drive_url, model_paragraph):
    # استخراج الـ ID من رابط جوجل درايف
    file_id = drive_url.split('id=')[-1] 
    
    # ملاحظة: سنحتاج للحصول على Token من الـ Service Account هنا
    # تم تبسيط الكود للعرض، وسأكمل لك الربط في الخطوة القادمة
    print(f"Processing DX Mission for File ID: {file_id}")
    
    # (سيتم إضافة كود سحب الصورة والـ OCR هنا)
    return "DX Mission Processed"
