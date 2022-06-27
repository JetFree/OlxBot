import time
import requests
import telebot

import AdParser

bot = telebot.TeleBot("5244658028:AAF7lbFLl8Mfg5_j_YjJ-1Va34S9nlnt2jE")
url = "https://www.olx.pl/nieruchomosci/mieszkania/wynajem/warszawa/" \
      "?search[filter_float_price:to]=4000&" \
      "search[filter_float_m:from]=60&" \
      "search[filter_enum_rooms][0]=two&" \
      "search[filter_enum_rooms][1]=three"
last_updated_datetime = None
base_url = "https://olx.pl"


def find_new_ads(ads_list):
    global last_updated_datetime
    ads_list.sort(key=lambda r: r.add_time, reverse=True)
    if last_updated_datetime is None:
        last_updated_datetime = ads_list[0].get_time()
        return list()
    else:
        filtered = list(filter(lambda ad: ad.get_time() > last_updated_datetime,
                               ads_list))
        if len(filtered) > 0:
            update_datetime(filtered)
        return filtered


def update_datetime(new_ads):
    global last_updated_datetime
    sorted_list = sorted(new_ads, key=lambda x: x.get_time(), reverse=True)
    last_updated_datetime = sorted_list[0].get_time()
    print(f"New ad was found. Time: {last_updated_datetime}")


def construct_msg(ad):
    return f"**{ad.get_title()}**\n" \
           f"**Цена:  {ad.get_price()}\n" \
           f"Дата:  {ad.add_time}\n"


@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id, 'Привет, Я помогаю найти квартиру с '
                                'помощью сайта Olx.pl')
    bot.send_message(m.chat.id, 'Всё, что мне от тебя нужно, это сбросить ссылку'
                                ' с нужными тебе применёнными фильтрами поиска')
    bot.send_message(m.chat.id, f'Например: {url}')
    while True:
        session = requests.Session()
        resp = session.get(url)
        ad_parser = AdParser.Parser(resp.content, session)
        ads_list = ad_parser.parse_ads(base_url)
        new_ads = find_new_ads(ads_list)
        if len(new_ads) > 0:
            for adOjb in new_ads:
                adOjb.download_images()
                keyboard = telebot.types.InlineKeyboardMarkup()
                link_button = telebot.types.InlineKeyboardButton(
                    text="Ссылка на объявление", url=f"{adOjb.get_link()}")
                keyboard.add(link_button)
                bot.send_message(m.chat.id, construct_msg(adOjb),
                                 parse_mode="MARKDOWN", reply_markup=keyboard)
                bot.send_media_group(m.chat.id, [telebot.types.InputMediaPhoto(
                    open(photo, 'rb')) for photo in adOjb.get_files()[0:10]])
        time.sleep(60)


@bot.message_handler(content_types=["text"])
def handle_text(message):
    bot.send_message(message.chat.id,
                     'Я занят поиском тебе новой квартиры, не отвлекай меня')


bot.infinity_polling(long_polling_timeout=5, timeout=10)
