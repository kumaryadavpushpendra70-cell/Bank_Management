from flask import Flask, render_template, request, redirect, session, url_for
from api import auth, transaction

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(transaction.bp)

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("transaction.dashboard"))
    return redirect(url_for("auth.login"))

if __name__ == "__main__":
    app.run(debug=True)

