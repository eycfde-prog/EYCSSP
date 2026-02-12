import os
import json
import difflib
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build
from ocr_handler import DXProcessor

# تهيئة المحرك
dx_engine = DXProcessor()

def log_to_notes(email, activity, error_msg, extracted_text=""):
    """تسجيل التنبيهات في ورقة Notes للمراجعة اليدوية"""
    try:
        info = json.loads(os.environ.get('GCP_SERVICE_ACCOUNT_KEY'))
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=creds)
        spreadsheet_id = '1-21tDcpqJGRtTUf4MCsuOHrcmZAq3tV34fbQU5wGRws'
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        values = [[timestamp, email, activity, error_msg, extracted_text]]
        
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range="Notes!A:E",
            valueInputOption="USER_ENTERED",
            body={"values": values}
        ).execute()
        print(f"⚠️ Logged to Notes for {email}")
    except Exception as e:
        print(f"❌ Notes Log Error: {e}")

def update_sheet_grade(email, grade):
    """تحديث الدرجة في الشيت"""
    try:
        info = json.loads(os.environ.get('GCP_SERVICE_ACCOUNT_KEY'))
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=creds)
        spreadsheet_id = '1-21tDcpqJGRtTUf4MCsuOHrcmZAq3tV34fbQU5wGRws'
        
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Sheet1!A:B").execute()
        rows = result.get('values', [])
        
        for i, row in enumerate(rows):
            if len(row) > 1 and row[1] == email:
                row_num = i + 1
                cell = f"Sheet1!F{row_num}"
                res = sheet.values().get(spreadsheetId=spreadsheet_id, range=cell).execute()
                current = int(res.get('values', [[0]])[0][0] or 0)
                
                sheet.values().update(
                    spreadsheetId=spreadsheet_id, range=cell,
                    valueInputOption="USER_ENTERED",
                    body={"values": [[current + grade]]}
                ).execute()
                print(f"✅ Grade Updated: +{grade}")
                return True
    except Exception as e:
        print(f"❌ Sheet Error: {e}")
    return False

def process_submissions():
    raw_data = os.environ.get('SUBMISSION_DATA')
    if not raw_data: return

    try:
        data = json.loads(raw_data)
        email = data.get('email')
        act_code = data.get('actCode')
        task_num = data.get('taskNum')
        answer = data.get('answer')

        print(f"🚀 Processing {act_code} Task {task_num}")

        # تحميل الإعدادات من JSON
        with open('config/activities.json', 'r', encoding='utf-8') as f:
            full_config = json.load(f)
        config = full_config.get(act_code, {}).get(str(task_num))

        if not config:
            print("⚠️ Config not found")
            return

        final_grade = 0
        student_text = ""

if act_code == 'DX':
            model_text = config.get('model_text', '')
            final_grade, student_text = dx_engine.process_dx(answer, model_text)
            
            # تسجيل في النوتس دائماً لنرى النتائج في البداية
            log_to_notes(email, f"DX-{task_num}", f"Grade: {final_grade}/10", student_text)
        
        elif act_code == 'AS':
            from ocr_handler import difflib # استخدام الدالة الموجودة
            model_ans = config.get('answers', [])
            # منطق الـ AS البسيط
            final_grade = 5 # (يمكنك دمج دالة fuzzy_grade هنا لاحقاً)

        if final_grade > 0:
            update_sheet_grade(email, final_grade)
            
    except Exception as e:
        print(f"❌ Global Error: {e}")

if __name__ == "__main__":
    process_submissions()
