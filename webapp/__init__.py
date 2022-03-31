
from flask import Flask, render_template, Response, request
from webapp.gen_frames import gen_registration_frames, gen_detection_frames
from webapp.memberslist import get_members
import os
from faceapp.datagathering import register
from faceapp.sms import send_sms



app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

@app.route('/', methods=["GET", "POST"])
def index():
    from settings import settings, Settings
    
    settings = settings
    if request.method == "POST":
        settings = Settings(**request.form)
        settings.save()
    
    members = get_members()
    
    return render_template('index.html', members = members, settings = settings)


@app.route('/reg_video_feed')
def reg_video_feed():
    name = ""
    gen_registration_frames(name)
    return {}


@app.route('/det_video_feed')
def det_video_feed():
    face, p = gen_detection_frames()
    
    if p != None:
        p = int([*p.values()][0])
        
    if face is None:
        if p != None:
            if  p < 30:
                msg = "Intruder at the door."
                num = "+255712111936, +255755554741"
                send_sms(num, msg)
                return {"message":"no face detected"}
            
        msg = "Intruder at the door."
        num = "+255712111936, +255755554741"
        send_sms(num, msg)
        return {"message":"no face detected"}
    
    
    print(face, p)
    
    return {"message":face}


