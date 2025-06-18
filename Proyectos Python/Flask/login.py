from flask import Flask, request, render_template
import sqlite3

def iniciar_db():
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            username TEXT NOT NULL
        )
    ''')
    c.execute("INSERT OR IGNORE INTO usuarios (email, password, username) VALUES (?, ?, ?)", ("matiastmarquez@gmail.com", "mamapapa", "Matias T. Marquez"))
    conn.commit()
    conn.close()

def validar_usuario(email, password):
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE email=? AND password=?", (email, password))
    usuario = c.fetchone()
    conn.close()
    return usuario


#python -m flask --app login run
iniciar_db()
app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        usuario_db = validar_usuario(email, password)
        if usuario_db:
            return render_template('home.html', username=usuario_db[3])
        else:
            error = "Email o contraseña incorrectos."
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    error = None
    mensaje = None
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('usuarios.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO usuarios (username, email, password) VALUES (?, ?, ?)", (username, email, password))
            conn.commit()
            mensaje = "¡Registro exitoso!"
        except sqlite3.IntegrityError:
            error = "El nombre de usuario o email ya está registrado."
        finally:
            conn.close()
            return render_template('register.html', error=error, mensaje=mensaje)
    

@app.route("/logout")
def logout():
    return login()

