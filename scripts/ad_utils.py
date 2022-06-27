def update_datetime(new_ads):
    sorted_list = sorted(new_ads, key=lambda x: x.get_time(), reverse=True)
    last_updated_datetime = sorted_list[0].get_time()
    print(f"New ad was found. Time: {last_updated_datetime}")
    return last_updated_datetime


def construct_msg(ad):
    return f"**{ad.get_title()}**\n" \
           f"**Цена:  {ad.get_price()}\n" \
           f"Дата:  {ad.add_time}\n"


