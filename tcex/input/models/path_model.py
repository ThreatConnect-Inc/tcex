"""Path Model"""
# standard library
import tempfile

# third-party
from pydantic import BaseModel


class PathModel(BaseModel):
    """Path Model

    Supported for the following runtimeLevel:
    * ApiService
    * Playbook
    * Organization
    * WebhookTriggerService
    * TriggerService
    """

    #
    # ThreatConnect Provided Inputs
    #

    # the path to the Apps "in" directory
    tc_in_path: str = tempfile.gettempdir() or '/tmp'  # nosec

    # the path to the App "log" directory
    tc_log_path: str = tempfile.gettempdir() or '/tmp'  # nosec

    # the path to the Apps "out" directory
    tc_out_path: str = tempfile.gettempdir() or '/tmp'  # nosec

    # the path to the Apps "tmp" directory
    tc_temp_path: str = tempfile.gettempdir() or '/tmp'  # nosec
