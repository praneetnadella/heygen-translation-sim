import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Logger")
        
def serverLog(message):
    logger.info(f"SERVER: {message}")

def serverError(message):
    logger.error(f"SERVER: {message}")

def clientLog(message, clientId):
    logger.info(f"CLIENT {clientId}: {message}")

def clientError(message, clientId):
    logger.error(f"CLIENT {clientId}: {message}")