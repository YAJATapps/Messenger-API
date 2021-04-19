import os
from fastapi import FastAPI
import hashlib
import mysql.connector
import time

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

    exists = await valid_username(user)

    if exists:
        return 'alreadyExists'
    else:
        appCursor = appDb.cursor()

        sql = "INSERT INTO UsersAuth (username, password) VALUES (%s, %s)"
        val = (user, sha256(pwd))
        appCursor.execute(sql, val)

        appDb.commit()

        return 'addedUser'


@app.post('/api/v1/messenger/users/user')
async def valid_username(user: str = None):
    # Returns true if user exists

    if user == None:
        return 'user missing'

    appCursor = appDb.cursor()

    sql = "SELECT * FROM UsersAuth WHERE username=%s"
    val = (user,)
    appCursor.execute(sql, val)
    result = appCursor.fetchone()

    return result != None


@app.post('/api/v1/messenger/users/login')
async def valid_login(user: str = None, pwd: str = None):
    # Returns true if user and pwd credentials are correct

    if user == None or pwd == None:
        return 'user or pwd missing'

    appCursor = appDb.cursor()

    sql = "SELECT * FROM UsersAuth WHERE username=%s AND password=%s"
    val = (user, sha256(pwd))
    appCursor.execute(sql, val)
    result = appCursor.fetchone()

    return result != None


@app.post('/api/v1/messenger/messages/add')
async def add_message(frm: str = None, to: str = None, msg: str = None):
    # Add a new message with ids of from and to. Also the current time

    if frm == None or to == None or msg == None:
        return 'frm, to or msg missing'

    appCursor = appDb.cursor()

    currentTime = time.strftime('%Y-%m-%d %H:%M:%S')

    sql = "INSERT INTO Messages (msgFrom, msgTo, message, time) VALUES (%s, %s, %s, %s)"
    val = (int(frm), int(to), msg, currentTime)
    appCursor.execute(sql, val)

    appDb.commit()

    return 'addedMessage'


def sha256(hash: str):
    # Util function to return sha256 hash of the passed argument

    return hashlib.sha256(hash.encode()).hexdigest()
