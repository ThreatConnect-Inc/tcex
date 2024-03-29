"""TcEx Framework Module"""

# standard library
from datetime import datetime
from enum import Enum

# third-party
from arrow import Arrow

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.filter_abc import FilterABC
from tcex.api.tc.v3.tql.tql_type import TqlType


class UserFilter(FilterABC):
    """Filter Object for Users"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.USERS.value

    def disabled(self, operator: Enum, disabled: bool):
        """Filter Disabled based on **disabled** keyword.

        Args:
            operator: The operator enum for the filter.
            disabled: A flag indicating whether or not the user's account has been disabled.
        """
        self._tql.add_filter('disabled', operator, disabled, TqlType.BOOLEAN)

    def first_name(self, operator: Enum, first_name: list | str):
        """Filter First Name based on **firstName** keyword.

        Args:
            operator: The operator enum for the filter.
            first_name: The first name of the user.
        """
        if isinstance(first_name, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('firstName', operator, first_name, TqlType.STRING)

    def group_id(self, operator: Enum, group_id: int | list):
        """Filter groupID based on **groupId** keyword.

        Args:
            operator: The operator enum for the filter.
            group_id: The ID of the group the user belongs to.
        """
        if isinstance(group_id, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('groupId', operator, group_id, TqlType.INTEGER)

    def id(self, operator: Enum, id: int | list):  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the user.
        """
        if isinstance(id, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('id', operator, id, TqlType.INTEGER)

    def job_function(self, operator: Enum, job_function: list | str):
        """Filter Job Function based on **jobFunction** keyword.

        Args:
            operator: The operator enum for the filter.
            job_function: The user's job function.
        """
        if isinstance(job_function, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('jobFunction', operator, job_function, TqlType.STRING)

    def job_role(self, operator: Enum, job_role: list | str):
        """Filter Job Role based on **jobRole** keyword.

        Args:
            operator: The operator enum for the filter.
            job_role: The user's job role.
        """
        if isinstance(job_role, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('jobRole', operator, job_role, TqlType.STRING)

    def last_login(self, operator: Enum, last_login: Arrow | datetime | int | str):
        """Filter Last Login based on **lastLogin** keyword.

        Args:
            operator: The operator enum for the filter.
            last_login: The last time the user logged in.
        """
        last_login = self.util.any_to_datetime(last_login).strftime('%Y-%m-%d %H:%M:%S')
        self._tql.add_filter('lastLogin', operator, last_login, TqlType.STRING)

    def last_name(self, operator: Enum, last_name: list | str):
        """Filter Last Name based on **lastName** keyword.

        Args:
            operator: The operator enum for the filter.
            last_name: The last name of the user.
        """
        if isinstance(last_name, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('lastName', operator, last_name, TqlType.STRING)

    def last_password_change(
        self, operator: Enum, last_password_change: Arrow | datetime | int | str
    ):
        """Filter Last Password Change based on **lastPasswordChange** keyword.

        Args:
            operator: The operator enum for the filter.
            last_password_change: The last time the user changed their password.
        """
        last_password_change = self.util.any_to_datetime(last_password_change).strftime(
            '%Y-%m-%d %H:%M:%S'
        )
        self._tql.add_filter('lastPasswordChange', operator, last_password_change, TqlType.STRING)

    def locked(self, operator: Enum, locked: bool):
        """Filter Locked based on **locked** keyword.

        Args:
            operator: The operator enum for the filter.
            locked: A flag indicating whether or not the user's account has been locked.
        """
        self._tql.add_filter('locked', operator, locked, TqlType.BOOLEAN)

    def password_reset_required(self, operator: Enum, password_reset_required: bool):
        """Filter Password Reset Required based on **passwordResetRequired** keyword.

        Args:
            operator: The operator enum for the filter.
            password_reset_required: A flag indicating whether or not the user's password needs to
                be reset upon next login.
        """
        self._tql.add_filter(
            'passwordResetRequired', operator, password_reset_required, TqlType.BOOLEAN
        )

    def pseudonym(self, operator: Enum, pseudonym: list | str):
        """Filter Pseudonym based on **pseudonym** keyword.

        Args:
            operator: The operator enum for the filter.
            pseudonym: The user's pseudonym.
        """
        if isinstance(pseudonym, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('pseudonym', operator, pseudonym, TqlType.STRING)

    def system_role(self, operator: Enum, system_role: list | str):
        """Filter Role Name based on **systemRole** keyword.

        Args:
            operator: The operator enum for the filter.
            system_role: The system role name defined for the user.
        """
        if isinstance(system_role, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('systemRole', operator, system_role, TqlType.STRING)

    def terms_accepted(self, operator: Enum, terms_accepted: bool):
        """Filter Terms Accepted based on **termsAccepted** keyword.

        Args:
            operator: The operator enum for the filter.
            terms_accepted: Flag indicating whether user has accepted the current Terms of Service.
        """
        self._tql.add_filter('termsAccepted', operator, terms_accepted, TqlType.BOOLEAN)

    def terms_accepted_date(
        self, operator: Enum, terms_accepted_date: Arrow | datetime | int | str
    ):
        """Filter Terms Accepted Date based on **termsAcceptedDate** keyword.

        Args:
            operator: The operator enum for the filter.
            terms_accepted_date: Date and time the user accepted the current Terms of Service.
        """
        terms_accepted_date = self.util.any_to_datetime(terms_accepted_date).strftime(
            '%Y-%m-%d %H:%M:%S'
        )
        self._tql.add_filter('termsAcceptedDate', operator, terms_accepted_date, TqlType.STRING)

    def tql_timeout(self, operator: Enum, tql_timeout: int | list):
        """Filter TQL Timeout based on **tqlTimeout** keyword.

        Args:
            operator: The operator enum for the filter.
            tql_timeout: The custom TQL timeout value (if defined).
        """
        if isinstance(tql_timeout, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('tqlTimeout', operator, tql_timeout, TqlType.INTEGER)

    def user_name(self, operator: Enum, user_name: list | str):
        """Filter User Name based on **userName** keyword.

        Args:
            operator: The operator enum for the filter.
            user_name: The user name of the user.
        """
        if isinstance(user_name, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('userName', operator, user_name, TqlType.STRING)
