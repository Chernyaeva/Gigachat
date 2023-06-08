import logging

# Create formatter:
cl_formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

# Create and setup log handler
file_handler = logging.FileHandler('./Logs/client_logs.log', encoding='utf-8')
file_handler.setFormatter(cl_formatter)

# Create and setup logger
logger = logging.getLogger('client')
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

