import cryptocompare
import requests
import json
from pprint import pprint
import datetime
from queue import Queue
import threading
import time

redditstats = ['Points', 'comments_per_day', 'comments_per_hour', 'name', 'posts_per_day', 'posts_per_hour', 'subscribers']
twitterstats = ['Points', 'followers', 'statuses']
generalstats = ['CoinName']
facebookstats = ['Points', 'likes', 'talking_about']
cryptocomparestats = ['Points', 'Followers', 'PageViews', 'PageViewsSplit']
repostats = ['stars', 'language', 'forks', 'subscribers', 'open_total_issues']

# master dictionary for all important stats
masterstats = {}
masterstats['Reddit'] = redditstats
masterstats['Twitter'] = twitterstats
masterstats['General'] = generalstats
masterstats['Facebook'] = facebookstats
masterstats['CryptoCompare'] = cryptocomparestats
masterstats['Repo'] = repostats

# cryptocompare raw data
coinlist = cryptocompare.get_coin_list()
print('finished getting list of coins')

# dict of coin ids; format -> {coin: id} 
symbol_id_dict = {
    'BTC': 1182,
    'ETH': 7605,
    'LTC': 3808,
    'XRP': 5031,
    'ETC': 5324,
    'ZIL': 716725,
    'DASH': 3807,
    'SC': 13072,
    'XMR': 5038,
    'NEO': 27368,
    'BAT': 107672
}

# for coin in coinlist.keys():
#     symbol_id_dict[coin] = coinlist[coin]['Id']

symbols = list(symbol_id_dict.keys())
# print('finished getting symbols')

# use symbol id to scrape live social status data
def live_social_status(symbol, symbol_id_dict={}):
    if not symbol_id_dict:
        symbol_id_dict = {
            'BTC': 1182,
            'ETH': 7605,
            'LTC': 3808,
            'XRP': 5031,
            'ETC': 5324,
            'ZIL': 716725,
            'DASH': 3807,
            'SC': 13072,
            'XMR': 5038,
            'NEO': 27368,
            'BAT': 107672 
        }
    symbol_id = symbol_id_dict[symbol.upper()]
    url = 'https://www.cryptocompare.com/api/data/socialstats/?id={}'\
            .format(symbol_id)
    page = requests.get(url)
    data = page.json()['Data']
    return data

def get_stats(coinsymbol, master_stats): 
    time.sleep(0.5)
    coindict = {}
    for social_site in master_stats.keys():
        
        social_dict = {}
        for stat in master_stats[social_site]:
            try:
                social_dict[stat] = live_social_status(coinsymbol, symbol_id_dict)[social_site][stat]
            except:
                continue
        coindict[social_site] = social_dict  
    
    print('finished: ' + str(coinsymbol))
    print('--------------------------')
    return coindict

# worker function
def worker(queue):
    queue_full = True
    while queue_full:

        # get data off queue and do work
        coin = q.get()        
        data = get_stats(coin, masterstats)
        with master_lock:
            master[coin] = data
        q.task_done()

# save data to file if new file, append to old file if exists
def save_file(data, newfile=False, filename='coindata.txt'):
    if newfile:
        with open(filename, 'w') as outfile:
            json.dump(data, outfile)
    else:
        try:
            json_data = json.load(open('coindata.txt'))
            json_data[now] = data
        except IOError:
            print('FILE NOT FOUND')
            
def load_file(filename):
    json_data = json.load(open(filename))
    return json_data

if __name__ == "__main__":

	# MASTER DICTIONARY
	master = {}

	# implementing threading lock
	master_lock = threading.Lock()

	# Load up a queue with symbols
	q = Queue()
	for coin in symbols:
	    q.put(coin)
    
	# start time   
	start = time.time()

	# create threads
	thread_count = 10
	for i in range(thread_count):
	    t = threading.Thread(target=worker, args = (q,))
	    t.daemon = True
	    t.start()
    
	# wait until thread terminates
	q.join()
	print('total time taken: ', time.time() - start)

	now = str(datetime.datetime.now().isoformat())
	save_file(master, newfile=True)
