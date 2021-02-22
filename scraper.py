import requests
import os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from threading import Timer


class Scraper:
    def __init__(self, keywords, urls):
        self.markup = requests.get('https://www.marketwatch.com/latest-news').text
        self.keywords = keywords
        self.urls = urls
        self.saved_links = []
        self.db = {}
        self.already_seen = []
        self.send_email = True

    def filter_links(self, links):
        for link in links:
            link_text = link.text.lower().split(' ')
            for keyword in self.keywords:
                if keyword in link_text and link not in self.saved_links:
                    self.saved_links.append(link)

    def parse(self):
        for url in self.urls:
            if "marketwatch" in url:
                self.parse_marketwatch(url)
            elif "seekingalpha" in url:
                self.parse_seekingalpha(url)
            elif "businessinsider" in url:
                self.parse_businessinsider(url)

    def parse_marketwatch(self, url):
        markup = requests.get(url).text
        soup = BeautifulSoup(markup, "html.parser")
        links = soup.find_all("a", {"class": "link", "target": "_blank"})
        self.filter_links(links)

    def parse_seekingalpha(self, url):
        markup = requests.get(url).text
        soup = BeautifulSoup(markup, "html.parser")
        latest_news = soup.find("ul", {"id": "latest-news-list"})
        links = []

        for a in latest_news:
            soup = BeautifulSoup(str(a), "html.parser")
            for tag in soup.find_all('a'):
                tag['href'] = 'https://seekingalpha.com/' + tag['href']
                links.append(tag)

        self.filter_links(links)

    def parse_businessinsider(self, url):
        markup = requests.get(url).text  # get html from website
        soup = BeautifulSoup(markup, "html.parser")  # use html parser
        latest_news = soup.find_all("a",
                                    {"class": "teaser-headline"})  # find all html 'a' tags with class=teaser-headline
        links = []

        # loop through all 'a' tags and save the link to article
        for tag in latest_news:
            tag['href'] = 'https://markets.businessinsider.com' + tag['href']
            links.append(tag)

        latest_news = soup.find_all("a", {"class": "news-link"})

        for tag in latest_news:
            tag['href'] = 'https://markets.businessinsider.com' + tag['href']
            links.append(tag)

        self.filter_links(links)

    def store(self):
        current_links = self.db.keys()
        new_articles = {}

        for link in self.saved_links:
            if link.text in current_links:
                self.already_seen.append(link.text)
            elif link.text not in self.already_seen:
                new_articles[link.text] = str(link)

        self.db = new_articles

    def email(self):
        links = [self.db.get(k) for k in self.db.keys()]

        if len(links) > 0:  # only send out email if there is something to send
            # email
            fromEmail = 'disruptstudionewsdigest@gmail.com'
            toEmail = 'showmikgupta@gmail.com'

            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Financial News Digest {datetime.today().strftime('%m-%d-%Y')}"
            msg["From"] = fromEmail
            msg["To"] = toEmail

            html = """
                <h4> %s  new articles:</h4>

                %s
            """ % (len(links), '<br/><br/>'.join(links))

            mime = MIMEText(html, 'html')

            msg.attach(mime)

            try:
                mail = smtplib.SMTP('smtp.gmail.com', 587)
                mail.ehlo()
                mail.starttls()
                mail.login(fromEmail, os.getenv('EMAIL_PASSWORD'))
                mail.sendmail(fromEmail, toEmail, msg.as_string())
                mail.quit()
                print('Email sent!')
            except Exception as e:
                print('Something went wrong... %s' % e)

    def start(self):
        self.parse()  # scrape data from websites
        self.store()  # store relevant links in internal dictionary

        x = datetime.now()

        if 0 < x.hour < 9:  # only send email between 9-12am
            self.send_email = False
        else:
            self.send_email = True

        if self.send_email:
            self.email()  # sends email containing relevant links

        y = x.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        delta = y - x
        secs = delta.total_seconds()
        t = Timer(secs, self.start)
        t.start()

    def clear_db(self):
        self.db.clear()
        self.already_seen = []
        self.saved_links = []
        self.start_db_clear_timer()

    def start_db_clear_timer(self):
        x = datetime.now()
        y = x.replace(hour=6, minute=30, second=0, microsecond=0) + timedelta(days=1)
        delta = y - x
        secs = delta.total_seconds()
        t = Timer(secs, self.clear_db)
        t.start()
