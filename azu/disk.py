from azure.mgmt.compute import ComputeManagementClient
from datetime import datetime, timedelta
from ._base import AzureResourceCleanup

class DiskCleanup(AzureResourceCleanup):
    def __init__(self, subscription_id, resource_group=None):
        super().__init__(subscription_id, resource_group)
        self.client = ComputeManagementClient(self.credentials, self.subscription_id)

    def cleanup(self):
        four_hours_ago = datetime.utcnow() - timedelta(hours=4)
        
        try:
            if self.resource_group:
                disks = self.client.disks.list_by_resource_group(self.resource_group)
            else:
                disks = self.client.disks.list()

            for disk in disks:
                if not disk.managed_by and disk.time_created < four_hours_ago:
                    self.log_deletion("unattached disk", disk.name)
                    self.client.disks.begin_delete(disk.resource_group_name, disk.name)
        except Exception as e:
            print(f"Error cleaning up disks: {str(e)}")
