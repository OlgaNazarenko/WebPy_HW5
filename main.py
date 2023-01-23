import asyncio
import json
import os
import sys
from datetime import timedelta , date , datetime
from time import time
from typing import Any

import aiohttp

from settings import FOLDER_PATH

CURRENCY: list = ["EUR", "USD"]
URL: str = f'https://api.privatbank.ua/p24api/exchange_rates?json&date='


def the_date() -> int:
    exit_counter = 1
    while True:
        try:
            day = int(input("Enter the required days (up to 10): "))
        except ValueError:
            print('Not correct number of days. Enter again: ')
        else:
            if 1 < day < 11:
                break
            else:
                print("Dates not in range")

                exit_counter += 1
                if exit_counter > 2:
                    print("Good bye")
                    sys.exit(0)
    return day


def currency_list(data: dict, currency: list) -> dict[Any, dict[Any, Any]]:
    new_list = {}
    for item in data["exchangeRate"]:
        if item["currency"] in currency:
            the_list = {
                item["currency"]: {
                    "sale": item["saleRateNB"],
                    "purchase": item["purchaseRateNB"],
                }
            }
            new_list.update(the_list)
    cur_list = {data['date']: new_list}
    return cur_list


def saving_file(file: dict) -> None:

    if os.path.exists(FOLDER_PATH):
        with open(FOLDER_PATH, 'a') as f:
            inform = json.dumps(file, indent = 4)
            f.write(inform)


async def currency_per_day(session, days):
    try:
        async with session.get(f'{URL}{days}') as response:
            if response.status == 200:
                result = await response.json()
                res = currency_list(result, CURRENCY)
                print(res)
                saving_file(res)
                loop1 = asyncio.get_running_loop()
                loop1.close()
                return res
            elif response.status == 429:
                time.sleep(int(response.headers["Retry-After"]))
            else:
                print(f"Error status: {response.status} for {URL}{days}")

    except aiohttp.ClientConnectorError as error:
        print(f'Connection error: {URL}{days}', str(error))


async def main(days):
    _date: date = datetime.now().date()
    print(f"Today's date is: {_date}")
    res = {}
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(currency_per_day(session, (_date - timedelta(i)).strftime('%d.%m.%Y')))
                 for i in range(int(days))]
        results = await asyncio.gather(*tasks, return_exceptions = True)
        for i in range(int(days)):
            if isinstance(results[i], dict):
                res.update(results[i])
        # saving_file(res)
        print('Done')


if __name__ == '__main__':
    day = the_date()
    start = time()
    asyncio.run(main(day))
    print(time() - start)
