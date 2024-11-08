import logging
from azure.core.exceptions import AzureError
from .disk import DiskCleanup
from .ip import IPCleanup
from .nic import NICCleanup
from .vm import VMCleanup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_cleanup(subscription_id, resource_group=None):
    """Run all cleanup operations"""
    cleaners = [
        DiskCleanup(subscription_id, resource_group),
        IPCleanup(subscription_id, resource_group),
        NICCleanup(subscription_id, resource_group),
        VMCleanup(subscription_id, resource_group)
    ]

    for cleaner in cleaners:
        try:
            logger.info(f"\nRunning {cleaner.__class__.__name__}...")
            cleaner.cleanup()
        except AzureError as e:
            logger.error(f"Azure error in {cleaner.__class__.__name__}: {str(e)}")
        except Exception as e:
            logger.error(f"Error in {cleaner.__class__.__name__}: {str(e)}")
