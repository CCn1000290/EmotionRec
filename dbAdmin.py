import sqlite3
import bcrypt



def init_db():
    db_path = 'users.db'  # Consider using an absolute path for production
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT UNIQUE, 
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database initialized at {db_path}")


def add_user(username, password):
    try:
        password = password.encode('utf-8')
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        print("Username already exists.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def authenticate_user(username, password):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT password FROM users WHERE username = ?', (username,))
        db_password = c.fetchone()
        if db_password:
            print(f"DB password: {db_password[0]}")
            print(f"User password: {password}")
            if bcrypt.checkpw(password.encode('utf-8'), db_password[0]):
                print("Password match")
                return True
            else:
                print("Password does not match")
        return False
    except Exception as e:
        print(f"An error occurred during login: {e}")
        return False


def check_tables():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    print(tables)
    conn.close()
