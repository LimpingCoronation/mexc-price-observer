from fastapi import WebSocket, WebSocketDisconnect


class WebSocketManager:
    clients: dict[str, list[WebSocket]] = {}

    async def notificate(self, symbol, data: dict):
        if self.clients.get(symbol) is None:
            return
        
        for client in self.clients[symbol]:
            try:
                await client.send_json(data)
            except WebSocketDisconnect:
                self.clients[symbol].remove(client)
            except:
                pass
                

    def add_connection(self, symbol, connection: WebSocket):
        connections = self.clients.get(symbol)
        if connections is None:
            self.clients[symbol] = [connection]
        else:
            self.clients[symbol].append(connection)
