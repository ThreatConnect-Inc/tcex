"""."""


class MigrationType(str):
    """Migration type for pydantic model."""

    @classmethod
    def __get_validators__(cls):
        """."""
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        """."""
        # __modify_schema__ should mutate the dict it receives in place,
        # the returned value will be ignored
        field_schema.update(default='target')

    @classmethod
    def validate(cls, v, values, **kwargs):
        """."""
        # if not isinstance(v, str):
        #     raise TypeError('string required')

        if v is None:
            v = 'target'
        # print('!!!!!!!!!!!!v', v)
        # print('!!!!!!!!!!!!values', values)
        # print('!!!!!!!!!!!!kwargs', kwargs)
        return v

    def __repr__(self):
        """."""
        return f'MigrationType({super().__repr__()})'
