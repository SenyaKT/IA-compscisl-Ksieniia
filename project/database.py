import sqlite3
import json
import hashlib
from datetime import datetime

DATABASE_NAME="app.db"

class HistoryRecord:
    def __init__(self, username, season, score, answers, timestamp=None):
        self.__username=hashlib.sha256(username.encode()).hexdigest()
        self.__season=season
        self.__score=score
        self.__answers=json.dumps(answers)
        self.__date= datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_username(self):
        return self.__username
    def get_season(self):
        return self.__season
    def get_score(self):
        return self.__score
    def get_answers(self):
        return self.__answers
    def get_date(self):
        return self.__date
    
def create_history_table():
        conn=sqlite3.connect(DATABASE_NAME)
        cursor=conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS history(
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT NOT NULL,
                       season_name TEXT NOT NULL,
                       score INTEGER NOT NULL,
                       answers TEXT NOT NULL,
                       date_time TEXT NOT NULL
                       )
        """)
        conn.commit()
        conn.close()

def save_analysis(username, season_name, score, answers):
        record=HistoryRecord(username, season_name, score, answers)
        conn=sqlite3.connect(DATABASE_NAME)
        cursor=conn.cursor()
        cursor.execute("""
        INSERT INTO history(username, season_name, score, answers, date_time)
                       VALUES(?, ?, ?, ?, ?)
        """,(
            record.get_username(),
            record.get_season(),
            record.get_score(),
            record.get_answers(),
            record.get_date()
        ))
        conn.commit()
        conn.close()

def get_history():
        conn=sqlite3.connect(DATABASE_NAME)
        cursor=conn.cursor()
        cursor.execute("""
        SELECT username, season_name, score, answers, date_time FROM history ORDER BY id DESC
                       
        """)
        rows=cursor.fetchall()
        conn.close()

        history_function=[]
        for username , season_name, score, answers, date_time in rows:
            history_function.append({
                "username": username,
                "season_name": season_name,
                "score":score,
                "answers":json.loads(answers),
                "date_time": date_time

            })
        return history_function

                       
                       