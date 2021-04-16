"""Proxy Model"""
# standard library
from typing import Optional

# third-party
from pydantic import BaseModel


class ProxyModel(BaseModel):
    """Proxy Model

    Supported for the following runtimeLevel:
    * ApiService
    * Playbook
    * Organization
    * WebhookTriggerService
    * TriggerService
    """

    # the proxy server hostname or ip address
    # supported runtimeLevel: [Organization, Playbook, WebhookTriggerService]
    tc_proxy_host: Optional[str]

    # the proxy server port
    # supported runtimeLevel: [Organization, Playbook, WebhookTriggerService]
    tc_proxy_port: Optional[int]

    # the proxy server username
    # supported runtimeLevel: [Organization, Playbook, WebhookTriggerService]
    tc_proxy_username: Optional[str]

    # the proxy server password
    # supported runtimeLevel: [Organization, Playbook, WebhookTriggerService]
    tc_proxy_password: Optional[str]

    # if True, external API connections should be proxied
    # supported runtimeLevel: [Organization, Playbook, WebhookTriggerService]
    tc_proxy_external: Optional[bool] = False

    # if True, connections to the ThreatConnect API should be proxied
    # supported runtimeLevel: [Organization, Playbook, WebhookTriggerService]
    tc_proxy_tc: Optional[bool] = False
