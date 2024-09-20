from flask import Flask, render_template, request, redirect, g
import sqlite3
import re

app = Flask(__name__)

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
 
DATABASE = "login_credentials.db"

# <----- connecting database when reqd----->
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

# <----- closing connection when not reqd ----->
@app.teardown_appcontext
def close_db(error):
    if 'db' in g:
        g.db.close()

def email_check(email):
 
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False

@app.route("/", methods=['GET','POST'])
def Login():
    if request.method=="POST":
        if request.form.get("button")=="login":
            username=request.form['username']
            password=request.form['password']
            if username=="" or password=="":
                return render_template("login.html",invalid_cred="Fields cannot be left blank!")
            db = get_db()
            pass_check=db.execute(f"""SELECT passw FROM cred WHERE usr='{username}';""").fetchone()
            if pass_check is not None and password==pass_check[0]:
                  return render_template("welcome.html", usr=username)
            else:
                return render_template("login.html",invalid_cred="Invalid username or password!")
        elif request.form.get("button")=="register_page":
            return redirect("/register")
    return render_template("login.html")


@app.route("/register", methods=["POST","GET"])
def Register():
    if request.method=="POST":
        if request.form.get("button")=="create":
            user=request.form["username"]
            email=request.form["email"]
            db = get_db()
            if user=="":
                return render_template("register.html",invalid_usr="Username cannot be left blank")
            elif email=="":
                return render_template("register.html", invalid_email="Email cannot be left blank", usr_place=user)
            elif request.form["passw"]=="" or request.form["c_passw"]=="":
                return render_template("register.html",invalid_passw="Password cannot be left blank", usr_place=user, em_place=email)
            elif db.execute(f"""SELECT usr FROM cred WHERE usr='{request.form["username"]}';""").fetchone()!=None:
                return render_template("register.html", invalid_usr="Username already in use",em_place=email)
            elif not email_check(request.form["email"]):
                return render_template("register.html", invalid_email="Invalid Email address",usr_place=user)
            elif db.execute(f"""SELECT email FROM cred WHERE email='{request.form["email"]}';""").fetchone()!=None:
                return render_template("register.html", invalid_email="Email address already in use", usr_place=user)
            elif request.form["passw"]!=request.form["c_passw"]:
                return render_template("register.html",invalid_passw="Passwords do not match",usr_place=user,em_place=email)
            else:
                db.execute("INSERT INTO cred VALUES (?,?,?)", (request.form["username"],request.form["email"],request.form["c_passw"]))
                db.commit()
                return render_template("register.html",success_msg="Registration successful! Please Login to continue")
        elif request.form.get("button")=="login_page":
            return redirect("/")
    return render_template("register.html")

if __name__=="__main__":

    app.run(debug=True)