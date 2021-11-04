# All
python tcex/api/tc/v3/_gen/_gen.py all --help

## Create/Replace All Files
python tcex/api/tc/v3/_gen/_gen.py all

## Create/Replace All Filter Files
python tcex/api/tc/v3/_gen/_gen.py all --gen_type filter

## Create/Replace All Model Files
python tcex/api/tc/v3/_gen/_gen.py all --gen_type model

## Create/Replace All Object Files
python tcex/api/tc/v3/_gen/_gen.py all --gen_type object

# Args
python tcex/api/tc/v3/_gen/_gen.py args --help

## Generate Args
python tcex/api/tc/v3/_gen/_gen.py args --type indicators --indent_blocks 2

# Filters
python tcex/api/tc/v3/_gen/_gen.py filter --help

## Create Specific Filter Type
python tcex/api/tc/v3/_gen/_gen.py filter --type cases

# Models
python tcex/api/tc/v3/_gen/_gen.py model --help

## Create Specific Model Type
python tcex/api/tc/v3/_gen/_gen.py model --type cases

# Object File
python tcex/api/tc/v3/_gen/_gen.py object --help

## Create Specific Object Type
python tcex/api/tc/v3/_gen/_gen.py object --type cases
