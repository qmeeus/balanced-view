import logzero
import os


os.makedirs('outputs', exist_ok=True)
log_file = 'outputs/logs.txt'
logger = logzero.logger
logzero.loglevel('DEBUG')
logzero.logfile(log_file, maxBytes=1e6, backupCount=3)
