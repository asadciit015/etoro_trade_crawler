#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
import pytz
import json, time
import  config, helpers
from etoro import Etoro
from analyzer import AnalyzeStocks
from apscheduler.schedulers.blocking import BlockingScheduler
from crawler_logging import logger
from datetime import datetime, timezone, timedelta



def get_etoro_instance():
	
	# Open Web Driver
	etoro_instance = Etoro()
	
	#Login To Site
	login_status = etoro_instance.login()

	if login_status is True:

		if config.AccountType == "VIRTUAL":
			logger.info(f"Switching to VIRTUAL Account ...")
			time.sleep(5)
			etoro_instance.switch_account(to_demo=True)
			time.sleep(3)

		if config.AccountType != etoro_instance.current_account_type:
			raise Exception(
				f"Switch Account Failed. should be <{config.AccountType}>"
				f" instead of <{etoro_instance.current_account_type}> !")

		return etoro_instance


	elif login_status is False and (
		etoro_instance.has_server_error or etoro_instance.site_not_reachable()
	):
		retries = 2
		while(login_status is False and retries < etoro_instance.MAX_RETRIES):
			logger.warning(
				f'Error Login :: {config.login_fail_msg}, Auto Retrying:'
				f'{retries}/{etoro_instance.MAX_RETRIES}'
			)
			# del etoro_instance
			# etoro_instance = Etoro()
			etoro_instance.login()
			login_status = etoro_instance.get_loggedin_username()
			retries+=1

		if login_status is False:
			raise Exception("Max retries done to login but failed")

	else:
		raise Exception("Login Failed. Check Username or Password")



def buy_trade(etoro_instance):
	try:
		detail = ""

		# etoro_instance.login()
		#checking  current balance
		clientCredit = helpers.clientCredit(login_data=etoro_instance.get_login_info)

		open_markets_only = config.analyze_open_markets_only
		logger.info(
			f"Analyzing Today Stocks For {'opened' if open_markets_only else 'all'} markets ..."
		)
		
		analyzer = AnalyzeStocks()
		
		top_markets = analyzer.today_price_analysis(
			stocks_sort_by=config.stocks_sort_by,
			open_markets_only=open_markets_only)
		
		helpers.set_data(
			data=top_markets,
			path=config.temp_dir+f"/top_markets_{'opened' if open_markets_only else 'all'}.json"
		)

		for t1, top_market in enumerate(top_markets):
			logger.info(f"\nGoing to open Buying Trade for :\n{top_market}\n")
			buy_trade, buy_trade_res  = etoro_instance.trade(
				ins=top_market.get("InstrumentId"), IsBuy=True)
			if buy_trade is False:
				detail = (
					f"Couldnot open buying position for: '{top_market.get('SymbolFull')}'"
					f" reason :\n{buy_trade_res}\n")
				logger.warning(detail)
			else:
				detail = (
					f"Opened buying position for: '{top_market.get('SymbolFull')}'"
					f" response :\n{buy_trade_res}\n")
				logger.info(detail)
				break

		logger.info(f"\nGoing to update User Date ...")
		user_data = etoro_instance.get_login_info
		logger.info(f"\nGot User Data :\n{user_data}\n")


		logger.info(f"\nGoing to update User Trade History ...")
		user_trade_history = etoro_instance.get_trade_history
		logger.info(f"\nGot User Trade History :\n{user_trade_history}\n")
		
		msg = '<buy_trade> finished ...'
		print('+'*len(msg))
		print(msg)
		print('+'*len(msg))

	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		err_detail = e, fname, exc_tb.tb_lineno
		detail = f"Following Error occured in buy_trade ::\n{err_detail}\n"
		logger.error(detail)

	#write trade logs
	helpers.write_csv("Buying", detail)



