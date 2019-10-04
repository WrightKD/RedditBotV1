# -*- coding: utf-8 -*-
"""RedditBot2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_4YPw80O0PWBJhUsqiq3JcxYtmEMAqmF
"""

import praw
import regex as re
from datetime import datetime
import time
import pymongo
import os

reddit = praw.Reddit(user_agent='Reddit Bot (by /u/KenKiKeo)',
                     client_id = os.environ['client_id'], client_secret = os.environ['client_secret'],
                     username = os.environ['username'], password = os.environ['password'])

client = pymongo.MongoClient(os.environ['MongoClient'])
db = client["RedditBot"]
collection = db["Botv1"]

delay = int(os.environ['delay'])
subreddits = os.environ['subreddits']

#confidence+socialskills+making_friends+dating_advice

subreddit = reddit.subreddit(subreddits)

comment_stream = subreddit.stream.comments(pause_after=-1,skip_existing=True)
submission_stream = subreddit.stream.submissions(pause_after=-1,skip_existing=True)

KEYS = ['self-esteem', 'anxiety', 'nervous', 'self-doubt', 'no confidence', 'no charisma']

messageQueue = []

def FindKeys(sentence):

  isKey = False
  foundWord = 'None'

  sentence= re.sub(r"\p{P}", lambda m: "-" if m.group(0) == "-" else "", sentence)

  if ('no charisma' in sentence.lower()):
    return {'Key' : True , 'keyword' : 'no charisma'}

  if ('no confidence' in sentence.lower()):
    return {'Key' : True , 'keyword' : 'no confidence'}

  words = sentence.split()

  for word in words:

    if word.lower() in KEYS:
      foundWord = word.lower()
      isKey = True
      break
  
  return {'Key' : isKey , 'keyword' : foundWord}

def getTimeDelay(start, end):

  FMT = '%H:%M:%S'
  tdelta = datetime.strptime(end, FMT) - datetime.strptime(start, FMT)

  if tdelta.days < 0:
    tdelta = timedelta(days=0,
                seconds=tdelta.seconds, microseconds=tdelta.microsecond)
    
  minutes = divmod(tdelta.seconds, 60)[0]
    
  if minutes >= delay:
    return True
  else:
    return False

def SendMessage(author,id,keyword):

  post = reddit.info([id])

  title = None
  url = None

  for submission in post:
    title = submission.title
    url   = submission.url

  thread = '[' + title + ']'+'(' + url + ')'
    
  message = 'Hi ' + author + '\n\n Your message on the '+ thread +' post about ' + keyword + ' got me thinking.Perhaps I can be of service by providing you with some interesting information. \n\n My name is Diran and I send out a weekly newsletter discussing strategies to help people overcome low self-esteem and self-doubt, so they can successfully go after whatever they want in life. I also coach specifically to retrain mindset and help people ace social interactions. \n\n I believe you would find value from it. Would you like me to send you the link to the website so you can subscribe? \n\n Thanks'
  
  reddit.redditor(author).message('Need Help',message)

if __name__ == "__main__":

  print('Bot is up-and-running')

  while True:

      for message in messageQueue:

        end = datetime.now().strftime("%H:%M:%S")

        if getTimeDelay(message['time'], end):

          SendMessage(message['author'],message['id'],message['keyword'])
          print('\t\tSent message to : ', message['author'])

          messageQueue.remove(message)


      for comment in comment_stream:

          if comment is None:
              break

          query = FindKeys(comment.body)
        
          if query['Key']:

            message = {'author' : comment.author.name, 'id' :comment.link_id, 'keyword' : query['keyword'], 'time' : datetime.now().strftime("%H:%M:%S") }

            query = { 'author': message['author'] }

            doc = collection.find(query)

            if doc.count() > 0:
              print('Already sent/queued message : ', message['author'])
            else:
              messageQueue.append(message)
              x = collection.insert_one(message)
              print('New message added to queue from comment : ', message['author'])
          

      for submission in submission_stream:

          if submission is None:
              break

          query = FindKeys(submission.title + ' ' + submission.selftext)

          if query['Key']:

            message = {'author' : submission.author.name, 'id' :'t3_'+submission.id, 'keyword' : query['keyword'], 'time' : datetime.now().strftime("%H:%M:%S") }

            query = { 'author': message['author'] }

            doc = collection.find(query)

            if doc.count() > 0:
              print('Already sent/queued message : ', message['author'])
            else:
              messageQueue.append(message)
              x = collection.insert_one(message)
              print('New message added to queue from submission/post : ', message['author'])