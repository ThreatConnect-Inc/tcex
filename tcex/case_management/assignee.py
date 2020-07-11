# -*- coding: utf-8 -*-
"""ThreatConnect Assignee Module"""


class User:
    """User Object used for assignee and createdBy.

    Args:
        first_name (str, kwargs): The first name of the user.
        id (id, kwargs): The id of the user.
        last_name (str, kwargs): The last name of the user.
        pseudonym (str, kwargs): The pseudonym of the user.
        role (str, kwargs): The role of the user.
        user_name (str, kwargs): The user name of the user.
    """

    def __init__(self, **kwargs):
        """Initialize Class properties."""
        self._transform_kwargs(kwargs)
        self._first_name = kwargs.get('first_name', None)
        self._id = kwargs.get('id', None)
        self._last_name = kwargs.get('last_name', None)
        self._pseudonym = kwargs.get('pseudonym', None)
        self._role = kwargs.get('role', None)
        self._user_name = kwargs.get('user_name', None)

    def __str__(self):
        """Printable version of Object"""
        printable_string = ''
        for key, value in sorted(vars(self).items()):
            key = f'{key.lstrip("_")} '
            if value is None:
                printable_string += f'{key:.<40} {"null":<50}\n'
            elif isinstance(value, (int, str)):
                printable_string += f'{key:.<40} {value:<50}\n'
            else:
                printable_string += f'{key:.<40} {"<object>":<50}\n'
        return printable_string

    @property
    def _metadata_map(self):
        """Return a mapping of kwargs to expected args."""
        return {
            'dateAdded': 'date_added',
            'firstName': 'first_name',
            'lastName': 'last_name',
            'userName': 'user_name',
        }

    def _transform_kwargs(self, kwargs):
        """Map the provided kwargs to expected arguments."""
        for key in dict(kwargs):
            new_key = self._metadata_map.get(key, key)
            kwargs[new_key] = kwargs.pop(key)

    @property
    def body(self):
        """Return a dict representation of the Creator class."""
        return self.as_dict

    @property
    def as_dict(self):
        """Return a dict representation of the Creator class."""
        properties = vars(self)
        as_dict = {}
        for key, value in properties.items():
            key = key.lstrip('_')
            if value is None:
                continue
            as_dict[key] = value

        if not as_dict:
            return None

        return as_dict

    @property
    def as_entity(self):
        """Return the USER as a entity."""
        return {'type': 'User', 'value': self.user_name, 'id': self.id}

    @property
    def first_name(self):
        """Return the First Name for the Case Creator."""
        return self._first_name

    @first_name.setter
    def first_name(self, first_name):
        """Set the First Name for the Case Creator."""
        self._first_name = first_name

    @property
    def id(self):
        """Return the ID for the Case Creator."""
        return self._id

    @id.setter
    def id(self, creator_id):
        """Set the ID for the Case Creator."""
        self._id = creator_id

    @property
    def last_name(self):
        """Return the **Last Name** for the User Object."""
        return self._last_name

    @last_name.setter
    def last_name(self, last_name):
        """Set the **Last Name** for the User Object."""
        self._last_name = last_name

    @property
    def pseudonym(self):
        """Return the Pseudonym for the Case Creator."""
        return self._pseudonym

    @pseudonym.setter
    def pseudonym(self, pseudonym):
        """Set the Pseudonym for the Case Creator."""
        self._pseudonym = pseudonym

    @property
    def role(self):
        """Return the Role for the Case Creator."""
        return self._role

    @role.setter
    def role(self, role):
        """Set the Role for the Case Creator."""
        self._role = role

    @property
    def user_name(self):
        """Return the User Name for the Case Creator."""
        return self._user_name

    @user_name.setter
    def user_name(self, user_name):
        """Set the User Name for the Case Creator."""
        self._user_name = user_name


class Users:
    """Sub class of the Cases object. Used to map the users to.

    Args:
        users (list): A array of user data
    """

    def __init__(self, users=None):
        """Initialize Class properties."""
        if users is None:
            users = []
        self._users = []

        for user in users:
            if isinstance(user, User):
                self._users.append(user)
            else:
                self._users.append(User(**user))

    @property
    def users(self):
        """Return the **Users**."""
        return self._users

    @users.setter
    def users(self, users):
        """Set the **Users**."""
        self._users = users

    @property
    def as_dict(self):
        """Return a dict representation of the UsersData class."""
        data = []
        for user in self.users:
            data.append(user.as_dict)

        return {'data': data}

    @property
    def body(self):
        """Return a body representation of the Creator class."""
        body = []
        for user in self.users:
            body.append(user.body)

        return {'data': body}


class Assignee(User):
    """Assignee Object for Case Management.

    For User type the user_name or id fields is required and
    for the Group type the name or id is required.

    Args:
        first_name (str, kwargs): The first name of the User.
        id (id, kwargs): The id of the User.
        name (str, kwargs): The name of the Group.
        last_name (str, kwargs): The last name of the user.
        pseudonym (str, kwargs): The pseudonym of the User.
        role (str, kwargs): The role of the User.
        user_name (str, kwargs): The user name of the User.
        type (str, kwargs): The assignee type. Default to User.
    """

    def __init__(self, type='User', **kwargs):  # pylint: disable=redefined-builtin
        """Initialize Class properties."""
        self._name = kwargs.get('name')
        self._type = type
        super().__init__(**kwargs)

    @property
    def as_dict(self):
        """Return a dict representation of the Assignee class."""
        user_data = super().as_dict
        del user_data['type']
        data = {
            'data': user_data,
            'type': self._type,
        }
        if self._name:
            data['data']['name'] = self._name
        return data
