from azure.identity import DefaultAzureCredential

class AzureResourceCleanup:
    def __init__(self, subscription_id, resource_group=None):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.credentials = DefaultAzureCredential()

    def cleanup(self):
        raise NotImplementedError("Cleanup method must be implemented by subclasses")

    def log_deletion(self, resource_type, resource_name):
        print(f"Deleting {resource_type}: {resource_name}")
