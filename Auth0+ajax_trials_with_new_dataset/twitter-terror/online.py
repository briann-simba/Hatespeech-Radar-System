from __future__ import absolute_import, print_function
import numpy as np
import pandas as pd

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import dataset
import sys
import send_sms
from sqlalchemy.exc import ProgrammingError
from app import db,Tweet
import time
import sys
import os
from os import environ as env
from dotenv import find_dotenv, load_dotenv

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


from deploy import Hate

consumer_key =  env.get("consumer_key")
consumer_secret = env.get("consumer_secret")
access_token = env.get("access_token")
access_token_secret =env.get("access_token_secret")


class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_connect(self):
        print('Stream starting...')

    
    def on_status(self, status):
       
        
        k= Hate()
        k.cleanTrain()
        m=k.interface(status)
        w= m['weight']
        print(status.text)
        print(status.user.location)
        print(status.user.id)
        label=max(w)
        print(f'int val of label is {label}')
        label="NOT HATESPEECH" if label < 1 else "HATESPEECH"
        print(f'This tweet is {label}')
        tweet_body=status.text if not status.truncated else status.extended_tweet['full_text']
        if (label=="HATESPEECH"):
            try:
                message = send_sms.client.messages.create(to="+254797911505",
                 from_="+19705949675",body=f"POTENTIALLY OFFENSIVE TWEET ALERT!! sender:{status.user.name},  \
                               tweet:{tweet_body} ,  location:{status.user.location}, time_posted:{status.created_at}     ")
                print(message.sid)
                print("message sent")
            except:
                print('unknown error occurred when sending tweet!')
        try:
            test_tweet=Tweet.query.filter_by(tweet_body=tweet_body).first()
            if not test_tweet:
                t1=Tweet(user_name=status.user.name,tweet_body=tweet_body,\
                    location=status.user.location,created_at=status.created_at,label=label)
                db.session.add(t1)
                db.session.commit()
        except:
            print('unknown error occurred when posting tweet!')
       
        
        return True
    def on_error(self, status_code):
        if status_code == 420:
            
            return False

    






l = StdOutListener()
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
locations=[33.8935689697, -4.67677, 41.8550830926, 5.506]
def maine(track):
    
    stream = Stream(auth, l)
    stream.filter(track=track,languages=["en"])
    


