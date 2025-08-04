from fastapi import APIRouter, Query
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
from lib.database import fetch_data
from commonutility import setup_logger
from datetime import datetime

logger = setup_logger("api")
router = APIRouter()
executor = ThreadPoolExecutor(max_workers=5)

@router.get("/logs/")
async def get_logs(
    host: str = Query(..., description="Host name"),
    timestamp: str = Query(..., description="ISO format: YYYY-MM-DDTHH:MM:SS"),
    log_type: str = Query("top_logs", description="Log type: top | cpu | memory")
):
    try:
        parsed_ts = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        logger.warning("Invalid timestamp format received.")
        return {"error": "Invalid timestamp format. Use ISO format: YYYY-MM-DDTHH:MM:SS"}

    if log_type not in ["top", "cpu", "memory"]:
        return {"error": "Invalid log_type. Choose from: top, cpu, memory"}

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, fetch_data, host, parsed_ts, log_type)
    return {"count": len(result), "data": result}
