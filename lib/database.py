from psycopg2.extras import RealDictCursor
import psycopg2
from datetime import datetime, timedelta
from lib.config import config
from commonutility import setup_logger

logger = setup_logger("log_search_api_db")
DB_CONFIG = config["postgres"]

TABLE_MAP = {
    "top": "cpu_top_logs_parsed",
    "cpu": "cpu_top_cpu_logs",
    "memory": "cpu_top_mem_logs"
}

def fetch_data(host: str, target_ts: datetime, log_type: str):
    logger.info(f"fetch_data() started for host={host}, timestamp={target_ts.isoformat()}, log_type={log_type}")

    start_ts = target_ts - timedelta(minutes=5)
    end_ts = target_ts + timedelta(minutes=5)

    if log_type == "top":
        query = """
            SELECT timestamp, command, cpu, mem
            FROM cpu_top_logs_parsed
            WHERE host = %s
            AND timestamp BETWEEN %s AND %s
            ORDER BY timestamp;
        """
    elif log_type == "cpu":
        query = """
            SELECT timestamp, command, cpu
            FROM cpu_top_cpu_logs
            WHERE host = %s
            AND timestamp BETWEEN %s AND %s
            ORDER BY timestamp;
        """
    elif log_type == "memory":
        query = """
            SELECT timestamp, command, mem
            FROM cpu_top_mem_logs
            WHERE host = %s
            AND timestamp BETWEEN %s AND %s
            ORDER BY timestamp;
        """
    else:
        logger.warning(f"Invalid log_type: {log_type}")
        return []
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (host, start_ts, end_ts))
                results = cur.fetchall()
                logger.info(f"fetch_data() ended. Retrieved {len(results)} rows.")
                return results
    except Exception as e:
        logger.error(f"fetch_data() failed: {e}", exc_info=True)
        return []
