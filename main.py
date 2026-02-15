from servicenow_client import ServiceNowClient
from rules_repository import RulesRepository
from config import ASSIGNMENT_GROUP_SYS_ID
from event_emitter import emitter
from database_manager import DatabaseManager
import uuid
import asyncio

def process_incidents():
    """Process incidents with real-time event broadcasting and logging"""
    execution_id = str(uuid.uuid4())
    db_manager = DatabaseManager()
    
    sn = ServiceNowClient()
    rules_repo = RulesRepository()

    incidents = sn.fetch_eligible_incidents(ASSIGNMENT_GROUP_SYS_ID)

    if not incidents:
        print("No eligible incidents found")
        db_manager.log_event(execution_id, "execution_completed", 
                            message="No eligible incidents found")
        return

    # Broadcast execution started
    emitter.emit_sync("execution_started", {"total_incidents": len(incidents)})
    db_manager.log_event(execution_id, "execution_started", 
                        message=f"Processing {len(incidents)} incidents")
    
    stats = {"success": 0, "failed": 0, "skipped": 0}

    for inc in incidents:
        incident_number = inc.get("number", "UNKNOWN")
        short_desc = inc.get("short_description", "")
        desc = inc.get("description", "")
        sys_id = inc.get("sys_id", "")

        # Broadcast processing started
        emitter.emit_sync("incident_processing", {
            "incident_number": incident_number,
            "short_description": short_desc
        })
        db_manager.log_event(execution_id, "incident_processing", 
                            incident_number=incident_number,
                            message=f"Processing incident {incident_number}")

        rule = rules_repo.find_matching_resolve_rule(short_desc, desc)

        if not rule:
            print(f"Skipped {incident_number} (no SOP match)")
            stats["skipped"] += 1
            
            # Broadcast skipped
            emitter.emit_sync("incident_skipped", {
                "incident_number": incident_number,
                "reason": "No SOP match found"
            })
            
            db_manager.log_incident_processing(
                incident_number, sys_id, short_desc, None, 
                "skipped", "skipped", "No SOP match found"
            )
            continue

        # Broadcast rule matched
        emitter.emit_sync("rule_matched", {
            "incident_number": incident_number,
            "rule": {
                "id": rule.get("id"),
                "closure_note": rule.get("closure_note"),
                "work_notes": rule.get("work_notes")
            }
        })

        try:
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

            sn.update_and_resolve_incident(sys_id, payload)
            print(f"Resolved {incident_number} using SOP rule")
            stats["success"] += 1
            
            # Broadcast resolved
            emitter.emit_sync("incident_resolved", {
                "incident_number": incident_number,
                "rule_id": str(rule.get("id"))
            })
            
            db_manager.log_incident_processing(
                incident_number, sys_id, short_desc, rule.get("id"),
                "resolved", "success"
            )
            
        except Exception as e:
            error_msg = str(e)
            print(f"Failed to resolve {incident_number}: {error_msg}")
            stats["failed"] += 1
            
            # Broadcast error
            emitter.emit_sync("error_occurred", {
                "incident_number": incident_number,
                "error": error_msg
            })
            
            db_manager.log_incident_processing(
                incident_number, sys_id, short_desc, rule.get("id"),
                "failed", "failed", error_msg
            )
    
    # Broadcast execution completed
    emitter.emit_sync("execution_completed", {"stats": stats})
    db_manager.log_event(execution_id, "execution_completed",
                        message=f"Completed: {stats}")
    db_manager.close()

if __name__ == "__main__":
    process_incidents()
