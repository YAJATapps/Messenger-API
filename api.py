import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import hashlib
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

    appDb.commit()

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

    appDb.commit()

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

    appDb.commit()

    users = []

    for x in result:
        users.append({"id": x[0], "name": x[1]})

    return users


@app.post('/api/v1/messages/list')
async def fetch_messages(frm: str = None, to: str = None):
    # Returns messages which were sent to or from userId

    if frm == None or to == None:
        return 'frm/toMissing'

    if not frm.isdigit():
        return 'frmNotInt'

    if not to.isdigit():
        return 'toNotInt'

    appCursor = appDb.cursor()

    sql = "SELECT * FROM Messages WHERE (msgFrom=%s AND msgTo=%s) OR (msgFrom=%s AND msgTo=%s) ORDER BY msgTime"
    val = (frm, to, to, frm)
    appCursor.execute(sql, val)

    result = appCursor.fetchall()

    appDb.commit()

    messages = []

    # Return the array with an additional parameter of sent
    for x in result:
        messages.append({"msg": x[3], "sent": x[1] == int(frm)})

    return messages


@app.post('/api/v1/users/id')
async def fetch_id(user: str = None):
    # Returns id from username

    if user == None:
        return 'userMissing'

    appCursor = appDb.cursor()

    sql = "SELECT id FROM UsersAuth WHERE username=%s"
    val = (user,)
    appCursor.execute(sql, val)
    result = appCursor.fetchone()

    appDb.commit()

    return result


@app.post('/api/v1/users/contacts')
async def fetch_contacts(user: str = None):
    # Returns users who were contacted by user or the contacts who contacted user

    if user == None:
        return 'userMissing'

    appCursor = appDb.cursor()

    sql = "SELECT id, username FROM UsersAuth WHERE id IN (SELECT msgTo FROM Messages WHERE msgFrom=%s)\
        OR id IN (SELECT msgFrom FROM Messages WHERE msgTo=%s)"
    val = (user, user)
    appCursor.execute(sql, val)
    result = appCursor.fetchall()

    appDb.commit()
    
    contacts = []

    for x in result:
        contacts.append({"id": x[0], "name": x[1]})

    return contacts


def sha256(hash: str):
    # Util function to return sha256 hash of the passed argument

    return hashlib.sha256(hash.encode()).hexdigest()
