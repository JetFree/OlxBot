import datetime
import re
from bs4 import BeautifulSoup
from AdObject import Ad


class Parser:

    def __init__(self, html_content, session):
        self.id = None
        self.session = session
        self.html = html_content
        self.soup = BeautifulSoup(self.html, "html.parser")

    def find_ad_time(self, ad_html):
        tag = ad_html.findNext("i", attrs={"data-icon": "clock"}).find_parent()
        date_string = tag.text
        if date_string.find("dzisiaj") != -1:
            date = datetime.datetime.today()
            m = re.search("\d+:\d+$", date_string)
            time_str = m.group(0)
            time = datetime.time(int(time_str.split(":")[0]),
                                 int(time_str.split(":")[1]), 0)
            return datetime.datetime.combine(date, time)
        elif date_string.find("wczoraj") != -1:
            date = datetime.datetime.today() - datetime.timedelta(days=1)
            m = re.search("\d+:\d+$", date_string)
            time_str = m.group(0)
            time = datetime.time(int(time_str.split(":")[0]),
                                 int(time_str.split(":")[1]), 0)
            return datetime.datetime.combine(date, time)
        else:
            return datetime.datetime.today() - datetime.timedelta(days=2)

    def find_price(self, ad_html):
        tag = ad_html.findNext("p", class_="price")
        return tag.text.replace("\n", "")

    def find_title(self, ad_html):
        tag = ad_html.findNext("a", attrs={"data-cy": "listing-ad-title"})
        return tag.text.replace("\n", "")

    def parse_img_urls(self, url, response):
        img_urls = list()
        if self.id is not None:
            soup = BeautifulSoup(response.content, "html.parser")
            img_containers = soup.find_all("div", attrs={
                "data-cy": "adPhotos-swiperSlide"})
            for img_element in img_containers:
                img_url = img_element.findNext("img").get("src")
                if img_url is None:
                    img_url = img_element.findNext("img").get("data-src")
                img_urls.append(img_url)
            return img_urls
        elif url.find("otodom") != -1:
            list_q = re.findall(r"medium\":\"https[^\",]+\"",
                                response.content.decode())
            for img_url in list_q:
                img_urls.append(img_url.split(":\"")[1].replace("\"", ""))
            return img_urls
        else:
            raise Exception(f"Ad id is not define: URL: {url}")

    def parse_id(self, url, response):
        if url.find("otodom") == -1:
            try:
                soup = BeautifulSoup(response.content, "html.parser")
                elem = soup.find("a", attrs={"data-testid": "refresh-link"})
                if elem is None:
                    self.id = None
                    print("Can't parse ad's id. Looks like this ad is"
                          " not actual anymore.")
                else:
                    self.id = elem["href"].split("id=")[1]
            except Exception as e:
                print(e)
        else:
            self.id = None

    # def get_contact_number(self, url):
    #     resp = self.session.get(url)
    #     soup = BeautifulSoup(resp.content, "html.parser")
    #     elem = soup.find("a", attrs={"data-testid": "refresh-link"})
    #     self.id = elem["href"].split("id=")[1]
    #     resp = self.session.get(
    #         f"https://www.olx.pl/api/v1/offers/{self.id}/limited-phones/")
    #     phone = resp.json()["data"]["phones"][0]
    #     return phone

    def find_link(self, ad_html):
        tag = ad_html.findNext("a", attrs={"data-cy": "listing-ad-title"})
        return tag["href"]

    def parse_ads(self):
        wrapper_list = self.soup.find_all("div", class_="offer-wrapper")
        ads_list = list()
        for wrapper in wrapper_list:
            title = self.find_title(wrapper)
            price = self.find_price(wrapper)
            link = self.find_link(wrapper)
            ad_response = self.session.get(link)
            self.parse_id(link, ad_response)
            # number = self.get_contact_number(link)
            add_time = self.find_ad_time(wrapper)
            list_images = self.parse_img_urls(link, ad_response)
            ads_list.append(
                Ad(title, price, None, link, add_time, list_images))
        return ads_list
