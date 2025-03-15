from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Создание папки для видео
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Создаём базу данных и таблицу
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS videos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT,
                        tags TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['video']
    tags = request.form.get('tags', '')

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filename)

    # Сохранение в базу данных
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO videos (filename, tags) VALUES (?, ?)", (file.filename, tags))
    conn.commit()
    conn.close()

    return jsonify({'message': 'File uploaded successfully'})

@app.route('/search', methods=['GET'])
def search_videos():
    tag_query = request.args.get('tag', '')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT filename FROM videos WHERE tags LIKE ?", ('%' + tag_query + '%',))
    videos = cursor.fetchall()
    conn.close()

    return jsonify({'videos': [video[0] for video in videos]})

@app.route('/delete', methods=['POST'])
def delete_video():
    data = request.get_json()
    filename = data.get('filename')

    if not filename:
        return jsonify({'error': 'Filename is required'}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(filepath):
        os.remove(filepath)

        # Удаляем запись из базы данных
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM videos WHERE filename = ?", (filename,))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Видео удалено успешно'})
    else:
        return jsonify({'error': 'Файл не найден'}), 404

from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)