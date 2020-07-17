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


class AnalyzeStocks(object):
	"""docstring for AnalyzeStocks"""


	def get_instruments(self):
		logging.info("getting instruments data ...")
		return helpers.get_instruments(config.instruments_file)

	def get_closing_prices(self):
		logging.info("getting closing prices ...")
		r = requests.get(config.Closingprices_Url+helpers.device_id())
		return r.json()



	def get_today_prices(self, time_slots_count=200):
		if time_slots_count < 0:
			raise ValueError("time_slots_count cannot be in negative")
		logging.info("getting today prices ...")
		r = requests.get(config.Todayprices_Url.format(time_slots_count, helpers.device_id()))
		return r.json()



	def today_market_prices(self, time_slots_count=200, open_markets_only=True):
		ClosingPrices  = sorted(self.get_closing_prices(), key=lambda k: float(k['InstrumentId']))
		TodayPrices    = sorted(self.get_today_prices(time_slots_count), key=lambda k: float(k['InstrumentId']))
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
			elem.update(InstrumentDetail)
			elem['Prices'] = Prices.get('Prices', [])
			res.append(elem)

		return res


	
	def today_price_analysis(self, stocks_sort_by, time_slots_count=24, open_markets_only=True, time_slots_pick=2):
		
		logging.info(
			f"getting today's price analysis of {'opened' if open_markets_only else 'all'}"
			f" markets sorted by {stocks_sort_by} ..."
		)
		
		file_name = f"markets_{'opened' if open_markets_only else 'all'}" \
					f"_{time_slots_count}_time_slots" \
					f"_time_compare_{time_slots_pick}_today_price_analysis.json"
		res = []
		
		for P in self.today_market_prices(
			time_slots_count=time_slots_count,
			open_markets_only=open_markets_only
		):
			PriceStats = {}
			InstrumentId = P['InstrumentId']
			Prices = P['Prices']

			if len(Prices)<time_slots_pick: 
				# print(Prices, "\n") 
				continue

			# d2 = parse(Prices[-1]['ToTime']) 
			# d1 = parse(Prices[-3]['ToTime']) 
			# print("dis -> ",(d2-d1).seconds/60)


			PricesToMonitor = Prices[int(f"-{time_slots_pick}"):]

			PricesRange = [_P['Price'] for _P in PricesToMonitor]
			
			PricesDateRange = [_P['ToTime'] for _P in PricesToMonitor]
			
			PricesRange = np.array(PricesRange, dtype=float)

			Dx = np.diff(PricesRange) / PricesRange[:-1] * 100
			
			# MaxIncrease = sum([100 * (b - a) / a for a, b in zip(PricesRange[::1], PricesRange[1::1])])/len(PricesRange)
			MaxIncrease =  Dx.max()  if Dx.any() else 0.00
			MeanIncrease = Dx.mean() if Dx.any() else 0.00
			PriceStats["InstrumentId"] = InstrumentId
			PriceStats["MaxIncrease"]  = MaxIncrease
			PriceStats["MeanIncrease"] = MeanIncrease
			PriceStats["PricesRange"] = PricesToMonitor
			PriceStats["OfficialClosingPrice"] = P['OfficialClosingPrice']
			PriceStats["IsMarketOpen"] = P['IsMarketOpen']
			PriceStats["OfficialClosingPrice"] = P['OfficialClosingPrice']
			PriceStats["ClosingPrices"] = P['ClosingPrices']
			PriceStats["InstrumentDisplayName"] = P.get('InstrumentDisplayName')
			PriceStats["ExchangeID"] = P.get('ExchangeID')
			PriceStats["SymbolFull"] = P.get('SymbolFull')
			res.append(PriceStats)
			

		res = sorted(res, 
						key=lambda k: float(k[stocks_sort_by]),
						reverse=True
				)

		helpers.set_data(data=res, path=f"{config.temp_dir}/{file_name}")

		return res


	def trade_insights(self, Insights, open_markets_only=True, sort_by="growth"):
		
		if sort_by not in ("percentage", "growth"):
			raise Exception(f'<sort_by> value must be in {("percentage", "growth").join(" OR ")} ')
		logging.info(
			f"Getting Trade Insights of {'opened' if open_markets_only else 'all'} markets ..."
		)
		ClosingPrices  = sorted(self.get_closing_prices(), key=lambda k: float(k['InstrumentId']))
		Instruments    = sorted(self.get_instruments(), key=lambda k: float(k['InstrumentID']))
		InstrumentIds  = [Instrument["InstrumentID"] for Instrument in Instruments]

		res = []

		for elem in ClosingPrices:
			if elem['InstrumentId'] not in InstrumentIds:
				continue
			if open_markets_only and elem['IsMarketOpen'] == False:
				continue
			
			ElemInsight = helpers.find_in_list(Insights,
							'instrumentId', elem['InstrumentId'])

			if not ElemInsight:
				continue

			InstrumentDetail	= helpers.find_in_list(Instruments,
											'InstrumentID', elem['InstrumentId'])

			elem.update({k:v for k,v in InstrumentDetail.items()
				if k in ("InstrumentDisplayName", "SymbolFull",)})
			elem.update(ElemInsight)
			res.append(elem)
		

		res = sorted(res, key=lambda k: float(k[sort_by]), reverse=True)

		helpers.set_data(
			data=res,
			path=config.temp_dir+f"/{'opened' if open_markets_only else 'all'}_markets_insights_by_{sort_by}.json"
		)

		return res
	


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