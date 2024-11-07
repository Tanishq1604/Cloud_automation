from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError
import logging
from datetime import datetime, timezone

class NICManager:
    def __init__(self, subscription_id):
        self.credential = DefaultAzureCredential()
        self.network_client = NetworkManagementClient(self.credential, subscription_id)
        self.compute_client = ComputeManagementClient(self.credential, subscription_id)
        self.logger = logging.getLogger(__name__)

    def create_nic(self, resource_group, nic_name, location, subnet_id):
        """Create a new network interface"""
        try:
            poller = self.network_client.network_interfaces.begin_create_or_update(
                resource_group,
                nic_name,
                {
                    "location": location,
                    "ip_configurations": [{
                        "name": f"{nic_name}-ipconfig",
                        "subnet": {
                            "id": subnet_id
                        }
                    }]
                }
            )
            nic = poller.result()
            self.logger.info(f"Created NIC: {nic.name}")
            return nic
        except Exception as e:
            self.logger.error(f"Error creating NIC: {str(e)}")
            raise

    def delete_nic(self, resource_group, nic_name):
        """Delete a network interface"""
        try:
            poller = self.network_client.network_interfaces.begin_delete(
                resource_group,
                nic_name
            )
            result = poller.result()
            self.logger.info(f"Deleted NIC: {nic_name}")
            return result
        except ResourceNotFoundError:
            self.logger.warning(f"NIC {nic_name} not found")
            return None
        except Exception as e:
            self.logger.error(f"Error deleting NIC: {str(e)}")
            raise

    def list_nics(self, resource_group):
        """List all network interfaces in a resource group"""
        try:
            nics = self.network_client.network_interfaces.list(resource_group)
            nic_list = []
            for nic in nics:
                nic_list.append({
                    'name': nic.name,
                    'id': nic.id,
                    'location': nic.location,
                    'provisioning_state': nic.provisioning_state
                })
            return nic_list
        except Exception as e:
            self.logger.error(f"Error listing NICs: {str(e)}")
            raise

    def get_nic(self, resource_group, nic_name):
        """Get details of a specific network interface"""
        try:
            nic = self.network_client.network_interfaces.get(
                resource_group,
                nic_name
            )
            return nic
        except ResourceNotFoundError:
            self.logger.warning(f"NIC {nic_name} not found")
            return None
        except Exception as e:
            self.logger.error(f"Error getting NIC details: {str(e)}")
            raise

    def is_nic_attached(self, nic):
        """Check if NIC is attached to any VM"""
        return nic.virtual_machine is not None

    def get_unattached_nics(self, resource_group):
        """Find all unattached NICs in a resource group"""
        try:
            nics = self.network_client.network_interfaces.list(resource_group)
            unattached_nics = []
            
            for nic in nics:
                if not self.is_nic_attached(nic):
                    unattached_nics.append({
                        'name': nic.name,
                        'id': nic.id,
                        'location': nic.location,
                        'resource_group': resource_group,
                        'created_time': nic.time_created.strftime('%Y-%m-%d %H:%M:%S') if nic.time_created else 'Unknown'
                    })
            
            return unattached_nics
        except Exception as e:
            self.logger.error(f"Error finding unattached NICs: {str(e)}")
            raise

    def cleanup_unattached_nics(self, resource_group, age_days=30, dry_run=True):
        """Delete unattached NICs older than specified days"""
        try:
            unattached_nics = self.get_unattached_nics(resource_group)
            deleted_nics = []
            current_time = datetime.now(timezone.utc)

            for nic in unattached_nics:
                if nic['created_time'] != 'Unknown':
                    created_time = datetime.strptime(nic['created_time'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
                    age = (current_time - created_time).days

                    if age >= age_days:
                        if not dry_run:
                            self.delete_nic(resource_group, nic['name'])
                            self.logger.info(f"Deleted unattached NIC: {nic['name']}, Age: {age} days")
                        else:
                            self.logger.info(f"Would delete unattached NIC: {nic['name']}, Age: {age} days (dry run)")
                        deleted_nics.append(nic)

            return deleted_nics
        except Exception as e:
            self.logger.error(f"Error cleaning up unattached NICs: {str(e)}")
            raise

if __name__ == "__main__":
    # Example usage
    subscription_id = "your-subscription-id"
    resource_group = "your-resource-group"
    nic_manager = NICManager(subscription_id)
    
    # List NICs
    nics = nic_manager.list_nics(resource_group)
    for nic in nics:
        print(f"NIC: {nic['name']}")
    
    # Find and cleanup unattached NICs
    unattached = nic_manager.get_unattached_nics(resource_group)
    print(f"Found {len(unattached)} unattached NICs")
    
    # Cleanup NICs older than 30 days (dry run)
    cleaned = nic_manager.cleanup_unattached_nics(resource_group, age_days=30, dry_run=True)
    print(f"Identified {len(cleaned)} NICs for cleanup")
