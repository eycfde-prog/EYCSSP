import os
import json
import difflib
from google.oauth2 import service_account
from googleapiclient.discovery import build
from ocr_handler import DXProcessor

# تهيئة المحركات
dx_engine = DXProcessor()

def fuzzy_grade(student_answer, model_answers, max_points=5):
    if not student_answer or not model_answers: return 0
    s_list = [a.strip().lower() for a in str(student_answer).split(',')]
    m_list = [m.strip().lower() for m in model_answers]
    correct = 0
    for i, s_ans in enumerate(s_list):
        if i < len(m_list):
            ratio = difflib.SequenceMatcher(None, s_ans, m_list[i]).ratio()
            if ratio >= 0.85: correct += 1
    return round((correct / len(m_list)) * max_points) if m_list else 0

def load_activity_config(act_code, task_num):
    try:
        with open('config/activities.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get(act_code, {}).get(str(task_num))
    except Exception as e:
        print(f"❌ JSON Config Error: {e}")
        return None

def update_sheet_grade(email, grade):
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
                cell_range = f"Sheet1!F{row_num}"
                current_val = sheet.values().get(spreadsheetId=spreadsheet_id, range=cell_range).execute()
                current_tokens = int(current_val.get('values', [[0]])[0][0] or 0)
                
                new_tokens = current_tokens + grade
                sheet.values().update(
                    spreadsheetId=spreadsheet_id,
                    range=cell_range,
                    valueInputOption="USER_ENTERED",
                    body={"values": [[new_tokens]]}
                ).execute()
                print(f"✅ Success! {email} total tokens: {new_tokens}")
                return True
    except Exception as e:
        print(f"❌ Sheet Update Failed: {e}")
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

        print(f"🚀 Processing {act_code} Task {task_num} for {email}")

        config = load_activity_config(act_code, task_num)
        if not config:
            print(f"⚠️ No config for {act_code}_{task_num}")
            return

        final_grade = 0
        if act_code == 'DX':
            final_grade, _ = dx_engine.process_dx(answer, config.get('model_text', ''))
        else:
            final_grade = fuzzy_grade(answer, config.get('answers', []), config.get('points', 5))

        print(f"🎯 Calculated Grade: {final_grade}")
        if final_grade > 0:
            update_sheet_grade(email, final_grade)
            
    except Exception as e:
        print(f"❌ Global Error: {e}")

if __name__ == "__main__":
    process_submissions()
