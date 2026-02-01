import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()


class PaperTradingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close(code=4001)
            return

        self.user_id = self.scope["user"].id
        self.group_name = f"paper_trading_{self.user_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def portfolio_update(self, event):
        await self.send(
            text_data=json.dumps({"type": "portfolio_update", "data": event["data"]})
        )

    async def order_update(self, event):
        await self.send(
            text_data=json.dumps({"type": "order_update", "data": event["data"]})
        )

    async def position_update(self, event):
        await self.send(
            text_data=json.dumps({"type": "position_update", "data": event["data"]})
        )
