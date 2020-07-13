# ETORO TRADE CRAWLER
	The site to be scraped is etoro.com  Data to be scraped is stock price, ticker name and date. The data is to be used by the bot to automate a couple of defined actions listed below.

#Task 1:
	The script is supposed to monitor all exchanges in the etoro category of stock exchanges for example NYSE for stocks whose price value increases by 10% using day timeline. If the bot notices another stock which has increased to 10% after the initial position is opened, the bot shall close the initial position and open a new buying position with newly identified stock.

#Task 2:
	The script is supposed to monitor the highest increase stock of the stock exchange in the last 8 minutes of exchange and the bot opens a buying position of that stock(if the value of the stock increases) or opens the selling position of that stock(if the value of the stock decreases)  in the last minute(s) before the exchange closes. The NYSE and NASDAQ takes high priority in this case followed by Hong Kong exchange.

#Task 3:
	The script identifies a bought stock in task 2, monitors it until it is closed. Then it opens a selling position on that same stock.

#Last milestone:
	After rigorous successful testing, the bot shall be uploaded to amazon ec2. And it will be tested on the platform. After successful tests

#Notes:
    1. The bot should be able to login without failure. (Sometimes the persistent cookie of etoro fails and it logs out the user or reject a login) if the login is rejected, the bot should immediately notify the end user of the problem.
    2. The leverage of buying a stock on etoro changes at times. Before it used to be X5, now it is X2. The bot should be able detect and use the highest possible leverage.
    3. Sometimes etoro deactivates the buy and sell button for some stocks. In that case, the bit should ignore the trade and move onto the next approved stock(the stock that meets our defined guidelines)
    4. Sometimes, etoro.com limits the number of shares for a particular stock to be bought. The bot can solve this problem by buying that stock in parts (defined as limited on etoro website). This means that the bot buys stock more than once.
    5. The bot shall take note of the available funds on etoro platform before making trades.
    6. It is preferable that the bot remains in passive mode. That’s to say. That the number of requests to etoro website should be as small as possible or better, it should capture information and process it.
    7. Different stock exchanges have different opening and closing times. Therefore the developer needs to program the bot with this in mind. For example NYSE and NASDAQ stock exchange open between 2pm to 9pm GMT+1. The bot doesn’t need to monitor the above exchanges during any other time apart from the one stated above.
    8. Trailing stop loss shall be used at all times for all tasks with a maximum 3% Stop loss of the trade amount for all tasks.
