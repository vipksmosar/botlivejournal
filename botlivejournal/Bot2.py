import feedparser
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from bs4 import BeautifulSoup
import os
import time

loginjournal = 'sha-julin'


def lparser(idpost, loginlive):
    time.sleep(2)
    rss_ = 'https://'+loginlive+'.livejournal.com/data/rss'
    rss_data = feedparser.parse(rss_)

    if 'items' not in rss_data:
        print("ERR 1")
        raise Exception("ERR: not items")

    # if idpost not in rss_data['items']:
    #     print("ERR 2")
    #     raise Exception("not id post")

    if 'title' not in rss_data['items'][idpost]:
        print("ERR 3")
        raise Exception("Err 3")

    titleu = rss_data['items'][idpost]['title']
    print("parser  OK")
    descriptionu = ''.join(BeautifulSoup((
        rss_data['items'][idpost]['description']
    ), "html.parser").find_all(text=True))
    print("parser  OK 2")
    linklive = rss_data['items'][idpost]['guid']
    print("parser  OK 3")
    feedtext=(titleu + '\n' + descriptionu[1:500] + '...\n Подробнее:' + linklive)
    print("parser  OK 4")
    return feedtext


REQUEST_KWARGS={
    'proxy_url': 'socks5://tkhpg.teletype.live:1080',
    'urllib3_proxy_kwargs': {
    'username': 'telegram',
    'password': 'telegram',
    }
}

updater = Updater(token="549557834:AAESyEgIiPFOA3gkEYcF9ihlpRBLs1Ucmys", request_kwargs=REQUEST_KWARGS)
dispatcher = updater.dispatcher

def startC(bot, update):
    print("HW")
    bot.send_message(chat_id=update.message.chat_id, text='Бот для чтения livejournal')

def textM(bot, update):
    print('i get:' +update.message.text)
    umt = update.message.text
    try:
        if "=" in umt:
            author_login = []
            author_name = []
            author_login.append(umt[:umt.find('=')].replace(" ", ""))
            author_name.append(umt[umt.find('=')+1:].replace(" ", ""))
            print(author_name[0])
            print(author_login[0])
        else:
            numfeed = int(update.message.text)
            print(numfeed)
            response = lparser(numfeed, loginjournal)
            response = response if response else 'EMPTY'
            print(response)
            bot.send_message(chat_id=update.message.chat_id, text=response)
    except Exception as e:
        print(str(e))


start_command_handler = CommandHandler('start', startC)
text_message_handler = MessageHandler(Filters.text, textM)
dispatcher.add_handler(start_command_handler)
dispatcher.add_handler(text_message_handler)
updater.start_polling(clean=True)
updater.idle()



