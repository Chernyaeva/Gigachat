import logging
import logging.handlers
import sys

# Create formatter:
srv_formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

# Create and setup log handler
file_handler = logging.handlers.TimedRotatingFileHandler('./Logs/server_logs.log', encoding='utf-8', interval=1, when='D')
file_handler.setFormatter(srv_formatter)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(srv_formatter)
stream_handler.setLevel(logging.ERROR)

# Create and setup logger
logger = logging.getLogger('server')
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)

