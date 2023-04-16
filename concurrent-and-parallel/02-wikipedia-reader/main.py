import time
import workers.WikiWorker as WikiWorker
import workers.YahooFinanceWorker as YahooFinanceWorker


def main():
    scraper_start_time = time.time()
    wiki_worker = WikiWorker.WikiWorker()
    current_threads = []
    for symbol in wiki_worker.get_sp_500_companies():
        yahoo_finance_worker = YahooFinanceWorker.YahooFinanceWorker(symbol=symbol)
        current_threads.append(yahoo_finance_worker)

    for thread in range(len(current_threads)):
        current_threads[thread].join()

    print(f'extracting time took: {round(time.time() - scraper_start_time, 1)}')


if __name__ == '__main__':
    main()
