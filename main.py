import time
from datetime import datetime

import pandas as pd
import requests


def fr24(timestamp, page=1, airport='tpe'):
    headers = {
        'authority': 'api.flightradar24.com',
        'accept': 'application/json',
        'origin': 'https://www.flightradar24.com',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
        'dnt': '1',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'cors',
        'referer': 'https://www.flightradar24.com/airport/tpe/arrivals',
        'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    params = (
        ('code', airport),
        ('plugin/[/]', 'schedule'),
        ('plugin-setting/[schedule/]/[mode/]', 'departures'),
        ('plugin-setting/[schedule/]/[timestamp/]', timestamp),
        ('page', page),
        ('limit', '100'),
        ('token', 'qPgPtpctGA0YZPTS9NF_mD6QVwq27mkhfOawf2qaSh4'),
    )

    response = requests.get(
        'https://api.flightradar24.com/common/v1/airport.json', headers=headers, params=params)

    j = response.json()
    data = j['result']['response']['airport']['pluginData']['schedule']['departures']['data']

    return data


def parse(data, origin):
    SULEM = []

    for v in data:
        try:
            callsign = v['flight']['identification']['number']['default']
            icao = v['flight']['airline']['code']['icao']
            callsign = icao+callsign[2:]
            model = v['flight']['aircraft']['model']['code']

            dest_code = v['flight']['airport']['destination']['code']['icao']
            icao = {'tpe': 'RCTP', 'tsa': 'RCSS', 'khh': 'RCKH', 'rmq': 'RCMQ'}
            flytime = {'tpe': 30*60, 'tsa': 25*60, 'khh': 50*60, 'rmq': 40*60}
            # status = flight['flight']['status']['text']

            if 'ZSPD' == dest_code or 'ZSSS' == dest_code:
                dep_t = v['flight']['time']['estimated']['departure']
                dt = datetime.fromtimestamp(dep_t).strftime("%H:%M")
                boundry_t = dep_t + flytime[origin]
                st = datetime.fromtimestamp(boundry_t).strftime("%H:%M")

                row = {'cs': callsign,
                       'type': model,
                       'dep': dep_t,
                       'slm time': boundry_t,
                       'from': icao[origin],
                       'dt': dt,
                       'to': dest_code,
                       'est slm': st}
                SULEM.append(row)
        except TypeError:
            pass

    return SULEM


def main():
    SULEM = []
    airports = ['tpe', 'tsa', 'khh', 'rmq']
    for airport in airports:
        for page in range(1, 2):
            timestamp = int(time.time() - 2*60*60)
            data = fr24(timestamp, page, airport)
            flights = parse(data, airport)
            SULEM.extend(flights)

    df = pd.DataFrame(SULEM)
    df.sort_values(by=['est slm'], inplace=True)
    print(df)


if __name__ == "__main__":
    main()
