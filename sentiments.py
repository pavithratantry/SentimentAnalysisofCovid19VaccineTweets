from flask import Blueprint, render_template, request
import matplotlib.pyplot as plt
import os
import tweepy
import csv
import re
from textblob import TextBlob
import string
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import TweetTokenizer
from itertools import zip_longest
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')

# register this file as a blueprint
second = Blueprint("second", __name__, static_folder="static", template_folder="template")

# class with main logic
class SentimentAnalysis:

	def __init__(self):
		self.tweets = []
		self.tweetText = []

	# This function first connects to the Tweepy API using API keys
	def DownloadData(self, keyword, tweets):

		# authenticating
		consumerKey = '---consumerkey---'
		consumerSecret = '---consumersecret---'
		accessToken = '---accesstoken---'
		accessTokenSecret = '---accesstokensecret---'
		auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
		auth.set_access_token(accessToken, accessTokenSecret)
		api = tweepy.API(auth, wait_on_rate_limit=True)

		tweets = int(tweets)

		# searching for tweets
		self.tweets = tweepy.Cursor(
			api.search_tweets, q=keyword, lang="en").items(tweets)

		# Open/create a file to append data to
		csvFile = open('newvaccination_all_tweets.csv', 'a')

		# Use csv writer
		csvWriter = csv.writer(csvFile)

		# creating some variables to store info
		polarity = 0
		positive = 0
		negative = 0
		neutral = 0
		subjectivity=0
		pol_list=[]
		tweet_list=[]

		# iterating through tweets fetched
		for tweet in self.tweets:
		
			# Append to temp so that we can store in csv later
			self.tweetText.append(self.cleanTweet(tweet.text).encode('utf-8'))
			
			
			analysis = TextBlob(tweet.text)
			
			pol_list.append(analysis.sentiment.polarity) # print tweet's polarity
			tweet_list.append(tweet.text)
			

			file_name = "newvaccination_all_tweets"
			

			# adding up polarities to find the average later
			polarity += analysis.sentiment.polarity
			subjectivity += analysis.sentiment.subjectivity

			# adding reaction of how people are reacting to find average later
			if (analysis.sentiment.polarity == 0):
				neutral += 1
			elif (analysis.sentiment.polarity > 0 and analysis.sentiment.polarity <= 1):
				positive += 1
			elif (analysis.sentiment.polarity >= -1 and analysis.sentiment.polarity <0):
				negative += 1

		#print(pol_list)
		#print(tweet_list)
		train_list=[pol_list, tweet_list]

		# with open('polarity.csv', 'w') as f:
		# 	writer = csv.writer(f)
		# 	for val in pol_list:
		# 		writer.writerow([val])

		export_data = zip_longest(*train_list, fillvalue = '')
		with open('polarity.csv', 'w', encoding="UTF-8", newline='') as myfile:
			wr = csv.writer(myfile)
			wr.writerow(("label", "tweet"))
			wr.writerows(export_data)
			myfile.close()

		# df = pd.read_csv('polarity.csv', header=None)
		# df.rename(columns={0: 'label'}, inplace=True)
		# df.to_csv('polarity.csv', index=False) # save to new csv file

		# Write to csv and close csv file
		csvWriter.writerow(self.tweetText)
		csvFile.close()

		# finding average of how people are reacting
		
		positive = self.percentage(positive, tweets)
		
		negative = self.percentage(negative, tweets)
		
		neutral = self.percentage(neutral, tweets)

		# finding average reaction
		polarity = polarity / tweets
		subjectivity=subjectivity/tweets

		# printing out data
		# print("How people are reacting on " + keyword + " by analyzing " + str(tweets) + " tweets.")
		# print()
		# print("General Report: ")

		if (polarity == 0):
			htmlpolarity = "Neutral"

		elif (polarity > 0 and polarity <= 1):
		 	htmlpolarity = "Positive"
		
		elif (polarity >= -1 and polarity <0):
		 	htmlpolarity = "Negative"
		

		self.plotPieChart(positive, negative,
						 neutral, keyword, tweets)
		#print(polarity, htmlpolarity)
		return polarity, htmlpolarity, positive, negative,  neutral, keyword, tweets, subjectivity


	def cleanTweet(self, tweet):
		# Remove Links, Special Characters etc from tweet
		return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w +:\ / \ / \S +)", " ", tweet).split())

	# function to calculate percentage
	def percentage(self, part, whole):
		temp = 100 * float(part) / float(whole)
		return format(temp, '.2f')


	def plotPieChart(self, positive,  negative, neutral, keyword, tweets):
		fig = plt.figure()
		labels = ['Positive [' + str(positive) + '%]',  'Neutral [' + str(neutral) + '%]',
				'Negative [' + str(negative) +	'%]']
		sizes = [positive, neutral, negative, ]
		colors = ['green', 'brown', 'red']
		patches, texts = plt.pie(sizes, colors=colors, startangle=90)
		plt.legend(patches, labels, loc="best")
		plt.axis('equal')
		plt.tight_layout()
		strFile = "plot.png"
		for filename in os.listdir('static/'):
			if filename.startswith('plot'):
				os.remove('static/' + filename)

		plt.savefig('static/' + strFile)
		# return render_template('piechart.html',graph=strFile)
		# if os.path.isfile(strFile):
		#  	os.remove(strFile) # Opt.: os.system("rm "+strFile)
		# plt.savefig(strFile)
		# plt.show()

	


@second.route('/sentiment_logic', methods=['POST', 'GET'])
def sentiment_logic():

# get user input of keyword to search and number of tweets from html form.
	keyword = request.form.get('keyword')
	tweets = request.form.get('tweets')
	sa = SentimentAnalysis()
	
	# set variables which can be used in the jinja supported html page
	polarity, htmlpolarity, positive, negative, neutral, keyword1, tweet1, subjectivity = sa.DownloadData(
		keyword, tweets)
	return render_template('sentiment_analyzer.html', polarity=polarity, htmlpolarity=htmlpolarity, positive=positive, 
						negative=negative, neutral=neutral, keyword=keyword1, tweets=tweet1, subjectivity=subjectivity)


@second.route('/visualize', methods=['POST', 'GET'])
def visualize():
	return render_template('visual.html')

@second.route('/visualize1', methods=['POST', 'GET'])
def visualize1():
	return render_template('visual copy.html')
	

