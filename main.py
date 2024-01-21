import os

import ray

from api.serve.base import ServeDeployment
from settings import settings
from utils.logger import logger

# Get the current working directory
current_dir = os.getcwd()

# Get the full path of the current working directory
full_path = os.path.abspath(current_dir)

# Add "/tmp" to the full path
temp_dir = os.path.join(full_path, "tmp")

if not ray.is_initialized():
    logger.info("Ray initialized")
    ray.init(address=settings.RAY_ADDRESS, ignore_reinit_error=True, _temp_dir=temp_dir)

app = ServeDeployment.bind()
