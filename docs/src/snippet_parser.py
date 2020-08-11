"""Parse tab separated value snippet file."""
# standard library
import csv

# print header
print('.. _snippets:\n')

feature = None
last_feature = None
docs = ''
with open('snippets.tsv') as fd:
    rd = csv.reader(fd, delimiter='\t', quotechar='"')
    for row in rd:
        feature = row[0]
        title = row[1]
        code = row[2]

        if last_feature != feature:
            docs += f"{len(feature) * '-'}\n"
            docs += f'{feature}\n'
            docs += f"{len(feature) * '-'}\n\n"

        # docs += f"{len(title) * '-'}\n"
        docs += f'{title}\n'
        docs += f'''{len(title) * '-'}\n\n'''
        docs += '.. code-block:: python\n'
        docs += '    :linenos:\n'
        docs += '    :lineno-start: 1\n\n'
        for c in code.split('\\n'):
            docs += f'    {c}\n'
        docs += '\n'

        # track last feature
        last_feature = feature

print(docs)
