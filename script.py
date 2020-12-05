# coding: utf-8
import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# Parameters

config = {
    "application_file": "/path/to/your/folder/application.txt",
    "twitter_api_key": f"Bearer *******************",
    "interval_check": 2,
    "smtp_server": "smtp.domain.com",
    "smtp_port": 465,
    "smtp_user": "user@domain.com",
    "smtp_password": "your_password",
    "subject": "[VULN] Vulnérabilité remontée sur ",
    "from": "Vuln monitoring",
    "to": "yourmaillist@domain.com"
}

def importApplicationList(application_file):
    f = open(application_file, "r")
    data = f.readlines()
    application_list = []
    for app in data:
        application_list.append(app.replace('\n','').lower())

    return application_list

def checkVulnCVETwitter(application_list):

    alert_list = []
    headers = {
        'authorization': config["twitter_api_key"],
    }

    # Date UTC
    date_start = datetime.now() - timedelta(hours=config["interval_check"]) # Last hour
    response = requests.get('https://api.twitter.com/2/tweets/search/recent?query=from:CVEnew&start_time='+date_start.strftime("%Y-%m-%dT%H:%M:%SZ"), headers=headers)
    #json.dumps(data, indent=4)
    data = response.json()
    if data["meta"]["result_count"] !=0:
        for tweet in data["data"]:
            #print(json.dumps(tweet, indent=4))
            url = tweet["text"].split(' ')[-1]
            #print(tweet["text"])
            for app in application_list:
                if app in tweet["text"].lower():
                    # Application name in description!
                    # Add to our alert_list
                    alert_list.append({"app_name": app, "description": tweet["text"].replace(' '+url, ''), "url": url})

    return alert_list
    

def checkVulnCERTFR(application_list):
    alert_list = []
    # Date UTC
    date_start = datetime.now() - timedelta(hours=config["interval_check"]) # Last hour

    r = requests.get('https://www.cert.ssi.gouv.fr/avis/feed/')
    #print(r.text)
    parser = BeautifulSoup(r.text, features="html.parser")
    #print(parser.channel.item)
    balises = parser.find_all("item")
    #print(balises)
    for item in balises:
        date_time_obj = datetime.strptime(item.pubdate.text, '%a, %d %b %Y %H:%M:%S +0000')
        
        if date_time_obj > date_start:
            for app in application_list:
                if app in item.title.text.lower():
                    # Application name in title!
                    # Add to our alert_list
                    print(item.title.text)
                    alert_list.append({"app_name": app, "description": item.title.text, "url": item.guid.text})
        else:
            continue


    return alert_list


def sendEmailAlert(application_name, description, url):

    message = MIMEMultipart("alternative")
    message["Subject"] = config["subject"]+str(application_name)
    message["From"] = config["from"]
    message["To"] = config["to"]
    
    text = """<html><head>	<meta http-equiv="content-type" content="text/html; charset=utf-8">  	<meta name="viewport" content="width=device-width, initial-scale=1.0;"> 	<meta name="format-detection" content="telephone=yes"/>	<style>        #content {            max-width: 500px;            margin: 0 auto;            text-align: center;        }        #intro {             text-align: center;            font-family: "Muller Regular";            font-style: italic;            letter-spacing: 1px;            font-size: 17px;        }        #app_name {             text-align: center;            font-family: "Muller Regular";            font-size: 26px;            color: #ff5f00;        }        #description {             text-align: center;            font-family: "Muller Regular";            font-size: 17px;            line-height: 160%;            border-collapse: collapse;             border-spacing: 0;             margin: 0;             padding: 0;             padding-left: 6.25%;             padding-right: 6.25%;             width: 87.5%;             font-size: 17px;             font-weight: 400;             line-height: 160%;			padding-top: 15px;         }        #footer {             text-align: center;            font-family: "Muller Regular";            font-size: 13px;            color: #565F73;        }        #url {             margin-top: 30px;            text-align: center;            font-family: "Muller Regular";            font-size: 17px;        }        a {            outline: none;            text-decoration: none;            color: #000000;        }        a:hover {             color: #ff5f00;        }        a:visited {            outline: none;            color: #000000;        }        img.displayed {            display: block;            margin-left: auto;            margin-right: auto;        }        hr  {            margin-top: 30px;            width: 15%;            color: #565F73;        }    </style>    <title>Vuln Monitoring</title></head><body>    <div id="content">        <img class="displayed" src="https://raw.githubusercontent.com/ArnaudLhutereau/vuln_monitoring/main/ressources/logo.png" width="280" height="113"/>        <div id="intro">            <p>Une nouvelle vulnérabilité a été remontée sur</p>        </div>        <div id="app_name">            <p>"""
    text = text+str(application_name)
    text = text+"""</p></div><div id="description">    <p>"""
    text = text+str(description)
    text = text+"""</p></div><div id="url">    <p><a href=" """
    text = text+str(url)+"""">"""+str(url)
    text = text+"""</a></p></div><hr><div id="footer">    <p>Envoyé automatiquement par Vuln Monitoring</p></div></div></body></html>"""
    part = MIMEText(text, "html")
    message.attach(part)

    try:
        server = smtplib.SMTP_SSL(config["smtp_server"], config["smtp_port"])
        server.ehlo()
        server.login(config["smtp_user"], config["smtp_password"])
        server.sendmail(config["smtp_user"], config["to"], message.as_string())
        server.close()

        print("Email sent!")
    except Exception as e:
        print(e)


def main():
    # Initialize alert feed
    alert_feed = []

    # Import  all monitored applications
    application_list = importApplicationList(config["application_file"])

    # CVEnew feed connector
    alert_feed.append(checkVulnCVETwitter(application_list))

    # CERT-FR feed connector
    alert_feed.append(checkVulnCERTFR(application_list))

    # Send useful alerts
    for source in alert_feed:
        for alert in source:
            print(json.dumps(alert, indent=4))
            sendEmailAlert(alert["app_name"], alert["description"], alert["url"])


if __name__ == "__main__":
    main()


