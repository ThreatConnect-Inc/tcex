"""Permutation"""
# standard library
import json
import logging
import os
import random
import re
import sys
from collections.abc import Generator, Iterator
from pathlib import Path
from typing import Any, NoReturn, cast

try:
    # standard library
    import sqlite3
except ImportError:  # pragma: no cover
    pass  # sqlite3 is only required for local development

# first-party
from tcex.app.config.install_json import InstallJson
from tcex.app.config.layout_json import LayoutJson
from tcex.app.config.model.install_json_model import OutputVariablesModel, ParamsModel
from tcex.app.config.model.layout_json_model import OutputsModel
from tcex.pleb.cached_property import cached_property
from tcex.pleb.none_model import NoneModel

# get tcex logger
tcex_logger = logging.getLogger('tcex')


class InputModel(ParamsModel):
    """Input Model"""

    value: Any

    def __hash__(self):
        """Make model hashable."""
        return hash(self.name)


class Permutation:
    """Permutations Module"""

    def __init__(self, logger: logging.Logger | None = None):
        """Initialize instance properties"""
        self.log = logger or tcex_logger

        # properties
        self._input_names = None
        self._input_table = 'inputs'
        self._input_permutations: list[list[InputModel]] = []
        self._output_permutations: list[list[OutputVariablesModel]] = []
        self.fqfn = Path(os.getcwd(), 'permutations.json')
        self.ij = InstallJson(logger=self.log)
        self.lj = LayoutJson(logger=self.log)

    @staticmethod
    def _create_input_model(ij_param: ParamsModel, value: Any) -> InputModel:
        """Create an input model from the install.json param model."""
        _input_model = InputModel(**ij_param.dict())
        # manually adding List values due to bug where data is not getting loaded into model in init
        _input_model.intel_type = ij_param.intel_type
        _input_model.playbook_data_type = ij_param.playbook_data_type
        _input_model.valid_values = ij_param.valid_values
        _input_model.value = value
        return _input_model

    @cached_property
    def _display_keywords(self) -> set[str]:
        """Return the display keywords."""
        _keywords = set()
        for param in self.lj.model.params.values():
            for keyword in (param.display or '').split(' '):
                keyword = re.sub(r'[^a-zA-Z0-9_]', '', keyword)
                if keyword in self.ij.model.param_names:
                    _keywords.add(keyword)
        self.log.debug(f'keywords={_keywords}')
        return _keywords

    def _gen_permutations(self, index: int = 0, params: list | None = None):
        """Iterate recursively over layout.json parameter names to build permutations.

        .. NOTE:: Permutations are for layout.json based Apps.

        Args:
            index: The current index position in the layout names list.
            params: The current list of args.
        """
        params = params or []
        try:
            # grab the name using the index value of all params in the layout.json file.
            # after the last name is hit the IndexError will trigger collecting outputs.
            name = list(self.lj.model.param_names)[index]

            # get layout.json param name and data
            lj_param = self.lj.model.get_param(name)

            # get install.json param to match layout.json param
            ij_param = self.ij.model.get_param(name)
            if ij_param is None:  # pragma: no cover
                self.log.error(f'No param found in install.json for "{name}".')
                sys.exit(1)

            if self.validate_layout_display(self._input_table, lj_param.display) or ij_param.hidden:
                # only process params that match display query or are hidden
                if name != 'tc_action' and name not in self._display_keywords:
                    params.append(self._create_input_model(ij_param, None))

                    # recursively call method to get all permutations
                    self._gen_permutations(index + 1, list(params))
                elif ij_param.type.lower() == 'boolean':
                    for val in [True, False]:
                        params.append(self._create_input_model(ij_param, val))

                        # update the data in the sqlite db so for next iteration
                        self.db_update_record(self._input_table, name, val)

                        # recursively call method to get all permutations
                        self._gen_permutations(index + 1, list(params))

                        # remove the previous arg before next iteration
                        params.pop()
                elif ij_param.type.lower() in ['choice', 'editchoice']:
                    for val in self.ij.expand_valid_values(ij_param.valid_values):
                        params.append(self._create_input_model(ij_param, val))

                        # update the data in the sqlite db so for next iteration
                        self.db_update_record(self._input_table, name, val)

                        # recursively call method to get all permutations
                        self._gen_permutations(index + 1, list(params))

                        # remove the previous arg before next iteration
                        params.pop()
                else:
                    params.append(self._create_input_model(ij_param, None))

                    # recursively call method to get all permutations
                    self._gen_permutations(index + 1, list(params))
            else:
                # do not add param since it's not required for this permutation
                self._gen_permutations(index + 1, list(params))
        except IndexError:
            # when IndexError is reached all params has been processed
            self._input_permutations.append(params)
            outputs: list[OutputVariablesModel] = []

            # iterate of InstallJsonModel -> PlaybookModel -> OutputVariablesModel
            if self.ij.model.playbook is not None:
                for o in self.ij.model.playbook.output_variables:
                    # get layout.json param to match install.json output variable
                    lj_output: NoneModel | OutputsModel = self.lj.model.get_output(o.name)
                    if isinstance(lj_output, OutputsModel):
                        valid = self.validate_layout_display(self._input_table, lj_output.display)
                        if lj_output.display is None or not valid:
                            continue
                    # output meet permutation check
                    outputs.append(o)
                self._output_permutations.append(outputs)

    @property
    def _params_data(self) -> Generator[ParamsModel, None, None]:
        """Return all defined params from layout.json/install.json, including hidden params."""
        # using inputs from layout.json since they are required to be in order
        # (display field can only use inputs previously defined)
        for input_name in self.lj.model.params:
            # get data from install.json based on name
            param = self.ij.model.get_param(input_name)
            if param is not None:
                yield param

        # hidden fields will not be in layout.json so they need to be include manually
        for input_name, ij_data in self.ij.model.filter_params(hidden=True).items():
            yield ij_data

    @cached_property
    def action_configurations(self) -> dict:
        """Return action configuration."""
        self.init_permutations()

        _action_configurations = {}
        for index, inputs in enumerate(self._input_permutations):
            for input_ in inputs:
                if input_.name == 'tc_action':
                    # the value should always be a string
                    action = cast(str, input_.value)
                    _action_configurations.setdefault(action, {'inputs': [], 'outputs': []})
                    _action_configurations[action]['inputs'].extend(inputs)
                    _action_configurations[action]['outputs'].extend(
                        self._output_permutations[index]
                    )
                    break

        for action, data in _action_configurations.items():
            _action_configurations[action] = {
                'inputs': sorted(list(set(data['inputs'])), key=lambda x: x.name),
                'outputs': sorted(list(set(data['outputs'])), key=lambda x: x.name),
            }

        return _action_configurations

    @cached_property
    def db_conn(self) -> sqlite3.Connection:  # type: ignore
        """Create a temporary in memory DB and return the connection."""
        try:
            return sqlite3.connect(':memory:')
        except sqlite3.Error as ex:  # pragma: no cover
            self.log.error(ex)
            sys.exit(1)

    def db_create_table(self, table_name: str, columns: list[str]):
        """Create a temporary DB table.

        Args:
            table_name: The DB table name.
            columns: The DB column names.
        """
        columns_ = ', '.join([f'''"{c.strip('"').strip("'")}" text''' for c in set(columns)])
        self.log.debug(f'action=db-create-table, table-name={table_name}, columns={columns_}')
        sql = f'CREATE TABLE IF NOT EXISTS {table_name} ({columns_});'
        try:
            cr = self.db_conn.cursor()
            cr.execute(sql)
        except sqlite3.Error as e:  # pragma: no cover
            self.handle_error(f'SQL create db failed - SQL: "{sql}", Error: "{e}"')

    def db_drop_table(self, table_name: str):
        """Drop a DB table.

        Args:
            table_name: The DB table name.
        """
        sql = f'DROP TABLE IF EXISTS {table_name};'
        try:
            cr = self.db_conn.cursor()
            cr.execute(sql)
        except sqlite3.Error as e:  # pragma: no cover
            self.handle_error(f'SQL drop db failed - SQL: "{sql}", Error: "{e}"')

    def db_insert_record(self, table_name: str, columns: list[str]):
        """Insert records into DB.

        A single row will all values as None so that values can be updated one at a
        time during parsing. The row and values will be used to determine permutations.

        Args:
            table_name: The DB table name.
            columns: The DB column names.
        """
        # sort and unique columns
        columns = sorted(list(set(columns)))
        bindings = ', '.join(['?'] * len(columns))
        columns_string = ', '.join([f'''"{c.strip('"').strip("'")}"''' for c in columns])
        values = [None] * len(columns)
        sql = f'INSERT INTO {table_name} ({columns_string}) VALUES ({bindings})'
        try:
            cur = self.db_conn.cursor()
            cur.execute(sql, values)
        except sqlite3.OperationalError as ex:  # type: ignore
            self.log.error(f'SQL insert failed - SQL: "{sql}", Error: "{ex}"')
            sys.exit(1)

    def db_update_record(self, table_name: str, column: str, value: bool | str | None):
        """Update a single column in the row-column create in db_insert_record.

        Args:
            table_name: The DB table name.
            column: The DB column names.
            value: The DB values to store (row data).
        """
        # escape any single quotes in value
        if isinstance(value, str):
            value = value.replace('\'', '\\')
        elif isinstance(value, bool):
            # core expects true/false so we convert bool value to string and lower
            value = str(value).lower()
        else:  # pragma: no cover
            # no other types can be used in a layout.json display clause
            return

        # only column defined in install.json can be updated
        if column in self.ij.model.param_names:
            # value should be wrapped in single quotes to be properly parsed
            sql = f'UPDATE {table_name} SET {column} = \'{value}\''
            try:
                cur = self.db_conn.cursor()
                cur.execute(sql)
            except sqlite3.OperationalError as ex:  # pragma: no cover
                self.log.error(f'SQL update failed - SQL: "{sql}", Error: "{ex}"')
                sys.exit(1)

    def handle_error(self, err: str) -> NoReturn:  # pragma: no cover
        """Print errors message and optionally exit.

        Args:
            err: The error message to print.
            halt: If True, the script will exit.
        """
        self.log.error(err)
        print(err)
        sys.exit(1)

    def get_action_input_names(self, action: str) -> list[str]:
        """Return the input names for the provided action."""
        return [i.name for i in self.get_action_inputs(action)]

    def get_action_inputs(self, action: str) -> list[InputModel]:
        """Return the inputs for the provided action."""
        return self.action_configurations.get(action, {}).get('inputs', [])

    def get_action_output_names(self, action: str) -> list[str]:
        """Return the output names for the provided action."""
        return [i.name for i in self.get_action_outputs(action)]

    def get_action_outputs(self, action: str) -> list[OutputVariablesModel]:
        """Return the outputs for the provided action."""
        return self.action_configurations.get(action, {}).get('outputs', [])

    def get_input_applies_to_all(self, input_name: str) -> bool:
        """Return the outputs for the provided action."""
        for data in self.action_configurations.values():
            for d in data.get('inputs', []):
                if d.name == input_name:
                    break
            else:
                return False  # not found
        return True

    def extract_tc_action_clause(self, display_clause: str | None) -> str | None:
        """Extract the tc_action part of the display clause."""
        if display_clause is not None:
            # action_clause_extract_pattern = r'(tc_action\sin\s\([^\)]*\))'
            action_clause_extract_pattern = r'''(tc_action\sin\s\(.+?(?<='\)))'''
            _tc_action_clause = re.search(
                action_clause_extract_pattern, display_clause, re.IGNORECASE
            )
            if _tc_action_clause is not None:
                self.log.debug(f'action=extract-action-clause, display-clause={display_clause}')
                return _tc_action_clause.group(1)
        return None

    # TODO: [bcs] this typing hing doesn't make sense on second yield
    @property
    def inputs_ordered(
        self,
    ) -> Generator[ParamsModel | str | None, None, None]:
        """Return inputs ordered properly.

        Layout based playbook Apps have the inputs ordered in
        the layout.json so that the display clause is guaranteed
        to have conditional defined before the clause is executed.
        """
        if self.lj.has_layout:
            for name in self.lj.model.param_names:
                yield self.ij.model.get_param(name)
        else:
            yield from self.lj.model.params

    # TODO: [low] improve this logic
    def init_permutations(self):
        """Process layout.json names/display to get all permutations of args."""
        if not all([self._input_permutations, self._output_permutations]):
            self._input_permutations = []
            self._output_permutations = []

            # create db for permutations testing
            self.db_create_table(self._input_table, self.ij.model.param_names)
            self.db_insert_record(self._input_table, self.ij.model.param_names)

            # only gen permutations if none have been generated previously
            self._gen_permutations()

            # drop database
            self.db_drop_table(self._input_table)

    def inputs_by_action(
        self, action: str, include_hidden: bool = True
    ) -> Iterator[dict[str, bool | ParamsModel]]:
        """Return all inputs for the provided action."""
        for ij_data in self._params_data:
            # get a display clause with just the tc_action condition
            display = self.extract_tc_action_clause(self.lj.model.get_param(ij_data.name).display)
            self.log.debug(f'action=input-by-action, input-name={ij_data.name}, display={display}')

            if ij_data.service_config:
                # inputs that are serviceConfig are not applicable for profiles
                continue

            if display is None:
                # when there is no display clause or the input is hidden,
                # then the input gets added to the AppBaseModel
                applies_to_all = True
            elif ij_data.hidden is True and include_hidden is True:
                applies_to_all = True
            elif self.validate_input_variable(ij_data.name, {'tc_action': action}, display):
                # each input will be checked for permutations if the App has layout and not hidden
                applies_to_all = False
            else:
                continue

            yield {'applies_to_all': applies_to_all, 'input': ij_data}

    def input_dict(self, permutation_id: int) -> dict:
        """Return all input permutation names for provided permutation id.

        {'tc_action': 'Append', 'input_strings': None, 'append_chars': None}

        Args:
            permutation_id: The index of the permutation input array.

        Returns:
            dict: A dict with key / value for each input for the provided permutation id.
        """
        input_dict = {}
        if self.lj.has_layout:
            for permutation in self.input_permutations[permutation_id]:
                input_dict.setdefault(permutation.name, permutation.value)
        return input_dict

    @cached_property
    def input_names(self) -> list[list[str]]:
        """Return all input permutation names for current App.

        Returns:
            list: List of Lists of input names.
        """
        input_names = []
        if self.lj.has_layout:
            for permutation in self.input_permutations:
                input_names.append([p.name for p in permutation])
        return input_names

    @property
    def input_permutations(self) -> list[list[InputModel]]:
        """Return all input permutations for current App.

        self._input_permutations is an array of permutations arrays.
        [[<perm obj #1], [<perm obj #2]]

        Returns:
            list: List of Lists of valid input permutations.
        """
        if not self._input_permutations and self.lj.has_layout:
            self.init_permutations()
        return self._input_permutations

    @property
    def output_permutations(self) -> list[list[OutputVariablesModel]]:
        """Return all output permutations for current App.

        Returns:
            list: List of Lists of valid outputs permutations.
        """
        if self._output_permutations is None:
            self.init_permutations()
        return self._output_permutations

    def outputs_by_action(self, action: str) -> Iterator[OutputVariablesModel]:
        """Return all inputs for the provided action."""
        yield from self.outputs_by_inputs({'tc_action': action})

    def outputs_by_inputs(self, inputs: dict[str, str]) -> Iterator[OutputVariablesModel]:
        """Return all output based on provided inputs

        Args:
            inputs: The args/inputs dict.

        Returns:
            list: List of Lists of valid outputs objects.
        """
        table = f'temp_{random.randint(100,999)}'  # nosec
        self.db_create_table(table, self.ij.model.param_names)
        self.db_insert_record(table, self.ij.model.param_names)

        for name, val in inputs.items():
            self.db_update_record(table, name, val)

        # iterate of InstallJsonModel -> PlaybookModel -> OutputVariablesModel
        if self.ij.model.playbook:
            for o in self.ij.model.playbook.output_variables:
                lj_output = self.lj.model.get_output(o.name)
                if isinstance(lj_output, NoneModel):  # pragma: no cover
                    # an output not listed in layout.json should always be shown
                    yield o
                elif self.validate_layout_display(table, lj_output.display):
                    # all other outputs must be validated
                    yield o

        # drop database
        self.db_drop_table(table)

    def permutations(self):
        """Process layout.json names/display to get all permutations of args."""
        if not self.lj.has_layout:  # pragma: no cover
            print('Only Apps with a layout.json are supported.')
            sys.exit(1)

        if 'sqlite3' not in sys.modules:  # pragma: no cover
            print('The sqlite3 module needs to be built-in to Python for this feature.')
            sys.exit(1)

        # create db for permutations testing
        self.db_create_table(self._input_table, self.ij.model.param_names)
        self.db_insert_record(self._input_table, self.ij.model.param_names)

        # only gen permutations if none have been generated previously
        if not all([self._input_permutations, self._output_permutations]):
            self._input_permutations = self._input_permutations or []
            self._output_permutations = self._output_permutations or []
            self._gen_permutations()

        # output permutations
        self.write_permutations_file()

    def validate_input_variable(
        self, input_name: str, inputs: dict, display: str | None = None
    ) -> bool:
        """Return True if the provided variables display where clause returns results.

        Args:
            input_name: The input variable name (e.g. tc_action).
            inputs: The current name/value dict.
            display: An optional display clause to validate. If not provided the
                display clause will be retrieved from the layout.json file.

        Returns:
            bool: True if the display value returns results.
        """
        # TODO: [low] re-evaluate this now that we only support layout.json Apps
        if not self.lj.has_layout or not inputs:  # pragma: no cover
            # always return true, even if current App doesn't have layouts
            return True

        table = f'temp_{random.randint(100,999)}'  # nosec
        self.db_create_table(table, self.ij.model.param_names)
        self.db_insert_record(table, self.ij.model.param_names)

        # APP-98 Added to cover the use case of interdependent variables in the layout.json.
        for name, param in self.ij.model.filter_params(_type='Boolean').items():
            self.db_update_record(table, name, param.default)

        for name, val in inputs.items():
            self.db_update_record(table, name, val)

        if display is None:
            lj_data = self.lj.model.get_param(input_name)
            if isinstance(lj_data, NoneModel):  # pragma: no cover
                # this shouldn't happen as all ij inputs must be in lj
                raise RuntimeError(f'The provided input {input_name} was not found in layout.json.')
            display = lj_data.display

        # check if provided variable meets display requirements
        valid = self.validate_layout_display(table, display)

        # cleanup temp table
        self.db_drop_table(table)

        return valid

    def validate_layout_display(self, table: str, display_condition: str | None) -> bool:
        """Check to see if the display condition passes.

        Args:
            table: The name of the DB table which hold the App data.
            display_condition: The "where" clause of the DB SQL statement.

        Returns:
            bool: True if the row count is greater than 0.
        """
        display = False
        if display_condition is None:
            display = True
        else:
            display_query = f'SELECT count(*) from {table} where {display_condition}'  # nosec
            try:
                cur = self.db_conn.cursor()
                cur.execute(display_query.replace('"', ''))
                rows = cur.fetchall()
                if rows[0][0] > 0:
                    display = True
            except sqlite3.Error as e:  # pragma: no cover
                print(f'"{display_query}" query returned an error: ({e}).')
                sys.exit(1)
        return display

    def write_permutations_file(self):
        """Print all valid permutations."""
        _permutations = []
        for index, permutations in enumerate(self.input_permutations):
            _permutations.append(
                {'index': index, 'args': [{'name': p.name, 'value': p.value} for p in permutations]}
            )

        with self.fqfn.open(mode='w') as fh:
            json.dump(_permutations, fh, indent=2, sort_keys=True)
        print('All permutations written to the "permutations.json" file.')
