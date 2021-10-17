import base64
from bottle import abort, get, post, redirect, request, response, run, template
import pyotp
import random
import time

PORT = 8000

TOKEN_LIFETIME = 60 * 60 * 24

LAST_LOGIN_ATTEMPT = 0

COOKIE_SECRET = 'nMNuRnvTczi2TU4jWZKfzTUzF'

SECRET = open('.totp_secret').read().strip()

class Token:
    def __init__(self, username, password) -> None:
        self.key = '%064x' % random.getrandbits(8*32)
        self.t = time.time()
        self.username = username
        self.password = password

    def invalid(self) -> bool:
        return time.time() - self.t >= TOKEN_LIFETIME

@get('/test')
def get_test():
    return 'Ok: ' + request.get_header('authorization')

@get('/auth/check')
def get_auth_check():
    token = request.get_cookie('token', secret=COOKIE_SECRET)
    if token is None or token.invalid():
        abort(401, '')
    response.set_header(
        'Authorization',
        'Basic ' + base64.b64encode(
            b'%s:%s' % (
                token.username.encode('utf-8'),
                token.password.encode('utf-8')
            )
        ).decode('utf-8')
    )
    return ''

@get('/auth/login')
def get_auth_login():
    return template('src/templates/login.tpl')

@get('/auth/logout')
def get_auth_logout():
    token = request.get_cookie('token', secret=COOKIE_SECRET)
    if token:
        response.set_cookie('token', '', path='/', expires=0, max_age=0)
    redirect('/', code=302)

@post('/auth/login')
def post_auth_login():
    # Login rate limit
    global LAST_LOGIN_ATTEMPT
    if time.time() - LAST_LOGIN_ATTEMPT < 1.0:
        abort(429, 'Too many login attempts. Try again a few seconds later.')
    LAST_LOGIN_ATTEMPT = time.time()

    username = request.forms.get('username')
    password = request.forms.get('password')
    totp     = request.forms.get('totp')
    totp_now = pyotp.TOTP(SECRET).now()

    if (totp == totp_now):
        token = Token(username, password)
        response.set_cookie('token', token, path='/', secret=COOKIE_SECRET)

    redirect('/', code=302)

run(host='localhost', port=PORT)
