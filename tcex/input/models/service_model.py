"""Service Model"""
# standard library
from typing import Optional

# third-party
from pydantic import BaseModel


class ServiceModel(BaseModel):
    """Input Service Model

    Supported runtimeLevel:
    * ApiService
    * WebhookTriggerService
    * TriggerService
    """

    #
    # ThreatConnect Provided Inputs
    #

    # the Broker SSL CA (full chain) certificate
    tc_svc_broker_cacert_file: str

    # the Broker SSL Server certificate
    tc_svc_broker_cert_file: str

    # the Broker service hostname.
    tc_svc_broker_host: str

    # this is for Java Apps
    tc_svc_broker_jks_file: Optional[str] = 'Unused'

    # this is for Java Apps
    tc_svc_broker_jks_pwd: Optional[str] = 'Unused'

    # the Broker service port
    tc_svc_broker_port: int

    # the Broker auth token
    tc_svc_broker_token: str
    # TODO: [med] switch ot use of SecretStr
    # tc_svc_broker_token: Optional[SecretStr]

    # the Broker client topic (messages to core)
    tc_svc_client_topic: str

    # the heartbeat interval in seconds
    tc_svc_hb_timeout_seconds: int = 20

    # the Broker server topic (messages to App)
    tc_svc_server_topic: str

    #
    # TcEx Specific
    #

    # the broker connection timeout
    tc_svc_broker_conn_timeout: int = 60

    # the broker server, either mqtt (default) or redis (deprecated)
    tc_svc_broker_service: Optional[str] = 'mqtt'

    # the broker service timeout in seconds
    tc_svc_broker_timeout: int = 60

    # the unique service id
    tc_svc_id: int

    # the testing framework context
    tcex_testing_context: Optional[str]
