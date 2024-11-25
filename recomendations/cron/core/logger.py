import logging

from core.config import settings

logging.basicConfig(level=logging.INFO,
                    filename=settings.cron_logfile,
                    filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")

logger = logging.getLogger('cron_log')
handler = logging.FileHandler(f"{settings.cron_logfile}", mode="a")
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

handler.setFormatter(formatter)

logger.addHandler(handler)

