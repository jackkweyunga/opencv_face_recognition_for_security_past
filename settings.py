


from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

import json

settings = {}
with open("settings.json", "r") as s:
    settings = json.load(s)


class Settings:
    
    def __init__(
        self,
        CAM_PORT = 0,
        NUMBER_OF_RECORDS = 20,
        DOORLOCK_PORT = "COM15",
        TWILIO_ACCOUNT_SID = "AC7580b24a06fffa8ca4d762c5c9053901",
        TWILIO_AUTH_TOKEN = "86dd6314aa511821ebaf83227dcad537",
        PHONE_NUMBERS = "+255712111936",
        TITLE = "TITLE"
        ):
        self.TITLE = TITLE
        self.CAM_PORT = CAM_PORT
        self.NUMBER_OF_RECORDS = NUMBER_OF_RECORDS
        self.DOORLOCK_PORT = DOORLOCK_PORT
        self.TWILIO_ACCOUNT_SID = TWILIO_ACCOUNT_SID
        self.TWILIO_AUTH_TOKEN = TWILIO_AUTH_TOKEN
        self.PHONE_NUMBERS = PHONE_NUMBERS
        
    def save(self):        
        with open("settings.json", "w") as s:
            json.dump(self.__dict__, s)

settings = Settings(**settings)