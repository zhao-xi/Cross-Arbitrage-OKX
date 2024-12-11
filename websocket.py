import asyncio
import websockets
import json
import requests
import hmac
import base64
import zlib
import datetime
import time

""" configs """
ratio_upper = 1.0001
ratio_lower = 0.9999
test_start_money = 1000.0


""" crypto pair candidates """
# usdt price
btc_usdt = {
    "price": 0,
    "ask": 0,
    "bid": 0,
    "ask_sz": 0,
    "bid_sz": 0,
    "timestamp": 0,
    "last_check": 0
}
eth_usdt = {
    "price": 0,
    "ask": 0,
    "bid": 0,
    "ask_sz": 0,
    "bid_sz": 0,
    "timestamp": 0,
    "last_check": 0
}
sol_usdt = {
    "price": 0,
    "ask": 0,
    "bid": 0,
    "ask_sz": 0,
    "bid_sz": 0,
    "timestamp": 0,
    "last_check": 0
}
dai_usdt = {
    "price": 0,
    "ask": 0,
    "bid": 0,
    "ask_sz": 0,
    "bid_sz": 0,
    "timestamp": 0,
    "last_check": 0
}
okb_usdt = {
    "price": 0,
    "ask": 0,
    "bid": 0,
    "ask_sz": 0,
    "bid_sz": 0,
    "timestamp": 0,
    "last_check": 0
}
bch_usdt = {
    "price": 0,
    "ask": 0,
    "bid": 0,
    "ask_sz": 0,
    "bid_sz": 0,
    "timestamp": 0,
    "last_check": 0
}
bsv_usdt = {
    "price": 0,
    "ask": 0,
    "bid": 0,
    "ask_sz": 0,
    "bid_sz": 0,
    "timestamp": 0,
    "last_check": 0
}
ltc_usdt = {
    "price": 0,
    "ask": 0,
    "bid": 0,
    "ask_sz": 0,
    "bid_sz": 0,
    "timestamp": 0,
    "last_check": 0
}
stx_usdt = {
    "price": 0,
    "ask": 0,
    "bid": 0,
    "ask_sz": 0,
    "bid_sz": 0,
    "timestamp": 0,
    "last_check": 0
}

# btc family
eth_btc = {
    "price": 0,
    "ask": 0,
    "bid": 0,
    "ask_sz": 0,
    "bid_sz": 0,
    "timestamp": 0,
    "last_check": 0
}
sol_btc = {
    "price": 0,
    "ask": 0,
    "bid": 0,
    "ask_sz": 0,
    "bid_sz": 0,
    "timestamp": 0,
    "last_check": 0
}
dai_btc = {
    "price": 0,
    "ask": 0,
    "bid": 0,
    "ask_sz": 0,
    "bid_sz": 0,
    "timestamp": 0,
    "last_check": 0
}
okb_btc = {
    "price": 0,
    "ask": 0,
    "bid": 0,
    "ask_sz": 0,
    "bid_sz": 0,
    "timestamp": 0,
    "last_check": 0
}
bch_btc = {
    "price": 0,
    "ask": 0,
    "bid": 0,
    "ask_sz": 0,
    "bid_sz": 0,
    "timestamp": 0,
    "last_check": 0
}
bsv_btc = {
    "price": 0,
    "ask": 0,
    "bid": 0,
    "ask_sz": 0,
    "bid_sz": 0,
    "timestamp": 0,
    "last_check": 0
}
ltc_btc = {
    "price": 0,
    "ask": 0,
    "bid": 0,
    "ask_sz": 0,
    "bid_sz": 0,
    "timestamp": 0,
    "last_check": 0
}
stx_btc = {
    "price": 0,
    "ask": 0,
    "bid": 0,
    "ask_sz": 0,
    "bid_sz": 0,
    "timestamp": 0,
    "last_check": 0
}

# eth family
dai_eth = {
    "price": 0,
    "ask": 0,
    "bid": 0,
    "ask_sz": 0,
    "bid_sz": 0,
    "timestamp": 0,
    "last_check": 0
}
sol_eth = {
    "price": 0,
    "ask": 0,
    "bid": 0,
    "ask_sz": 0,
    "bid_sz": 0,
    "timestamp": 0,
    "last_check": 0
}
""""""


