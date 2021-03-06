import os
import re
import time
import requests
from queue import Queue
from threading import Thread, current_thread, Lock


class PhSpider:
    def __init__(self):
        self.q = Queue()
        self.lock = Lock()
        self.thread_list = []
        self.url = 'https://www.piaohua.com/html/kehuan/list_{}.html'
        self.directory = 'temp/'

    def url_in(self):
        for i in range(1, 105):
            url = self.url.format(i)
            self.q.put(url)

    def get_html(self):
        while True:
            self.lock.acquire()
            if not self.q.empty():
                url = self.q.get()
                self.lock.release()
                res = requests.get(url=url)
                html = res.text
                self.get_url(html)
            else:
                self.lock.release()
                break

    def get_url(self, html):
        urls = re.findall('<img src="(.*?)"', html)[1:]
        for url in urls:
            self.get_picture(url)

    def get_picture(self, url):
        name = url.split('/')[-1]
        res = requests.get(url=url)
        img = res.content
        self.save_picture(name, img)

    def save_picture(self, name, img):
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        with open(self.directory + name, 'wb') as f:
            f.write(img)

    def run(self):
        self.url_in()
        for i in range(20):
            thread = Thread(target=self.get_html)
            thread.start()
            self.thread_list.append(thread)

        for i in self.thread_list:
            i.join()


if __name__ == '__main__':
    start_time = time.time()
    spider = PhSpider()
    spider.run()
    stop_time = time.time()
    times = stop_time - start_time
    print(times)
