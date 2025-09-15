import sqlite3

DB_PATH = "database/emergencias.db"

def conectar():
    return sqlite3.connect(DB_PATH)
