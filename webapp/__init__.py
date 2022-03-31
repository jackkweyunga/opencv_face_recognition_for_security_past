
from time import time
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
    import os, shutil
    try:
        shutil.rmtree('data/')
    except:
        pass
    
    try:
        os.mkdir("data")
    except:
        pass
    
    with open('data/data.md', 'w+') as f:
        f.write("# All data stays here")
        
    # remove database
    with open('db.json', 'w+') as d:
        d.write("[]")
    
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
    from settings import settings
    
    context = {
            "members" : get_members(),
            "settings": settings,
            "messages": [{
                "level":"info",
                "message": "Face Detection Program"
            }]
        }
    
    try:
        name = f"{request.form['first_name']} {request.form['last_name']}"
        print(name)
        gen_registration_frames(name)
        cv2.destroyAllWindows()
        # time.sleep(2)
        context["members"] = get_members()
        context["messages"] = [{
            "level":"info",
            "message":f"User {name} registered successfully"
        }]
        
        return render_template('index.html', **context)
    except:
        cv2.destroyAllWindows()
    
        context["messages"] = [{
            "level":"error",
            "message":f"User {name} registration failed"
        }]
        
        return render_template('index.html', **context)



@app.route('/det_video_feed')
def det_video_feed():
    
    from settings import settings
    
    context = {
            "members" : get_members(),
            "settings": settings,
            "messages": [{
                "level":"info",
                "message": "Face Detection Program"
            }]
        }
    
    try:
        from settings import settings
        face, p = gen_detection_frames()
        
        if face is None:
            if p != None:
                if  p < 50:
                    msg = "Intruder at the door."
                    num = settings.PHONE_NUMBERS
                    send_sms(num, msg)
                    return {"message":"no face detected"}
                
            msg = "Intruder at the door."
            num = settings.PHONE_NUMBERS
            send_sms(num, msg)
            context["messages"] = [{
                "level":"error",
                "message":f"Intruder Detected !!!"
            }]
            
            return render_template('index.html', **context)
        
        print(face, p)
        cv2.destroyAllWindows()
        context["messages"] = [{
            "level":"info",
            "message":f"welcome in {face}"
        }]
        
        return render_template('index.html', **context)
    
    except:
        
        cv2.destroyAllWindows()
    
        context["messages"] = [{
            "level":"error",
            "message":"Some error occured. Detection failed!!!"
        }]
        
        return render_template('index.html', **context)
        
