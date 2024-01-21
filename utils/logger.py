import json
import logging

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, json.dumps({"message": record.getMessage()})
        )


logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)


ray_logger = logging.getLogger("ray")
ray_serve_logger = logging.getLogger("ray.serve")

ray_logger.setLevel(logging.WARNING)
ray_serve_logger.setLevel(logging.WARNING)
ray_logger.addHandler(InterceptHandler())
ray_serve_logger.addHandler(InterceptHandler())
