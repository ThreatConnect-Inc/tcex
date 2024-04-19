"""TcEx Framework Module"""

# standard library
from datetime import datetime
from enum import Enum

# third-party
from arrow import Arrow

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.filter_abc import FilterABC
from tcex.api.tc.v3.tql.tql import Tql
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tcex.api.tc.v3.tql.tql_type import TqlType


class CaseAttributeFilter(FilterABC):
    """Filter Object for CaseAttributes"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.CASE_ATTRIBUTES.value

    def case_id(self, operator: Enum, case_id: int | list):
        """Filter Workflow ID based on **caseId** keyword.

        Args:
            operator: The operator enum for the filter.
            case_id: The ID of the case the workflow attribute is applied to.
        """
        if isinstance(case_id, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('caseId', operator, case_id, TqlType.INTEGER)

    def date_added(self, operator: Enum, date_added: Arrow | datetime | int | str):
        """Filter Date Added based on **dateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            date_added: The date the attribute was added to the system.
        """
        date_added = self.util.any_to_datetime(date_added).strftime('%Y-%m-%d %H:%M:%S')
        self._tql.add_filter('dateAdded', operator, date_added, TqlType.STRING)

    def date_val(self, operator: Enum, date_val: Arrow | datetime | int | str):
        """Filter Date based on **dateVal** keyword.

        Args:
            operator: The operator enum for the filter.
            date_val: The date value of the attribute (only applies to certain types).
        """
        date_val = self.util.any_to_datetime(date_val).strftime('%Y-%m-%d %H:%M:%S')
        self._tql.add_filter('dateVal', operator, date_val, TqlType.STRING)

    def default(self, operator: Enum, default: bool):
        """Filter Default based on **default** keyword.

        Args:
            operator: The operator enum for the filter.
            default: A flag that is set by an attribute type configuration.
        """
        self._tql.add_filter('default', operator, default, TqlType.BOOLEAN)

    def displayed(self, operator: Enum, displayed: bool):
        """Filter Displayed based on **displayed** keyword.

        Args:
            operator: The operator enum for the filter.
            displayed: Whether or not the attribute is displayed on the item.
        """
        self._tql.add_filter('displayed', operator, displayed, TqlType.BOOLEAN)

    @property
    def has_case(self):
        """Return **CaseFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.cases.case_filter import CaseFilter

        cases = CaseFilter(Tql())
        self._tql.add_filter('hasCase', TqlOperator.EQ, cases, TqlType.SUB_QUERY)
        return cases

    def id(self, operator: Enum, id: int | list):  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the attribute.
        """
        if isinstance(id, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('id', operator, id, TqlType.INTEGER)

    def int_val(self, operator: Enum, int_val: int | list):
        """Filter Integer Value based on **intVal** keyword.

        Args:
            operator: The operator enum for the filter.
            int_val: The integer value of the attribute (only applies to certain types).
        """
        if isinstance(int_val, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('intVal', operator, int_val, TqlType.INTEGER)

    def last_modified(self, operator: Enum, last_modified: Arrow | datetime | int | str):
        """Filter Last Modified based on **lastModified** keyword.

        Args:
            operator: The operator enum for the filter.
            last_modified: The date the attribute was last modified in the system.
        """
        last_modified = self.util.any_to_datetime(last_modified).strftime('%Y-%m-%d %H:%M:%S')
        self._tql.add_filter('lastModified', operator, last_modified, TqlType.STRING)

    def max_size(self, operator: Enum, max_size: int | list):
        """Filter Max Size based on **maxSize** keyword.

        Args:
            operator: The operator enum for the filter.
            max_size: The max length of the attribute text.
        """
        if isinstance(max_size, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('maxSize', operator, max_size, TqlType.INTEGER)

    def owner(self, operator: Enum, owner: int | list):
        """Filter Owner ID based on **owner** keyword.

        Args:
            operator: The operator enum for the filter.
            owner: The owner ID of the attribute.
        """
        if isinstance(owner, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('owner', operator, owner, TqlType.INTEGER)

    def owner_name(self, operator: Enum, owner_name: list | str):
        """Filter Owner Name based on **ownerName** keyword.

        Args:
            operator: The operator enum for the filter.
            owner_name: The owner name of the attribute.
        """
        if isinstance(owner_name, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('ownerName', operator, owner_name, TqlType.STRING)

    def pinned(self, operator: Enum, pinned: bool):
        """Filter Pinned based on **pinned** keyword.

        Args:
            operator: The operator enum for the filter.
            pinned: Whether or not the attribute is pinned with importance.
        """
        self._tql.add_filter('pinned', operator, pinned, TqlType.BOOLEAN)

    def short_text(self, operator: Enum, short_text: list | str):
        """Filter Text based on **shortText** keyword.

        Args:
            operator: The operator enum for the filter.
            short_text: The short text of the attribute (only applies to certain types).
        """
        if isinstance(short_text, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('shortText', operator, short_text, TqlType.STRING)

    def source(self, operator: Enum, source: list | str):
        """Filter Source based on **source** keyword.

        Args:
            operator: The operator enum for the filter.
            source: The source text of the attribute.
        """
        if isinstance(source, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('source', operator, source, TqlType.STRING)

    def text(self, operator: Enum, text: list | str):
        """Filter Text based on **text** keyword.

        Args:
            operator: The operator enum for the filter.
            text: The text of the attribute (only applies to certain types).
        """
        if isinstance(text, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('text', operator, text, TqlType.STRING)

    def type(self, operator: Enum, type: int | list):  # pylint: disable=redefined-builtin
        """Filter Type ID based on **type** keyword.

        Args:
            operator: The operator enum for the filter.
            type: The ID of the attribute type.
        """
        if isinstance(type, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('type', operator, type, TqlType.INTEGER)

    def type_name(self, operator: Enum, type_name: list | str):
        """Filter Type Name based on **typeName** keyword.

        Args:
            operator: The operator enum for the filter.
            type_name: The name of the attribute type.
        """
        if isinstance(type_name, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('typeName', operator, type_name, TqlType.STRING)

    def user(self, operator: Enum, user: list | str):
        """Filter User based on **user** keyword.

        Args:
            operator: The operator enum for the filter.
            user: The user who created the attribute.
        """
        if isinstance(user, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('user', operator, user, TqlType.STRING)
