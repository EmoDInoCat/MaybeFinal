from flask import Flask, request, redirect, url_for, render_template_string
import requests

app = Flask(__name__)

API_KEY = 'AIzaSyDRSyiaiDu35r7buUAoFz0nOPF9M_NLavc'

# Главная страница
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_url = request.form['url']
        video_id = extract_video_id(video_url)
        if video_id:
            return redirect(url_for('result', video_id=video_id))
    return render_template_string('''
        <!doctype html>
        <html lang="ru">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
            <title>Проверка видео</title>
            <style>
                body {
                    font-family: 'Roboto', sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f8f9fa;
                }
                .container {
                    text-align: center;
                }
                h1 {
                    font-size: 45px;
                }
                input[type="text"] {
                    width: 360px;
                    height: 56px;
                    font-size: 14px;
                    padding: 10px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    background-color: #e6e0e9;
                    margin-bottom: 20px;
                }
                input[type="submit"] {
                    width: 120px;
                    height: 40px;
                    font-size: 14px;
                    color: #fff;
                    background-color: #6750A4;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                input[type="submit"]:hover {
                    background-color: #5a4790;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Проверка видео</h1>
                <form method="post">
                    <input type="text" name="url" placeholder="Введите URL видео">
                    <br>
                    <input type="submit" value="Отправить">
                </form>
            </div>
        </body>
        </html>
    ''')


# Извлечение video_id из URL
def extract_video_id(url):
    if 'youtube.com' in url:
        from urllib.parse import urlparse, parse_qs
        query = urlparse(url).query
        params = parse_qs(query)
        return params.get('v', [None])[0]
    elif 'youtu.be' in url:
        return url.split('/')[-1]
    return None

# Результат
@app.route('/result')
def result():
    video_id = request.args.get('video_id')
    if not video_id:
        return "Не удалось получить идентификатор видео."

    video_info = get_video_info(video_id)
    if not video_info:
        return "Не удалось получить информацию о видео."

    is_kid_friendly = analyze_video(video_info)
    result_text = "Подходит для просмотра детьми" if is_kid_friendly else "Не подходит для просмотра детьми"
    
    return render_template_string(f'''
        <!doctype html>
        <html lang="ru">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
            <title>Результат проверки</title>
            <style>
                body {
                    font-family: 'Roboto', sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f8f9fa;
                }
                .container {
                    text-align: center;
                }
                h1 {
                    font-size: 45px;
                }
                a {
                    font-size: 14px;
                    text-decoration: none;
                    color: #6750A4;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Результат проверки</h1>
                <p>Результат для видео ID: {video_id} </p>
                <p> {result_text} </p>
                <a href="/">Вернуться на главную страницу</a>
            </div>
        </body>
        </html>
    ''')
    
# Получение информации о видео с помощью YouTube Data API
def get_video_info(video_id):
    url = f'https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={API_KEY}&part=snippet,contentDetails,statistics'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            return data['items'][0]
    return None

def analyze_video(video_info):
    # Ключевым слова в заголовке и описании
    kid_friendly_keywords = ['дети', 'мультик', 'игрушки', 'обучение', 'для детей', 'детское', 'песни', 'сказки']
    not_kid_friendly_keywords = ['насилие', 'оружие', '18+', 'страх', 'ужасы', 'секс', 'наркотики']
    snippet = video_info.get('snippet', {})
    title = snippet.get('title', '').lower()
    description = snippet.get('description', '').lower()
    
    # Ключевые слова(тест)
    for keyword in not_kid_friendly_keywords:
        if keyword in title or keyword in description:
            return False

    for keyword in kid_friendly_keywords:
        if keyword in title or keyword in description:
            return True
    
    # Категория видео
    kid_friendly_categories = ['Education', 'Film & Animation', 'Music', 'Family Entertainment']
    category_id = snippet.get('categoryId')
    if category_id:
        category = get_category_name(category_id)
        if category in kid_friendly_categories:
            return True

    # Возрастные ограничения
    content_details = video_info.get('contentDetails', {})
    if content_details.get('contentRating', {}).get('ytRating') == 'ytAgeRestricted':
        return False

    return False

# Получение названия категории видео
def get_category_name(category_id):
    url = f'https://www.googleapis.com/youtube/v3/videoCategories?id={category_id}&key={API_KEY}&part=snippet'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            return data['items'][0]['snippet']['title']
    return None

if __name__ == '__main__':
    app.run(debug=True)
