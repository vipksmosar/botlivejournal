from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from bs4 import BeautifulSoup
import os
import time
import requests
import re
import xmltodict
import json
import threading


class lj_news:
    def __init__ (self, login):
        self.login = login
    def parse_from_journal (self):
        session = requests.Session()
        req = session.get('https://'+self.login+'.livejournal.com/data/rss', headers={'Cache-Control': 'no-cache'})
        result = json.loads(json.dumps(xmltodict.parse(req.content)))
        result = result['rss']['channel']['item'][0]
        text_to_out = str(result['title']+'\n'+result['description']+'\n'+result['guid']['#text'])
        return text_to_out
    def parse_title(self):
        session = requests.Session()
        req = session.get('https://'+self.login+'.livejournal.com/data/rss', headers={'Cache-Control': 'no-cache'})
        result = json.loads(json.dumps(xmltodict.parse(req.content)))
        result = result['rss']['channel']['item'][0]
        text_to_out = result['title']
        return text_to_out
    def parse(self):
        out = self.parse_from_journal()
        return out
    def cycle_update(self, bot, chat_id):
        parse_title = ''
        while True:
            parse_title_now = self.parse_title()
            if parse_title != parse_title_now:
                try:
                    bot.send_message(chat_id=chat_id, text=self.parse_from_journal())
                except Exception as E:
                    print(E)
                parse_title = parse_title_now
            time.sleep(30)



class habr_news:
    def __init__ (self, login, company=False):
        self.login = login
        self.company = company
    def parse_from_habr_users(self):
        session = requests.Session()
        req=session.get('https://habr.com/ru/users/'+self.login+'/posts/')
        req.encoding = 'utf-8'
        soup = BeautifulSoup(''.join(req.text), "html.parser")
        req_find = soup.find('a',{'class':"post__title_link"})
        r_text = str(req_find.attrs['href']+'\n'+ req_find.text+'\n'+soup.find('div' ,{'class':'post__text'}).text[:800])
        return r_text
    def parse_from_habr_company(self):
        session = requests.Session()
        req=session.get('https://habr.com/ru/company/'+self.login)
        req.encoding = 'utf-8'
        soup = BeautifulSoup(''.join(req.text), "html.parser")
        req_find = soup.find('a',{'class':"post__title_link"})
        r_text = (req_find.attrs['href']+ '\n'+ req_find.text+ '\n'+ soup.find('div' ,{'class':'post__text'}).text[:800])
        return r_text
    def parse(self):
        if self.company==False:
            return self.parse_from_habr_users()        
        else:
            return self.parse_from_habr_company()

class dialog_bot:
    def __init__ (self, token, request_kwargs):
        self.updater = Updater(token=token, request_kwargs=request_kwargs)
        mhandler = MessageHandler(Filters.text, self.handle_message)
        chandler = CommandHandler('start', self.start_bot)
        addhabr = CommandHandler('habradd', self.habrMessage)
        addlj = CommandHandler('ljadd', self.ljMessage)
        self.updater.dispatcher.add_handler(chandler)
        self.updater.dispatcher.add_handler(mhandler)
        self.updater.dispatcher.add_handler(addhabr)
        self.updater.dispatcher.add_handler(addlj)
        print('init')
    def start (self):
        self.updater.start_polling()
        self.updater.idle()
    def start_bot (self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text='Бот для чтения новостей')
    def handle_message(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text='unknown command type /help for more information')
    def habrMessage(self, bot, update):
        print('i get:' +update.message.text)
        umt = update.message.text
        find = re.findall('[^/habradd ]\S+', str(umt))
        if len(find)>1:
            habr = habr_news(find[0], bool(find[1]))
            print(find[0], bool(find[1]))
        else:
            habr = habr_news(str(find[0]))
        text_to_bot = habr.parse()
        print(text_to_bot)
        bot.send_message(chat_id=update.message.chat_id, text=text_to_bot)
    def ljMessage (self, bot, update):
        print('i get:' +update.message.text)
        umt = update.message.text
        loginlj = re.findall('[^/ljadd ]\S+', str(umt))
        lj = lj_news(str(loginlj[0]))
        text_to_bot = lj.parse()
        print(text_to_bot)
        thread_s = threading.Thread(target=lj.cycle_update,kwargs={'bot': bot, 'chat_id': update.message.chat_id})
        thread_s.start() 

REQUEST_KWARGS={
    'proxy_url': 'socks5h://127.0.0.1:9050'
}


dialog = dialog_bot(botID_arg, REQUEST_KWARGS)
dialog.start()



