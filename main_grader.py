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
    # سيتم ربط هذا الجزء بـ Webhook لاحقاً لاستقبال البيانات من الأرينا
    # حالياً هذا هو الهيكل الذي سيعالج البيانات
    pass

if __name__ == "__main__":
    print("Grader Engine is Ready...")
