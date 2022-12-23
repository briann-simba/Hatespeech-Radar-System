import os
import sys
import time
from flask import Flask,render_template,jsonify,request,session,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
import numpy as np
from sqlalchemy import Column, Integer, String, distinct,func,DateTime, Boolean, Float,inspect
import pandas as pd
import sqlalchemy
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from tweepy import Stream
from deploy import Hate
from flask_cors import CORS
import online
import threading
import json
from datetime import datetime
from os import environ as env
from urllib.parse import quote_plus, urlencode
import multiprocessing

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


app=Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'


db=SQLAlchemy(app)
oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

class Tweet(db.Model):
    
    id = Column(Integer, primary_key=True)
    user_name = Column(String(256), nullable=False)
    tweet_body = Column(String(1000))
    location = Column(String(100))
    label = Column(String(20))
    date_posted=db.Column(db.DateTime(),nullable=False,default=datetime.utcnow)
    created_at=db.Column(db.DateTime(),nullable=False)
    def as_dict(self):
       return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}
class User(db.Model):
   id=db.Column(db.Integer,primary_key=True)
   username=db.Column(db.String(20),unique=True,nullable=False)
   email=db.Column(db.String(120),unique=True,nullable=False)
   image_file=db.Column(db.String(60),nullable=False,default='default.jpg')
   def as_dict(self):
       return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}
   


@app.route("/")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/home")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("login", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route("/home",methods=["GET","POST"])
def home():
  
    
   
    sesh=session.get('user')
    print(sesh["userinfo"]["name"])
    if not sesh:
        return redirect(url_for("login"))
   
    try:
        
        username=sesh["userinfo"]["name"]
        email=sesh["userinfo"]["email"]
        image_file=sesh["userinfo"]["picture"]
        test_user=User.query.filter_by(email=email).first()
        if not test_user:
         
                u1=User(username=username,email=email,image_file=image_file)
                db.session.add(u1)
                db.session.commit()
    except:
                print('error during committing')
                

    return render_template('home.html',title="Hatespeech Radar", \
        session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

@app.route("/account",methods=["GET"])
def account():
   
    sesh=session.get('user')
    
    if not sesh:
        return redirect(url_for("login"))
    return render_template('account.html',title="Hatespeech Radar", session=session.get('user'))


@app.route("/flagged",methods=["GET"])
def flagged():
    sesh=session.get('user')
    if not sesh:
        return redirect(url_for("login"))
    return render_template('flagged.html',title="Hatespeech Radar", session=session.get('user'))


@app.route("/stream",methods=["GET","POST"])
def stream():
    sesh=session.get('user')
    if not sesh:
        return redirect(url_for("login"))
    if request.method == 'POST':
        track = request.form.get('track')
        track_array=[]


    
    class Thread (threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            
 

        def run(self):
           
            if track:
                track_array.append(track)
                print(track_array)
                online.maine(track=track_array)
            online.maine(track=['kenya'])

        
    

    t = Thread()
    t.start()
    
    
    
    
    
    
   
    return render_template("home.html",title="Hatespeech Radar", session=session.get('user'))


@app.route("/get_tweets",methods=["GET","POST"])
def get_tweets():
    my_Arr=[]
    tweets=db.session.query(Tweet)
    desc_expression = sqlalchemy.sql.expression.desc(Tweet.date_posted)
    tweets= tweets.order_by(desc_expression)
    for entry in tweets:
        my_Arr.append(entry.as_dict())
    tweets=jsonify(my_Arr)
    tweets=json.loads(tweets.data)
    return {"tweets":tweets}


@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response
    





if __name__=='__main__':
    app.run(debug=True,threaded=True)