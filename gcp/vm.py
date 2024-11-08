from google.cloud import compute_v1
from ._base import GCPResourceCleanup
from .utils import is_resource_old_enough

class VMCleanup(GCPResourceCleanup):
    def cleanup(self):
        client = compute_v1.InstancesClient()
        
        for zone in self._get_zones():
            instances = client.list(project=self.project_id, zone=zone)
            for instance in instances:
                if instance.status == 'STOPPED' and is_resource_old_enough(instance.creation_timestamp):
                    print(f"Deleting stopped instance: {instance.name}")
                    client.delete(project=self.project_id, zone=zone, instance=instance.name)
    
    def _get_zones(self):
        client = compute_v1.ZonesClient()
        zones = client.list(project=self.project_id)
        return [zone.name for zone in zones]