""" util funcs that i don't care """
def get_timestamp():
    now = datetime.datetime.now()
    t = now.isoformat("T", "milliseconds")
    return t + "Z"

def sort_num(n):
    if n.isdigit():
        return int(n)
    else:
        return float(n)

def change(num_old):
    num = pow(2, 31) - 1
    if num_old > num:
        out = num_old - num * 2 - 2
    else:
        out = num_old
    return out
""""""


def login_params(timestamp, api_key, passphrase, secret_key):
    message = timestamp + 'GET' + '/users/self/verify'

    mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
    d = mac.digest()
    sign = base64.b64encode(d)

    login_param = {"op": "login", "args": [{"apiKey": api_key,
                                            "passphrase": passphrase,
                                            "timestamp": timestamp,
                                            "sign": sign.decode("utf-8")}]}
    login_str = json.dumps(login_param)
    return login_str


def update_bids(res, bids_p):
    # 获取增量bids数据
    bids_u = res['data'][0]['bids']
    # print('增量数据bids为：' + str(bids_u))
    # print('档数为：' + str(len(bids_u)))
    # bids合并
    for i in bids_u:
        bid_price = i[0]
        for j in bids_p:
            if bid_price == j[0]:
                if i[1] == '0':
                    bids_p.remove(j)
                    break
                else:
                    del j[1]
                    j.insert(1, i[1])
                    break
        else:
            if i[1] != "0":
                bids_p.append(i)
    else:
        bids_p.sort(key=lambda price: sort_num(price[0]), reverse=True)
        # print('合并后的bids为：' + str(bids_p) + '，档数为：' + str(len(bids_p)))
    return bids_p


def update_asks(res, asks_p):
    # 获取增量asks数据
    asks_u = res['data'][0]['asks']
    # print('增量数据asks为：' + str(asks_u))
    # print('档数为：' + str(len(asks_u)))
    # asks合并
    for i in asks_u:
        ask_price = i[0]
        for j in asks_p:
            if ask_price == j[0]:
                if i[1] == '0':
                    asks_p.remove(j)
                    break
                else:
                    del j[1]
                    j.insert(1, i[1])
                    break
        else:
            if i[1] != "0":
                asks_p.append(i)
    else:
        asks_p.sort(key=lambda price: sort_num(price[0]))
        # print('合并后的asks为：' + str(asks_p) + '，档数为：' + str(len(asks_p)))
    return asks_p

def check(bids, asks):
    # 获取bid档str
    bids_l = []
    bid_l = []
    count_bid = 1
    while count_bid <= 25:
        if count_bid > len(bids):
            break
        bids_l.append(bids[count_bid-1])
        count_bid += 1
    for j in bids_l:
        str_bid = ':'.join(j[0 : 2])
        bid_l.append(str_bid)
    # 获取ask档str
    asks_l = []
    ask_l = []
    count_ask = 1
    while count_ask <= 25:
        if count_ask > len(asks):
            break
        asks_l.append(asks[count_ask-1])
        count_ask += 1
    for k in asks_l:
        str_ask = ':'.join(k[0 : 2])
        ask_l.append(str_ask)
    # 拼接str
    num = ''
    if len(bid_l) == len(ask_l):
        for m in range(len(bid_l)):
            num += bid_l[m] + ':' + ask_l[m] + ':'
    elif len(bid_l) > len(ask_l):
        # bid档比ask档多
        for n in range(len(ask_l)):
            num += bid_l[n] + ':' + ask_l[n] + ':'
        for l in range(len(ask_l), len(bid_l)):
            num += bid_l[l] + ':'
    elif len(bid_l) < len(ask_l):
        # ask档比bid档多
        for n in range(len(bid_l)):
            num += bid_l[n] + ':' + ask_l[n] + ':'
        for l in range(len(bid_l), len(ask_l)):
            num += ask_l[l] + ':'

    new_num = num[:-1]
    int_checksum = zlib.crc32(new_num.encode())
    fina = change(int_checksum)
    return fina


