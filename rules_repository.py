import psycopg2
from config import PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASSWORD

class RulesRepository:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            dbname=PG_DB,
            user=PG_USER,
            password=PG_PASSWORD
        )

    def find_matching_resolve_rule(self, short_desc, description):
        query = """
            SELECT *
            FROM incident_sop_rules
            WHERE is_active = true
              AND action_type = 'RESOLVE'
              AND %s ILIKE '%%' || short_description_keyword || '%%'
              AND %s ILIKE '%%' || description_keyword || '%%'
            LIMIT 1;
        """

        with self.conn.cursor() as cur:
            cur.execute(query, (short_desc, description))
            row = cur.fetchone()

            if not row:
                return None

            columns = [desc[0] for desc in cur.description]
            return dict(zip(columns, row))
