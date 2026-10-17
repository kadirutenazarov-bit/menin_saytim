import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
auth = HTTPBasicAuth()

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

GENRES = ['Action', 'Romance', 'Fantasy', 'Comedy', 'Drama', 'Boshqa']

USERS = {
    "Ruw_x": "rsrqsh09"
}

TODOS = []

@auth.verify_password
def verify_password(username, password):
    if username in USERS and USERS[username] == password:
        return username

@app.route('/')
@auth.login_required
def index():
    manga_by_genre = {}
    for genre in GENRES:
        genre_folder = os.path.join(app.config['UPLOAD_FOLDER'], genre)
        if os.path.exists(genre_folder):
            files = [f for f in os.listdir(genre_folder) if f.endswith('.pdf')]
            if files:
                manga_by_genre[genre] = files

    return render_template('index.html', todos=TODOS, manga_by_genre=manga_by_genre, genres=GENRES)

# Reja qo'shish (Sana, Vaqt va Hafta kuni)
@app.route('/add_todo', methods=['POST'])
@auth.login_required
def add_todo():
    todo_text = request.form.get('todo')
    todo_date = request.form.get('todo_date')
    todo_time = request.form.get('todo_time')
    todo_day = request.form.get('todo_day')
    
    if todo_text and todo_date:
        TODOS.append({
            'text': todo_text,
            'date': todo_date,
            'time': todo_time,
            'day': todo_day
        })
        # Sana va vaqti bo'yicha tartiblaymiz
        TODOS.sort(key=lambda x: (x['date'], x['time']))
        
    return redirect(url_for('index'))

@app.route('/delete_todo/<int:index_id>')
@auth.login_required
def delete_todo(index_id):
    if 0 <= index_id < len(TODOS):
        TODOS.pop(index_id)
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
@auth.login_required
def upload_file():
    genre = request.form.get('genre', 'Boshqa')
    if 'pdf_file' in request.files:
        file = request.files['pdf_file']
        if file.filename != '' and file.filename.endswith('.pdf'):
            target_folder = os.path.join(app.config['UPLOAD_FOLDER'], genre)
            os.makedirs(target_folder, exist_ok=True)
            file.save(os.path.join(target_folder, file.filename))
    return redirect(url_for('index'))

@app.route('/uploads/<genre>/<filename>')
@auth.login_required
def uploaded_file(genre, filename):
    genre_folder = os.path.join(app.config['UPLOAD_FOLDER'], genre)
    return send_from_directory(genre_folder, filename)

if __name__ == '__main__':
    app.run()