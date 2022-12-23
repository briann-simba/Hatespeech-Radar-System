import sys
import re
import pandas as pd
from sklearn.utils import resample
from nltk.tokenize import word_tokenize,sent_tokenize

import numpy as np

#bow tools and classifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from sklearn.svm import LinearSVC,SVC
import pickle

#twilio rest api import package
from twilio.rest import Client

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score,precision_score,classification_report




stemmer = SnowballStemmer('english')    
words =  stopwords.words('english')

class Hate(object):
    def cleanTrain(self):
        #opening tweets dataset
        data=pd.read_csv('normal-binary-hate.csv')


        #cleaning the tweets
        def  clean_text(df, text_field):
            corpus=[]
            df=df.dropna()
            df = df.reset_index(drop=True)
            df[text_field] = df[text_field].str.lower()
            
            for i in range(0,len(df.copy())):
                review=re.sub('@[^\s]+','', df[text_field][i])
                review=re.sub(r'https?:\/\/\S+', '',review)
                review=re.sub(r'^RT[\s]+', '',review)
                review=re.sub(r'#', '',review)
                review=re.sub(r"www\.[a-z]?\.?(com)+|[a-z]+\.(com)", '',review)
                review=re.sub(r'{link}', '',review)
                review=re.sub(r'&[a-z]+;', '',review)
                review=re.sub(r"[^a-z\s\(\-:\)\\\/\];='#]", '',review)
                review=review.split()
                review=[stemmer.stem(word) for word in review if not word in words]
                review=" ".join(review)
                corpus.append(review)
            return corpus



            
            


        data_clean = clean_text(data, "tweet")
        X=data_clean
        print(f'cleaned X variable is a {type(X)}')
        Y =data['label'].values
     
        self.tfidf=TfidfVectorizer(max_features=5000)
        X=self.tfidf.fit_transform(X)
        
        return



    def interface(self,status):
        
        text_corpus=[]
        text =re.sub('@[^\s]+','', status if isinstance(status,str) else status.text)
        text=re.sub(r'https?:\/\/\S+', '',text)
        text=re.sub(r'^RT[\s]+', '',text)
        text=re.sub(r'#', '',text)
        text=re.sub(r"www\.[a-z]?\.?(com)+|[a-z]+\.(com)", '',text)
        text=re.sub(r'{link}', '',text)
        text=re.sub(r'&[a-z]+;', '',text)
        text=re.sub(r"[^a-z\s\(\-:\)\\\/\];='#]", '',text)
        text=text.lower()
      
        
        tfidf=self.tfidf
        vec=tfidf.transform([text])
        
        filename = 'finalized_model.sav'
        loaded_model = pickle.load(open(filename, 'rb'))
        

        my_val=(loaded_model.predict(vec)> 0.5).astype("int32")
      
        print(f'my_val:{my_val}')
       

        useful = {'weight':my_val}
       
        return useful
















