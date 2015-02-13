from template import Template
from core.concurrent import Future
from qt_app import QtApp
try:
    from web_app import WebApp
except ImportError:
    pass
