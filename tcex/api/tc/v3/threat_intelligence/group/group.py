"""Case Management"""
# third-party
from requests import Session

# first-party
from tcex.api.v3.threat_intelligence.group.type.adversary import Adversary, Adversaries


class Group:
    """Case Management

    Args:
        session: An configured instance of request.Session with TC API Auth.
    """

    def __init__(self, session: Session) -> None:
        """Initialize Class properties."""
        self.session = session

    def adversary(self, **kwargs) -> Adversary:
        """Return a instance of Adversary object."""
        return Adversary(session=self.session, **kwargs)

    def adversaries(self) -> Adversaries:
        """Return a instance of Adversaries object."""
        return Adversaries(session=self.session)

    def get(self, type_):
        try:
            return self.__getattribute__(type_.lower())
        except Exception:
            return None

    def create_entity(self, entity: dict, owner: str) -> dict:
        """Create a CM object provided a dict and owner."""
        entity_type = entity.pop('type').lower()
        entity_type = entity_type.replace(' ', '_')
        try:
            obj = getattr(self, entity_type)(**entity)
        except AttributeError:
            return {}

        r = obj.submit()
        data = {'status_code': r.status_code}
        if r.ok:
            data.update(r.json().get('data', {}))
            data['main_type'] = 'Group'
            data['sub_type'] = entity_type
            data['owner'] = owner

        return data