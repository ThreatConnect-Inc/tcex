from functools import reduce
from typing import Union

import jmespath

class StixParser:




    @staticmethod
    def _map(data: Union[list, dict], mapping: dict):

        if isinstance(data, dict):
            data = [data]

        for d in data:
            mapped_obj = mapping.copy()
            for key, value in mapping.items():
                if isinstance(value, list):
                    new_list = []
                    for item in value:
                        new_list.append(list(StixParser._map(d, item))[0])

                    mapped_obj[key] = new_list
                elif isinstance(value, dict):
                    mapped_obj[key] = list(StixParser._map(d, mapped_obj[key]))[0]
                else:
                    if not value.startswith('@'):
                        mapped_obj[key] = value
                    else:
                        mapped_obj[key] = jmespath.search(f'{value}', jmespath.search('@', d))
            yield mapped_obj