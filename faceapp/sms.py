

from twilio.rest import Client

from faceapp.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN


client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def send_sms(to: str, msg: str):
    message = client.messages \
                .create(
                     body=msg,
                     from_='+12182858596',
                     to=to
                 )
    return message.status
