import os
from fastapi import FastAPI
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
    if user == None or pwd == None:
        return 'user or pwd missing'

    appCursor = appDb.cursor()

    sql = "INSERT INTO UsersAuth (Username, Password) VALUES (%s, %s)"
    val = (user, pwd)
    appCursor.execute(sql, val)

    appDb.commit()

    return 'added'
