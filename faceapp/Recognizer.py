import cv2
import numpy as np
from PIL import Image
import os
import winsound
import cv2
import time

from fsdb.fsdb import get_by_id, get_by_name
from .settings import CAM_PORT, NUMBER_OF_RECORDS

path = 'data'
recognizer = cv2.face.LBPHFaceRecognizer_create()
detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml");


def recognize() -> str:
    
    # load classifier
    recognizer.read('recognizer.yml')
    
    cam= cv2.VideoCapture(CAM_PORT, cv2.CAP_DSHOW)
    
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
            if (confidence >= 50):
                
                if len(possible_faces) < NUMBER_OF_RECORDS:
                    possible_faces.append(id)
                
                else:
                    print(possible_faces)
                    p = {}
                    for i in possible_faces:
                        if i not in [k for k in p.keys()]:
                            p[i] = possible_faces.count(i)
                    
                    id = max(p)
                    
                        
                    data = get_by_id(id)
                    confidence = "  {0}%".format(round(100 - confidence))
                    cv2.putText(img, str(data.name), (x - 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
                    time.sleep(2)
                    
                    return data.name
            
            else:
                winsound.Beep(900, 500)
                confidence = "  {0}%".format(round(100 - confidence))
                
        cv2.imshow('camera', img)
        k = cv2.waitKey(10) & 0xff
        if k == 27:
            break    
        
        