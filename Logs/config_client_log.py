import logging
import sys

# Create formatter:
cl_formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(filename)s %(message)s')

# Create and setup log handler
file_handler = logging.FileHandler('./Logs/client_logs.log', encoding='utf-8')
file_handler.setFormatter(cl_formatter)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(cl_formatter)
stream_handler.setLevel(logging.ERROR)

# Create and setup logger
logger = logging.getLogger('client')
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)
