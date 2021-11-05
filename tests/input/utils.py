"""Class that contains shared logic that may be used by Input test suites"""

from tcex.pleb.registry import registry

class InputTest:
    """Class that contains shared logic used by Input test suites"""

    @staticmethod
    def _stage_key_value(config_key, variable_name, value, tcex):
        """Write values to key value store. Expects dictionary of variable_name: value"""
        registry.playbook.create(variable_name, value)

        # force inputs to resolve newly inserted key-values from key value store
        if 'contents_resolved' in tcex.inputs.__dict__:
            del tcex.inputs.__dict__['contents_resolved']

        # inputs get resolved during instantiation of tcex. This means that variables like
        # '#App:1234:my_binary!Binary' were resolved to None before having the chance to be
        # stage update inputs contents cached property from None to correct variable name so
        # that inputs contents_resolved logic may resolve variable
        #
        # UPDATE: tcex code now relies on inputs.data_unresolved, so the tcex should not resolve
        # the variable to None, but leaving this code here just in case tcex is changed to use
        # inputs.data at some point.
        tcex.inputs.__dict__['contents'][config_key] = variable_name

        # since tcex code is not using inputs.data, call it here to ensure variables are resolved
        _ = tcex.inputs.data
