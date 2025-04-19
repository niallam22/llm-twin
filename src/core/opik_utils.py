import os
import random

from .config import settings  # Corrected import path
from .logger_utils import get_logger

logger = get_logger(__name__)

try:
    import opik
    from opik.configurator.configure import OpikConfigurator
except Exception as e:
    logger.info(f"Could not import Opik and Comet {e}")


def configure_opik() -> None:
    if settings.COMET_API_KEY and settings.COMET_PROJECT:
        if settings.COMET_WORKSPACE:
            default_workspace = settings.COMET_WORKSPACE
        else:
            try:
                client = OpikConfigurator(api_key=settings.COMET_API_KEY)
                default_workspace = client._get_default_workspace()
            except Exception:
                logger.warning("Default workspace not found. Setting workspace to None and enabling interactive mode.")
                default_workspace = None

        os.environ["OPIK_PROJECT_NAME"] = settings.COMET_PROJECT

        opik.configure(
            api_key=settings.COMET_API_KEY,
            workspace=default_workspace,
            use_local=False,
            force=True,
        )
        logger.info("Opik configured successfully.")
    else:
        logger.warning("COMET_API_KEY and COMET_PROJECT are not set. Set them to enable prompt monitoring with Opik (powered by Comet ML).")


# Removed create_dataset_from_artifacts function as it relied on training artifacts


def create_dataset(name: str, description: str, items: list[dict]) -> opik.Dataset:
    client = opik.Opik()

    dataset = client.get_or_create_dataset(name=name, description=description)
    dataset.insert(items)

    dataset = client.get_dataset(name=name)

    return dataset


def add_to_dataset_with_sampling(item: dict, dataset_name: str) -> bool:
    if "1" in random.choices(["0", "1"], weights=[0.3, 0.7]):
        client = opik.Opik()
        dataset = client.get_or_create_dataset(name=dataset_name)
        dataset.insert([item])

        return True

    return False
