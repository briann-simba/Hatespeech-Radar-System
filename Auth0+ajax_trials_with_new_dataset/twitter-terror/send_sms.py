from twilio.rest import Client
from os import environ as env
from dotenv import find_dotenv, load_dotenv

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


# Your Account SID from twilio.com/console
account_sid = env.get("account_sid")
# Your Auth Token from twilio.com/console
auth_token  = env.get("auth_token")

client = Client(account_sid, auth_token)



