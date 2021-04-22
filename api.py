import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import hashlib
from mangum import Mangum
import mysql.connector
import time

app = FastAPI()

origins = [
    "https://messenger.yajatkumar.com",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


appDb = mysql.connector.connect(
    host=os.environ['DB_HOST'],
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASS'],
    database=os.environ['DB_NAME']
)


@app.post('/api/v1/users/add')
async def add_user(user: str = None, pwd: str = None):
    # Add a new user to UsersAuth database with passed username and sha256 encrypted password

    if user == None or pwd == None:
        return 'user/pwdMissing'

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


@app.post('/api/v1/users/user')
async def valid_username(user: str = None):
    # Returns true if user exists

    if user == None:
        return 'userMissing'

    appCursor = appDb.cursor()

    sql = "SELECT * FROM UsersAuth WHERE username=%s"
    val = (user,)
    appCursor.execute(sql, val)
    result = appCursor.fetchone()

    return result != None


@app.post('/api/v1/users/login')
async def valid_login(user: str = None, pwd: str = None):
    # Returns true if user and pwd credentials are correct

    if user == None or pwd == None:
        return 'user/pwdMissing'

    appCursor = appDb.cursor()

    sql = "SELECT * FROM UsersAuth WHERE username=%s AND password=%s"
    val = (user, sha256(pwd))
    appCursor.execute(sql, val)
    result = appCursor.fetchone()

    return result != None


@app.post('/api/v1/messages/add')
async def add_message(frm: str = None, to: str = None, msg: str = None):
    # Add a new message with ids of from and to. Also the current time

    if frm == None or to == None or msg == None:
        return 'frm/to/msgMissing'

    appCursor = appDb.cursor()

    currentTime = time.strftime('%Y-%m-%d %H:%M:%S')

    sql = "INSERT INTO Messages (msgFrom, msgTo, message, msgTime) VALUES (%s, %s, %s, %s)"
    val = (int(frm), int(to), msg, currentTime)
    appCursor.execute(sql, val)

    appDb.commit()

    return 'addedMessage'


@app.post('/api/v1/users/find')
async def search_users(user: str = None):
    # Returns users which contain the user str

    if user == None:
        return 'userMissing'

    appCursor = appDb.cursor()

    sql = "SELECT id, username FROM UsersAuth WHERE username LIKE '%" + user + "%'"
    appCursor.execute(sql)
    result = appCursor.fetchall()

    users = []

    for x in result:
        users.append({"id": x[0], "name": x[1]})

    return users


@app.post('/api/v1/messages/{userId}')
async def fetch_messages(userId: int = -1):
    # Returns messages which were sent to or from userId

    if userId == -1:
        return 'idMissing'

    appCursor = appDb.cursor()

    sql = "SELECT * FROM Messages WHERE msgFrom=%s OR msgTo=%s ORDER BY msgTime DESC"
    val = (userId, userId)
    appCursor.execute(sql, val)

    result = appCursor.fetchall()

    messages = []

    # Return the array with an additional parameter of sent
    for x in result:
        messages.append([x[0], x[1], x[2], x[3], x[4], x[1] == userId])

    return messages


def sha256(hash: str):
    # Util function to return sha256 hash of the passed argument

    return hashlib.sha256(hash.encode()).hexdigest()


handler = Mangum(app)
