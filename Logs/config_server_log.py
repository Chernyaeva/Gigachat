import logging
import logging.handlers

# Create formatter:
srv_formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

# Create and setup log handler
file_handler = logging.handlers.TimedRotatingFileHandler('./Logs/server_logs.log', encoding='utf-8', interval=1, when='D')
file_handler.setFormatter(srv_formatter)

# Create and setup logger
logger = logging.getLogger('server')
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

