import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        print(f"WebSocket Connect: User={self.user}, ID={self.user.id if hasattr(self.user, 'id') else 'N/A'}, Anon={self.user.is_anonymous}")
        
        if self.user.is_anonymous:
            print("WebSocket Rejected: User is anonymous")
            await self.close()
            return

        tenant_id = await self.get_user_tenant_id(self.user)
        
        if tenant_id:
            self.group_name = f"tenant_{tenant_id}"
            print(f"WebSocket Accepted: User {self.user.id} joining {self.group_name}")
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
        else:
            print(f"WebSocket Rejected: User {self.user.id} has no profile/tenant")
            await self.close()

    @database_sync_to_async
    def get_user_tenant_id(self, user):
        from accounts.models import UserProfile
        try:
            profile = UserProfile.objects.get(user=user)
            return profile.tenant.id
        except UserProfile.DoesNotExist:
            return None
        except Exception as e:
            print(f"Error fetching profile: {e}")
            return None

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def send_notification(self, event):
        message = event['message']
        title = event.get('title', 'Notification')
        # Support both 'level' (preferred) and 'type' (legacy/confusing)
        message_type = event.get('level', event.get('type', 'info'))
        
        await self.send(text_data=json.dumps({
            'title': title,
            'message': message,
            'body': message, # Backwards compatibility
            'type': message_type,
            'level': message_type # Backwards compatibility
        }))
