from azure.mgmt.network import NetworkManagementClient
from ._base import AzureResourceCleanup

class NICCleanup(AzureResourceCleanup):
    def cleanup(self):
        client = NetworkManagementClient(self.credentials, self.subscription_id)
        
        if self.resource_group:
            nics = client.network_interfaces.list(self.resource_group)
        else:
            nics = client.network_interfaces.list_all()

        for nic in nics:
            if not nic.virtual_machine:
                print(f"Deleting unattached NIC: {nic.name}")
                client.network_interfaces.begin_delete(
                    nic.resource_group_name, nic.name)
