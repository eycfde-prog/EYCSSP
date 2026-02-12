import os
import json
import difflib
from google.oauth2 import service_account
from googleapiclient.discovery import build
from ocr_handler import DXProcessor

# تهيئة المحركات
dx_engine = DXProcessor()

def load_activity_config(act_code, task_num):
    """تحميل إعدادات المهمة من ملف الـ JSON"""
    try:
        with open('config/activities.json', 'r') as f:
            config = json.load(f)
        return config.get(act_code, {}).get(str(task_num))
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return None

def update_sheet_grade(email, grade):
    """تحديث الدرجة في جوجل شيت"""
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
                # قراءة التوكنز الحالية
                current_val = sheet.values().get(spreadsheetId=spreadsheet_id, range=f"Sheet1!F{row_num}").execute()
                current_tokens = int(current_val.get('values', [[0]])[0][0] or 0)
                
                # تحديث القيمة
                new_tokens = current_tokens + grade
                sheet.values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f"Sheet1!F{row_num}",
                    valueInputOption="USER_ENTERED",
                    body={"values": [[new_tokens]]}
                ).execute()
                print(f"✅ Sheet updated: {email} now has {new_tokens} tokens")
                return True
    except Exception as e:
        print(f"❌ Sheet update error: {e}")
    return False

def process_submissions():
    raw_data = os.environ.get('SUBMISSION_DATA')
    if not raw_data: return

    try:
        data = json.loads(raw_data)
        email = data.get('email')
        act_code = data.get('actCode')
        task_num = data.get('taskNum')
        student_answer = data.get('answer')

        # تحميل الإعدادات من JSON
        config = load_activity_config(act_code, task_num)
        if not config:
            print(f"⚠️ No config found for {act_code} task {task_num}")
            return

        final_grade = 0
        
        # 1. منطق تصحيح الـ OCR (نشاط DX)
        if act_code == 'DX':
            model_text = config.get('model_text', '')
            final_grade, _ = dx_engine.process_dx(student_answer, model_text)
            
        # 2. منطق تصحيح النصوص (AS, GS, إلخ)
        else:
            model_ans = config.get('answers', [])
            # (يمكنك استخدام دالة fuzzy_grade هنا)
            from difflib import SequenceMatcher
            # ... دالة التصحيح ...
            final_grade = 5 # مؤقتاً للتجربة

        if final_grade > 0:
            update_sheet_grade(email, final_grade)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    process_submissions()
