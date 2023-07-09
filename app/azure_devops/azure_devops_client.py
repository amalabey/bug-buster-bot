import base64
import requests
import os


class AzureDevOpsClient():
    def __init__(self, personal_access_token=None):
        if personal_access_token != None:
            self.personal_access_token = personal_access_token
        else:
            from_env_var = os.getenv("AZURE_DEVOPS_PAT")
            self.personal_access_token = from_env_var

    def send_api_request(self, url, method="GET",
                         data=None, raiseOnErr=True, raw_data=False):
        header_value = f":{self.personal_access_token}"
        header_bytes = header_value.encode('utf-8')
        basic_auth_header_bytes = base64.b64encode(header_bytes)
        basic_auth_header = basic_auth_header_bytes.decode('utf-8')
        headers = {
            "Authorization": f"Basic {basic_auth_header}",
            "Content-Type": "application/json"
        }

        response = requests.request(method, url, headers=headers, data=data)
        if raiseOnErr:
            response.raise_for_status()

        if raw_data:
            return response.text
        else:
            return response.json()
