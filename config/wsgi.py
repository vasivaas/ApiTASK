"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import socketio
import eventlet
from django.core.wsgi import get_wsgi_application

from users.views import sio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
application = socketio.WSGIApp(sio, application)

eventlet.wsgi.server(eventlet.listen(('', 8000)), application)
