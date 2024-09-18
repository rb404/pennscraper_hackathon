from azure.storage.blob import BlobServiceClient
import json
with open('.secrets', 'r') as f:
    parameters = json.load(f)

service = BlobServiceClient(account_url=parameters['ACCOUNT_URL'], credential=parameters['SAS_TOKEN'])
blob = service.get_blob_client(container="doc-store", blob="ryans_file")

with open("./ryans_file.txt", "rb") as data:
   blob.upload_blob(data)


print("hello world")