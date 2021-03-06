
import cv2
import winsound

from fsdb.fsdb import get_by_id, get_by_name
import time 
from fsdb.fsdb import Data, get_by_name
import numpy as np
from faceapp.imagelables import imgsandlables


path = 'data'
recognizer = cv2.face.LBPHFaceRecognizer_create()
detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml");


def train():
    faces, ids = imgsandlables(path, detector)
    recognizer.train(faces, np.array(ids))
    
    recognizer.save("recognizer.yml")
        
    return recognizer


def gen_registration_frames(name: str):  
    from settings import settings
    print(settings.CAM_PORT)
    cam= cv2.VideoCapture(int(settings.CAM_PORT), cv2.CAP_DSHOW)
    
    WindowName="Face app"
    view_window = cv2.namedWindow(WindowName,cv2.WINDOW_FULLSCREEN)
    cv2.setWindowProperty(WindowName,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    cv2.moveWindow(WindowName, 350,120)
    
    if name != "" or name != None:
        new = Data(name)
        new.save()
        _id = get_by_name(new.name).id
        
        count = 0
        while(True):
            _, img= cam.read()
            img= cv2.flip(img, 1) # Flip camera vertically
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            faces = detector.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, )
            
            for (x,y,w,h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                count += 1
                cv2.imwrite(f"data/{_id}.{count}.jpg", gray[y:y+h,x:x+w])

            cv2.imshow(WindowName, img)
            k = cv2.waitKey(100) &  0xFF == ord('s')
            if k == 10:
                break
            elif count >= int(settings.NUMBER_OF_RECORDS):
                print("Started training data")
                
                train()
                cv2.destroyAllWindows()
                break
        else:
            print("No name provided")
            return None

            
            
def gen_detection_frames():  
    from settings import settings
    
    WindowName="Face app"
    view_window = cv2.namedWindow(WindowName,cv2.WINDOW_FULLSCREEN)
    cv2.setWindowProperty(WindowName,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    cv2.moveWindow(WindowName, 350,120)
    
    # load classifier
    recognizer.read('recognizer.yml')
    
    cam= cv2.VideoCapture(int(settings.CAM_PORT), cv2.CAP_DSHOW)
    
    possible_faces = []
    
    while True:
        _, img = cam.read()
        img = cv2.flip(img, 1)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = detector.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, )
        
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            id, confidence = recognizer.predict(gray[y:y + h, x:x + w])
            
            print(id, confidence)

            # Check if confidence is less them 100 ==> "0" is perfect match
            if (confidence >= 10):
                
                if len(possible_faces) < int(settings.NUMBER_OF_RECORDS):
                    possible_faces.append({
                        "id":id,
                        "confidence":confidence
                    })
                
                else:
                    # print(possible_faces)
                    ids = [i["id"] for i in possible_faces]
                    p = {}
                    for i in possible_faces:
                        if i["id"] not in [k for k in p.keys()]:
                            p[i["id"]] = ids.count(i["id"])
                    
                    id = max(p)
                    
                    # calculating average confidence
                    confid = max([p for p in [po["confidence"] for po in possible_faces if po["id"] == id]])
                    
                    print(confid)
                    print(p)
                    print(id)
                    
                    data = get_by_id(id)
                    
                    if data == None:
                        time.sleep(2)
                        cv2.destroyAllWindows()
                        return None, None
                    
                    confidence = "  {0}%".format(round(100 - confidence))
                    cv2.putText(img, str(data.name), (x - 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
                    time.sleep(2)
                    cv2.destroyAllWindows()
                    
                    return data.name, confid
            
            else:
                winsound.Beep(900, 500)
                confidence = "  {0}%".format(round(100 - confidence))
                
        cv2.imshow(WindowName, img)
        k = cv2.waitKey(10) & 0xff
        if k == 27:
            break   