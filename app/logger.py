import logging

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s]: %(message)s')
ch.setFormatter(formatter)

bili_logger = logging.getLogger('Bili')
for handler in bili_logger.handlers:
    bili_logger.removeHandler(handler)
bili_logger.setLevel(logging.INFO)
bili_logger.addHandler(ch)
