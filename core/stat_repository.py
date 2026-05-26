import logging
from datetime import datetime

import clickhouse_connect


class StatRepository:
    def __init__(self, username, password, database, host, port, table_name, logger: logging.Logger):
        self.username = username
        self.password = password
        self.database = database
        self.host = host
        self.port = port
        self.table_name = "statistic_" + table_name
        self.logger = logger
    
    async def get_client(self):
        return await clickhouse_connect.get_async_client(
            host = self.host,
            username = self.username,
            password = self.password,
            database = self.database,
            port = self.port
        )
    
    async def create_table(self):
        client = await self.get_client()
        await client.query(f"CREATE TABLE IF NOT EXISTS {self.table_name} (created_at DateTime('Europe/Moscow') default now(), price Float64, volume Float64, volume_cur Float64) Engine = MergeTree ORDER BY created_at;")
        await client.close()
    
    async def insert_stat(self, price, volume, volume_cur):
        client = await self.get_client()
        await client.query(f"INSERT INTO {self.table_name} VALUES (now(), {price}, {volume}, {volume_cur})")
        await client.close()
    
    async def get_last_stat(self, limit):
        client = await self.get_client()
        query = await client.query(f"SELECT * FROM {self.table_name} ORDER BY created_at DESC LIMIT {limit}")
        await client.close()
        return query.result_rows
    
    async def get_all_stat(self):
        client = await self.get_client()
        query = await client.query(f"SELECT * FROM {self.table_name} ORDER BY created_at DESC")
        await client.close()
        return query.result_rows
    
    async def get_stat_time_window(self, start: datetime, end: datetime):
        start_str = start.strftime("%Y-%m-%d %H:%M:%S")
        end_str = end.strftime("%Y-%m-%d %H:%M:%S")
        
        client = await self.get_client()
        query = await client.query(f"SELECT * FROM {self.table_name} WHERE created_at BETWEEN '{start_str}' AND '{end_str}' ORDER BY created_at DESC;")
        await client.close()
        return query.result_rows
