import requests
from bs4 import BeautifulSoup


class WikiWorker:
    _headers = ({
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
        'Accept-Language': 'en-US, en;q=0.5'
    })

    def __init__(self):
        self._url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

    @staticmethod
    def _extract_company_symbols(html_page):
        soup = BeautifulSoup(html_page, 'html.parser')
        table = soup.find(id='constituents')
        table_rows = table.find_all('tr')
        for row in table_rows[1:]:
            symbol = row.find('td').text.strip('\n')
            yield symbol

    def get_sp_500_companies(self):
        response = requests.get(self._url, headers=self._headers)
        if response.status_code != 200:
            print('error')
            return []

        yield from self._extract_company_symbols(response.text)
