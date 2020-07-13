import logging
import config

logger = logging.getLogger(__name__)
if config.DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)


handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(module)s: %(lineno)d - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# root_dir = os.path.dirname(os.path.abspath(__file__))
# log_file = os.path.join(root_dir, 'crawler.log')
# logging.basicConfig(level=logging.INFO)
# handler = logging.FileHandler(log_file)
# formatter = logging.Formatter('[%(asctime)s - %(name)s] - %(message)s')
# handler.setFormatter(formatter)
# logger = logging.getLogger(__name__)
# logger.addHandler(handler)