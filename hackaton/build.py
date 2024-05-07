from flask import Flask, render_template, request
from flaskwebgui import FlaskUI
import socket

app = Flask(__name__)

ui = FlaskUI(app=app, server='flask', width=500, height=500)

@app.route('/')
def hello_world():
	return render_template('index.html')

@app.route('/backend/', methods=['GET'])
def get():
    return request.args.get('dato')
	# return render_template('index.html')
        

if __name__ == '__main__':
	app.run()
