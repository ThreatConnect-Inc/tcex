"""TcEx Framework Module"""

# standard library
import logging
import re
from urllib.parse import quote

# third-party
import jmespath
from requests import Session

# first-party
from tcex.exit.error_code import handle_error
from tcex.logger.trace_logger import TraceLogger
from tcex.pleb.cached_property import cached_property

# get tcex logger
_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore


class ThreatIntelUtil:
    """Threat Intelligence Common Methods"""

    INDICATOR = 'Indicator'
    GROUP = 'Group'

    def __init__(self, session_tc: Session):
        """Initialize instance properties."""
        self.session_tc = session_tc

        # properties
        self.log = _logger
        self._ti = None

    @property
    def resolvable_variables(self) -> dict:
        """Return a dict of all the supported resolvable variables.

        Each entry in the dict has the variables corresponding url and jmespath for their values
        if available. Some variables do not have this data since no api endpoint is supported.
        """

        return {
            '${API_USERS}': {'url': '/v3/security/users', 'jmspath': 'data[*].userName'},
            '${ARTIFACT_TYPES}': {'url': '/v3/artifactTypes', 'jmspath': 'data[*].name'},
            '${ATTRIBUTES}': {'url': '/v3/attributeTypes', 'jmspath': 'data[*].name'},
            '${GROUP_TYPES}': None,  # Special Case since there is no api endpoint
            '${INDICATOR_TYPES}': {
                'url': '/v2/types/indicatorTypes',
                'jmspath': 'data.indicatorType[*].name',
            },
            '${OWNERS}': {'url': '/v3/security/owners', 'jmspath': 'data[*].name'},
            '${USER_GROUPS}': {'url': '/v3/security/userGroups', 'jmspath': 'data[*].name'},
            '${USERS}': {'url': '/v3/security/users', 'jmspath': 'data[*].userName'},
            '${WORKFLOW_TEMPLATES}': {
                'url': '/v3/workflowTemplates?tql=active = true',
                'jmspath': 'data[*].name',
            },
        }

    def _association_types(self):
        """Retrieve Custom Indicator Associations types from the ThreatConnect API."""

    @staticmethod
    def expand_indicators(indicator: str) -> list[str]:
        """Process indicators expanding file hashes/custom indicators into multiple entries.

        Args:
            indicator: A " : " delimited string.

        Returns:
            A list of indicators split on " : ".
        """
        if indicator.count(' : ') > 0:
            # handle all multi-valued indicators types (file hashes and custom indicators)
            indicator_list = []

            iregx_pattern = (
                # group 1 - lazy capture everything to first <space>:<space> or end of line
                r'^(.*?(?=\s\:\s|$))?'
                r'(?:\s\:\s)?'  # remove <space>:<space>
                # group 2 - look behind for <space>:<space>, lazy capture everything
                # to look ahead (optional <space>):<space> or end of line
                r'((?<=\s\:\s).*?(?=(?:\s)?\:\s|$))?'
                r'(?:(?:\s)?\:\s)?'  # remove (optional <space>):<space>
                # group 3 - look behind for <space>:<space>, lazy capture everything
                # to look ahead end of line
                r'((?<=\s\:\s).*?(?=$))?$'
            )
            iregx = re.compile(iregx_pattern)

            indicators = iregx.search(indicator)
            if indicators is not None:
                indicator_list = list(indicators.groups())
        else:
            # handle all single valued indicator types (address, host, etc)
            indicator_list = [indicator]

        return indicator_list

    @property
    def group_types(self) -> list[str]:
        """Return all defined ThreatConnect Group types.

        Returns:
            A list of ThreatConnect Group types.
        """
        return list(self.group_types_data.keys())

    @property
    def group_types_data(self) -> dict[str, dict]:
        """Return supported ThreatConnect Group types."""
        return {
            'Adversary': {'apiBranch': 'adversaries', 'apiEntity': 'adversary'},
            'Attack Pattern': {'apiBranch': 'attackPatterns', 'apiEntity': 'attackPattern'},
            'Campaign': {'apiBranch': 'campaigns', 'apiEntity': 'campaign'},
            'Course of Action': {'apiBranch': 'coursesOfAction', 'apiEntity': 'courseOfAction'},
            'Document': {'apiBranch': 'documents', 'apiEntity': 'document'},
            'Email': {'apiBranch': 'emails', 'apiEntity': 'email'},
            'Event': {'apiBranch': 'events', 'apiEntity': 'event'},
            'Incident': {'apiBranch': 'incidents', 'apiEntity': 'incident'},
            'Intrusion Set': {'apiBranch': 'intrusionSets', 'apiEntity': 'intrusionSet'},
            'Malware': {'apiBranch': 'malware', 'apiEntity': 'malware'},
            'Report': {'apiBranch': 'reports', 'apiEntity': 'report'},
            'Signature': {'apiBranch': 'signatures', 'apiEntity': 'signature'},
            'Tactic': {'apiBranch': 'tactics', 'apiEntity': 'tactic'},
            'Task': {'apiBranch': 'tasks', 'apiEntity': 'task'},
            'Threat': {'apiBranch': 'threats', 'apiEntity': 'threat'},
            'Tool': {'apiBranch': 'tools', 'apiEntity': 'tool'},
            'Vulnerability': {'apiBranch': 'vulnerabilities', 'apiEntity': 'vulnerability'},
        }

    def get_type_from_api_entity(self, api_entity: dict) -> str | None:
        """Return the object type as a string given a api entity.

        Args:
            api_entity: A TCEntity object.

        Returns:
            str, None: The type value or None.

        """
        merged = self.group_types_data.copy()
        merged.update(self.indicator_types_data)
        for key, value in merged.items():
            if value.get('apiEntity') == api_entity:
                return key
        return None

    @cached_property
    def indicator_associations_types_data(self) -> dict[str, dict]:
        """Return ThreatConnect associations type data.

        Retrieve the data from the API if it hasn't already been retrieved.

        Returns:
            (dict): A dictionary of ThreatConnect associations types.
        """
        _association_types = {}

        # Dynamically create custom indicator class
        r = self.session_tc.get('/v2/types/associationTypes')

        # check for bad status code and response that is not JSON
        if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
            self.log.warning(
                'feature=threat-intel-common, event=association-types-download, status=failure'
            )
            return _association_types

        # validate successful API results
        data: dict = r.json()
        if data.get('status') != 'Success':
            self.log.warning(
                'feature=threat-intel-common, event=association-types-download, status=failure'
            )
            return _association_types

        # TODO: [low] make an Model for this data and return model?
        try:
            # Association Type Name is not a unique value at this time, but should be.
            association_types = {}
            for association in data.get('data', {}).get('associationType', []):
                association_types[association.get('name')] = association
        except Exception as e:
            handle_error(code=200, message_values=[e])
        return _association_types

    @cached_property
    def indicator_types(self) -> list[str]:
        """Return ThreatConnect Indicator types.

        Retrieve the data from the API if it hasn't already been retrieved.

        Returns:
            (list): A list of ThreatConnect Indicator types.
        """
        return list(self.indicator_types_data.keys())

    def resolve_variables(self, inputs: list[str]) -> list[str]:
        """Resolve all of the provided inputs if appropriate.

        Args:
            inputs: A list of strings to resolve if string matches a entry in the
            "resolved_variables" dict.
        """
        resolved_inputs = []
        for input_ in inputs:
            # handle null inputs
            if not input_:
                resolved_inputs.append(None)
                continue

            # clean up input
            input_ = input_.strip()

            # handle unknown input types
            if input_ not in self.resolvable_variables:
                resolved_inputs.append(input_)
                continue

            # special handling of group types (no API request required)
            if input_ == '${GROUP_TYPES}':
                for type_ in self.group_types:
                    resolved_inputs.append(type_)
                continue

            # get variable settings
            resolvable_variable_details = self.resolvable_variables[input_]

            # make API call to retrieve variable data
            r = self.session_tc.get(
                resolvable_variable_details.get('url'), params={'resultLimit': 10_000}
            )

            if not r.ok:
                raise RuntimeError(f'Could not retrieve {input_} from ThreatConnect API.')

            json_ = r.json()
            for item in jmespath.search(resolvable_variable_details.get('jmspath'), json_):
                resolved_inputs.append(str(item))

        return resolved_inputs

    @cached_property
    def indicator_types_data(self) -> dict[str, dict]:
        """Return ThreatConnect indicator types data.

        Retrieve the data from the API if it hasn't already been retrieved.

        Returns:
            (dict): A dictionary of ThreatConnect Indicator data.
        """
        # retrieve data from API
        r = self.session_tc.get('/v2/types/indicatorTypes')

        # TODO: [low] use handle error instead
        if not r.ok:
            raise RuntimeError('Could not retrieve indicator types from ThreatConnect API.')

        _indicator_types = {}
        for itd in r.json().get('data', {}).get('indicatorType'):
            _indicator_types[itd.get('name')] = itd
        return _indicator_types

    @staticmethod
    def safe_indicator(indicator: str) -> str:
        """Format indicator value for safe HTTP request.

        Args:
            indicator: Indicator to URL Encode

        Returns:
            (str): The urlencoded string
        """
        if indicator is not None:
            indicator = quote(indicator, safe='~')
        return indicator

    @staticmethod
    def safe_rt(resource_type: str, lower: bool = False) -> str:
        """Format the Resource Type.

        Takes Custom Indicator types with a space character and return a *safe* string.

        (e.g. *User Agent* is converted to User_Agent or user_agent.)

        Args:
           resource_type: The resource type to format.
           lower: Return type in all lower case

        Returns:
            (str): The formatted resource type.
        """
        if resource_type is not None:
            resource_type = resource_type.replace(' ', '_')
            if lower:
                resource_type = resource_type.lower()
        return resource_type

    @staticmethod
    def safe_group_name(group_name: str, group_max_length: int = 100, ellipsis: bool = True) -> str:
        """Truncate group name to match limit breaking on space and optionally add an ellipsis.

        .. note:: Currently the ThreatConnect group name limit is 100 characters.

        Args:
           group_name: The raw group name to be truncated.
           group_max_length: The max length of the group name.
           ellipsis: If true the truncated name will have '...' appended.

        Returns:
            (str): The truncated group name with optional ellipsis.
        """
        ellipsis_value = ''
        if ellipsis:
            ellipsis_value = ' ...'

        if group_name is not None and len(group_name) > group_max_length:
            # split name by spaces and reset group_name
            group_name_array = group_name.split(' ')
            group_name = ''
            for word in group_name_array:
                word = f'{word}'
                if (len(group_name) + len(word) + len(ellipsis_value)) >= group_max_length:
                    group_name = f'{group_name}{ellipsis_value}'
                    group_name = group_name.lstrip(' ')
                    break
                group_name += f' {word}'
        return group_name

    @staticmethod
    def safe_tag(tag: str) -> str:
        """Encode and truncate tag to match limit (128 characters) of ThreatConnect API.

        Args:
           tag: The tag to be truncated

        Returns:
            (str): The truncated and quoted tag.
        """
        if tag is not None:
            tag = quote(tag[:128], safe='~')
        return tag

    @staticmethod
    def safe_url(url: str) -> str:
        """Encode value for safe HTTP request.

        Args:
            url (str): The string to URL Encode.

        Returns:
            (str): The urlencoded string.
        """
        if url is not None:
            url = quote(url, safe='~')
        return url

    @property
    def victim_asset_types(self) -> list:
        """Return all defined ThreatConnect Asset types.

        Returns:
            (list): A list of ThreatConnect Asset types.
        """
        return [
            'EmailAddress',
            'SocialNetwork',
            'NetworkAccount',
            'WebSite',
            'Phone',
        ]

    def validate_intel_types(self, types_list: list[str], restrict_to: str | None = None):
        """Validate that Types contained in types_list are valid Intel Types.

        :param types_list: list of types to validate. An exception is raised if a member of this
        list is not a valid intel type.

        :param restrict_to: If None, types_list will be validated to contain valid Indicator
        or Group types. If not None, this value must be set to self.INDICATOR or self.GROUP,
        and types_list will be validated to contain only Indicators or Groups depending on this
        value.
        """

        if restrict_to is not None and restrict_to not in [self.INDICATOR, self.GROUP]:
            raise ValueError(f'restrict_to must be {self.INDICATOR} or {self.GROUP}')

        if not isinstance(types_list, list):
            raise TypeError('types_list must be a a list.')

        if restrict_to:
            valid_types = self.group_types if restrict_to == self.GROUP else self.indicator_types
        else:
            valid_types = self.indicator_types + self.group_types

        if any(_type not in valid_types for _type in types_list):
            raise ValueError(f'Type list "{types_list}" contains invalid Intel Type.')
