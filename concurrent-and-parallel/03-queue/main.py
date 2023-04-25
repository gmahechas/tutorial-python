import time
import workers.WikiWorker as WikiWorker
import workers.YahooFinanceWorker as YahooFinanceWorker
from multiprocessing import Queue


def main():
    symbol_queue = Queue()
    scraper_start_time = time.time()

    wiki_worker = WikiWorker.WikiWorker()
    yahoo_finance_price_scheduler_threads = []
    num_yahoo_finance_price_workers = 2

    for worker in range(num_yahoo_finance_price_workers):
        yahoo_finance_price_scheduler = YahooFinanceWorker.YahooFinancePriceScheduler(input_queue=symbol_queue)
        yahoo_finance_price_scheduler_threads.append(yahoo_finance_price_scheduler)

    for symbol in wiki_worker.get_sp_500_companies():
        symbol_queue.put(symbol)

    for thread in range(len(yahoo_finance_price_scheduler_threads)):
        symbol_queue.put('DONE')

    for thread in range(len(yahoo_finance_price_scheduler_threads)):
        yahoo_finance_price_scheduler_threads[thread].join()

    print(f'extracting time took: {round(time.time() - scraper_start_time, 1)}')


if __name__ == '__main__':
    main()
