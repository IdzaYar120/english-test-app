import json
import os
import string
from flask import Flask, render_template, request

app = Flask(__name__)

# Функція для завантаження відповідей з JSON
def load_answers(student_id):
    filepath = os.path.join('answers', f'{student_id}.json')
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_result(student_id, student_name, student_group, score, total):
    results_file = 'test_results.json'
    results = []
    if os.path.exists(results_file):
        with open(results_file, 'r', encoding='utf-8') as f:
            try:
                results = json.load(f)
            except json.JSONDecodeError:
                pass
    
    results.append({
        'student_id': student_id,
        'student_name': student_name,
        'student_group': student_group,
        'score': score,
        'total': total
    })
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test/<student_id>', methods=['GET', 'POST'])
def show_test(student_id):
    if request.method == 'POST':
        correct_answers = load_answers(student_id)
        
        # Якщо файл з відповідями ще не створено
        if not correct_answers:
            return "Помилка: Ключі до цього тесту ще не завантажені на сервер.", 404

        score = 0
        total_questions = len(correct_answers)

        # Перевірка кожної відповіді
        for q_name, correct_val in correct_answers.items():
            user_answer = request.form.get(q_name, '').strip().lower().rstrip(string.punctuation)
            correct_ans = correct_val.lower().rstrip(string.punctuation)
            if user_answer == correct_ans:
                score += 1
        
        student_name = request.form.get('student_name', 'Невідомо').strip()
        student_group = request.form.get('student_group', 'Невідомо').strip()
        
        save_result(student_id, student_name, student_group, score, total_questions)
        
        return render_template('result.html', score=score, total=total_questions, student=student_name)

    # Для GET-запиту: перевіряємо, чи існує шаблон для студента
    template_name = f'test_{student_id}.html'
    template_path = os.path.join(app.root_path, 'templates', template_name)
    
    if os.path.exists(template_path):
        return render_template(template_name)
    else:
        return "Сторінка тесту ще не створена.", 404

@app.route('/results')
def show_results():
    results = []
    if os.path.exists('test_results.json'):
        with open('test_results.json', 'r', encoding='utf-8') as f:
            try:
                results = json.load(f)
            except json.JSONDecodeError:
                pass
    return render_template('test_results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)