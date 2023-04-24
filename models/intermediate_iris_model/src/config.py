import logging
import os
import sys

logging.basicConfig(
    stream=sys.stdout, level=logging.INFO, format="[%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)


RMQ_HOST = os.environ.get("RMQ_HOST", default="localhost")
RMQ_USER = os.environ.get("RMQ_USER", default="guest")
RMQ_PASSWORD = os.environ.get("RMQ_PASSWORD", default="guest")