# subscribe channels un_need login
async def do_subscribe(url_public, channels_public, url_trade):
    global btc_usdt,eth_usdt,sol_usdt,dai_usdt,okb_usdt,bch_usdt,bsv_usdt,ltc_usdt,stx_usdt,eth_btc,sol_btc,dai_btc,okb_btc,bch_btc,bsv_btc,ltc_btc,stx_btc,dai_eth,sol_eth
    l = []
    while True:
        try:
            async with websockets.connect(url_public) as ws, websockets.connect(url_trade) as trade_ws:
                # todo trade channel登录
                sub_param = {"op": "subscribe", "args": channels_public}
                sub_str = json.dumps(sub_param)
                await ws.send(sub_str)
                print(f"send: {sub_str}")

                while True:
                    try:
                        res = await asyncio.wait_for(ws.recv(), timeout=25)
                    except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed) as e:
                        try:
                            await ws.send('ping')
                            res = await ws.recv()
                            print(res)
                            continue
                        except Exception as e:
                            print("连接关闭，正在重连……")
                            break
                    try:
                        m = json.loads(res)['data'][0]
                        bid = float(m.get('bidPx'))
                        ask = float(m.get('askPx'))
                        price = (bid + ask) / 2
                        bid_sz = float(m.get('bidSz'))
                        ask_sz = float(m.get('askSz'))
                        inst_id = m.get('instId')
                        timestamp = int(m.get('ts'))
                        if inst_id == 'BTC-USDT':
                            btc_usdt["price"] = price
                            btc_usdt["bid"] = bid
                            btc_usdt["ask"] = ask
                            btc_usdt["bid_sz"] = bid_sz
                            btc_usdt["ask_sz"] = ask_sz
                            btc_usdt["timestamp"] = timestamp
                        elif inst_id == 'ETH-USDT':
                            eth_usdt["price"] = price
                            eth_usdt["bid"] = bid
                            eth_usdt["ask"] = ask
                            eth_usdt["bid_sz"] = bid_sz
                            eth_usdt["ask_sz"] = ask_sz
                            eth_usdt["timestamp"] = timestamp
                        elif inst_id == 'SOL-USDT':
                            sol_usdt["price"] = price
                            sol_usdt["bid"] = bid
                            sol_usdt["ask"] = ask
                            sol_usdt["bid_sz"] = bid_sz
                            sol_usdt["ask_sz"] = ask_sz
                            sol_usdt["timestamp"] = timestamp
                        elif inst_id == 'DAI-USDT':
                            dai_usdt["price"] = price
                            dai_usdt["bid"] = bid
                            dai_usdt["ask"] = ask
                            dai_usdt["bid_sz"] = bid_sz
                            dai_usdt["ask_sz"] = ask_sz
                            dai_usdt["timestamp"] = timestamp
                        elif inst_id == 'OKB-USDT':
                            okb_usdt["price"] = price
                            okb_usdt["bid"] = bid
                            okb_usdt["ask"] = ask
                            okb_usdt["bid_sz"] = bid_sz
                            okb_usdt["ask_sz"] = ask_sz
                            okb_usdt["timestamp"] = timestamp
                        elif inst_id == 'BCH-USDT':
                            bch_usdt["price"] = price
                            bch_usdt["bid"] = bid
                            bch_usdt["ask"] = ask
                            bch_usdt["bid_sz"] = bid_sz
                            bch_usdt["ask_sz"] = ask_sz
                            bch_usdt["timestamp"] = timestamp
                        elif inst_id == 'BSV-USDT':
                            bsv_usdt["price"] = price
                            bsv_usdt["bid"] = bid
                            bsv_usdt["ask"] = ask
                            bsv_usdt["bid_sz"] = bid_sz
                            bsv_usdt["ask_sz"] = ask_sz
                            bsv_usdt["timestamp"] = timestamp
                        elif inst_id == 'LTC-USDT':
                            ltc_usdt["price"] = price
                            ltc_usdt["bid"] = bid
                            ltc_usdt["ask"] = ask
                            ltc_usdt["bid_sz"] = bid_sz
                            ltc_usdt["ask_sz"] = ask_sz
                            ltc_usdt["timestamp"] = timestamp
                        elif inst_id == 'STX-USDT':
                            stx_usdt["price"] = price
                            stx_usdt["bid"] = bid
                            stx_usdt["ask"] = ask
                            stx_usdt["bid_sz"] = bid_sz
                            stx_usdt["ask_sz"] = ask_sz
                            stx_usdt["timestamp"] = timestamp
                        elif inst_id == 'ETH-BTC':
                            eth_btc["price"] = price
                            eth_btc["bid"] = bid
                            eth_btc["ask"] = ask
                            eth_btc["bid_sz"] = bid_sz
                            eth_btc["ask_sz"] = ask_sz
                            eth_btc["timestamp"] = timestamp
                        elif inst_id == 'SOL-BTC':
                            sol_btc["price"] = price
                            sol_btc["bid"] = bid
                            sol_btc["ask"] = ask
                            sol_btc["bid_sz"] = bid_sz
                            sol_btc["ask_sz"] = ask_sz
                            sol_btc["timestamp"] = timestamp
                        elif inst_id == 'DAI-BTC':
                            dai_btc["price"] = price
                            dai_btc["bid"] = bid
                            dai_btc["ask"] = ask
                            dai_btc["bid_sz"] = bid_sz
                            dai_btc["ask_sz"] = ask_sz
                            dai_btc["timestamp"] = timestamp
                        elif inst_id == 'OKB-BTC':
                            okb_btc["price"] = price
                            okb_btc["bid"] = bid
                            okb_btc["ask"] = ask
                            okb_btc["bid_sz"] = bid_sz
                            okb_btc["ask_sz"] = ask_sz
                            okb_btc["timestamp"] = timestamp
                        elif inst_id == 'BCH-BTC':
                            bch_btc["price"] = price
                            bch_btc["bid"] = bid
                            bch_btc["ask"] = ask
                            bch_btc["bid_sz"] = bid_sz
                            bch_btc["ask_sz"] = ask_sz
                            bch_btc["timestamp"] = timestamp
                        elif inst_id == 'BSV-BTC':
                            bsv_btc["price"] = price
                            bsv_btc["bid"] = bid
                            bsv_btc["ask"] = ask
                            bsv_btc["bid_sz"] = bid_sz
                            bsv_btc["ask_sz"] = ask_sz
                            bsv_btc["timestamp"] = timestamp
                        elif inst_id == 'LTC-BTC':
                            ltc_btc["price"] = price
                            ltc_btc["bid"] = bid
                            ltc_btc["ask"] = ask
                            ltc_btc["bid_sz"] = bid_sz
                            ltc_btc["ask_sz"] = ask_sz
                            ltc_btc["timestamp"] = timestamp
                        elif inst_id == 'STX-BTC':
                            stx_btc["price"] = price
                            stx_btc["bid"] = bid
                            stx_btc["ask"] = ask
                            stx_btc["bid_sz"] = bid_sz
                            stx_btc["ask_sz"] = ask_sz
                            stx_btc["timestamp"] = timestamp
                        elif inst_id == 'DAI-ETH':
                            dai_eth["price"] = price
                            dai_eth["bid"] = bid
                            dai_eth["ask"] = ask
                            dai_eth["bid_sz"] = bid_sz
                            dai_eth["ask_sz"] = ask_sz
                            dai_eth["timestamp"] = timestamp
                        elif inst_id == 'SOL-ETH':
                            sol_eth["price"] = price
                            sol_eth["bid"] = bid
                            sol_eth["ask"] = ask
                            sol_eth["bid_sz"] = bid_sz
                            sol_eth["ask_sz"] = ask_sz
                            sol_eth["timestamp"] = timestamp
                        check_prices()
                    except Exception as e:
                        print(e) # 刚开始时会打一堆 keyError: 'data'，这是某种意义上的启动信息，不要在意
                        pass
                    res = eval(res)
                    if 'event' in res:
                        continue
        except Exception as e:
            print("连接断开，正在重连……")
            continue


