import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL

server = Flask(__name__)
mysql = MySQL(server)

# config
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = os.environ.get("MYSQL_PORT")

@server.route('/login', methods=["POST"])
def login():
    # Use basic authentication, which is a username and a password
    # Authorization: Basic <base64encoded username:password>
    auth = request.authorization
    
    if not auth:
        return "missing credentials", 401

    # check db for username and password
    # Task:
        # secure this to prevent sql injection
    cur = mysql.connection.cursor()
    res = cur.execute(
        f"SELECT email, password FROM user WHERE email={auth.username};"
    )
    
    if res > 0:
        user_row = cur.fetchone()
        email = user_row[0]
        password = user_row[1]
        
        if auth.username != email or auth.password != password:
            return "invalid credentials", 401
        else:
            return createJWT(auth.username, os.environ.get("JWT_SECRET"), True)
    else:
        return "invalid credentials", 401

@server.route("/validate", methods=["POST"])
def validate():
    # Authorization: Bearer <token>
    encoded_jwt = request.headers["Authorization"]
    
    if not encoded_jwt:
        return "missing credentials", 401
    
    encoded_jwt = encoded_jwt.split(' ')[1]
    
    try:
        decoded = jwt.decode(encoded_jwt, os.environ.get("JWT_SECRET"), algorithms="HS256")
    except:
        return "not_authorized", 401
    
    return decoded, 200
    

def createJWT(username, secret, is_admin):
    return jwt.encode(
        {
            "username": username,
            "expiration": datetime.datetime.utcnow() + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "admin": is_admin,
        },
        secret,
        algorithm="HS256"
    )

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)