import psycopg2
import psycopg2.extras
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from config import PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASSWORD
import uuid

class DatabaseManager:
    """Manages database operations for execution logging and history"""
    
    def __init__(self):
        self.conn = None
        self.use_memory = False
        self.memory_logs = []
        self.memory_history = []
        
        try:
            self.conn = psycopg2.connect(
                host=PG_HOST,
                port=PG_PORT,
                dbname=PG_DB,
                user=PG_USER,
                password=PG_PASSWORD
            )
            self.conn.autocommit = True
            self._ensure_tables_exist()
            print("✓ Database connected successfully")
        except Exception as e:
            print(f"⚠️  Database connection failed: {e}")
            print("📝 Using in-memory storage (data will not persist)")
            self.use_memory = True
    
    def _ensure_tables_exist(self):
        """Create tables if they don't exist"""
        with self.conn.cursor() as cur:
            # Execution logs table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS execution_logs (
                    id SERIAL PRIMARY KEY,
                    execution_id UUID NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    event_type VARCHAR(50) NOT NULL,
                    incident_number VARCHAR(50),
                    message TEXT,
                    metadata JSONB
                );
            """)
            
            # Incident processing history table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS incident_processing_history (
                    id SERIAL PRIMARY KEY,
                    incident_number VARCHAR(50) NOT NULL,
                    incident_sys_id VARCHAR(100),
                    short_description TEXT,
                    matched_rule_id INTEGER,
                    action_taken VARCHAR(50),
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) NOT NULL,
                    error_message TEXT
                );
            """)
            
            # Create indexes for better query performance
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_execution_logs_execution_id 
                ON execution_logs(execution_id);
            """)
            
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_execution_logs_timestamp 
                ON execution_logs(timestamp DESC);
            """)
            
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_incident_history_processed_at 
                ON incident_processing_history(processed_at DESC);
            """)
    
    def log_event(self, execution_id: str, event_type: str, 
                  incident_number: Optional[str] = None,
                  message: Optional[str] = None,
                  metadata: Optional[Dict[str, Any]] = None):
        """Log an execution event"""
        if self.use_memory:
            self.memory_logs.append({
                'execution_id': execution_id,
                'event_type': event_type,
                'incident_number': incident_number,
                'message': message,
                'metadata': metadata,
                'timestamp': datetime.now().isoformat()
            })
            return
            
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO execution_logs 
                (execution_id, event_type, incident_number, message, metadata)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                execution_id,
                event_type,
                incident_number,
                message,
                json.dumps(metadata) if metadata else None
            ))
    
    def log_incident_processing(self, incident_number: str, incident_sys_id: str,
                               short_description: str, matched_rule_id: Optional[int],
                               action_taken: str, status: str,
                               error_message: Optional[str] = None):
        """Log incident processing result"""
        if self.use_memory:
            self.memory_history.append({
                'incident_number': incident_number,
                'incident_sys_id': incident_sys_id,
                'short_description': short_description,
                'matched_rule_id': matched_rule_id,
                'action_taken': action_taken,
                'status': status,
                'error_message': error_message,
                'processed_at': datetime.now().isoformat()
            })
            return
            
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO incident_processing_history
                (incident_number, incident_sys_id, short_description, 
                 matched_rule_id, action_taken, status, error_message)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                incident_number,
                incident_sys_id,
                short_description,
                matched_rule_id,
                action_taken,
                status,
                error_message
            ))
    
    def get_recent_executions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent execution logs"""
        if self.use_memory:
            return sorted(self.memory_logs, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]
            
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM execution_logs
                ORDER BY timestamp DESC
                LIMIT %s
            """, (limit,))
            return [dict(row) for row in cur.fetchall()]
    
    def get_processing_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get incident processing history"""
        if self.use_memory:
            return sorted(self.memory_history, key=lambda x: x.get('processed_at', ''), reverse=True)[:limit]
            
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM incident_processing_history
                ORDER BY processed_at DESC
                LIMIT %s
            """, (limit,))
            return [dict(row) for row in cur.fetchall()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        if self.use_memory:
            from datetime import date
            today = date.today().isoformat()
            today_items = [h for h in self.memory_history if h.get('processed_at', '').startswith(today)]
            
            return {
                "today": {
                    "total": len(today_items),
                    "success": len([h for h in today_items if h.get('status') == 'success']),
                    "failed": len([h for h in today_items if h.get('status') == 'failed']),
                    "skipped": len([h for h in today_items if h.get('status') == 'skipped'])
                },
                "all_time": {
                    "total": len(self.memory_history)
                }
            }
            
        with self.conn.cursor() as cur:
            # Total processed today
            cur.execute("""
                SELECT COUNT(*) FROM incident_processing_history
                WHERE DATE(processed_at) = CURRENT_DATE
            """)
            today_total = cur.fetchone()[0]
            
            # Success count today
            cur.execute("""
                SELECT COUNT(*) FROM incident_processing_history
                WHERE DATE(processed_at) = CURRENT_DATE
                AND status = 'success'
            """)
            today_success = cur.fetchone()[0]
            
            # Failed count today
            cur.execute("""
                SELECT COUNT(*) FROM incident_processing_history
                WHERE DATE(processed_at) = CURRENT_DATE
                AND status = 'failed'
            """)
            today_failed = cur.fetchone()[0]
            
            # Skipped count today
            cur.execute("""
                SELECT COUNT(*) FROM incident_processing_history
                WHERE DATE(processed_at) = CURRENT_DATE
                AND status = 'skipped'
            """)
            today_skipped = cur.fetchone()[0]
            
            # All time total
            cur.execute("SELECT COUNT(*) FROM incident_processing_history")
            all_time_total = cur.fetchone()[0]
            
            return {
                "today": {
                    "total": today_total,
                    "success": today_success,
                    "failed": today_failed,
                    "skipped": today_skipped
                },
                "all_time": {
                    "total": all_time_total
                }
            }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
