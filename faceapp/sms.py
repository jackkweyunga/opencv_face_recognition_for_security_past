

from twilio.rest import Client

from settings import settings


client = Client("AC7580b24a06fffa8ca4d762c5c9053901", "c975a5ce350454548a4bfb07464da76b")


def send_sms(to, msg: str):
    
    # try:
    for t in to.split(","):
        message = client.messages \
                    .create(
                        body=msg,
                        from_='+12182858596',
                        to=t.strip()
                    )
        print(f"Sending sms to "+t)
    # except:
        # return "send failed"
