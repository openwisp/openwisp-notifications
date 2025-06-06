import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from openwisp_notifications.websockets.routing import get_routes

if os.environ.get("SAMPLE_APP", False):
    # Load custom routes:
    # This should be done when you are extending the app and modifying
    # the web socket consumer in your extended app.
    from .sample_notifications import consumers

    routes = get_routes(consumers)

else:
    # Load openwisp_notifications consumers:
    # This can be used when you are extending the app but not making
    # any changes in the web socket consumer.
    routes = get_routes()


application = ProtocolTypeRouter(
    {
        "websocket": (AuthMiddlewareStack(URLRouter(routes))),
        "http": get_asgi_application(),
    }
)
