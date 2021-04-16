"""CAL Settings Model"""
# third-party
from pydantic import BaseModel


class CalSettingsModel(BaseModel):
    """CAL Settings Model

    Feature: CALSettings

    Supported for the following runtimeLevel:
    * ApiService
    * Playbook
    * WebhookTriggerService
    * TriggerService
    """

    # the ThreatConnect CAL hostname
    tc_cal_host: str

    # the ThreatConnect CAL API token
    tc_cal_token: str

    # the ThreatConnect CAL API token timestamp
    tc_cal_timestamp: int
