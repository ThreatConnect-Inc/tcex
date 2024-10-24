"""TcEx Framework Module"""

# third-party
from requests import Session  # TYPE-CHECKING

# first-party
from tcex.api.tc.v2.batch.batch import Batch
from tcex.api.tc.v2.batch.batch_submit import BatchSubmit
from tcex.api.tc.v2.batch.batch_writer import BatchWriter
from tcex.api.tc.v2.datastore.cache import Cache
from tcex.api.tc.v2.datastore.datastore import DataStore
from tcex.api.tc.v2.metric.metric import Metric
from tcex.api.tc.v2.notification.notification import Notification
from tcex.api.tc.v2.threat_intelligence.threat_intelligence import ThreatIntelligence
from tcex.input.input import Input  # TYPE-CHECKING


class V2:
    """API -> TC -> V2

    Args:
        inputs: An instance of the Input class.
        session_tc: An configured instance of request.Session with TC API Auth.
    """

    def __init__(self, inputs: Input, session_tc: Session):
        """Initialize instance properties."""
        self.inputs = inputs
        self.session_tc = session_tc

    def batch(
        self,
        owner: str,
        action: str = 'Create',
        attribute_write_type: str = 'Replace',
        halt_on_error: bool = False,
        playbook_triggers_enabled: bool = False,
        tag_write_type: str = 'Replace',
        security_label_write_type: str = 'Replace',
    ) -> Batch:
        """Return instance of Batch

        Args:
            owner: The ThreatConnect owner for Batch action.
            action: Action for the batch job ['Create', 'Delete'].
            attribute_write_type: Write type for TI attributes ['Append', 'Replace'].
            halt_on_error: If True any batch error will halt the batch job.
            playbook_triggers_enabled: Deprecated input, will not be used.
            security_label_write_type: Write type for labels ['Append', 'Replace'].
            tag_write_type: Write type for tags ['Append', 'Replace'].
        """
        return Batch(
            self.inputs,
            self.session_tc,
            owner,
            action,
            attribute_write_type,
            halt_on_error,
            playbook_triggers_enabled,
            tag_write_type,
            security_label_write_type,
        )

    def batch_submit(
        self,
        owner: str,
        action: str = 'Create',
        attribute_write_type: str = 'Replace',
        halt_on_error: bool = False,
        playbook_triggers_enabled: bool = False,
        tag_write_type: str = 'Replace',
        security_label_write_type: str = 'Replace',
    ) -> BatchSubmit:
        """Return instance of Batch

        Args:
            owner: The ThreatConnect owner for Batch action.
            action: Action for the batch job ['Create', 'Delete'].
            attribute_write_type: Write type for TI attributes ['Append', 'Replace'].
            halt_on_error: If True any batch error will halt the batch job.
            playbook_triggers_enabled: Deprecated input, will not be used.
            security_label_write_type: Write type for labels ['Append', 'Replace'].
            tag_write_type: Write type for tags ['Append', 'Replace'].
        """
        return BatchSubmit(
            self.inputs,
            self.session_tc,
            owner,
            action,
            attribute_write_type,
            halt_on_error,
            playbook_triggers_enabled,
            tag_write_type,
            security_label_write_type,
        )

    def batch_writer(self, output_dir: str, **kwargs) -> BatchWriter:
        """Return instance of Batch

        Args:
            output_dir: Deprecated input, will not be used.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            output_extension (str): Append this extension to output files.
            write_callback (Callable): A callback method to call when a batch json file is
                written. The callback will be passed the fully qualified name of the written file.
            write_callback_kwargs (dict): Additional values to send to callback method.
        """
        return BatchWriter(self.inputs, self.session_tc, output_dir, **kwargs)

    def cache(
        self,
        domain: str,
        data_type: str,
        ttl_seconds: int | None = None,
        mapping: dict | None = None,
    ) -> Cache:
        """Get instance of the Cache module.

        Args:
            domain: The domain can be either "system", "organization", or "local". When using
                "organization" the data store can be accessed by any Application in the entire org,
                while "local" access is restricted to the App writing the data. The "system" option
                should not be used in almost all cases.
            data_type: The data type descriptor (e.g., tc:whois:cache).
            ttl_seconds: The number of seconds the cache is valid.
            mapping: Advanced - The datastore mapping if required.
        """
        return Cache(self.session_tc, domain, data_type, ttl_seconds, mapping)

    def datastore(self, domain: str, data_type: str, mapping: dict | None = None) -> DataStore:
        """Return Datastore Module.

        Args:
            domain: The domain can be either "system", "organization", or "local". When using
                "organization" the data store can be accessed by any Application in the entire org,
                while "local" access is restricted to the App writing the data. The "system" option
                should not be used in almost all cases.
            data_type: The data type descriptor (e.g., tc:whois:cache).
            mapping: ElasticSearch mapping data.
        """
        return DataStore(
            session_tc=self.session_tc, domain=domain, data_type=data_type, mapping=mapping
        )

    def metric(
        self,
        name: str,
        description: str,
        data_type: str,
        interval: str,
        keyed: bool = False,
    ) -> Metric:
        """Get instance of the Metrics module.

        Args:
            name: The name for the metric.
            description: The description of the metric.
            data_type: The type of metric: Sum, Count, Min, Max, First, Last, and Average.
            interval: The metric interval: Hourly, Daily, Weekly, Monthly, and Yearly.
            keyed: Indicates whether the data will have a keyed value.
        """
        return Metric(
            session_tc=self.session_tc,
            name=name,
            description=description,
            data_type=data_type,
            interval=interval,
            keyed=keyed,
        )

    @property
    def notification(self) -> Notification:
        """Get instance of the Notification module."""
        return Notification(self.session_tc)

    @property
    def ti(self) -> ThreatIntelligence:
        """Get instance of the Notification module."""
        return ThreatIntelligence(self.session_tc)
