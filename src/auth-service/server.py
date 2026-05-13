import jwt, datetime, os, time
import psycopg2
from psycopg2 import sql
from flask import Flask, request

server = Flask(__name__)

DB_CONNECT_RETRIES = int(os.getenv('DB_CONNECT_RETRIES', '6'))
DB_CONNECT_RETRY_DELAY = float(os.getenv('DB_CONNECT_RETRY_DELAY', '2'))
DB_CONNECT_TIMEOUT = int(os.getenv('DB_CONNECT_TIMEOUT', '5'))


def get_db_connection():
    last_error = None
    for attempt in range(1, DB_CONNECT_RETRIES + 1):
        try:
            return psycopg2.connect(
                host=os.getenv('DATABASE_HOST'),
                database=os.getenv('DATABASE_NAME'),
                user=os.getenv('DATABASE_USER'),
                password=os.getenv('DATABASE_PASSWORD'),
                port=5432,
                connect_timeout=DB_CONNECT_TIMEOUT,
            )
        except psycopg2.OperationalError as e:
            last_error = e
            if attempt == DB_CONNECT_RETRIES:
                raise
            time.sleep(DB_CONNECT_RETRY_DELAY)
    raise last_error


@server.route('/login', methods=['POST'])
def login():
    auth_table_name = os.getenv('AUTH_TABLE')
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return 'Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'}

    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        query = sql.SQL("SELECT email, password FROM {} WHERE email = %s").format(
            sql.Identifier(auth_table_name)
        )
        cur.execute(query, (auth.username,))
        user_row = cur.fetchone()

        if not user_row:
            return 'Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'}

        email, password = user_row
        if auth.username != email or auth.password != password:
            return 'Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'}

        return CreateJWT(auth.username, os.environ['JWT_SECRET'], True)
    except psycopg2.OperationalError as e:
        return f'Database unavailable: {e}', 503
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

def CreateJWT(username, secret, authz):
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1),
            "iat": datetime.datetime.now(tz=datetime.timezone.utc),
            "admin": authz,
        },
        secret,
        algorithm="HS256",
    )

@server.route('/validate', methods=['POST'])
def validate():
    encoded_jwt = request.headers['Authorization']
    
    if not encoded_jwt:
        return 'Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'}

    encoded_jwt = encoded_jwt.split(' ')[1]
    try:
        decoded_jwt = jwt.decode(encoded_jwt, os.environ['JWT_SECRET'], algorithms=["HS256"])
    except:
        return 'Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'}
    
    return decoded_jwt, 200

if __name__ == '__main__':
    server.run(host='0.0.0.0', port=5000)
