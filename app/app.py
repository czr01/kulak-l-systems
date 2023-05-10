from flask import Flask, render_template

app = Flask(__name__)

@app.route("/index")
def index():
    with open("./app/history.txt", 'r') as f:
        lsystem_fields = ["timestamp","variables","constants","axiom","rules","translations","iterations","resulting_string"]
        recent_lsystem = f.readlines()[-1][:-1].split("\t")
        recent_lsystem = {k: v for k, v in zip(lsystem_fields, recent_lsystem)}

    return render_template("index.html", recent_lsystem=recent_lsystem)