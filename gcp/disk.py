
from google.cloud import compute_v1
from datetime import datetime, timedelta
from ._base import GCPResourceCleanup

class DiskCleanup(GCPResourceCleanup):
    def cleanup(self):
        client = compute_v1.DisksClient()
        four_hours_ago = datetime.utcnow() - timedelta(hours=4)
        
        for disk in client.list(project=self.project_id):
            if not disk.users and disk.creation_timestamp < four_hours_ago.isoformat():
                print(f"Deleting unattached disk: {disk.name}")
                client.delete(project=self.project_id, zone=disk.zone, disk=disk.name)
