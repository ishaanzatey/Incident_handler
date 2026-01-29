import requests
from requests.auth import HTTPBasicAuth
from config import SN_url, SN_username, SN_password

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

class ServiceNowClient:
    def __init__(self):
        self.auth = HTTPBasicAuth(SN_username, SN_password)
        self.incident_url = f"{SN_url}/api/now/table/incident"

    def fetch_eligible_incidents(self, assignment_group_sys_id):
        params = {
            "sysparm_query": (
                f"assignment_group={assignment_group_sys_id}"
                "^assigned_toISEMPTY"
                "^stateNOT IN3,4,6,7"
            ),
            "sysparm_fields": (
                "sys_id,number,short_description,description,state"
            ),
            "sysparm_limit": 100
        }

        response = requests.get(
            self.incident_url,
            headers=HEADERS,
            params=params,
            auth=self.auth,
            timeout=30
        )
        response.raise_for_status()
        return response.json().get("result", [])

    def update_and_resolve_incident(self, sys_id, payload):
        url = f"{self.incident_url}/{sys_id}"
        response = requests.patch(
            url,
            headers=HEADERS,
            json=payload,
            auth=self.auth,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