def check_prices():
    global test_start_money
    # eth-btc-usdt
    if eth_usdt["price"] != 0 and btc_usdt["price"] != 0 and eth_btc["price"] != 0:
        ratio = (eth_usdt["price"] / btc_usdt["price"]) / eth_btc["price"]
        if ratio > ratio_upper or ratio < ratio_lower:
            # print(f'{date_str} eth-btc {ratio}')
            determine_trade(eth_usdt, btc_usdt, eth_btc, ratio, "eth", "btc")
            pass
    # sol-btc-usdt
    if sol_usdt["price"] != 0 and btc_usdt["price"] != 0 and sol_btc["price"] != 0:
        ratio = (sol_usdt["price"] / btc_usdt["price"]) / sol_btc["price"]
        if ratio > ratio_upper or ratio < ratio_lower:
            # print(f'{date_str} sol-btc {ratio}')
            determine_trade(sol_usdt, btc_usdt, sol_btc, ratio, "bsv", "btc")
            pass
    # dai-btc-usdt
    if dai_usdt["price"] != 0 and btc_usdt["price"] != 0 and dai_btc["price"] != 0:
        ratio = (dai_usdt["price"] / btc_usdt["price"]) / dai_btc["price"]
        if ratio > ratio_upper or ratio < ratio_lower:
            # print(f'{date_str} dai-btc {ratio}')
            determine_trade(dai_usdt, btc_usdt, dai_btc, ratio, "dai", "btc")
            pass
    # okb-btc-usdt
    if okb_usdt["price"]!= 0 and btc_usdt["price"] != 0 and okb_btc["price"] != 0:
        ratio = (okb_usdt["price"] / btc_usdt["price"]) / okb_btc["price"]
        if ratio > ratio_upper or ratio < ratio_lower:
            # print(f'{date_str} okb-btc {ratio}')
            determine_trade(okb_usdt, btc_usdt, okb_btc, ratio, "okb", "btc")
            pass
    # bch-btc-usdt
    if bch_usdt["price"] != 0 and btc_usdt["price"] != 0 and bch_btc["price"] != 0:
        ratio = (bch_usdt["price"] / btc_usdt["price"]) / bch_btc["price"]
        if ratio > ratio_upper or ratio < ratio_lower:
            # print(f'{date_str} bch-btc {ratio}')
            determine_trade(bch_usdt, btc_usdt, bch_btc, ratio, "bch", "btc")
            pass
    # bsv-btc-usdt
    if bsv_usdt["price"] != 0 and btc_usdt["price"] != 0 and bsv_btc["price"] != 0:
        ratio = (bsv_usdt["price"] / btc_usdt["price"]) / bsv_btc["price"]
        if ratio > ratio_upper or ratio < ratio_lower:
            # print(f'{date_str} bsv-btc {ratio}')
            determine_trade(bsv_usdt, btc_usdt, bsv_btc, ratio, "bsv", "btc")
            pass
    # ltc-btc-usdt
    if ltc_usdt["price"] != 0 and btc_usdt["price"] != 0 and ltc_btc["price"] != 0:
        ratio = (ltc_usdt["price"] / btc_usdt["price"]) / ltc_btc["price"]
        if ratio > ratio_upper or ratio < ratio_lower:
            # print(f'{date_str} ltc-btc {ratio}')
            determine_trade(ltc_usdt, btc_usdt, ltc_btc, ratio, "ltc", "btc")
            pass
    # stx-btc-usdt
    if stx_usdt["price"] != 0 and btc_usdt["price"] != 0 and stx_btc["price"] != 0:
        ratio = (stx_usdt["price"] / btc_usdt["price"]) / stx_btc["price"]
        if ratio > ratio_upper or ratio < ratio_lower:
            # print(f'{date_str} stx-btc {ratio}')
            determine_trade(stx_usdt, btc_usdt, stx_btc, ratio, "stx", "btc")
            pass

    # dat-eth-usdt
    if dai_usdt["price"] != 0 and eth_usdt["price"] != 0 and dai_eth["price"] != 0:
        ratio = (dai_usdt["price"] / eth_usdt["price"]) / dai_eth["price"]
        if ratio > ratio_upper or ratio < ratio_lower:
            # print(f'{date_str} dai-eth {ratio}')
            determine_trade(dai_usdt, eth_usdt, dai_eth, ratio, "dai", "eth")
            pass
    # sol-eth-usdt
    if sol_usdt["price"] != 0 and eth_usdt["price"] != 0 and sol_eth["price"] != 0:
        ratio = (sol_usdt["price"] / eth_usdt["price"]) / sol_eth["price"]
        if ratio > ratio_upper or ratio < ratio_lower:
            # print(f'{date_str} sol-eth {ratio}')
            determine_trade(sol_usdt, eth_usdt, sol_eth, ratio, "okb", "btc")
            pass


