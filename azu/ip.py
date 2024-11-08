from azure.mgmt.network import NetworkManagementClient
from datetime import datetime, timedelta
from ._base import AzureResourceCleanup

class IPCleanup(AzureResourceCleanup):
    def __init__(self, subscription_id, resource_group=None):
        super().__init__(subscription_id, resource_group)
        self.client = NetworkManagementClient(self.credentials, self.subscription_id)

    def cleanup(self):
        four_hours_ago = datetime.utcnow() - timedelta(hours=4)
        
        try:
            if self.resource_group:
                ips = self.client.public_ip_addresses.list(self.resource_group)
            else:
                ips = self.client.public_ip_addresses.list_all()

            for ip in ips:
                if not ip.ip_configuration and ip.time_created < four_hours_ago:
                    self.log_deletion("unattached IP address", ip.name)
                    self.client.public_ip_addresses.begin_delete(ip.resource_group_name, ip.name)
        except Exception as e:
            print(f"Error cleaning up IP addresses: {str(e)}")
