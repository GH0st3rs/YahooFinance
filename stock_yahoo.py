#!/usr/bin/python3
import json
from argparse import ArgumentParser

import requests


def parge_args():
    parser = ArgumentParser()
    parser.add_argument('-s', dest='symbol', help='Symbol')
    parser.add_argument('-p', dest='purchased', action='store_true', help='Purchased status', default=False)
    parser.add_argument('-d', dest='delete', help='Delete symbol')
    return parser.parse_args()


URL = 'https://query1.finance.yahoo.com/v7/finance/quote'
data = {
    'lang': 'en-US',
    'region': 'US',
    'corsDomain': 'finance.yahoo.com',
}
FIELDS = [
    'symbol',
    'marketState',
    'regularMarketPrice',
    'regularMarketChange',
    'regularMarketChangePercent',
    'preMarketPrice',
    'preMarketChange',
    'preMarketChangePercent',
    'postMarketPrice',
    'postMarketChange',
    'postMarketChangePercent',
    'shortName',
    'longName'
]
CONFIG_NAME = 'config.json'
config = {}


def getSymbolPrint(name, price, diff, percent, marketState, status):
    column_offsets = [10, 450, 540, 610]
    output = ''
    if status:
        output += '${offset ' + column_offsets[0] + '}${font Ubuntu:size=12:normal}${color4}%s'  # name
    else:
        output += '${offset ' + column_offsets[0] + '}${font Ubuntu:size=12:normal}${color1}%s'  # name
    output += '${goto ' + column_offsets[1] + '}${font Ubuntu:size=12:bold}${color1}%.2f'  # price
    color = 'color6' if diff < 0 else 'color5'
    output += '${goto ' + column_offsets[2] + '}${font Ubuntu:size=12:normal}${PRICE_COLOR}%.2f'  # diff
    output += '${goto ' + column_offsets[3] + '}${font Ubuntu:size=12:normal}(${PRICE_COLOR}%.2f%%)'  # percent
    output = output.replace('PRICE_COLOR', color)
    output += '${alignr}${font Ubuntu:size=12:normal}${color1}%s'  # marketState
    return output % (name, price, diff, percent, marketState)


def parseResp(resp):
    for symbol in resp:
        if symbol.get('marketState') == 'PRE' and symbol.get('preMarketChange'):
            marketState = '*'
            price = symbol.get('preMarketPrice')
            diff = symbol.get('preMarketChange')
            percent = symbol.get('preMarketChangePercent')
        elif symbol.get('marketState') != 'REGULAR' and symbol.get('postMarketChange'):
            marketState = '*'
            price = symbol.get('postMarketPrice')
            diff = symbol.get('postMarketChange')
            percent = symbol.get('postMarketChangePercent')
        else:
            marketState = ' '
            price = symbol.get('regularMarketPrice')
            diff = symbol.get('regularMarketChange')
            percent = symbol.get('regularMarketChangePercent')

        if symbol.get('longName') is not None:
            longName = symbol.get('longName').replace(', Inc.', '')
        else:
            longName = ' '.join(symbol.get('shortName').split()[:2])
        name = '%s (%s)' % (longName, symbol.get('symbol'))
        purchased = getStatus(symbol.get('symbol'))
        print(getSymbolPrint(name, price, diff, percent, marketState, purchased))


def loadConfig():
    global config
    config = json.load(open(CONFIG_NAME))
    symbols = ['^GSPC', '^IXIC']
    symbols += sorted(map(lambda x: x, config))
    return symbols


def getStatus(symbol):
    for item in config:
        if item == symbol:
            return config[item]['purchased']


def addSymbol(symbol, cfg, purchased, notify):
    cfg[symbol] = {
        'notify': notify,
        'purchased': purchased
    }
    return cfg


def main():
    global config
    args = parge_args()
    SYMBOLS = loadConfig()
    if args.delete:
        cfg = {}
        for symbol in config:
            if symbol != args.delete:
                cfg.update({symbol: config[symbol]})
        json.dump(cfg, open(CONFIG_NAME, 'w'))
        exit()
    if args.symbol:
        config = addSymbol(args.symbol, config, args.purchased, [])
        json.dump(config, open(CONFIG_NAME, 'w'))
        exit()

    data['fields'] = ','.join(FIELDS)
    data['symbols'] = ','.join(SYMBOLS)

    resp = requests.get(URL, params=data, headers={'User-Agent': 'curl'}).json()['quoteResponse']['result']
    parseResp(resp)


if __name__ == '__main__':
    main()