def determine_trade(a_u, b_u, a_b, ratio, a_name, b_name):
    global test_start_money
    # if a_u["last_check"] == a_u["timestamp"] or a_b["last_check"] == a_b["timestamp"] or b_u["last_check"] == b_u["timestamp"]:
    #     # 如果你任何时候在determine_trade中操作了交易，那么这三个币对的last_check应该都更新了。避免用旧数据交易
    #     return
    # a_u["last_check"] = a_u["timestamp"]
    # b_u["last_check"] = b_u["timestamp"]
    # a_b["last_check"] = a_b["timestamp"]

    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if ratio > ratio_upper:
        # stx便宜，买btc换stx
        buy_btc_use_ustd_price = b_u["ask"]
        buy_stx_use_btc_price = a_b["ask"]
        sell_stx_to_usdt_price = a_u["bid"]
        new_money = test_start_money / buy_btc_use_ustd_price / buy_stx_use_btc_price * sell_stx_to_usdt_price * 0.999 * 0.999 * 0.999
        if new_money > test_start_money: # todo 暂时不考虑买卖size
            # todo 接入交易api
            record_str = f"\n======\n{date_str} {b_name}_usdt: {b_u}, {a_name}_{b_name}: {a_b}, {a_name}_usdt: {a_u}\n" + \
            f"{date_str} {a_name} cheap. buy {b_name} on {buy_btc_use_ustd_price}, exchange {b_name} to {a_name} at {buy_stx_use_btc_price}, then sell {a_name} for usdt at {sell_stx_to_usdt_price}\n" + \
            f"{date_str} this trade profit ratio: {'%.6f' % (new_money / test_start_money)}\n======\n\n"
            print(record_str)
            with open("record.txt", "a") as f:
                f.write(record_str)
    else:
        # btc便宜，买stx换btc
        buy_stx_use_usdt_price = a_u["ask"]
        sell_stx_to_btc_price = a_b["bid"]
        sell_btc_to_usdt_price = b_u["bid"]
        new_money = test_start_money / buy_stx_use_usdt_price * sell_stx_to_btc_price * sell_btc_to_usdt_price * 0.999 * 0.999 * 0.999
        if new_money > test_start_money: # todo 暂时不考虑买卖size
            # todo 接入交易api
            record_str = f"\n======\n{date_str} {b_name}_usdt: {b_u}, {a_name}_{b_name}: {a_b}, {a_name}_usdt: {a_u}\n" + \
            f"{date_str} {b_name} cheap. buy {a_name} on {buy_stx_use_usdt_price}, exchange {a_name} to {b_name} at {sell_stx_to_btc_price}, then sell {b_name} for usdt at {sell_btc_to_usdt_price}\n" + \
            f"{date_str} this trade profit ratio: {'%.6f' % (new_money / test_start_money)}\n======\n\n"
            print(record_str)
            with open("record.txt", "a") as f:
                f.write(record_str)


