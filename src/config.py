# from seleniumrequests import Firefox, Chrome
import os, random
root_dir  = os.path.dirname(os.path.abspath(__file__))

# temp directory configurations
temp_dir = os.path.join(root_dir, 'temp')
if os.path.exists(temp_dir)==False:	os.mkdir(temp_dir)

page_source_file = os.path.join(temp_dir, 'page_source.html')
logindata_file = os.path.join(temp_dir, 'logindata.json')
closed_trade_history_file = os.path.join(temp_dir, 'closed_trade_history.json')
last_trade_done_file = os.path.join(temp_dir, 'last_trades_done.json')

# closing_prices directory configurations
closing_prices_dir = os.path.join(temp_dir, 'closing_prices')
if os.path.exists(closing_prices_dir)==False:	os.mkdir(closing_prices_dir)

# today_prices directory configurations
today_prices_dir = os.path.join(temp_dir, 'today_prices')
if os.path.exists(today_prices_dir)==False:	os.mkdir(today_prices_dir)




# default directory configurations
default_dir = os.path.join(root_dir, 'default')
if os.path.exists(default_dir)==False:	os.mkdir(default_dir)

instruments_file = os.path.join(default_dir, 'instruments.json')
markethourscsv_file = os.path.join(default_dir, 'market-hours-and-events.csv')


DRIVER_NAME = 'Chrome'


DRIVER_OPTIONS = [
	# '--disable-gpu',
	# '--always-authorize-plugins',
	'--user-data-dir=./ChromeProfile',
	# '--remote-debugging-port=5000',
	'--profile-directory=Etoro',
	# '--disable-geolocation',
	# '--disable-notifications',
	# '--disable-plugins-discovery',
	'--start-maximized',
	# '--disable-session-crashed-bubble',                
	# '--disable-save-password-bubble',
	# '--disable-permissions-bubbles',
	# '--bwsi',
	# '--incognito',
	# '--disable-extensions',
	# '--useAutomationExtension=false',
	# '--disable-infobars'
	# '--disable-dev-shm-usage',
	# '--headless',
	# '--no-sandbox'
]

# add proxy here:
PROXY = True

#Logging Level
DEBUG = False

# DRIVER_OPTIONS.append(f'--proxy-server={PROXY}')


#Retry Attempts:
retries = 3

# Seconds between any user action
WAIT_BETWEEN_USER_ACTIONS = 0.5


#Account Type
AccountType = "REAL"
AccountType = "VIRTUAL"
ApiAccountType = 'demo' if AccountType=="VIRTUAL" else 'real'

#Default Exchange to Follow:
Default_Exchange = "Hong Kong Stock Exchange"

#Schedular Start Before Followed Exchange Closes (in minutes):
Exchange_Schedular_Minutes = 10

# Market Stocks Prices Sorting in Analyzer
stocks_sort_by = "MaxIncrease"
# stocks_sort_by = "MeanIncrease"
analyze_open_markets_only = True

# Stop_Loss Configurations
Stop_Loss = 25 #(in percentage)
Max_Stop_Loss = True #if set to true above Stop_Loss percentage will be neglected
Trailing_Stop_Loss = True


#Site Credentials
USER       		  	= "assadnadeem"
PASSWORD    		= "bUKcF9tG==L&x+G"

#Base Url
URL 			  	= "https://www.etoro.com/login"
Watchlist_url		= "https://www.etoro.com/watchlists"
Procharts_Url 	  	= "https://www.etoro.com/app/procharts"
Stocks_Url		  	= "https://www.etoro.com/discover/markets/stocks/exchange/nyse?sort=-change"
Closingprices_Api 	= "https://api.etorostatic.com/sapi/candles/closingprices.json"
Market_Url 			= "https://www.etoro.com/markets/{}"
Logindata_Url 		= "https://www.etoro.com/api/logininfo/v1.1/logindata"
Closingprices_Url   = "https://api.etorostatic.com/sapi/candles/closingprices.json?cv="
Todayprices_Url 	= "https://www.etoro.com/sapi/candles/quickcharts.json/today/22?client_request_id={}"
Portfolio_Url 	    = "https://www.etoro.com/portfolio"
TradeHistory_Url 	= "https://www.etoro.com/portfolio/history"
TradeHistoryApi_Url = f"https://www.etoro.com/sapi/trade-data-{ApiAccountType}/history/private/credit/flat?"
#css selectors
user_elem 			= '#username'
password_elem 		= '#password'
remember_me_elem    = '#login-remember-me label'
submit_elem 		= 'button[automation-id="login-sts-btn-sign-in"]'

loggedin_profile_elem = 'a[class="i-menu-user-username pointer"]'
search_elem			  = 'input[placeholder="Markets / People search"]'

login_fail_512_elem   = "div[automation-id='login-sts-error-password-or-username']"
login_fail_msg 		  = "An error has occurred, please try again"

# users_tab_elem 		= 'h3[role="tab"]'
# all_users_elems       = '.wijmo-checkbox-relative'
# user_selected_elem    = '#userlistselected'
