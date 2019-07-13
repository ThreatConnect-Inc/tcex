# -*- coding: utf-8 -*-
"""TcEx Framework Service module"""
from .service_api import ServiceApi
from .service_trigger import ServiceTrigger
from .service_webhook import ServiceWebhook


class Service(ServiceApi, ServiceTrigger, ServiceWebhook):
    """Combined Service Class"""
