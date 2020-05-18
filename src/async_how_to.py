import asyncio
import requests
import time

async def my_async_func(my_arg_1, my_arg_2):
    '''
        An async function that makes a get call
        in an async way
    '''
    x = requests.get('https://www.google.com')
    print(x.status_code)
    print("End of running async function with args (%s, %s)" % (my_arg_1, my_arg_2))


def non_async_caller():
    loop = asyncio.get_event_loop()
    for i in range(5):
        loop.run_until_complete(my_async_func(i, i + 20))

    time.sleep(30)


def main():
    loop = asyncio.get_event_loop()
    future = asyncio.Future()
    asyncio.ensure_future(non_async_caller())

    loop.run_until_complete(future)
    # non_async_caller()

main()
