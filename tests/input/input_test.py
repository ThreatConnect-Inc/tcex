"""Class that contains shared logic that may be used by Input test suites"""


class InputTest:

    @staticmethod
    def _stage_key_value(config_key, variable_name, value, tcex):
        """Write values to key value store. Expects dictionary of variable_name: value"""
        tcex.inputs.playbook.create(variable_name, value)

        # force inputs to resolve newly inserted key-values from key value store
        if 'contents_resolved' in tcex.inputs.__dict__:
            del tcex.inputs.__dict__['contents_resolved']

        # inputs get resolved during instantiation of tcex. This means that variables like
        # '#App:1234:my_binary!Binary' were resolved to None before having the chance to be
        # stage update inputs contents cached property from None to correct variable name so
        # that inputs contents_resolved logic may resolve variable
        tcex.inputs.__dict__['contents'][config_key] = variable_name