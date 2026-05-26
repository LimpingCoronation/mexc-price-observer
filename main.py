import asyncio
from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from core.websocket_manager import WebSocketManager
from core.mexc_api import MexcAPI
from core.stat_repository import StatRepository
from schemas.price_scheme import PriceScheme
from settings import SYMBOL, CLICKHOUSE_HOST, CLICKHOUSE_PORT, CLICKHOUSE_PASSWORD, CLICKHOUSE_USER, CLICKHOUSE_DB, logger, SERVER_PORT

manager = WebSocketManager()
mexc_api = MexcAPI()
stat_repo = StatRepository(CLICKHOUSE_USER, CLICKHOUSE_PASSWORD, CLICKHOUSE_DB, CLICKHOUSE_HOST, CLICKHOUSE_PORT, SYMBOL, logger)
base_symbol = SYMBOL


async def observe_market(manager: WebSocketManager, api: MexcAPI):
    while True:
        try:
            data = await api.get_volume_price(base_symbol)
            await manager.notificate(base_symbol, data)
            await stat_repo.insert_stat(data['price'], data['volume'], data['volume_cur'])
            await asyncio.sleep(5)
        except Exception as e:
            logger.info(e)
            await asyncio.sleep(30)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.sleep(10)
    
    logger.info("Init clickhouse table")
    await stat_repo.create_table()
    
    asyncio.create_task(observe_market(manager, mexc_api))
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws/observe")
async def observe_endpoint(websocket: WebSocket):    
    await websocket.accept()
    manager.add_connection(base_symbol, websocket)
    
    while True:
        try:
            await websocket.receive_text()
        except WebSocketDisconnect:
            print("Client disconnected")
        except:
            pass
        finally:
            break


@app.get("/last-prices")
async def get_last_prices() -> list[PriceScheme]:
    query = await stat_repo.get_last_stat(1000)
    return [{'created_at': q[0], 'price': q[1], 'volume': q[2], 'volume_cur': q[3]} for q in query]


@app.get("/prices-window")
async def get_prices_in_window(
    start: datetime,
    end: datetime
) -> list[PriceScheme]:
    query = await stat_repo.get_stat_time_window(start, end)
    return [{'created_at': q[0], 'price': q[1], 'volume': q[2], 'volume_cur': q[3]} for q in query]


@app.get("/prices")
async def get_all_prices() -> list[PriceScheme]:
    query = await stat_repo.get_all_stat()
    return [{'created_at': q[0], 'price': q[1], 'volume': q[2], 'volume_cur': q[3]} for q in query]


@app.get('/')
async def index():
    return RedirectResponse("/static/index.html")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)
