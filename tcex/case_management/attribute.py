"""ThreatConnect Attribute"""

from .api_endpoints import ApiEndpoints
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .filter import Filter
from .tql import TQL


class Attributes(CommonCaseManagementCollection):
    """Attributes Class for Case Management Collection

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        # Example of params input
        {
            'result_limit': 100,  # How many results are retrieved.
            'result_start': 10,  # Starting point on retrieved results.
            'fields': ['caseId', 'summary']  # Additional fields returned on the results
        }

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        initial_response (dict, optional): Initial data in
            Case Object for Attribute. Defaults to None.
        tql_filters (list, optional): List of TQL filters. Defaults to None.
        params(dict, optional): Dict of the params to be sent while
            retrieving the Attributes objects.
    """

    def __init__(self, tcex, initial_response=None, tql_filters=None, params=None):
        """Initialize Class properties"""
        super().__init__(
            tcex,
            ApiEndpoints.ATTRIBUTES,
            initial_response=initial_response,
            tql_filters=tql_filters,
            params=params,
        )
        # self.params.setdefault('fields', []).append('dateAdded')
        # self.params.setdefault('fields', []).append('lastModified')

        if initial_response:
            for item in initial_response.get('data', []):
                self.added_items.append(Attribute(tcex, **item))

    def __iter__(self):
        """Object iterator"""
        return self.iterate(initial_response=self.initial_response)

    def add_attribute(self, attribute):
        """Add an Attribute.

        Args:
            Attribute (Attribute): The Attribute Object to add.
        """
        self.added_items.append(attribute)

    def entity_map(self, entity):
        """Map a dict to a Attribute.

        Args:
            entity (dict): The Attribute data.

        Returns:
            CaseManagement.Attribute: An Attribute Object
        """
        return Attribute(self.tcex, **entity)

    @property
    def filter(self):
        """Return instance of FilterAttribute Object."""
        return FilterAttributes(ApiEndpoints.ATTRIBUTES, self.tcex, self.tql)


