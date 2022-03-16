
from flask import Flask, render_template, Response
from webapp.gen_frames import gen_frames
from webapp.memberslist import get_members
import os

app = Flask(__name__)


@app.route('/')
def index():
    
    members = get_members()
    
    return render_template('index.html', members = members)


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/settings', methods=['POST'])
def settings():
    return {}

