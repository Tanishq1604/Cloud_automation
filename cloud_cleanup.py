
from gcp.disk import DiskCleanup as GCPDiskCleanup
from azu.disk import DiskCleanup as AzureDiskCleanup

def main():
    # Initialize parameters
    gcp_project_id = "your-gcp-project-id"
    azure_subscription_id = "your-azure-subscription-id"
    
    # Run GCP cleanup
    gcp_disk_cleanup = GCPDiskCleanup(gcp_project_id)
    gcp_disk_cleanup.cleanup()
    
    # Run Azure cleanup
    azure_disk_cleanup = AzureDiskCleanup(azure_subscription_id)
    azure_disk_cleanup.cleanup()

if __name__ == "__main__":
    main()
