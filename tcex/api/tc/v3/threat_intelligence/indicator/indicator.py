"""Case Management"""
# third-party
from requests import Session

# first-party
from tcex.api.v3.threat_intelligence.indicator.type.file import File, Files


class Indicator:
    """Case Management

    Args:
        session: An configured instance of request.Session with TC API Auth.
    """

    def __init__(self, session: Session) -> None:
        """Initialize Class properties."""
        self.session = session

    def file(self, **kwargs) -> File:
        """Return a instance of File object."""
        return File(session=self.session, **kwargs)

    def files(self) -> Files:
        """Return a instance of Files object."""
        return Files(session=self.session)

    def get(self, _type):
        try:
            return self.__getattribute__(_type.lower())
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
            data['main_type'] = 'Indicator'
            data['sub_type'] = entity_type
            data['owner'] = owner

        return data