def sell_trade(etoro_instance):
	try:
		detail = ""
		# etoro_instance.login()

		logger.info(f"Going to get last Ordered Trades (For Opening Selling Position ) ...")

		lastOrderedTrades = helpers.lastOrderedTrade(isBuy=True)

		if not lastOrderedTrades:
			logger.info(f"No Last Ordered Trades found to open a selling position.")

		for t1, lastOrderedTrade in enumerate(lastOrderedTrades):

			instrumentID = lastOrderedTrade['InstrumentID']
			instrumentData = helpers.find_instrument_by_id(instrumentID)
			lastOrderedTrade.update({k:v for k,v in instrumentData.items()
				if k in ("InstrumentDisplayName", "SymbolFull",)})
			instrumentSymbol = instrumentData["SymbolFull"]
			instrumentDisplayName = instrumentData["InstrumentDisplayName"]
			instrumentTitle = f"{instrumentSymbol} - {instrumentDisplayName}"
			positionID = lastOrderedTrade['PositionID']
			

			logger.info(f"\n[{t1+1}/{len(lastOrderedTrades)}] :\n{lastOrderedTrade}\n")

			logger.info(f"Going to get User Trade History ...")
			tradeHistory = etoro_instance.get_trade_history

			closedOrder = helpers.isOrderClosed(
				positionID, data_list=tradeHistory,
				path=config.closed_trade_history_file)

			if not closedOrder:
				logger.info(
					f"<[{instrumentTitle}]: postionID->"
					f"{positionID} instrumentID->{instrumentID}>"
					" is not closed yet. skipping this...")
				continue

			# here opens a selling postion for this trade
			
			logger.info(f"Going to open Selling Trade for: {instrumentTitle}\n")
			sell_trade, sell_trade_res  = etoro_instance.trade(
				ins=instrumentID, IsBuy=False)

			if sell_trade is False:
				detail = (
					f"Couldnot open selling position for: '{instrumentTitle}'"
					f" reason :\n{sell_trade_res}\n")
				logger.warning(detail)
			else:
				detail = (
					f"Opened selling position for: '{instrumentTitle}'"
					f" response :\n{sell_trade_res}\n")
				logger.info(detail)

			logger.info(f"\nGoing to update User Date ...")
			user_data = etoro_instance.get_login_info
			logger.info(f"\nGot User Data :\n{user_data}\n")


			logger.info(f"\nGoing to update User Trade History ...")
			user_trade_history = etoro_instance.get_trade_history
			logger.info(f"\nGot User Trade History :\n{user_trade_history}\n")

		msg = "<sell_trade> finished ..."
		print('+'*len(msg))
		print(msg)
		print('+'*len(msg))
		
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		err_detail = e, fname, exc_tb.tb_lineno
		detail = f"Following Error occured in sell_trade ::\n{err_detail}\n"
		logger.error(detail)

	#write trade logs
	helpers.write_csv("Selling", detail)


if __name__ == '__main__':
	exchange_to_follow = helpers.get_exchange_info(config.Default_Exchange)
	day_of_week_opens = exchange_to_follow['Market Opens'].split()[0].lower().replace("day","")
	day_of_week_closes = exchange_to_follow['Market Closes'].split()[0].lower().replace("day","")
	exchange_closing = datetime.strptime(exchange_to_follow['Market Closes'].split()[1], "%H:%M")
	hour_minute = exchange_closing - timedelta(minutes=config.Exchange_Schedular_Minutes)
	day_of_week = f"{day_of_week_opens}-{day_of_week_closes}"

	logger.info(f"\nScheduler started at: {datetime.now().astimezone(pytz.timezone('UTC'))}\n")
	logger.info(
		f"Trader For <{exchange_to_follow['Exchange']}> scheduled to run at:"
		f"\n[Day Weeks: {day_of_week}]\t[Exchange closing hour: "
		f"{exchange_closing.hour}:{exchange_closing.minute:02d} UTC]\t[Job starts at: "
		f"{hour_minute.hour}:{hour_minute.minute:02d} UTC]\n")

	#graps etoro instance with logged in driver and swticed to virtual/real account
	etoro_instance = get_etoro_instance()

	#scheduler = BlockingScheduler({'apscheduler.timezone': 'Europe/London'})
	scheduler = BlockingScheduler({'apscheduler.timezone': 'UTC'})

	# schedular to buy_trade 
	scheduler.add_job(
		buy_trade, 'cron', args=[etoro_instance], day_of_week=day_of_week,
		minute=hour_minute.minute, hour=hour_minute.hour
	)

	# schedular to sell_trade 
	scheduler.add_job(sell_trade,'interval',args=[etoro_instance],minutes=35)
	
	# scheduler.add_job(buy_trade, 'cron', args=[etoro_instance],
	# 	minute=9, hour=00)
	
	#scheduler to display scheduled jobs
	scheduler.add_job(lambda : scheduler.print_jobs(),'interval',minutes=10)
	scheduler.start()