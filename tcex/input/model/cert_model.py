"""TcEx Framework Module"""

from pydantic import BaseModel, Field


class CertModel(BaseModel):
    """Input Service Model

    Supported runtimeLevel:
    * ApiService
    * Playbook
    * Organization
    * TriggerService
    * WebhookTriggerService
    """

    # @bcs - for service App these should be required, for any other App type making them
    # required would force a min server version of 7.4
    tc_svc_broker_cacert_file: str | None = Field(
        default=None,
        description='The Broker SSL CA (full chain) certificate.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
    tc_svc_broker_cert_file: str | None = Field(
        default=None,
        description='The Broker SSL Server certificate.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
    tc_svc_broker_jks_file: str | None = Field(
        default='Unused',
        description='Input for Java Apps.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
    tc_svc_broker_jks_pwd: str | None = Field(
        default='Unused',
        description='Input for Java Apps.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
    tc_svc_broker_key_file: str | None = Field(
        default=None,
        description='The Broker SSL Key (full chain) certificate.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
