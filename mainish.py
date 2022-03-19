#Created by Korrie Goodrich, Adam Tapp, and Jacob Olson

import datetime
from datetime import timedelta

#finnhub is an open-source python library made specifically for calling information from finhubb's API
import finnhub

import json
import os
import pandas as pd
import pandas_datareader as pdr
import requests
import matplotlib as mpl
import matplotlib.pyplot as plt

#This module allows us to time when the program runs. We chose this module due to the high amount of customization and simplicity
import schedule

#The remaining imports are all related to sending emails
import smtplib
import time
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import StockClass
from StockClass import *

#The setup client for finnhub
finnhub_client = finnhub.Client(api_key="c8qjaoqad3ienapjn90g")

ticker_list = []

tickers = ['AMZN', 'AMD', 'AAPL','ADBE', 'DIS', 'GOOG', 'MSFT']


#Logic for running the API call and saving results to JSON
def saveJSON(tickers):
    #Gets the current stock price
    for ticker in tickers:
        
        #finnhub_client.quote() is a custom python function available in the finnhub module.
        #It will return the current price, daily change, daily percent change, the highest and lowest prices of the day,
        #the opening price, the previous close price, and the stock ticker for everything in the tickers list. 
        
        minute_info = finnhub_client.quote(ticker) 
        
        #Adds the stock ticker to the data pulled from finnhub
        minute_info['Symbol'] = ticker
        
        #Logic to append new stock data to StockPrices.json
        with open('/home/ubuntu/environment/StockPrices.json','a') as outfile:
            outfile.write(json.dumps(minute_info))
            outfile.write(", \n")

#saveJSON(tickers)

#Logic for sending emails when a trade is completed
#The code sending the emails was set up specifically for HackUSU as a demonstration. 
#Secure coding is farther along th development path than we were able to achieve in this time. 
#The HackUSU will be deleted immediately after the event, and any 
#other identifiable personal information will be replaced with placeholder variables.
def sendEmail(number, symbol, dollars,change,money):
    fromaddr = "HackUSU2022.AWS@gmail.com"
    toaddr = "tappadw@gmail.com"
    
    msg = MIMEMultipart()
    
    #Storing the senders/recievers email address and subject line
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Stock Trade Alert"
    
    #Logic to 
    portfolio = (number * dollars + money)
    if change > 0:
        body = f"Congrats, you have have {number} stonks of {symbol} at {dollars} each. You gained ${change}. Your portfolio is worth {portfolio}"
    if change <= 0:
        body = f"wow idiot, you have have {number} stonks of {symbol} at {dollars} each. You lost ${change}. Your portfolio is worth {portfolio}"
    #Attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))
    
    #Open the file to be sent 
    filename = "money.png"
    attachment = open("money.png", "rb")
    
    #Instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)
    
    #Creating SMTP session, starting TLS, and entering credentials for the sending email address
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(fromaddr, "#HackUSU2022")
    
    #Converts the Multipart msg into a string
    text = msg.as_string()
    
    #Sending the mail and terminating the session
    s.sendmail(fromaddr, toaddr, text)
    s.quit()


  
#Official Schedule Code
#If t is between 8:30 AM and 4:00 PM ET, then scheduler runs and sends the email.
#The reason the code starts the time at 8:30 is because scheduler doesn't run when 
#initially run. This allows scheduler to get opening prices when the stock market opens
t = datetime.datetime.now()

#Logic to begin trading at 8:30 AM Eastern Time (6:30 PM Mountain Time)
start_time = '08:30:00.00'
start = datetime.datetime.strptime(start_time, '%H:%M:%S.%f')

#Logic to end trading at 4:00 Eastern Time (2:00 PM Mountain Time)
end_time = '04:00:00.00'
end = datetime.datetime.strptime(end_time, '%H:%M:%S.%f')

#This for loop determines if the stock market is open. If yes, times are scheduled for SaveJSON and sendEmail to run
#If no, then an error message is returned and the loop is broken. 
for ticker in tickers:
    if start <= t or t >= end:
        
        scheduler = schedule.Scheduler()
        
        scheduler.every(30).minutes.do(saveJSON,tickers = tickers)
        #scheduler.every(30).seconds.do(sendEmail, number=number, symbol=symbol, dollars = dollars)
    else:
        print("The stock market is currently closed")
        break


#Logic to continue running scheduler after each completion of the code

def main():
    adobe = Stock('ADBE',0)
    microsoft = Stock('MSFT',5)
    amd = Stock('AMD',0)
    disney = Stock('DIS',0)
    hpq = Stock('HPQ',0)
    verizon = Stock('VZ',0)
    #initialize stocks with market data
    stocks = [adobe,microsoft,amd,disney,hpq,verizon]
    sold = False
    day = []
    last = 0
    for i in range(20):
        for j in range(3):
            day.append(datetime.datetime(2021, j+1, i+2))
    # for i in range(15):
    #     for j in range(1):
    #         day.append(datetime.datetime(2021, j+1, i+2))
    change = 0
    dollars = 0
    number,symbol,dollars,change,money,money_points = execute(stocks,day)
    x = []
    for i in range(len(money_points)):
        x.append(i)
    plt.plot(x,money_points)
    z = np.polyfit(x,money_points,1)
    p = np.poly1d(z)
    plt.plot(x,p(x),'r--')
    plt.savefig('money.png')
    sendEmail(number, symbol, dollars,change,money)



main()
