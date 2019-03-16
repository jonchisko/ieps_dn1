import threading
from random import randint
from time import sleep


def print_number(number):
    # Sleeps a random 1 to 10 seconds
    rand_int_var = randint(1, 3)
    sleep(rand_int_var)
    print("Thread " + str(number) + " slept for " + str(rand_int_var) + " seconds")

thread_list = []

for i in range(1, 10):
    # Instantiates the thread
    # (i) does not make a sequence, so (i,)
    t = threading.Thread(target=print_number, args=(i,))
    # Sticks the thread in a list so that it remains accessible
    thread_list.append(t)

# Starts threads
for thread in thread_list:
    thread.start()

# This blocks the calling thread until the thread whose join() method is called is terminated.
# From http://docs.python.org/2/library/threading.html#thread-objects
for thread in thread_list:
    thread.join()

# Demonstrates that the main process waited for threads to complete
print("Done")


def foo(bar, baz):
  print('hello {0}'.format(bar))
  return 'foo' + baz

from multiprocessing.pool import ThreadPool
pool = ThreadPool(processes=1)

async_result = pool.apply_async(foo, ('world', 'foo')) # tuple of args for foo

# do some other stuff in the main process

return_val = async_result.get()  # get the return value from your function.

print("This is the return_val: " + return_val)


# YouTube Link: https://www.youtube.com/watch?v=u2jTn-Gj2Xw

# One can create a pool of processes which will carry out tasks submitted to
# it with the Pool class.

# A process pool object which controls a pool of worker processes to which
# jobs can be submitted. It supports asynchronous results with timeouts and
# callbacks and has a parallel map implementation.

import time
from multiprocessing import Pool


def sum_square(number):
    s = 0
    for i in range(number):
        s += i * i
    return s


def sum_square_with_mp(numbers):

    start_time = time.time()
    p = Pool()
    result = p.map(sum_square, numbers)

    p.close()
    p.join()

    end_time = time.time() - start_time

    print(f"Processing {len(numbers)} numbers took {end_time} time using multiprocessing.")


def sum_square_no_mp(numbers):

    start_time = time.time()
    result = []

    for i in numbers:
        result.append(sum_square(i))
    end_time = time.time() - start_time

    print(f"Processing {len(numbers)} numbers took {end_time} time using serial processing.")


if __name__ == '__main__':
    numbers = range(10000)
    sum_square_with_mp(numbers)
    sum_square_no_mp(numbers)