import os
from twilio.rest import Client

account_sid = "AC024a6c69dc9d367255de079c80288594"
auth_token = "408b734fbfd9b480f8d4392129718687"

client = Client(account_sid, auth_token)

client.messages.create(
    to="6177330634",
    from_="+16178299666",
    body="testing lalala"
)

# (C) William Wan
