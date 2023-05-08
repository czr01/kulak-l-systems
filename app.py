from flask import Flask, render_template

app = Flask(__name__)
history_file = "history.txt"

@app.route("/index")
def index():
    with open(history_file, 'r') as f:
        recent_lsystem = f.readlines()[-1]
        result = recent_lsystem.split("\t")[-1][:-1]
        translations = recent_lsystem.split("\t")[-3]
    return render_template("index.html", recent_lsystem=recent_lsystem, result=result, translations=translations)

app.run(debug=True)