import string
import random
import glob, os
import json
import time
import config
import helpers
import numpy as np
import requests
from crawler_logging import logger as logging


# class AnalyzeStocks(object):
# 	"""docstring for AnalyzeStocks"""
# 	def __init__(self, today_prices_dir, today_price_analysis_dir, stocks_sort_by):
# 		super(AnalyzeStocks, self).__init__()
# 		self.today_prices_dir = today_prices_dir
# 		self.today_price_analysis_dir = today_price_analysis_dir
# 		self.stocks_sort_by = stocks_sort_by
# 		self.gen_today_price_analysis_dir()
# 		# self.analyze_today_price_analysis_dir()
		
	
# 	def gen_today_price_analysis_dir(self):
# 		os.chdir(self.today_prices_dir)
# 		for File in glob.glob("*.json"):
# 			Date = File.split(".json")[0]  
# 			TodayPrices = helpers.json_file_data(self.today_prices_dir+"/"+File)
# 			PriceStatsList = []
# 			for P in TodayPrices:
# 				PriceStats = {}
# 				InstrumentId = P['InstrumentId']
# 				Prices = P['Prices']
# 				PricesOnly = [_P['Price'] for _P in Prices]
# 				PricesRange = (PricesOnly[0], PricesOnly[-1]) \
# 					if len(PricesOnly)>1 else None
# 				PricesDateRange = (Prices[0]['ToTime'], Prices[-1]['ToTime']) \
# 					if len(Prices)>1 else None
# 				PricesOnly = np.array(PricesOnly, dtype=float)
# 				Dx = np.diff(PricesOnly)
# 				Increase = Dx[Dx > 0]
# 				MaxIncrease =  Increase.max()  if Increase.any() else 0.00
# 				MeanIncrease = Increase.mean() if Increase.any() else 0.00
# 				PriceStats["InstrumentId"] = InstrumentId
# 				PriceStats["MaxIncrease"]  = MaxIncrease
# 				PriceStats["MeanIncrease"] = MeanIncrease
# 				PriceStats["PricesRange"] = PricesRange
# 				PriceStats["PricesDateRange"] = PricesDateRange
# 				PriceStatsList.append(PriceStats)
			

# 			PriceStatsListSorted = sorted(
# 				PriceStatsList, key=lambda k: float(k[self.stocks_sort_by]), reverse=True
# 			) 

# 			helpers.set_data(
# 				data=PriceStatsListSorted,
# 				path=self.today_price_analysis_dir+"/"+File
# 			)



class AnalyzeStocks(object):
	"""docstring for AnalyzeStocks"""


	def get_instruments(self):
		logging.info("getting instruments data ...")
		return helpers.get_instruments(config.instruments_file)

	def get_closing_prices(self):
		logging.info("getting closing prices ...")
		r = requests.get(config.Closingprices_Url+helpers.device_id())
		return r.json()



	def get_today_prices(self):
		logging.info("getting today prices ...")
		r = requests.get(config.Todayprices_Url.format(helpers.device_id()))
		return r.json()



	def today_market_prices(self, open_markets_only=True):
		ClosingPrices  = sorted(self.get_closing_prices(), key=lambda k: float(k['InstrumentId']))
		TodayPrices    = sorted(self.get_today_prices(), key=lambda k: float(k['InstrumentId']))
		Instruments    = sorted(self.get_instruments(), key=lambda k: float(k['InstrumentID']))
		InstrumentIds = [Instrument["InstrumentID"] for Instrument in Instruments]

		res = []

		for elem in ClosingPrices:
			if elem['InstrumentId'] not in InstrumentIds:
				continue
			if open_markets_only and elem['IsMarketOpen'] == False:
				continue
			Prices 				= helpers.find_in_list(TodayPrices,
											'InstrumentId', elem['InstrumentId'])
			InstrumentDetail	= helpers.find_in_list(Instruments,
											'InstrumentID', elem['InstrumentId'])

			# print("\n----------------")
			# print(InstrumentDetail)
			# print("----------------\n")
			
			# InstrumentDetail = {k:v for k,v in InstrumentDetail.items()
			# 						if k in ('InstrumentDisplayName', 'ExchangeID', 'SymbolFull')
			# 					}
			elem.update(InstrumentDetail)
			elem['Prices'] = Prices.get('Prices', [])
			res.append(elem)

		return res


	
	def today_price_analysis(self, stocks_sort_by, open_markets_only=True):
		logging.info(
			f"getting today's price analysis of {'opened' if open_markets_only else 'all'}"
			f" markets sorted by {stocks_sort_by} ..."
		)
		PriceStatsList = []
		for P in self.today_market_prices(open_markets_only):
			PriceStats = {}
			InstrumentId = P['InstrumentId']
			Prices = P['Prices']
			PricesOnly = [_P['Price'] for _P in Prices]
			PricesRange = (PricesOnly[0], PricesOnly[-1]) \
				if len(PricesOnly)>1 else None
			PricesDateRange = (Prices[0]['ToTime'], Prices[-1]['ToTime']) \
				if len(Prices)>1 else None
			PricesOnly = np.array(PricesOnly, dtype=float)
			Dx = np.diff(PricesOnly)
			Increase = Dx[Dx > 0]
			MaxIncrease =  Increase.max()  if Increase.any() else 0.00
			MeanIncrease = Increase.mean() if Increase.any() else 0.00
			PriceStats["InstrumentId"] = InstrumentId
			PriceStats["MaxIncrease"]  = MaxIncrease
			PriceStats["MeanIncrease"] = MeanIncrease
			PriceStats["PricesRange"] = PricesRange
			PriceStats["PricesDateRange"] = PricesDateRange
			PriceStats["OfficialClosingPrice"] = P['OfficialClosingPrice']
			PriceStats["IsMarketOpen"] = P['IsMarketOpen']
			PriceStats["OfficialClosingPrice"] = P['OfficialClosingPrice']
			PriceStats["ClosingPrices"] = P['ClosingPrices']
			PriceStats["InstrumentDisplayName"] = P.get('InstrumentDisplayName')
			PriceStats["ExchangeID"] = P.get('ExchangeID')
			PriceStats["SymbolFull"] = P.get('SymbolFull')
			PriceStatsList.append(PriceStats)
			

		return sorted(PriceStatsList, 
						key=lambda k: float(k[stocks_sort_by]),
		 				reverse=True
				)

	


if __name__ == '__main__':
	analyzer = AnalyzeStocks()
	open_markets_only = config.analyze_open_markets_only
	top_markets = analyzer.today_price_analysis(
		stocks_sort_by=config.stocks_sort_by, open_markets_only=open_markets_only)

	helpers.set_data(
		data=top_markets,
		path=config.temp_dir+f"/top_markets_{'opened' if open_markets_only else 'all'}.json"
	)
	# print(json.dumps(top_markets[:20], indent=2))