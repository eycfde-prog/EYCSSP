import os
import json
import difflib

def fuzzy_grade(student_answer, model_answers, max_points=5):
    """منطق تصحيح الكلمات - يسمح بخطأ بسيط"""
    if not student_answer or not model_answers:
        return 0
        
    student_list = [a.strip().lower() for a in student_answer.split(',')]
    model_list = [m.strip().lower() for m in model_answers]
    
    correct_count = 0
    for i, s_ans in enumerate(student_list):
        if i < len(model_list):
            ratio = difflib.SequenceMatcher(None, s_ans, model_list[i]).ratio()
            if ratio >= 0.85: 
                correct_count += 1
                
    score = (correct_count / len(model_list)) * max_points if len(model_list) > 0 else 0
    return round(score)

def process_submissions():
    """المحرك الرئيسي - يقرأ البيانات ويعالجها"""
    raw_data = os.environ.get('SUBMISSION_DATA')
    
    if not raw_data:
        print("❌ No data received in SUBMISSION_DATA")
        return

    try:
        # فك تشفير البيانات القادمة من GitHub Action
        data = json.loads(raw_data)
        
        email = data.get('email', 'Unknown')
        act_code = data.get('actCode', 'N/A')
        answer = data.get('answer', '')

        print(f"✅ Processing submission for: {email}")
        print(f"📊 Activity Code: {act_code}")
        print(f"✍️ Student Answer: {answer}")

        # اختبار أولي لنشاط AS
        if act_code == 'AS':
            model_ans = ["sun", "sea", "to", "no"] 
            result = fuzzy_grade(answer, model_ans)
            print(f"🎯 Final Grade: {result}/5")
            
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")

if __name__ == "__main__":
    process_submissions()