# trade
async def trade(url, api_key, passphrase, secret_key, trade_param):
    while True:
        try:
            async with websockets.connect(url) as ws:
                # login
                timestamp = str(int(time.time()))
                login_str = login_params(timestamp, api_key, passphrase, secret_key)
                await ws.send(login_str)
                # print(f"send: {login_str}")
                res = await ws.recv()
                print(res)

                # trade
                sub_str = json.dumps(trade_param)
                await ws.send(sub_str)
                print(f"send: {sub_str}")

                while True:
                    try:
                        res = await asyncio.wait_for(ws.recv(), timeout=25)
                    except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed) as e:
                        try:
                            await ws.send('ping')
                            res = await ws.recv()
                            print(res)
                            continue
                        except Exception as e:
                            print("连接关闭，正在重连……")
                            break

                    print(get_timestamp() + res)

        except Exception as e:
            print("连接断开，正在重连……")
            continue


# unsubscribe channels
async def unsubscribe(url, api_key, passphrase, secret_key, channels):
    async with websockets.connect(url) as ws:
        # login
        timestamp = str(int(time.time()))
        login_str = login_params(timestamp, api_key, passphrase, secret_key)
        await ws.send(login_str)
        # print(f"send: {login_str}")

        res = await ws.recv()
        print(f"recv: {res}")

        # unsubscribe
        sub_param = {"op": "unsubscribe", "args": channels}
        sub_str = json.dumps(sub_param)
        await ws.send(sub_str)
        print(f"send: {sub_str}")

        res = await ws.recv()
        print(f"recv: {res}")


