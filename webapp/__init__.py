
from flask import Flask, render_template, Response, request, redirect, url_for
from webapp.gen_frames import gen_registration_frames, gen_detection_frames
from webapp.memberslist import get_members
import os
from faceapp.datagathering import register
from faceapp.sms import send_sms
import settings
import cv2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True


@app.route('/')
def index():
    from settings import settings
    
    context = {
        "members" : get_members(),
        "settings": settings,
        "messages": [{
            "level":"info",
            "message": "Face Detection Program"
        }]
    }
    
    
    return render_template('index.html', **context)

@app.route('/clear_data')
def clear_data():
    
    return redirect(url_for('index'))

@app.route('/settings', methods=["POST"])
def settings():
    from settings import Settings
    
    settings = Settings(**request.form)
    settings.save()
    members = get_members()
    return render_template('index.html', members = members, settings = settings)



@app.route('/reg_video_feed', methods=["POST"])
def reg_video_feed():
    name = f"{request.form['first_name']} {request.form['last_name']}"
    print(name)
    gen_registration_frames(name)
    cv2.destroyAllWindows()
    return {}


@app.route('/det_video_feed')
def det_video_feed():
    from settings import settings
    face, p = gen_detection_frames()
    
    if p != None:
        p = int([*p.values()][0])
        
    if face is None:
        if p != None:
            if  p < 30:
                msg = "Intruder at the door."
                num = settings.PHONE_NUMBERS
                send_sms(num, msg)
                return {"message":"no face detected"}
            
        msg = "Intruder at the door."
        num = settings.PHONE_NUMBERS
        send_sms(num, msg)
        return {"message":"no face detected"}
    
    print(face, p)
    cv2.destroyAllWindows()
    
    return {"message":face}


