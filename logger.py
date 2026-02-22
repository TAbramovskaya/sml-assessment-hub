import logging
import os
import datetime as dt

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_RETENTION_DAYS = 3


def _cleanup_old_logs(logger):
    cutoff = (dt.datetime.now() - dt.timedelta(days=LOG_RETENTION_DAYS)).date()

    for filename in os.listdir(LOG_DIR):
        if not filename.endswith(".log") or filename == 'validation.log':
            continue
        try:
            date_str = os.path.splitext(filename)[0]
            file_date = dt.datetime.strptime(date_str, "%Y-%m-%d").date()
            if file_date <= cutoff:
                try:
                    os.remove(os.path.join(LOG_DIR, filename))
                    logger.info(f"Removed old log file: {filename}")
                except OSError as e:
                    logger.warning(f"Could not remove log file {filename}:\n{e}")
                    pass
        except ValueError:
            logger.warning(f"Unexpected log file name: {filename}")
            pass


def get_general_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    today = dt.datetime.now().strftime("%Y-%m-%d")
    log_path = os.path.join(LOG_DIR, f"{today}.log")

    file_exists = os.path.isfile(log_path)
    file_handler = logging.FileHandler(log_path, mode='a', encoding="utf-8")

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.propagate = False

    if not file_exists:
        logger.info(f"New log file is created: {os.path.basename(log_path)}")

    _cleanup_old_logs(logger)

    return logger


def get_validation_failures_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    log_path = os.path.join(LOG_DIR, "validation.log")  # always same file
    handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False

    return logger