# unsubscribe channels
async def unsubscribe_without_login(url, channels):
    async with websockets.connect(url) as ws:
        # unsubscribe
        sub_param = {"op": "unsubscribe", "args": channels}
        sub_str = json.dumps(sub_param)
        await ws.send(sub_str)
        print(f"send: {sub_str}")

        res = await ws.recv()
        print(f"recv: {res}")


api_key = ""
secret_key = ""
passphrase = ""

if __name__ == '__main__':
    # WebSocket公共频道 public channels
    # 实盘 real trading
    url = "wss://ws.okx.com:8443/ws/v5/public"
    # 模拟盘 demo trading
    # url = "wss://ws.okx.com:8443/ws/v5/public?brokerId=9999"

    # WebSocket私有频道 private channels
    # 实盘 real trading
    url_private = "wss://ws.okx.com:8443/ws/v5/private"
    # 模拟盘 demo trading
    # url = "wss://ws.okx.com:8443/ws/v5/private?brokerId=9999"

    '''
    公共频道 public channel
    :param channel: 频道名
    :param instType: 产品类型
    :param instId: 产品ID
    :param uly: 合约标的指数
    
    '''

    # 产品频道
    # channels = [{"channel": "instruments", "instType": "FUTURES"}]
    # 行情频道 tickers channel
    channels = [
        {"channel": "tickers", "instId": "BTC-USDT"},
        {"channel": "tickers", "instId": "ETH-USDT"},
        {"channel": "tickers", "instId": "SOL-USDT"},
        {"channel": "tickers", "instId": "DAI-USDT"},
        {"channel": "tickers", "instId": "OKB-USDT"},
        {"channel": "tickers", "instId": "OKB-USDT"},
        {"channel": "tickers", "instId": "BCH-USDT"},
        {"channel": "tickers", "instId": "BSV-USDT"},
        {"channel": "tickers", "instId": "LTC-USDT"},
        {"channel": "tickers", "instId": "STX-USDT"},
        {"channel": "tickers", "instId": "ETH-BTC"},
        {"channel": "tickers", "instId": "SOL-BTC"},
        {"channel": "tickers", "instId": "DAI-BTC"},
        {"channel": "tickers", "instId": "OKB-BTC"},
        {"channel": "tickers", "instId": "BCH-BTC"},
        {"channel": "tickers", "instId": "BCH-BTC"},
        {"channel": "tickers", "instId": "LTC-BTC"},
        {"channel": "tickers", "instId": "STX-BTC"},
        {"channel": "tickers", "instId": "DAI-ETH"},
        {"channel": "tickers", "instId": "SOL-ETH"},

    ]
    # 持仓总量频道
    # channels = [{"channel": "open-interest", "instId": "BTC-USD-210326"}]
    # K线频道
    # channels = [{"channel": "candle1m", "instId": "BTC-USD-210326"}]
    # 交易频道
    # channels = [{"channel": "trades", "instId": "BTC-USD-201225"}]
    # 预估交割/行权价格频道
    # channels = [{"channel": "estimated-price", "instType": "FUTURES", "uly": "BTC-USD"}]
    # 标记价格频道
    # channels = [{"channel": "mark-price", "instId": "BTC-USDT-210326"}]
    # 标记价格K线频道
    # channels = [{"channel": "mark-price-candle1D", "instId": "BTC-USD-201225"}]
    # 限价频道
    # channels = [{"channel": "price-limit", "instId": "BTC-USD-201225"}]
    # 深度频道
    # channels = [{"channel": "books", "instId": "BTC-USD-SWAP"}]
    # 期权定价频道
    # channels = [{"channel": "opt-summary", "uly": "BTC-USD"}]
    # 资金费率频道
    # channels = [{"channel": "funding-rate", "instId": "BTC-USD-SWAP"}]
    # 指数K线频道
    # channels = [{"channel": "index-candle1m", "instId": "BTC-USDT"}]
    # 指数行情频道
    # channels = [{"channel": "index-tickers", "instId": "BTC-USDT"}]
    # status频道
    # channels = [{"channel": "status"}]

    '''
    私有频道 private channel
    :param channel: 频道名
    :param ccy: 币种
    :param instType: 产品类型
    :param uly: 合约标的指数
    :param instId: 产品ID
    
    '''

    # 账户频道
    # channels = [{"channel": "account", "ccy": "BTC"}]
    # 持仓频道
    # channels = [{"channel": "positions", "instType": "FUTURES", "uly": "BTC-USDT", "instId": "BTC-USDT-210326"}]
    # 订单频道
    # channels = [{"channel": "orders", "instType": "FUTURES", "uly": "BTC-USD", "instId": "BTC-USD-201225"}]
    # 策略委托订单频道
    # channels = [{"channel": "orders-algo", "instType": "FUTURES", "uly": "BTC-USD", "instId": "BTC-USD-201225"}]

    '''
    交易 trade
    '''

    # 下单
    # trade_param = {"id": "1512", "op": "order", "args": [{"side": "buy", "instId": "BTC-USDT", "tdMode": "isolated", "ordType": "limit", "px": "19777", "sz": "1"}]}
    # 批量下单
    # trade_param = {"id": "1512", "op": "batch-orders", "args": [
    #         {"side": "buy", "instId": "BTC-USDT", "tdMode": "isolated", "ordType": "limit", "px": "19666", "sz": "1"},
    #         {"side": "buy", "instId": "BTC-USDT", "tdMode": "isolated", "ordType": "limit", "px": "19633", "sz": "1"}
    #     ]}
    # 撤单
    # trade_param = {"id": "1512", "op": "cancel-order", "args": [{"instId": "BTC-USDT", "ordId": "259424589042823169"}]}
    # 批量撤单
    # trade_param = {"id": "1512", "op": "batch-cancel-orders", "args": [
    #         {"instId": "BTC-USDT", "ordId": "259432098826694656"},
    #         {"instId": "BTC-USDT", "ordId": "259432098826694658"}
    #     ]}
    # 改单
    # trade_param = {"id": "1512", "op": "amend-order", "args": [{"instId": "BTC-USDT", "ordId": "259432767558135808", "newSz": "2"}]}
    # 批量改单
    # trade_param = {"id": "1512", "op": "batch-amend-orders", "args": [
    #         {"instId": "BTC-USDT", "ordId": "259435442492289024", "newSz": "2"},
    #         {"instId": "BTC-USDT", "ordId": "259435442496483328", "newSz": "3"}
    #     ]}


    loop = asyncio.get_event_loop()

    # 公共频道 不需要登录（行情，持仓总量，K线，标记价格，深度，资金费率等）
    loop.run_until_complete(do_subscribe(url, channels, url_private))

    # 私有频道 需要登录（账户，持仓，订单等）
    # loop.run_until_complete(subscribe(url, api_key, passphrase, secret_key, channels))

    # 交易（下单，撤单，改单等）
    # loop.run_until_complete(trade(url, api_key, passphrase, secret_key, trade_param))



    loop.close()