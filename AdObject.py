import requests
import random
import string


class Ad:

    def __init__(self, title, price, contact_number, link, add_time, *args):
        self.title = title
        self.price = price
        self.contact_number = contact_number
        self.link = link
        self.add_time = add_time
        self.images_urls = args[0]
        self.files = list()

    def get_time(self):
        return self.add_time

    def get_title(self):
        return self.title

    def get_price(self):
        return self.price

    def get_contact_number(self):
        return self.contact_number

    def get_link(self):
        return self.link

    def download_images(self):
        i = 0
        for img_url in self.images_urls:
            resp = requests.get(img_url, stream=True)
            filename = f"./images/" \
                       f"{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}" \
                       f"_{i}.jpg"
            self.files.append(filename)
            with open(filename, "wb") as file:
                for chunk in resp.iter_content(chunk_size=64000):
                    file.write(chunk)
            i = i + 1

    def get_files(self):
        return self.files
