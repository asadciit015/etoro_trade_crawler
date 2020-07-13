import string
import random
import glob, os
import json
import csv
import time
import config
from crawler_logging import logger as logging

# DictInt = TypeVar('DictInt', dict, list)
# defaul_time_cache = 60

def find_in_list(arr, key, value):
    return next((item for item in arr if item[key] == value), {})

def is_digit(value):
    try:
        int(str(value).strip().replace(",", "").replace(".", "").replace("$", ""))
        return True
    except Exception as e:
        return False
    
def id_generator(size=8, chars='absdef' + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def device_id():
    pattern = "xxxxtxxx-xxxx-4xxx-yxxx-xxxxxxtxxxxx"
    pattern = pattern.replace('t', hex(int(time.time()) % 16).replace('0x', ''))
    pattern_list = list(pattern)
    for key, symblol in enumerate(list(pattern_list)):
        if symblol == 'x' or symblol == 'y':
            n = 16 * random.random()
            if n:
                n /= 3
            else:
                n = 8
            pattern_list[key] = hex(int(n)).replace('0x', '')
    return "".join(pattern_list)


def json_file_data(path):
    f = open(path) 
    return json.load(f)



def read_csv(path) -> dict:
    rows = []
    with open(path, 'rt') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def get_exchange_info(name):
    arr = read_csv(config.markethourscsv_file)
    return find_in_list(arr, "Exchange", name)


# def set_cache(key: string, data: DictInt) -> None:
#     base_path = os.path.dirname(__file__)
#     try:
#         with open(os.path.join(base_path, 'temp', key), 'w') as fd:
#             fd.write(json.dumps(data))
#     except TypeError:
#         logging.error('Type error')
#         set_cache(key, {})
#     except json.JSONDecodeError:
#         logging.error('Json decode error')


# def cookies_parse(response_cookies):
#     cookies_dict = {}
#     cookies = response_cookies
#     for cookie in str(cookies).split('\r\n'):
#         cookie = cookie.split(' ')
#         if len(cookie) > 1:
#             cookie_list = cookie[1].split('=')
#             if len(cookie_list) == 2:
#                 cookies_dict[cookie_list[0]] = cookie_list[1]
#             elif len(cookie_list) > 2:
#                 cookies_dict[cookie_list[0]] = cookie_list[1]
#                 for i in range(len(cookie_list) - 2):
#                     cookies_dict[cookie_list[0]] += '='
#     return cookies_dict


# def get_cache(key: string, number_of_time: int=1) -> dict:
#     base_path = os.path.dirname(__file__)
#     path = os.path.join(base_path, 'temp', key)
#     if os.path.isfile(path):
#         mod_time = time.time() - os.path.getmtime(path)
#         if number_of_time and mod_time > (number_of_time*defaul_time_cache):
#             return {}
#         with open(path, 'r') as fd:
#             file_content = fd.read()
#         fd.close()
#         try:
#             return json.loads(file_content)
#         except json.decoder.JSONDecodeError:
#             return {}
#     else:
#         return {}


# def get_list_instruments(aggregate_data, type='Buy'):
#     if not aggregate_data:
#         return {}
#     max_store = {'count': 0, 'ids': []}
#     for instr_id in aggregate_data[type]:
#         if max_store['count'] < aggregate_data[type][instr_id]:
#             max_store['count'] = aggregate_data[type][instr_id]
#             max_store['ids'] = [instr_id]
#         if max_store['count'] == aggregate_data[type][instr_id]:
#             if instr_id not in max_store['ids']:
#                 max_store['ids'].append(instr_id)
#     return max_store


def set_login_data(data, path=config.logindata_file):
    try:
        with open(path, 'w') as fd:
            fd.write(json.dumps(data, indent=2))
    except TypeError:
        logging.error('Type error')
        set_login_data({})
    except json.JSONDecodeError:
        logging.error('Json decode error')


def set_data(data, path):
    try:
        with open(path, 'w') as fd:
            fd.write(json.dumps(data, indent=2))
    except TypeError:
        logging.error('Type error')
        set_data({}, path)
    except json.JSONDecodeError:
        logging.error('Json decode error')


def get_login_data_saved(path=config.logindata_file):
    f = open(path) 
    return json.load(f)

            

        
def clientPostions(login_data):
    """ opened trade positions by user"""
    return login_data.get("AggregatedResult", {}).get("ApiResponses", {}
            ).get("PrivatePortfolio", {}).get("Content", {}
            ).get("ClientPortfolio", {}).get("Positions", [])


def clientStockOrders(login_data):
    return login_data.get("AggregatedResult", {}).get("ApiResponses", {}
            ).get("PrivatePortfolio", {}).get("Content", {}
            ).get("ClientPortfolio", {}).get("StockOrders", [])


def clientOrders(login_data):
    return login_data.get("AggregatedResult", {}).get("ApiResponses", {}
            ).get("PrivatePortfolio", {}).get("Content", {}
            ).get("ClientPortfolio", {}).get("Orders", [])


def clientEntryOrders(login_data):
    return login_data.get("AggregatedResult", {}).get("ApiResponses", {}
            ).get("PrivatePortfolio", {}).get("Content", {}
            ).get("ClientPortfolio", {}).get("EntryOrders", [])


def clientExitOrders(login_data):
    return login_data.get("AggregatedResult", {}).get("ApiResponses", {}
            ).get("PrivatePortfolio", {}).get("Content", {}
            ).get("ClientPortfolio", {}).get("ExitOrders", [])


def clientMirrors(login_data):
    return login_data.get("AggregatedResult", {}).get("ApiResponses", {}
            ).get("PrivatePortfolio", {}).get("Content", {}
            ).get("ClientPortfolio", {}).get("Mirrors", [])


def clientCredit(login_data):
    return login_data.get("AggregatedResult", {}).get("ApiResponses", {}
            ).get("PrivatePortfolio", {}).get("Content", {}
            ).get("ClientPortfolio", {}).get("Credit")


def clientBonusCredit(login_data):
    return login_data.get("AggregatedResult", {}).get("ApiResponses", {}
            ).get("PrivatePortfolio", {}).get("Content", {}
            ).get("ClientPortfolio", {}).get("BonusCredit")


def clientRealCID(login_data):
    users = login_data.get("AggregatedResult", {}).get("ApiResponses", {}
            ).get("CurrentUserData", {}).get("Content", {}
            ).get("users", [])
    user = users[0] if len(users)>0 else {}

    return user.get("realCID")


def clientDemoCID(login_data):
    users = login_data.get("AggregatedResult", {}).get("ApiResponses", {}
            ).get("CurrentUserData", {}).get("Content", {}
            ).get("users", [])
    user = users[0] if len(users)>0 else {}

    return user.get("demoCID")


def historyPositions(data_list=[], path=config.closed_trade_history_file):
    if data_list:
        pass
    elif path:
        data_list = json_file_data(path)

    data =data_list or {}

    return data.get("HistoryPositions", [])


def isOrderClosed(PositionID, data_list=[], path=config.closed_trade_history_file):
    return find_in_list(
            historyPositions(data_list=data_list, path=path), 'OriginalPositionID',
            int(PositionID)
        )



def isOrderOpened(instruments_id, data_list, return_data=False):
    d = find_in_list(
                clientPostions(data_list), 'InstrumentID',
                int(instruments_id)
            )
    if return_data:
        return d
    else:
        return d != {}


def lastOrderedTrade(isBuy=True):
    """ get last ordered trades saved in json file
        isBuy => True then only returns buying trades else returns all
    """
    data = json_file_data(config.last_trade_done_file)
    if isBuy:   data = [k for k in data if k["IsBuy"]==True]

    return data


def addLastOrderedTrade(openedTrade):
    """ add last ordered trades in json file"""
    trades = json_file_data(config.last_trade_done_file) or []

    #if openedTrade is selling trade => 
    #   find already exisiting trade for openedTrade in history and if buying found remove buying one
    if(openedTrade['IsBuy'] ==False):
        openedTradeHistory = find_in_list(trades, "InstrumentID", openedTrade["InstrumentID"])
        if openedTradeHistory and openedTradeHistory["IsBuy"]==True:
            logging.info('Removing openedTrade buying trade history ...')
            trades.remove(openedTradeHistory)

    instrumentData = find_instrument_by_id(openedTrade['InstrumentID'])
    openedTrade.update({k:v for k,v in instrumentData.items() 
        if k in ("InstrumentDisplayName", "SymbolFull")})
    trades.append(openedTrade)
    set_data(trades, config.last_trade_done_file)
    return json_file_data(config.last_trade_done_file)


def orderedTrade(instruments_id, login_data):
    """ get opened ordered trade by instrument id"""
    return find_in_list(
            clientPostions(login_data), 'InstrumentID',
            int(instruments_id)
        )


def get_instruments(path=config.instruments_file):
    return json_file_data(path)['InstrumentDisplayDatas']

def find_instrument_by_id(id, path=config.instruments_file):
    instruments = get_instruments(path)
    return find_in_list(instruments, "InstrumentID", int(id))

def find_instrument_by_symbol(symbol, path=config.instruments_file):
    instruments = get_instruments(path)
    return find_in_list(instruments, "SymbolFull", symbol.upper())



if '__main__' == __name__:
    o = {'PositionID': 1782205451,
         'CID': 16393103,
         'OpenDateTime': '2020-07-13T10:24:52.203Z',
         'OpenRate': 9219.32,
         'InstrumentID': 100000,
         'IsBuy': False,
         'TakeProfitRate': 0.01,
         'StopLossRate': 11502.32,
         'MirrorID': 0,
         'ParentPositionID': 0,
         'Amount': 5100.0,
         'Leverage': 2,
         'OrderID': 0,
         'Units': 1.106372,
         'TotalFees': 0.0,
         'InitialAmountInDollars': 5100.0,
         'IsTslEnabled': True,
         'StopLossVersion': 1,
         'IsSettled': False,
         'RedeemStatusID': 0,
         'InitialUnits': 1.106372,
         'IsPartiallyAltered': False,
         'UnitsBaseValueDollars': 5100.0,
         'IsDiscounted': False}

    print(addLastOrderedTrade(o))
    # print( json.dumps( lastOrderedTrade(), indent=2) )
    # print( json.dumps( find_instrument_by_id(1), indent=2) )


    # _lastOrderedTrade = lastOrderedTrade(isBuy=True)[0]
    # instrumentData = find_instrument_by_id(_lastOrderedTrade["InstrumentID"])
    # _lastOrderedTrade.update({k:v for k,v in instrumentData.items()
    #             if k in ("InstrumentDisplayName", "SymbolFull",)})
    # print( json.dumps( _lastOrderedTrade, indent=4) )

    # print( json.dumps( read_csv(config.markethourscsv_file), indent=2) )
    # print(device_id())
    # d = get_login_data_saved()
    # print(clientCredit(d))
    # print(clientBonusCredit(d))
    # print(clientRealCID(d))
    # print(clientDemoCID(d))
    # print(clientPostions(d))
    # print(clientOrders(d))
    # print(clientExitOrders(d))
    

    # from datetime import datetime
    # import calendar

    # # import pytz
    # # bst = pytz.timezone('Europe/London')
    # # dt = datetime.strptime('2012-10-12T19:30:00', '%Y-%m-%dT%H:%M:%S')

    # def utc_to_local(utc_dt):
    #     '''Converts a utc datetime obj to local datetime obj.'''
    #     t = utc_dt.timetuple()
    #     secs = calendar.timegm(t)
    #     loc = time.localtime(secs)
    #     return datetime.fromtimestamp(time.mktime(loc))

    # # print(utc_to_local(datetime.utcnow()).strftime("%Y-%m-%dT%H:%M:%S.%f%Z"))

    # # print(set_login_data(d))
    # # f = open('instruments.json',) 
    # # instruments_data = json.load(f)['InstrumentDisplayDatas']
    # # print(instruments_data[1])