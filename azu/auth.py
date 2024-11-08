from azure.identity import ClientSecretCredential

def get_azure_credentials(client_id, client_secret, tenant_id):
    return ClientSecretCredential(client_id=client_id, client_secret=client_secret, tenant_id=tenant_id)
