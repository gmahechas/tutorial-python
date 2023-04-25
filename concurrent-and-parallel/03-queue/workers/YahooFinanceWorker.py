import threading
from bs4 import BeautifulSoup
from lxml import etree
import requests
import time
import random


class YahooFinancePriceScheduler(threading.Thread):
    def __init__(self, input_queue, **kwargs):
        super(YahooFinancePriceScheduler, self).__init__(**kwargs)
        self._input_queue = input_queue
        self.start()

    def run(self):
        while True:
            val = self._input_queue.get()
            if val == 'DONE':
                break

            yahoo_finance_price_worker = YahooFinanceWorker(symbol=val)
            price = yahoo_finance_price_worker.get_price()
            print(f'price for {val} is: {price}')
            time.sleep(20 * random.random())


class YahooFinanceWorker:
    _headers = ({
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
        'Accept-Language': 'en-US, en;q=0.5'
    })

    def __init__(self, symbol):
        self._symbol = symbol
        self._base_url = 'https://finance.yahoo.com/quote/'
        self._url = f'{self._base_url}{self._symbol}'

    def get_price(self):
        response = requests.get(self._url, headers=self._headers)

        if response.status_code != 200:
            print('error')
            return

        soup = BeautifulSoup(response.content, 'html.parser')
        dom = etree.HTML(str(soup))

        # dom = etree.fromstring(response.content)  # (does not WWork) it does not two lines above
        raw_price = dom.xpath(
            '/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[6]/div/div/div/div[3]/div[1]/div[1]/fin-streamer[1]'
        )[0].text

        price = float(raw_price.replace(',', ''))
        return price


if __name__ == '__main__':
    pass

# /html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[6]/div/div/div/div[3]/div[1]/div[1]/fin-streamer[1]
# Fw(b) Fz(36px) Mb(-4px) D(ib)
# Fw(b) Fz(36px) Mb(-4px) D(ib)
