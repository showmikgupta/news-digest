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

    def filter_links(self, links):
        for link in links:
            link_text = link.text.lower().split(' ')
            for keyword in self.keywords:
                if keyword in link_text and link not in self.saved_links:
                    self.saved_links.append(link)

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
        for url in self.urls:
            if "marketwatch" in url:
                self.parse_marketwatch(url)
            elif "seekingalpha" in url:
                self.parse_seekingalpha(url)

        self.store()
        self.email()

        x = datetime.now()
        y = x + timedelta(hours=1)
        delta = y - x
        secs = delta.total_seconds()
        t = Timer(secs, self.start)
        t.start()

    def clear_db(self):
        self.db.clear()
        self.start_db_clear_timer()

    def start_db_clear_timer(self):
        x = datetime.now()
        y = x + timedelta(days=1)
        delta = y - x
        secs = delta.total_seconds()
        t = Timer(secs, self.clear_db)
        t.start()
