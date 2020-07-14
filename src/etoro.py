#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,json, re
import socket, http.client
import functools
from datetime import datetime
from time import sleep
from random import randint
from selenium.common.exceptions import TimeoutException, NoSuchWindowException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.remote.command import Command
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire import webdriver
from seleniumrequests import Firefox, Chrome
from selenium.webdriver.common.action_chains import ActionChains
from crawler_logging import logger
import logging
import config
import helpers

seleniumwire_logger = logging.getLogger('seleniumwire')
seleniumwire_logger.setLevel(logging.DEBUG)  # Run selenium wire at ERROR level

class Etoro():
	def __init__(self):
		self.driver_options = config.DRIVER_OPTIONS
		self.__buildDriver__(driver_options=self.driver_options)
		self.actions = ActionChains(self.driver)
		
		self.allRequestCount = 0 #count of all requests made to site
		self.resetDriverRequestCount = 0 #count of all requests since last driver was reset
		self.resetDriverAfter = 20 # requests threshold number to reset driver if resetDriverRequestCount reached
		self.resetDriverCount = 0 # number of times driver is reset on threshold reach

		self.primary_window_handle = self.driver.window_handles[0] if len(self.driver.window_handles) > 0 else None

		self.MAX_RETRIES = config.retries

	
	def __buildDriver__(self, driver_options):


		# Ubuntu
		if (os.name == 'posix'):
			chromedriver = 'chromedriver'

		# Windows
		if (os.name == 'nt'):
			chromedriver = 'chromedriver.exe'

		if chromedriver:

			if config.DRIVER_NAME == 'Chrome':
				logger.info("Using Chrome Driver ...")
				options = webdriver.ChromeOptions()
				options.add_experimental_option("excludeSwitches", ["enable-automation"])
				options.add_experimental_option('useAutomationExtension', False)
				options.add_experimental_option('w3c', False)

				for driver_option in driver_options:
					# if "--proxy-server" in driver_option:
					# 	print(f"\nADDING PROXY: [{driver_option}]\n")
					options.add_argument(driver_option)
				
				capabilities = None
				if config.PROXY:
					# print(f"\nADDING PROXY: [{config.PROXY}]\n")
					# prox = Proxy()
					# prox.proxy_type = ProxyType.MANUAL
					# prox.http_proxy = config.PROXY
					# # prox.socks_proxy = config.PROXY
					# prox.ssl_proxy = config.PROXY

					capabilities = webdriver.DesiredCapabilities.CHROME
					capabilities['loggingPrefs'] = { 'performance':'ALL' }
					# prox.add_to_capabilities(capabilities)
				
				if capabilities:
					self.driver =  webdriver.Chrome(desired_capabilities=capabilities, options=options)
					# self.driver = config.DRIVER_NAME(desired_capabilities=capabilities, options=options)
				else:
					self.driver =  webdriver.Chrome(chromedriver, options=options)
					# self.driver =  config.DRIVER_NAME(chromedriver, options=options)

			else:
				logger.info("Using Firefox Driver ...")
				self.driver =  webdriver.Firefox()


		self.min_wait = WebDriverWait(self.driver, 5)
		self.max_wait = WebDriverWait(self.driver, 20)
		self.els_css = self.driver.find_elements_by_css_selector
		self.el_css = self.driver.find_element_by_css_selector
		self.els_xpath = self.driver.find_elements_by_xpath
		self.el_xpath = self.driver.find_element_by_xpath
		self.driver.set_script_timeout(30)
		return self.driver


	def __del__(self):
		try:
			self.driver.close()
			self.driver.quit()
		except:
			pass


	def download_page(self):
		with open(config.page_source_file, "w") as f:
			f.write(self.driver.page_source)

	@property
	def deleteDriver(self):
		self.driver.close()
		self.driver.quit()


	def reset_driver(self):
		self.driver.delete_all_cookies()
		print(f"\n ... cookies reset ...\n")
		self.resetDriverRequestCount = 0
		self.resetDriverCount +=1
		self.deleteDriver
		print(f"\n ... driver reset ...\n")
		self.__buildDriver__(driver_options=self.driver_options)


	def openUrl(self, url, close_secondary_tabs=True, title_display=""):
		title_display = f"[{title_display}] Requesting URL => " if title_display else "Request-URL => " 

		url_msg = f"{title_display} {url}\n"
		print('+'*len(url_msg))
		print(url_msg)
		print('+'*len(url_msg))

		self.switchToMainTab(close_secondary_tabs)
		opened = False
		retries = 1

		while(url and opened is False and retries < self.MAX_RETRIES):

			try:
				self.driver.get(url)
				self.delay()
				self.close_popup()


				if config.Portfolio_Url in self.driver.current_url:
					opened = self.wait_and_get_elems(
						"[data-etoro-automation-id='title']") != []
				elif config.TradeHistory_Url in self.driver.current_url:
					opened = self.wait_and_get_elems(
						"div[class='table-first-name ng-binding']") != []
				elif "https://www.etoro.com/markets/" in self.driver.current_url:
					opened = self.wait_and_get_elems(
						'[automation-id="market-header-nickname"]') != []
				else:
					opened = self.wait_and_get_elems("a.i-logo") != []
			
				# if not any( 1 for i in ['/sapi/', '/api/', '/login'] if i in self.driver.current_url):
				# 	opened = self.wait_and_get_elems(".ng-hide") != []
				# 	self.close_popup()
				# else:
				# 	opened =True

				if opened:
					self.allRequestCount += 1
					url_msg = f"\nRequest-Count -> {self.allRequestCount}\n"
					print('+'*len(url_msg))
					print(url_msg)
					print('+'*len(url_msg))
				else:
					raise Exception(f" Error: Cannot open url")
			except Exception as e:
				retries +=1
				print(f'Error Opening URL :: {e}, Autoretry:{retries}/{self.MAX_RETRIES}')
				
		return opened


	def switchToMainTab(self, close_secondary_tabs=True):
		if close_secondary_tabs: self.closeSecondaryTabs()
		if len(self.driver.window_handles)>=1:
			self.driver.switch_to.window(self.driver.window_handles[0])
		else:
			raise NoSuchWindowException("Cannot switch to Main Tab: target window already closed.")


	def closeSecondaryTabs(self):
		for window in self.driver.window_handles:
			if window != self.primary_window_handle:	
				self.driver.switch_to.window(window)
				self.driver.close()


	def openUrlNewTab(self, url, close_secondary_tabs=True, title_display=""):
		self.switchToMainTab(close_secondary_tabs)
		self.driver.execute_script("window.open()")
		if len(self.driver.window_handles)>1 :
			self.driver.switch_to.window(self.driver.window_handles[-1])
			return self.openUrl(url, title_display=title_display)
		else:
			raise NoSuchWindowException("Cannot switch to New Tab: target window already closed.")



	def doRequest(self, url, method="GET", data={}, json_response=True):
		method = method or "GET"
		request_args = {}
		if data:
			request_args['data'] = data
		# if self.REQUEST_HEADERS:
		# 	request_args['headers'] = self.REQUEST_HEADERS

		url_msg = f"{method}-Request-URL -> {url}"
		print('+'*len(url_msg))
		print(url_msg)
		print('+'*len(url_msg))

		# if getattr(self, "DELETE_COOKIE_BEFORE_EVERY_REQUEST", False):
		# 	self.driver.delete_all_cookies()

		response = self.driver.request(method, url, **request_args)
		if not response.raise_for_status():
			return response.json() if json_response else response


	def delay(self):
		_delay = randint(4, 8)
		print("{} seconds delay ...\n".format(_delay))
		sleep(_delay)


	def wait_and_get_elems(self, css_selector, try_except=True,
						   autoattempts=3, max_timeout=8):

		def _get_elems():
			return WebDriverWait(self.driver, max_timeout).until(
				EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector))
			)

		if not try_except:
			return _get_elems()
		else:
			while 1:
				for t in range(autoattempts):
					try:
						while 1:
							for i in range(autoattempts):
								elems = _get_elems()
								if functools.reduce(lambda x, y: x or y, [elem.is_enabled() for elem in elems]):
									return elems
								else:
									print('{} enabled: {}'.format(css_selector, elems[0].is_enabled()))
									print('Autoretry during {} seconds'.format(max_timeout / 2))
									sleep(max_timeout)
									continue
							print('{0} not enabled'.format(css_selector))
							print('Elems not found. Return False')
							s = 'Q'  # hard coded Quit
							if re.findall('(?i)[QqЙй]', s):
								return []
							continue
					except:
						print("Problem with getting {0}. Element doesn't exist".format(css_selector))
						print('Autoretry during {0} seconds'.format(max_timeout / 2))
						sleep(max_timeout)
						continue
				print("Problem with getting {0}. Element doesn't exist".format(css_selector))
				s = 'Q'  # hard coded Quit
				print('Elems not found')
				if re.findall('(?i)[Qq]', s):
					return []
				continue

	def get_json_response(self, url, tag_name):
		self.driver.get(url)
		res_elems = self.driver.find_elements_by_tag_name(tag_name)
		res = res_elems[0].text if res_elems else ""
		if res:
			return json.loads(res)


	def get_status_of_driver(self):
		try:
			self.driver.execute(Command.STATUS)
			return "Alive"
		except (socket.error, http.client.CannotSendRequest):
			return "Dead"


	def get_loggedin_username(self):
		try:
			return (
				self.wait_and_get_elems(config.loggedin_profile_elem)[0].get_attribute("href").split("/")[-1]
			)
		except Exception as e:
			return False



	def do_login_request(self):
		if config.URL not in self.driver.current_url:
			self.openUrl(config.URL, title_display="Attempting Login <Etoro>")
		logger.info("Please wait Logging in ...")
		
		# self.wait_and_get_elems(config.user_elem)
		
		# self.wait_and_get_elems(config.password_elem)[0].send_keys(config.PASSWORD)
		# sleep(1)
		# self.wait_and_get_elems(config.submit_elem)[0].click()
		# sleep(2)

		# Login screen elements
		username_el = self.wait_and_get_elems(config.user_elem)

		if not username_el:
			if config.URL in self.driver.current_url:
				if self.has_server_error:
					raise Exception(self.has_server_error)
				else:
					raise Exception("Could not access site.")
			elif self.already_loggedin:
				return True
			else:
				raise Exception("Unknown error or access failed.")

		username_el = username_el[0]
		password_el = self.wait_and_get_elems(config.password_elem)[0]
		remember_me_el = self.wait_and_get_elems(config.remember_me_elem)[0]
		login_button_el = self.wait_and_get_elems(config.submit_elem)[0]
		

		# Perform the actions
		username_el.send_keys(config.USER)
		sleep(config.WAIT_BETWEEN_USER_ACTIONS)
		password_el.send_keys(config.PASSWORD)
		sleep(config.WAIT_BETWEEN_USER_ACTIONS)
		self.actions.move_to_element(remember_me_el).click().perform()
		sleep(config.WAIT_BETWEEN_USER_ACTIONS)
		self.actions.move_to_element(login_button_el).click().perform()
		sleep(config.WAIT_BETWEEN_USER_ACTIONS)



	@property
	def has_server_error(self):
		error512 = bool( 
			self.els_css(config.login_fail_512_elem) and
			self.el_css(config.login_fail_512_elem).text == config.login_fail_msg
		)
		error5xx = self.els_css("p") and "Error code:" in self.els_css("p")[0].text

		if error512:
			return config.login_fail_msg
		elif error5xx:
			return self.els_css("p")[0].text
		else:
			return False


	def site_not_reachable(self, css_selector=None):
		if css_selector:
			return self.els_css(css_selector) == []
		else:
			return self.els_css(config.user_elem) == []



	@property
	def already_loggedin(self):
		try:
			return WebDriverWait(self.driver, 15).until(
					EC.presence_of_all_elements_located((By.CSS_SELECTOR, config.loggedin_profile_elem))
				)
		except:
			return False


	def login(self):
		try:

			self.openUrl(config.URL, title_display="<Etoro>")

			if self.already_loggedin:
				logger.info(
					f'Already Logged as User:"{config.USER}".'
				)
				return True

			logger.info(
				f'Attempting Login as User:"{config.USER}".'
			)
			driver_status = self.get_status_of_driver()

			if driver_status is "Dead":
				logger.error("Cannot Login ([Error:: '<Driver Not Alive>'")
				return False
			# logger.info('Driver getting url: {}'.format(config.URL))
			
			self.do_login_request()

			login_status = self.get_loggedin_username()
			
			if  login_status:
				logger.info("Login Successful: '{}'".format(
					login_status)
				)
				return True
			else:
				return False		
		except Exception as e:
			logger.error("Cannot Login ([Error:: '<{}>'])".format(str(e)))
			return False


	def close_popup(self):
		if self.els_css('a[automation-id="close-dialog-btn"]'):
			self.actions.move_to_element(
				self.el_css('a[automation-id="close-dialog-btn"]')).click().perform()

		if self.els_css('a[class="pre-push-popup-button sprite close"]'):
			self.actions.move_to_element(
				self.el_css('a[class="pre-push-popup-button sprite close"]')).click().perform()

			

	@property
	def toggle_account_switcher(self):
		self.actions.move_to_element(
			self.el_css('et-select[automation-id="menu-layout-link-mode"]')).click().perform()
		


	@property
	def current_account_type(self):
		return self.el_css('et-select-header div').text


	def switch_account(self, to_demo=True):

		if to_demo and self.current_account_type == 'VIRTUAL':
			logger.info("Already on <VIRTUAL Account>")
			return True
		elif to_demo is False and self.current_account_type == 'REAL':
			logger.info("Already on <REAL Account>")
			return True

		if to_demo:
			self.close_popup()
			self.toggle_account_switcher

			if self.els_css('et-select-body-option'):
				self.actions.move_to_element(
					self.els_css('et-select-body-option')[-1]).click().perform()
				self.actions.move_to_element(
					self.els_css('.toggle-account-button')[0]).click().perform()

			logger.info("Switched to <VIRTUAL Account>")

		else:
			self.close_popup()
			self.toggle_account_switcher
			
			if self.els_css('et-select-body-option'):
				self.actions.move_to_element(
					self.els_css('et-select-body-option')[0]).click().perform()
				self.actions.move_to_element(
					self.els_css('.toggle-account-button')[0]).click().perform()

			logger.info("Switched to <REAL Account>")

		return True



	@property
	def get_login_info(self) -> dict:

		self.openUrl(
			config.Portfolio_Url,
			title_display="Portfolio View"
		)
		self.delay()

		login_info_list = [json.loads(r.response.body) 
			for r in self.driver.requests if config.Logindata_Url in r.path
		]

		if login_info_list == [] and not \
			self.has_server_error and not \
			self.site_not_reachable(css_selector="[data-etoro-automation-id='title']"
		):
			return self.get_login_info

		login_info_data = login_info_list[-1] if len(login_info_list)>0 else {}
		helpers.set_login_data(login_info_data)
		return login_info_data


	@property
	def get_trade_history(self) -> dict:
	
		self.openUrl(
			config.TradeHistory_Url,
			title_display="Trade History View"
		)
		self.delay()

		trade_history_list = [json.loads(r.response.body) 
			for r in self.driver.requests if config.TradeHistoryApi_Url in r.path
		]

		if trade_history_list == [] and not \
			self.has_server_error and not \
			self.site_not_reachable(css_selector="[data-etoro-automation-id='title']"
		):
			return self.get_trade_history


		helpers.set_data(
				trade_history_list[-1], config.closed_trade_history_file
			)
		return trade_history_list[-1]

	# @property
	# def get_closing_prices(self):
	# 	closing_prices_list = [r for r in self.driver.requests
	# 		if config.Closingprices_Url in r.path
	# 	]
	# 	for closing_prices_r in closing_prices_list:
	# 		closing_prices_file = os.path.join(
	# 			config.closing_prices_dir,
	# 			f'{closing_prices_r.response.headers["Date"]}.json'
	# 		)
	# 		helpers.set_data(
	# 			json.loads(closing_prices_r.response.body), closing_prices_file
	# 		)


	# @property
	# def get_today_prices(self):
	# 	self.driver.get(url=config.Todayprices_Url.format(helpers.device_id()))
	# 	today_prices_list = [r for r in self.driver.requests
	# 		if "https://www.etoro.com/sapi/candles/quickcharts.json/today" in r.path
	# 		and "&instruments=" not in r.path
	# 	]
	# 	for today_prices_r in today_prices_list:
	# 		today_prices_file = os.path.join(
	# 			config.today_prices_dir,
	# 			f'{today_prices_r.response.headers["Date"]}.json'
	# 		)
	# 		helpers.set_data(json.loads(today_prices_r.response.body), today_prices_file)                                                          

	@property
	def is_on_rate_view(self):
		self.els_css(
			"a[data-etoro-automation-id='execution-stop-loss-rate-editing-switch-to-amount-button']"
		) != []

	@property
	def is_on_amount_view(self):
		self.els_css(
			"a[data-etoro-automation-id='execution-stop-loss-amount-editing-switch-to-rate-button']"
		) != []


	def trade(self, ins, IsBuy=True):

		if helpers.is_digit(ins):
			InstrumentData = helpers.find_instrument_by_id(ins)
		else:
			InstrumentData = helpers.find_instrument_by_symbol(ins)

		if not InstrumentData:
			raise Exception(f"no Instrument found by: '{ins}'")

		Instrument = InstrumentData['SymbolFull']
		url = config.Market_Url.format(Instrument.lower().strip())
		res = ""

		if url not in self.driver.current_url:
			self.openUrl(url, title_display=f"Going to Trade <{Instrument}> IsBuy <{IsBuy}>")

		self.actions.move_to_element(
			self.wait_and_get_elems('div[automation-id="trade-button"]')[0]).click().perform()

		if self.wait_and_get_elems(
			'a[href="https://www.etoro.com/trading/market-hours-and-events/"]')[0].text == 'MARKET CLOSED':
			res = f"[MARKET CLOSED] Trade Cannot Be Opened for <{Instrument}> IsBuy:{IsBuy}"
			logger.warning(res)
			return False , res

		if IsBuy:
			self.actions.move_to_element(
				self.wait_and_get_elems('button[ng-class="{active: model.isBuy }"]')[0]
			).click().perform()
		else:
			#sell
			self.actions.move_to_element(
				self.wait_and_get_elems('button[ng-class="{active: !model.isBuy }"]')[0]
			).click().perform()

		#select leverage:
		self.wait_and_get_elems(
			'div[data-etoro-automation-id="execution-leverage-tab-title-value"]')[0].click()
		leverages = self.wait_and_get_elems('a[ng-repeat="leverage in model.displayLeverages"]')
		self.actions.move_to_element(leverages[-1]).click().perform() # select max leverage value

		if config.Trailing_Stop_Loss:
			self.actions.move_to_element(self.el_css(
				"div[data-etoro-automation-id='execution-stop-loss-tab-title-label']"
			)).click().perform()

			self.actions.move_to_element(self.el_css(
				"input[data-etoro-automation-id='execution-stop-loss-editing-tsl-check-box']"
			)).click().perform()

			if self.is_on_rate_view:
				#switch to amount view 
				self.actions.move_to_element(self.wait_and_get_elems(
					"a[data-etoro-automation-id='execution-stop-loss-amount-editing-switch-to-rate-button']"
				)[0]).click().perform()

			stoploss_input = self.els_css("input[data-etoro-automation-id='input']")[-1]
			stoploss_input.clear()

			amount_input = self.els_css("input[data-etoro-automation-id='input']")[0]
			amount_input_val = float(
				amount_input.get_attribute("value").replace("$","").replace(",",""))

			if config.Max_Stop_Loss:
				stoploss_input.send_keys('999999'+Keys.RETURN ) #this will validate and selects max SL
			else:
				stoploss_input.send_keys(f'-{amount_input_val*float(config.Stop_Loss)}'+Keys.RETURN )
			

		#click trade button
		self.actions.move_to_element(
			self.wait_and_get_elems(
				'button[data-etoro-automation-id="execution-open-position-button"]'
		)[0]).click().perform()

		res = f"Trade Opened for <{Instrument}> IsBuy:{IsBuy} at {datetime.now()}"
		logger.info(res)
		

		#getting login info to check trade successfull ?
		openedTrade = helpers.isOrderOpened(InstrumentData["InstrumentID"], self.get_login_info, True)

		#save last trade done
		helpers.addLastOrderedTrade(openedTrade)

		return bool(openedTrade!={}), res
		
		

	# def order(self, session, InstrumentID, ClientViewRate, IsBuy=True, IsTslEnabled=False, Leverage=1, Amount=25):
	# 	logger.info('Order is opened. Instrument: {}. IsBuy: {}'.format(InstrumentID, IsBuy))
	# 	url = 'https://www.etoro.com/sapi/trade-{account_type}/positions?client_request_id={}'.format(
	# 		helpers.device_id(), account_type='demo' if config.AccountType=="VIRTUAL" else 'real')
	# 	stop_loss = (ClientViewRate * 1.4) if not IsBuy else (ClientViewRate * 0.6)
	# 	take_profit = (ClientViewRate * 1.4) if IsBuy else (ClientViewRate * 0.6)
	# 	# headers = helpers.get_cache('headers')
	# 	payload = {
	# 		'Amount': Amount,
	# 		'ClientViewRate': ClientViewRate,
	# 		'InstrumentID': InstrumentID,
	# 		'IsBuy': IsBuy,
	# 		'IsTslEnabled': IsTslEnabled,
	# 		'Leverage': Leverage,
	# 		'StopLossRate': stop_loss,
	# 		'TakeProfitRate': take_profit,
	# 	}

	# 	request_args = {"data": json.dumps(payload) }
	# 	request_args['data'] = data

	# 	response = self.driver.request("POST", url, json.dumps(payload))

	# 	resp = self.doRequest(url, method="POST", data=json.dumps(payload), json_response=True)
	# 	# self.doRequest(url, data=json.dumps(payload), headers=headers) as response:
	# 		# resp = await response.json()
	# 	return resp
		

	# def procharts_search(self, keyword):
		
	# 	if config.Procharts_Url not in self.driver.current_url:
	# 		self.openUrl(
	# 			config.Procharts_Url,
	# 			title_display="Procharts View"
	# 		)
	# 	logger.info(f"procharts_search by: '{keyword}'")
		
	# 	self.wait_and_get_elems(config.search_elem)
	# 	self.wait_and_get_elems(config.search_elem)[0].clear()
	# 	self.wait_and_get_elems(config.search_elem)[0].send_keys(keyword)



	# 	self.wait_and_get_elems(config.password_elem)[0].send_keys(config.PASSWORD)
	# 	sleep(1)
	# 	self.wait_and_get_elems(config.submit_elem)[0].click()
	# 	sleep(2)

	def Get_Stocks_Closing_Price(self):
		
		if config.Stocks_Url not in self.driver.current_url:
			self.openUrl(
				config.Stocks_Url,
				title_display="Stocks View"
			)

		for request in self.driver.requests:
			if request.response and  config.Closingprices_Api in request.path \
				and request.response.status_code == 200:
					resp = request.response.body
					resp_json = json.loads(resp)
					print(resp_json)