from flask import Flask, request, redirect, url_for, render_template_string
import random

app = Flask(__name__)

# Главная страница с формой для ввода URL
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        return redirect(url_for('result', url=url))
    return '''
        <form method="post">
            Введите URL: <input type="text" name="url">
            <input type="submit" value="Отправить">
        </form>
    '''

# Страница с результатом
@app.route('/result')
def result():
    url = request.args.get('url')
    decision = random.choice(['подходит для просмотра', 'не подходит для просмотра'])
    return f'''
        <p>Результат для URL: {url}</p>
        <p>{decision}</p>
        <a href="/">Вернуться на главную страницу</a>
    '''

if __name__ == '__main__':
    app.run(debug=True)
