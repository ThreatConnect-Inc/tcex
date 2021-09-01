"""Case Management Collection Abstract Base Class"""
# standard library
import logging
from abc import ABC
from typing import TYPE_CHECKING, Optional, Union

from requests.exceptions import ProxyError

from tcex.case_management.tql import TQL

# third-party
from requests import Response
from tcex.utils import Utils
from tcex.pleb import Event


if TYPE_CHECKING:
    # first-party
    from tcex.case_management.artifact import Artifact
    from tcex.case_management.case import Case
    from tcex.case_management.case_management import CaseManagement
    from tcex.case_management.note import Note
    from tcex.case_management.tag import Tag
    from tcex.case_management.task import Task
    from tcex.case_management.workflow_event import WorkflowEvent

    # Case Management Types
    CaseManagementType = Union[
        Artifact,
        Case,
        Note,
        Tag,
        Task,
        WorkflowEvent,
    ]

# get tcex logger
logger = logging.getLogger('tcex')


class SecurityCollectionABC(ABC):
    """Case Management Collection Abstract Base Class

    This class is a base class for Case Management collections that use
    multi-inheritance with a pydantic BaseModel class. To ensure
    properties are not added to the model both @property and @setter
    methods are used.
    """

    def __init__(
        self,
        session,
        tql_filters: Optional[list] = None,  # This will be removed!
        params: Optional[dict] = None,
    ) -> None:
        """Initialize class properties."""
        self._params = params or {}
        self._tql_filters = tql_filters or []

        # properties
        self._session = session
        self.log = logger
        self.tql = TQL()
        self._utils = Utils()
        self._event = Event()
        self._model = None

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, data):
        self._model = type(self.model)(**data)

    def __len__(self) -> int:
        """Return the length of the collection."""
        parameters = self._params
        parameters['result_limit'] = 1
        tql_string = self.tql.raw_tql
        if not self.tql.raw_tql:
            tql_string = self.tql.as_str
        if tql_string:
            parameters['tql'] = tql_string

        # convert all keys to camel case
        for k, v in list(parameters.items()):
            k = self._utils.snake_to_camel(k)
            parameters[k] = v

        r = self._session.get(self._api_endpoint, params=parameters)
        return r.json().get('count')
    # def __str__(self) -> str:
    #     """Object iterator"""
    #     printable_string = ''
    #     for obj in self.iterate(initial_response=self.initial_response):
    #         printable_string += f'{"-" * 50}\n'
    #         printable_string += str(obj)
    #     return printable_string

    # @property
    # def _filter_map_method(self) -> str:
    #     """Return a property for keyword mapping."""
    #     method_data = (
    #         f'\n{" " * 4}@property\n'
    #         f'\n{" " * 4}def keyword_map(self):\n'
    #         f'{" " * 8}"""Return keyword to method name map."""\n\n'
    #         f'{" " * 8}return {{\n'
    #     )
    #     for t in sorted(self.tql_data, key=lambda i: i['keyword']):
    #         method_data += f"""{" " * 12}'{t.get('keyword')}': '{t.get('keyword')}',\n"""
    #     method_data += f'{" " * 8}}}\n'

    #     return method_data

    # @property
    # def _filter_class(self) -> str:
    #     """Return a Filter Class for current object."""
    #     filter_class = (
    #         f'\nclass Filter{self.__class__.__name__}(Filter):\n'
    #         f'{" " * 4}"""Filter Object for {self.__class__.__name__}"""\n'
    #     )

    #     for t in sorted(self.tql_data, key=lambda i: i['keyword']):
    #         class_name = self.tcex.utils.camel_to_space(self.__class__.__name__).title()
    #         description = t.get('description')
    #         keyword = t.get('keyword')
    #         keyword_snake = self.tcex.utils.camel_to_snake(keyword)

    #         # get the arg type
    #         keyword_type = 'str'
    #         tql_type = 'TQL.Type.STRING'
    #         if t.get('type') in ['Integer', 'Long']:
    #             keyword_type = 'int'
    #             tql_type = 'TQL.Type.INTEGER'
    #         elif t.get('type') == 'Boolean':
    #             keyword_type = 'bool'
    #             tql_type = 'TQL.Type.BOOLEAN'

    #         comment = ''
    #         if keyword_snake in ['id', 'type']:
    #             comment = '  # pylint: disable=redefined-builtin'

    #         if keyword_snake == 'has_artifact':
    #             filter_class += (
    #                 f'\n{" " * 4}@property\n'
    #                 f'{" " * 4}def has_artifact(self) -> FilterArtifacts:\n'
    #                 f'{" " * 8}"""Return **FilterArtifacts** for further filtering."""\n'
    #                 f'{" " * 8}from .artifact import FilterArtifacts\n\n'
    #                 f'{" " * 8}artifacts = FilterArtifacts'
    #                 f'(ApiEndpoints.ARTIFACTS, self._tcex, TQL())\n'
    #                 f"""{" " * 8}self._tql.add_filter('hasArtifact', """
    #                 f'TQL.Operator.EQ, artifacts, TQL.Type.SUB_QUERY)\n'
    #                 f'{" " * 8}return artifacts\n'
    #             )
    #         elif keyword_snake == 'has_case':
    #             filter_class += (
    #                 f'\n{" " * 4}@property\n'
    #                 f'{" " * 4}def has_case(self) -> FilterCases:\n'
    #                 f'{" " * 8}"""Return **FilterCases** for further filtering."""\n'
    #                 f'{" " * 8}from .case import FilterCases  # pylint: disable=cyclic-import\n\n'
    #                 f'{" " * 8}cases = FilterCases(ApiEndpoints.CASES, self._tcex, TQL())\n'
    #                 f"""{" " * 8}self._tql.add_filter('hasCase', """
    #                 f'TQL.Operator.EQ, cases, TQL.Type.SUB_QUERY)\n'
    #                 f'{" " * 8}return cases\n'
    #             )
    #         elif keyword_snake == 'has_note':
    #             filter_class += (
    #                 f'\n{" " * 4}@property\n'
    #                 f'{" " * 4}def has_note(self) -> FilterNotes:\n'
    #                 f'{" " * 8}"""Return **FilterNotes** for further filtering."""\n'
    #                 f'{" " * 8}from .note import FilterNotes\n\n'
    #                 f'{" " * 8}notes = FilterNotes(ApiEndpoints.NOTES, self._tcex, TQL())\n'
    #                 f"""{" " * 8}self._tql.add_filter('hasNote', """
    #                 f'TQL.Operator.EQ, notes, TQL.Type.SUB_QUERY)\n'
    #                 f'{" " * 8}return notes\n'
    #             )
    #         elif keyword_snake == 'has_tag':
    #             filter_class += (
    #                 f'\n{" " * 4}@property\n'
    #                 f'{" " * 4}def has_tag(self) -> FilterTags:\n'
    #                 f'{" " * 8}"""Return **FilterTags** for further filtering."""\n'
    #                 f'{" " * 8}from .tag import FilterTags\n\n'
    #                 f'{" " * 8}tags = FilterTags(ApiEndpoints.TAGS, self._tcex, TQL())\n'
    #                 f"""{" " * 8}self._tql.add_filter('hasTag', """
    #                 f'TQL.Operator.EQ, tags, TQL.Type.SUB_QUERY)\n'
    #                 f'{" " * 8}return tags\n'
    #             )
    #         elif keyword_snake == 'has_task':
    #             filter_class += (
    #                 f'\n{" " * 4}@property\n'
    #                 f'{" " * 4}def has_task(self) -> FilterTasks:\n'
    #                 f'{" " * 8}"""Return **FilterTask** for further filtering."""\n'
    #                 f'{" " * 8}from .task import FilterTasks\n'
    #                 f'{" " * 8}tasks = FilterTasks(ApiEndpoints.TASKS, self._tcex, TQL())\n'
    #                 f"""{" " * 8}self._tql.add_filter('hasTask', """
    #                 f'TQL.Operator.EQ, tasks, TQL.Type.SUB_QUERY)\n'
    #                 f'{" " * 8}return tasks\n'
    #             )
    #         else:
    #             # build method
    #             filter_class += (
    #                 f'\n{" " * 4}def {keyword_snake}(self, operator, {keyword_snake}):{comment}\n'
    #                 f'{" " * 8}"""Filter {class_name} based on **{keyword}** keyword.\n\n'
    #                 f'{" " * 8}Args:\n'
    #                 f'{" " * 12}operator (enum): The operator enum for the filter.\n'
    #                 f'{" " * 12}{keyword_snake} ({keyword_type}): {description}.\n'
    #                 f'{" " * 8}"""\n'
    #                 f"{' ' * 8}self._tql.add_filter('{keyword}', operator, "
    #                 f'{keyword_snake}, {tql_type})\n'
    #             )

    #     return filter_class

    @property
    def filter(self) -> None:  # pragma: no cover
        """Return filter method."""
        raise NotImplementedError('Child class must implement this method.')

    @property
    def _api_endpoint(self) -> None:  # pragma: no cover
        """Return filter method."""
        raise NotImplementedError('Child class must implement this method.')

    def iterate(self, base_class) -> 'CaseManagementType':
        parameters = self.params

        # convert all keys to camel case
        for k, v in list(parameters.items()):
            k = self._utils.snake_to_camel(k)
            parameters[k] = v

        url = self._api_endpoint

        tql_string = self.tql.raw_tql or self.tql.as_str

        if tql_string:
            parameters['tql'] = tql_string

        while True:
            r = None
            try:
                r = self._session.get(url, params=parameters)
                print(r)
                print(r.text)
                self.log.debug(
                    f'Method: ({r.request.method.upper()}), '
                    f'Status Code: {r.status_code}, '
                    f'URl: ({r.url})'
                )
            except (ConnectionError, ProxyError):  # pragma: no cover
                self._event.send(
                    'handle_error',
                    code=951,
                    message_values=[
                        'OPTIONS',
                        407,
                        '{\"message\": \"Connection Error\"}',
                        self._api_endpoint,
                    ],
                )

            if not self.success(r):
                err = r.text or r.reason
                self._event.send(
                    'handle_error',
                    code=950,
                    message_values=[
                        'OPTIONS',
                        r.status_code,
                        f'"message": "{err}"',
                        r.url,
                    ],
                )

            # reset some vars
            parameters = {}

            data = r.json().get('data', [])
            url = r.json().pop('next', None)

            for result in data:
                yield base_class(session=self._session, **result)

            # break out of pagination if no next url present in results
            if not url:
                break

    # @staticmethod
    # def list_as_dict(added_items: 'CaseManagementType') -> dict:
    #     """Return the dict representation of the case management collection object."""
    #     as_dict = {'data': []}
    #     for item in added_items:
    #         as_dict['data'].append(item.as_dict)
    #     return as_dict

    @property
    def params(self) -> dict:
        """Return the parameters of the case management object collection."""
        return self._params

    @params.setter
    def params(self, params: dict) -> None:
        """Set the parameters of the case management object collection."""
        self._params = params

    @staticmethod
    def success(r: Response) -> bool:
        """Validate the response is valid.

        Args:
            r (requests.response): The response object.

        Returns:
            bool: True if status is "ok"
        """
        status = True
        if r.ok:
            try:
                if r.json().get('status') != 'Success':  # pragma: no cover
                    status = False
            except Exception:  # pragma: no cover
                status = False
        else:
            status = False
        return status

    @property
    def timeout(self) -> int:
        """Return the timeout of the case management object collection."""
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: int) -> None:
        """Set the timeout of the case management object collection."""
        self._timeout = timeout

    # @property
    # def tql_data(self) -> dict:
    #     """Return TQL data keywords."""
    #     if self._tql_data is None:
    #         r = self.tcex.session.options(f'{self.api_endpoint}/tql', params={})
    #         if r.ok:
    #             self._tql_data = r.json()['data']

    #     return self._tql_data
