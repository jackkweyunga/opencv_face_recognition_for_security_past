import cv2
import numpy as np
from PIL import Image
import winsound
import cv2
import time

from fsdb.fsdb import get_by_id, get_by_name
from settings import settings
import mediapipe as mp
from .preprocess import gammaCorrection , sharppen
from .utils import maxk

path = 'data'
recognizer = cv2.face.LBPHFaceRecognizer_create()
detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml");


# create holistics instances
# 
mp_drawing_utils = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic
mp_drawing_styles = mp.solutions.drawing_styles


def recognize(n_frames = 100) -> str:
    
    # load classifier
    recognizer.read('recognizer.yml')
    
    # cam= cv2.VideoCapture(int(settings.CAM_PORT), cv2.CAP_DSHOW)
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    possible_faces = []
    track_frames = 0
    with mp_holistic.Holistic(min_detection_confidence=0.5,min_tracking_confidence=0.5) as holistic:
        
        while cam.isOpened():
            _, img = cam.read()
            
            # sharpen
            img = sharppen(img)
            
            # gamma correction
            gamma = 1.5
            img = gammaCorrection(img, gamma=gamma)
            
            # resolution
            # failed
            
            image=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            
            image = cv2.flip(image, 1)
            
            result=holistic.process(image)
            
            image=cv2.cvtColor(image,cv2.COLOR_RGB2BGR)
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            box1 = [200,40]
            box2 = [500,400]
            
            image=cv2.rectangle(image,np.array(box1),np.array(box2),(0,0,255),3)

            # faces = detector.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, )
                            
            # Check if confidence is less them 100 ==> "0" is perfect match
            try:
            # if True:
                coord1=tuple(np.multiply(np.array((result.face_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_EAR].x,result.face_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_EAR].y)),[640,480]).astype('int'))
                
                z = result.face_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_EYE].z
                
                coord1=np.array(coord1)+np.array((100,-110))
                
                coord2=tuple(np.multiply(np.array((result.face_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_EAR].x,result.face_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_EAR].y)),[640,480]).astype('int'))
                
                coord2=np.array(coord2)+np.array((-60,130))
                
                # print(coord1, coord2)
                
                id, confidence = recognizer.predict(gray[coord1[1]:coord2[1], coord2[0]:coord1[0]])
                data = get_by_id(id)
                
                # draw on image
                image=cv2.rectangle(image,box1,box2,(0,0,255),3)
                
                z = result.face_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_EYE].z
                # print(z)
                
                cv2.putText(img=image, text = f"User Name", org = np.array(box1)+np.array((-180,20)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=.6, color=(255,0,0), thickness=2)
                cv2.putText(img=image, text = f"{data.name}", org = np.array(box1)+np.array((-180,50)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=.6, color=(255,0,0), thickness=2)
                cv2.putText(img=image, text = f"Dist. from cam", org = np.array(box1)+np.array((-180,100)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=.6, color=(255,0,0), thickness=2)
                cv2.putText(img=image, text = f"{str(z)[:6]}", org = np.array(box1)+np.array((-180,130)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=.6, color=(255,0,0), thickness=2)
                
            
                if z<-0.04 and z>-0.05 and (confidence >= 50):
                    image1=cv2.rectangle(image,box1,box2,(0,255,0),5)
                    cv2.imshow('raw',image1)
                    
                    face=np.array(result.face_landmarks.landmark)
                    # print(face)
                    image = gray[coord1[1]:coord2[1], coord2[0]:coord1[0]]

                    # cv2.imwrite(f"data/{id}.{str(track_frames)}.jpg", image)
                    
                    if len(possible_faces) < int(settings.NUMBER_OF_RECORDS):
                        possible_faces.append(id)
                    else:
                        print(possible_faces)
                        p = { i:possible_faces.count(i) for i in possible_faces}
                        print(p)
                        id = maxk(p)
                        print(id)
                        
                        data = get_by_id(id)
                        # confidence = "  {0}%".format(round(100 - confidence))
                        # cv2.putText(img, str(data.name), (x - 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
                        time.sleep(1)
                        cam.release()
                        cv2.destroyAllWindows() 
                        
                        return data.name
                    
                    print(id, confidence)
                    track_frames += 1
                elif z<-0.05:
                    cv2.putText(img=image, text = f"TOO CLOSE", org = np.array(box1)+np.array((-180,190)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=.7, color=(0,0,255), thickness=2)
                    cv2.imshow('raw',image)  
                else:
                    cv2.putText(img=image, text = f"MOVE CLOSER", org = np.array(box1)+np.array((-180,190)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=.7, color=(0,0,255), thickness=2)
                    cv2.imshow('raw',image)    
                    
            except:
                # print("Execption occured")
                cv2.imshow('raw',image)
                
            if (cv2.waitKey(10) & 0xFF == ord('Q')) or track_frames > n_frames :
                break
                
            # else:
            #     winsound.Beep(900, 500)
            #     confidence = "  {0}%".format(round(100 - confidence))
            # cv2.imshow('camera', img)
              
    cam.release()
    cv2.destroyAllWindows() 
    
    return "Not recognized"
            