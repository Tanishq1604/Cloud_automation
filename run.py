import os
from dotenv import load_dotenv
import logging

try:
    from azu.main import run_cleanup as azure_cleanup
    from gcp.main import GCPCleanupOrchestrator
except ImportError as e:
    logging.error(f"Failed to import cleanup modules: {e}")
    raise

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def run_azure_cleanup():
    subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
    resource_group = os.getenv('AZURE_RESOURCE_GROUP')
    
    if not subscription_id:
        raise ValueError("AZURE_SUBSCRIPTION_ID environment variable is required")
    
    logger.info("Starting Azure cleanup...")
    azure_cleanup(subscription_id, resource_group)
    logger.info("Azure cleanup completed")

def run_gcp_cleanup():
    project_id = os.getenv('GCP_PROJECT_ID')
    service_account_key_path = os.getenv('GCP_SERVICE_ACCOUNT_KEY_PATH')
    cleanup_types = os.getenv('GCP_CLEANUP_TYPES')
    
    if not project_id:
        raise ValueError("GCP_PROJECT_ID environment variable is required")
    
    logger.info("Starting GCP cleanup...")
    orchestrator = GCPCleanupOrchestrator(project_id, service_account_key_path)
    
    # Parse cleanup types if specified
    cleanup_list = None
    if cleanup_types:
        cleanup_list = [t.strip() for t in cleanup_types.split(',')]
        logger.info(f"Running specific cleanup types: {cleanup_list}")
    
    success = orchestrator.run_all_cleanups(cleanup_types=cleanup_list)
    
    if success:
        logger.info("GCP cleanup completed successfully")
    else:
        logger.warning("GCP cleanup completed with some errors")

def main():
    # Load environment variables
    load_dotenv()
    
    # Get cloud provider selection from environment
    cloud_providers = os.getenv('CLOUD_PROVIDERS', 'all').lower()
    
    try:
        if cloud_providers in ['all', 'azure']:
            run_azure_cleanup()
            
        if cloud_providers in ['all', 'gcp']:
            run_gcp_cleanup()
            
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise

if __name__ == "__main__":
    main()
