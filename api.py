import os
from fastapi import FastAPI
import hashlib
import mysql.connector

app = FastAPI()

appDb = mysql.connector.connect(
    host=os.environ['DB_HOST'],
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASS'],
    database=os.environ['DB_NAME']
)


@app.get('/')
async def home():
    return 'Invalid'


@app.post('/api/v1/messenger/users/add')
async def add_user(user: str = None, pwd: str = None):
    # Add a new user to UsersAuth database with passed username and sha256 encrypted password

    if user == None or pwd == None:
        return 'user or pwd missing'

    appCursor = appDb.cursor()

    sql = "INSERT INTO UsersAuth (username, password) VALUES (%s, %s)"
    val = (user, sha256(pwd))
    appCursor.execute(sql, val)

    appDb.commit()

    return 'added'


def sha256(hash: str):
    # Util function to return sha256 hash of the passed argument

    return hashlib.sha256(hash.encode()).hexdigest()