class Attribute(CommonCaseManagement):
    """Attribute object for Case Management.

    Args:
        type (str, kwargs): [Required] The **Type** for the Attribute.
        value (str, kwargs): [Required] The **Value** for the Attribute.
    """

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties"""
        super().__init__(tcex, ApiEndpoints.ATTRIBUTES, kwargs)
        self.attribute_filter = [
            {
                'keyword': 'AttributeId',
                'operator': TQL.Operator.EQ,
                'value': self.id,
                'type': TQL.Type.INTEGER,
            }
        ]

        self._source = kwargs.get('source', None)
        self._date_added = kwargs.get('date_added', None)
        self._last_modified = kwargs.get('last_modified', None)
        self._displayed = kwargs.get('displayed', None)
        self._type = kwargs.get('type', None)
        self._value = kwargs.get('value', None)
        self.case_id = kwargs.get('case_id', None)

    @property
    def body(self):
        """Return the body representation of the CM object."""
        body = {
            'type': self.type,
            'value': self.value,
            'source': self.source,
            'date_added': self.date_added,
            'displayed': self.displayed,
            'lastModified': self.last_modified,
            'caseId': self.case_id,
        }

        if self.id:
            body.pop('type')

        body = {k: v for k, v in body.items() if v is not None}

        return body

    @property
    def case_id(self):
        """Return the **Source** for the Attribute."""
        return self._case_id

    @case_id.setter
    def case_id(self, case_id):
        """Return the **CaseId** for the Attribute."""
        self._case_id = case_id

    @property
    def source(self):
        """Return the **Source** for the Attribute."""
        return self._source

    @source.setter
    def source(self, source):
        """Return the **Source** for the Attribute."""
        self._source = source

    @property
    def date_added(self):
        """Return the **dateAdded** for the Attribute."""
        return self._date_added

    @date_added.setter
    def date_added(self, date_added):
        """Return the **dateAdded** for the Attribute."""
        self._date_added = date_added

    @property
    def last_modified(self):
        """Return the **lastModified** for the Attribute."""
        return self._last_modified

    @last_modified.setter
    def last_modified(self, last_modified):
        """Return the **lastModified** for the Attribute."""
        self._last_modified = last_modified

    @property
    def displayed(self):
        """Return the **Displayed** for the Attribute."""
        return self._displayed

    @displayed.setter
    def displayed(self, displayed):
        """Return the **Displayed** for the Attribute."""
        self._displayed = displayed

    @property
    def type(self):
        """Return the **Type** for the Attribute."""
        return self._type

    @type.setter
    def type(self, type_):
        """Return the **Value** for the Attribute."""
        if self._type and self.id:
            raise RuntimeError('Cannot update type of existing attribute.')
        self._type = type_

    @property
    def value(self):
        """Return the **Value** for the Attribute."""
        return self._value

    @value.setter
    def value(self, value):
        """Return the **Value** for the Attribute."""
        self._value = value

    @property
    def as_entity(self):
        """Return the entity representation of the Attribute."""
        return {'type': 'Attribute', 'value': self.value, 'id': self.id}

    def entity_mapper(self, entity):
        """Update current object with provided object properties.

        Args:
            entity (dict): An entity dict used to update the Object.
        """
        new_attribute = Attribute(self.tcex, **entity)
        self.__dict__.update(new_attribute.__dict__)


class FilterAttributes(Filter):
    """Filter Object for Attributes"""

    def case_id(self, operator, case_id):
        """Filter Attributes based on the ID of the case the workflow attribute is applied to.

        Args:
            operator (enum): The operator enum for the filter.
            case_id (int): The ID of the case the workflow attribute is applied to.
        """
        self._tql.add_filter('caseId', operator, case_id, TQL.Type.INTEGER)

    def date_added(self, operator, date_added):
        """Filter Attributes based on the date the attribute was added to the system

        Args:
            operator (enum): The operator enum for the filter.
            date_added (str): The date the attribute was added to the system.
        """
        self._tql.add_filter('dateAdded', operator, date_added, TQL.Type.STRING)

    def last_modified(self, operator, last_modified):
        """Filter Attributes based on the date the attribute was added to the system

        Args:
            operator (enum): The operator enum for the filter.
            last_modified (str): The date the attribute was added to the system.
        """
        self._tql.add_filter('lastmodified', operator, last_modified, TQL.Type.STRING)

    def dateval(self, operator, date_added):
        """Filter Attributes based on the date value of the attribute (only applies to certain types)

        Args:
            operator (enum): The operator enum for the filter.
            date_added (str): The date the attribute was added to the system.
        """
        self._tql.add_filter('dateval', operator, date_added, TQL.Type.STRING)

    def intval(self, operator, intval):
        """Filter Attributes based on the date value of the attribute (only applies to certain types)

        Args:
            operator (enum): The operator enum for the filter.
            intval (str): The date the attribute was added to the system.
        """
        self._tql.add_filter('intval', operator, intval, TQL.Type.INTEGER)

    def max_size(self, operator, max_size):
        """Filter Attributes based on the date value of the attribute (only applies to certain types)

        Args:
            operator (enum): The operator enum for the filter.
            max_size (str): The date the attribute was added to the system.
        """
        self._tql.add_filter('maxsize', operator, max_size, TQL.Type.INTEGER)

    def displayed(self, operator, displayed):
        """Filter Attributes based on the date value of the attribute (only applies to certain types)

        Args:
            operator (enum): The operator enum for the filter.
            displayed (str): The date the attribute was added to the system.
        """
        self._tql.add_filter('displayed', operator, displayed, TQL.Type.BOOLEAN)

    def security_label(self, operator, security_label):
        """Filter Attributes based on the date value of the attribute (only applies to certain types)

        Args:
            operator (enum): The operator enum for the filter.
            security_label (str): The date the attribute was added to the system.
        """
        self._tql.add_filter('hassecuritylabel', operator, security_label, TQL.Type.INTEGER)

    @property
    def has_case(self):
        """Return **FilterCase** for further filtering."""
        from .case import FilterCases  # pylint: disable=cyclic-import

        cases = FilterCases(ApiEndpoints.Cases, self._tcex, TQL())
        self._tql.add_filter('hasCase', TQL.Operator.EQ, cases, TQL.Type.SUB_QUERY)
        return cases

    def text(self, operator, text):  # pylint: disable=redefined-builtin
        """Filter Attributes based on **id** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            text (int): The ID of the Attribute.
        """
        self._tql.add_filter('text', operator, text, TQL.Type.STRING)

    def id(self, operator, id):  # pylint: disable=redefined-builtin
        """Filter Attributes based on **id** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            id (int): The ID of the Attribute.
        """
        self._tql.add_filter('id', operator, id, TQL.Type.INTEGER)

    def source(self, operator, source):
        """Filter Attributes based on **source** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            source (str): The source of the Attribute.
        """
        self._tql.add_filter('source', operator, source, TQL.Type.STRING)

    def type(self, operator, type_):
        """Filter Attributes based on **typeName** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            type_(str): The type name of the Attribute.
        """
        self._tql.add_filter('type', operator, type_, TQL.Type.INTEGER)

    def type_name(self, operator, type_name):
        """Filter Attributes based on **typeName** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            type_name(str): The type name of the Attribute.
        """
        self._tql.add_filter('typename', operator, type_name, TQL.Type.STRING)

    def owner(self, operator, owner):
        """Filter Attributes based on **typeName** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            owner(str): The type name of the Attribute.
        """
        self._tql.add_filter('owner', operator, owner, TQL.Type.INTEGER)

    def owner_name(self, operator, owner_name):
        """Filter Attributes based on **typeName** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            owner_name(str): The type name of the Attribute.
        """
        self._tql.add_filter('ownername', operator, owner_name, TQL.Type.STRING)
