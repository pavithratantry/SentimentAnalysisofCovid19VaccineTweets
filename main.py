from flask import Flask, render_template, request, redirect, session
from sentiments import second
import os


app = Flask(__name__)

# initializing the user cookie
app.secret_key = os.urandom(24)

# blueprint to call the second python file in the project.
app.register_blueprint(second)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/')
def sentiment_analyzer():
 	return render_template('sentiment_analyzer.html')


if __name__ == "__main__":
	app.run(debug=True)


