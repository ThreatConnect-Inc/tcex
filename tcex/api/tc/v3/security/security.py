"""TcEx Framework Module"""

# third-party
from requests import Session

# first-party
from tcex.api.tc.v3.security.owner_roles.owner_role import OwnerRole, OwnerRoles
from tcex.api.tc.v3.security.owners.owner import Owner, Owners
from tcex.api.tc.v3.security.system_roles.system_role import SystemRole, SystemRoles
from tcex.api.tc.v3.security.user_groups.user_group import UserGroup, UserGroups
from tcex.api.tc.v3.security.users.user import User, Users


class Security:
    """Security

    Args:
        session: An configured instance of request.Session with TC API Auth.
    """

    def __init__(self, session: Session):
        """Initialize instance properties."""
        self.session = session

    def owner_role(self, **kwargs) -> OwnerRole:
        """Return a instance of Owner Role object."""
        return OwnerRole(session=self.session, **kwargs)

    def owner_roles(self, **kwargs) -> OwnerRoles:
        """Return a instance of Owner Roles object."""
        return OwnerRoles(session=self.session, **kwargs)

    def owner(self, **kwargs) -> Owner:
        """Return a instance of Owner object."""
        return Owner(session=self.session, **kwargs)

    def owners(self, **kwargs) -> Owners:
        """Return a instance of Owners object."""
        return Owners(session=self.session, **kwargs)

    def system_role(self, **kwargs) -> SystemRole:
        """Return a instance of System Role object."""
        return SystemRole(session=self.session, **kwargs)

    def system_roles(self, **kwargs) -> SystemRoles:
        """Return a instance of System Roles object."""
        return SystemRoles(session=self.session, **kwargs)

    def user_group(self, **kwargs) -> UserGroup:
        """Return a instance of User Group object."""
        return UserGroup(session=self.session, **kwargs)

    def user_groups(self, **kwargs) -> UserGroups:
        """Return a instance of User Group object."""
        return UserGroups(session=self.session, **kwargs)

    def user(self, **kwargs) -> User:
        """Return a instance of User object."""
        return User(session=self.session, **kwargs)

    def users(self, **kwargs) -> Users:
        """Return a instance of Users object."""
        return Users(session=self.session, **kwargs)
