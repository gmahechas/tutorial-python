import time
from workers.SleepyWorker import SleepyWorker
from workers.SquaredSumWorker import SquaredSumWorker


def main():
    # squares
    calc_start_time = time.time()

    current_threads = []
    for i in range(5):
        maximum_value = (i + 1) * 1000000
        squared_sum_worker = SquaredSumWorker(n=maximum_value)
        current_threads.append(squared_sum_worker)

    for thread in range(len(current_threads)):
        current_threads[thread].join()

    print(f'calculating sum of squares took: {round(time.time() - calc_start_time, 1)}')

    # time
    sleep_start_time = time.time()

    current_threads = []
    for seconds in range(1, 6):
        sleepy_worker = SleepyWorker(seconds=seconds)
        current_threads.append(sleepy_worker)

    for thread in range(len(current_threads)):
        current_threads[thread].join()

    print(f'sleep took: {round(time.time() - sleep_start_time, 1)}')


if __name__ == '__main__':
    main()
