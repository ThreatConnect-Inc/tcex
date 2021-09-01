"""Case Management"""
# third-party
from requests import Session

# first-party
from tcex.security.user import User, Users
from tcex.security.user_group import UserGroup, UserGroups

class Security:
    """V3 Security API Endpoint

    Args:
        session: An configured instance of request.Session with TC API Auth.
    """

    def __init__(self, session: Session) -> None:
        """Initialize Class properties."""
        self.session = session

    def user_group(self, **kwargs) -> UserGroup:
        return UserGroup(session=self.session, **kwargs)

    def user_groups(self, **kwargs) -> UserGroups:
        return UserGroups(session=self.session, **kwargs)

    def users(self, **kwargs) -> Users:
        return Users(session=self.session, **kwargs)

    def user(self, **kwargs) -> User:
        return User(session=self.session, **kwargs)

