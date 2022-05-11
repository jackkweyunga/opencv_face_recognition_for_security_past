import time
import cv2
from fsdb.fsdb import Data, get_by_name
from settings import settings
import numpy as np
from faceapp.imagelables import imgsandlables
import mediapipe as mp
import pandas as pd
from .preprocess import gammaCorrection, sharppen

path = 'data'
recognizer = cv2.face.LBPHFaceRecognizer_create()
detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml");


# create holistics instances
# 
mp_drawing_utils = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic
mp_drawing_styles = mp.solutions.drawing_styles

def train():
    faces, ids = imgsandlables(path, detector)
    print(faces)
    recognizer.train(faces, np.array(ids))
    
    recognizer.save("recognizer.yml")
        
    return recognizer
            

# preparation

def register(name: str, n_frames = 2):
    
    # cam = cv2.VideoCapture(int(settings.CAM_PORT), cv2.CAP_DSHOW)
    cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    
    new = Data(name)
    new.save()
    id = get_by_name(new.name).id
    
    track_frames = 0 
    with mp_holistic.Holistic(min_detection_confidence=0.5,min_tracking_confidence=0.5) as holistic:
       
        while cam.isOpened():
            _,image=cam.read()
            
            # sharpen
            image = sharppen(image)
            
            # gamma correction
            gamma = 1.5
            image = gammaCorrection(image, gamma=gamma)
            
            image=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
            
            image = cv2.flip(image, 1)
            
            result=holistic.process(image)
            
            image=cv2.cvtColor(image,cv2.COLOR_RGB2BGR)
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            box1 = [200,40]
            box2 = [500,400]
            
            image=cv2.rectangle(image,np.array(box1),np.array(box2),(0,0,255),3)
            
            
            # mp_drawing_utils.draw_landmarks(
            # image,
            # result.face_landmarks,
            # mp_holistic.FACEMESH_TESSELATION,
            # landmark_drawing_spec=None,
            # connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style())
            # mp_drawing_utils.draw_landmarks(image,result.pose_landmarks,mp_holistic.POSE_CONNECTIONS)
            # mp_drawing_utils.draw_landmarks(image,result.right_hand_landmarks,mp_holistic.HAND_CONNECTIONS)
            # mp_drawing_utils.draw_landmarks(image,result.left_hand_landmarks,mp_holistic.HAND_CONNECTIONS)
            # #image = cv2.resize(image, (1000,7000))
            
            try:
                coord1=tuple(np.multiply(np.array((result.face_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_EAR].x,result.face_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_EAR].y)),[640,480]).astype('int'))
                
                z = result.face_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_EYE].z
                # cv2.putText(img=image, text = str(z)[:8], org = np.array(coord1)+np.array((100,-110)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255,0,0), thickness=3)
                
                coord1=np.array(coord1)+np.array((100,-110))
                coord2=tuple(np.multiply(np.array((result.face_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_EAR].x,result.face_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_EAR].y)),[640,480]).astype('int'))
                
                coord2=np.array(coord2)+np.array((-60,130))
                
                image=cv2.rectangle(image,box1,box2,(0,0,255),3)
                
                z = result.face_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_EYE].z
            
                cv2.putText(img=image, text = f"User Name", org = np.array(box1)+np.array((-180,20)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=.6, color=(255,0,0), thickness=2)
                cv2.putText(img=image, text = f"{name}", org = np.array(box1)+np.array((-180,50)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=.6, color=(255,0,0), thickness=2)
                cv2.putText(img=image, text = f"Sample No.", org = np.array(box1)+np.array((-180,100)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=.6, color=(255,0,0), thickness=2)
                cv2.putText(img=image, text = f"{track_frames}", org = np.array(box1)+np.array((-180,130)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=.6, color=(255,0,0), thickness=2)
                
                if z<-0.04 and z>-0.05:
                    image1=cv2.rectangle(image,box1,box2,(0,255,0),5)
                    
                    face=np.array(result.face_landmarks.landmark)
                    cv2.imshow('raw',image1)
                    
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    image = image[coord1[1]:coord2[1], coord2[0]:coord1[0]]
                    cv2.imwrite(f"data/{id}.{str(track_frames)}.jpg", image)
                    track_frames += 1
                
                elif z>-0.05:
                    cv2.putText(img=image, text = f"TOO CLOSE", org = np.array(box1)+np.array((-180,190)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=.7, color=(0,0,255), thickness=2)
                    cv2.imshow('raw',image)  
                else:
                    cv2.putText(img=image, text = f"MOVE CLOSER", org = np.array(box1)+np.array((-180,190)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=.7, color=(0,0,255), thickness=2)
                    cv2.imshow('raw',image) 
                     
            except:
                # print("Execption occured")
                cv2.imshow('raw',image)
                
            if track_frames > n_frames:
                print("Started training data")
                time.sleep(2)
                train()
                break
                
            if (cv2.waitKey(10) & 0xFF == ord('Q')) :
                
                break
            
    # destroy frame window
    cam.release()
    cv2.destroyAllWindows()   
            
          
