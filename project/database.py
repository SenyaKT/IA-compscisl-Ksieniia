#This module manages database storage from the completed analyses, to appear in history window.
#There is only one database called app.db which stores both history of responses and wrist analysis data


#Technologies
import sqlite3 #database management
import json # python dicts to strings (for SQLite to work as it uses TEXT)
import hashlib # Hashing of usernames for privacy called SHA256
from datetime import datetime #creates timestampsfor saved records
import os

DATABASE_NAME=os.path.join(os.path.dirname(os.path.abspath(__file__)),"app.db")

#OOP with private attributes that stores data for history table
class HistoryRecord: 
    def __init__(self, username, season, score, answers, timestamp=None): #Initializes the recerord
        self.__username=hashlib.sha256(username.encode()).hexdigest() #hashed with SHA256 so that real names are not visible anymore, creatings a unique hash with 64 character hexadecimal for each username, except duplicates.
        self.__season=season #"__"private attributes , needs getters and setters to change or access, cann not be accessed from outside
        self.__score=score
        self.__answers=json.dumps(answers) # J son converts from dict to string
        self.__date= datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_username(self): #Only way to read private attributes
        return self.__username
    def get_season(self):
        return self.__season
    def get_score(self):
        return self.__score
    def get_answers(self):
        return self.__answers
    def get_date(self):
        return self.__date
    
def create_history_table():  #Initializes the database if it doesnt exist yet, creating table to fill out
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
        #id is unique and auto generated number
        conn.commit()
        conn.close()

def save_analysis(username, season_name, score, answers): # Create HistoryRecord object and save it to the database
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
        )) #Values are in tuple format
        conn.commit() #Saves changes
        conn.close() #Closes access

def get_history():
        conn=sqlite3.connect(DATABASE_NAME)
        cursor=conn.cursor()
        cursor.execute("""
        SELECT username, season_name, score, answers, date_time FROM history ORDER BY id DESC
                       
        """) #Calls from the newest to oldest recorsds
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

            }) #json loads converts string back to dict
        return history_function #Displays llist of dicts

                       
