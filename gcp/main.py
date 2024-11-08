from .vm import VMCleanup
from .disk import DiskCleanup
from .ip import IPCleanup
from .nic import NICCleanup
from .network import NetworkEndpointGroupCleanup
from .ssh import SSHKeyCleanup
from .auth import get_gcp_credentials

class GCPCleanupOrchestrator:
    def __init__(self, project_id, service_account_key_path=None):
        """
        Initialize the GCP cleanup orchestrator.
        
        Args:
            project_id (str): GCP project ID
            service_account_key_path (str, optional): Path to service account key file
        """
        self.project_id = project_id
        self.credentials = None
        if service_account_key_path:
            self.credentials = get_gcp_credentials(service_account_key_path)

    def run_all_cleanups(self, cleanup_types=None):
        """
        Run all specified cleanup operations.
        
        Args:
            cleanup_types (list, optional): List of cleanup types to run.
                                          If None, runs all cleanups.
        """
        cleanup_map = {
            'vm': VMCleanup,
            'disk': DiskCleanup,
            'ip': IPCleanup,
            'nic': NICCleanup,
            'neg': NetworkEndpointGroupCleanup,
            'ssh': SSHKeyCleanup
        }

        if cleanup_types is None:
            cleanup_types = cleanup_map.keys()

        errors = []
        for cleanup_type in cleanup_types:
            if cleanup_type not in cleanup_map:
                print(f"Warning: Unknown cleanup type '{cleanup_type}'")
                continue

            try:
                cleanup_class = cleanup_map[cleanup_type]
                cleanup_instance = cleanup_class(self.project_id)
                print(f"\nStarting {cleanup_type} cleanup...")
                cleanup_instance.cleanup()
                print(f"Completed {cleanup_type} cleanup")
            except Exception as e:
                error_msg = f"Error during {cleanup_type} cleanup: {str(e)}"
                errors.append(error_msg)
                print(error_msg)

        if errors:
            print("\nThe following errors occurred during cleanup:")
            for error in errors:
                print(f"- {error}")
            return False
        return True

