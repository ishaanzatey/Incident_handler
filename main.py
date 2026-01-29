from servicenow_client import ServiceNowClient
from rules_repository import RulesRepository
from config import ASSIGNMENT_GROUP_SYS_ID

def process_incidents():
    sn = ServiceNowClient()
    rules_repo = RulesRepository()

    incidents = sn.fetch_eligible_incidents(ASSIGNMENT_GROUP_SYS_ID)

    if not incidents:
        print("No eligible incidents found")
        return

    for inc in incidents:
        short_desc = inc.get("short_description", "")
        desc = inc.get("description", "")

        rule = rules_repo.find_matching_resolve_rule(short_desc, desc)

        if not rule:
            print(f"Skipped {inc['number']} (no SOP match)")
            continue

        payload = {
            "state": "6",
            "close_code": "Solved (Permanently)",
            "close_notes": rule.get("closure_note"),
            "work_notes": rule.get("work_notes"),
            "u_jira_reference": rule.get("jira_reference"),
            "parent_incident": rule.get("parent_incident"),
            "u_kb_article": rule.get("kb_article")
        }

        # Remove empty fields
        payload = {k: v for k, v in payload.items() if v}

        sn.update_and_resolve_incident(inc["sys_id"], payload)
        print(f"Resolved {inc['number']} using SOP rule")

if __name__ == "__main__":
    process_incidents()
