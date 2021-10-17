import base64
from bottle import abort, get, post, redirect, request, response, run, SimpleTemplate
import hashlib
import pyotp
import yaml
import random
import time

class Token:
    def __init__(self, username, password) -> None:
        self.key = '%064x' % random.getrandbits(8*32)
        self.t = time.time()
        self.username = username
        self.password = password

    def invalid(self) -> bool:
        return time.time() - self.t >= TOKEN_LIFETIME

class User:
    def validate_totp_with_secret(self, secret: str, totp: str) -> str:
        return totp == pyotp.TOTP(secret).now()

    def validate_password(self, password: str) -> bool:
        return False
    
    def validate_totp(self, totp: str) -> bool:
        return False

class AuthBackend:
    def fetch_user(self, username: str) -> User:
        return None

class AuthBackendConfig(AuthBackend):
    class AuthBackendConfigUser(User):
        def __init__(self, user_config: dict) -> None:
            self.config = user_config

        def validate_password(self, password: str) -> bool:
            pwc = self.config['password']
            if not pwc['check']:
                return True
            pbkdf2 = pwc['pbkdf2']
            hmac = hashlib.pbkdf2_hmac(
                pbkdf2['hash_name'],
                password.encode('utf-8'),
                pbkdf2['salt'].encode('utf-8'),
                pbkdf2['iterations']
            ).hex()
            print(pbkdf2['hmac'])
            print(hmac)
            return not pwc['check'] or pbkdf2['hmac'] == hmac
        
        def validate_totp(self, totp: str) -> bool:
            totpc = self.config['totp']
            return not totpc['require'] or self.validate_totp_with_secret(
                totpc['secret'],
                totp
            )

    def __init__(self, backend_config: dict) -> None:
        self.config = backend_config

    def fetch_user(self, username: str) -> User:
        users = self.config['users']
        if username not in users:
          return None
        return self.AuthBackendConfigUser(users[username])

config_file = open('config.yaml', 'r')
config = yaml.full_load(config_file.read())
config_file.close()

PORT = config['app']['port']
TOKEN_LIFETIME = config['app']['token_lifetime']
COOKIE_SECRET = config['app']['cookie_secret']

AFTER_LOGIN_REDIRECT = config['app']['after_login_redirect']

PASS_UNKNOWN = config['auth']['policy']['pass_unkown']

LAST_LOGIN_ATTEMPT = 0

BACKEND = AuthBackendConfig(config['auth']['backend']['config'])

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
    return SimpleTemplate(config['templates']['login']).render()

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

    user = BACKEND.fetch_user(username)

    if (
        user is None and PASS_UNKNOWN or
        user is not None and user.validate_password(password) and user.validate_totp(totp)
    ):
        token = Token(username, password)
        response.set_cookie('token', token, path='/', secret=COOKIE_SECRET)

    redirect(AFTER_LOGIN_REDIRECT, code=302)

run(host='localhost', port=PORT)
