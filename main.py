from fastapi import FastAPI, Query
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from lib.database import fetch_data
from lib.commonutility import setup_logger
from datetime import datetime

app = FastAPI()
executor = ThreadPoolExecutor(max_workers=5)
logger = setup_logger("log_search_api_main")

@app.get("/logs/")
async def get_logs(
    host: str = Query(..., description="Host name"),
    timestamp: str = Query(..., description="Timestamp in ISO format, e.g., 2025-07-02T12:00:00"),
    log_type: str = Query("top_logs", description="Log type: top | cpu | memory")
):
    logger.info("get_logs() started for host=%s, timestamp=%s, log_type=%s", host, timestamp, log_type)
    try:
        parsed_ts = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        logger.warning("Invalid timestamp format received")
        return {"error": "Invalid timestamp format. Use ISO format: YYYY-MM-DDTHH:MM:SS"}

    if log_type not in ["top", "cpu", "memory"]:
        return {"error": "Invalid log_type. Choose from: top, cpu, memory"}

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, fetch_data, host, parsed_ts, log_type)

    logger.info("get_logs() ended. Returning %d records.", len(result))
    return {"count": len(result), "data": result}