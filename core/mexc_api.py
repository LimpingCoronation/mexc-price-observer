import aiohttp


class MexcAPI:
    BASE_API = "https://api.mexc.com"
    
    async def get_volume_price(self, symbol):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE_API + f"/api/v3/ticker/24hr?symbol={symbol}") as response:
                data = await response.json()
                return {
                    "price": data['lastPrice'],
                    "volume": data['quoteVolume'],
                    "volume_cur": data['volume'],
                }
