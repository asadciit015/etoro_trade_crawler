# from apscheduler.schedulers.blocking import BlockingScheduler
# from crawler_logging import logger
# from datetime import datetime, timezone, timedelta
# import config, helpers , json
# import pytz, time

# exchange_to_follow = helpers.get_exchange_info(config.Default_Exchange)
# day_of_week_opens = exchange_to_follow['Market Opens'].split()[0].lower().replace("day","")
# day_of_week_closes = exchange_to_follow['Market Closes'].split()[0].lower().replace("day","")
# exchange_closing = datetime.strptime(exchange_to_follow['Market Closes'].split()[1], "%H:%M")
# hour_minute = exchange_closing - timedelta(minutes=config.Exchange_Schedular_Minutes)
# day_of_week = f"{day_of_week_opens}-{day_of_week_closes}"

# logger.info(f"\nScheduler started at: {datetime.now().astimezone(pytz.timezone('UTC'))}\n")
# logger.info(
# 	f"Trader For <{exchange_to_follow['Exchange']}> scheduled to run at:"
# 	f"\n[Day Weeks: {day_of_week}]\t[Exchange closing hour: "
# 	f"{exchange_closing.hour}:{exchange_closing.minute:02d} UTC]\t[Job starts at: "
# 	f"{hour_minute.hour}:{hour_minute.minute:02d} UTC]\n")

# #scheduler = BlockingScheduler({'apscheduler.timezone': 'Europe/London'})
# scheduler = BlockingScheduler({'apscheduler.timezone': 'UTC'})

# def trade_job():
#     logger.info(f'trade job ran ...')


# def countdown(t):
#     while t:
#         mins, secs = divmod(t, 60)
#         timeformat = '{:02d}:{:02d}'.format(mins, secs)
#         print(timeformat, end='\r')
#         time.sleep(1)
#         t -= 1


# scheduler.add_job(
# 	trade_job, 'cron', day_of_week=day_of_week,
# 	minute=hour_minute.minute, hour=hour_minute.hour
# )
# # scheduler.add_job(countdown,'interval', args=[10], seconds=1)
# scheduler.add_job(lambda : scheduler.print_jobs(),'interval',seconds=10)
# scheduler.start()

# # countdown(60)