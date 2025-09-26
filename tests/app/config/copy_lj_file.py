"""Layout JSON File Copier for Test Configuration.

This module provides functionality to copy layout.json files from various TCEx project
directories to a centralized test configuration location for testing purposes.

Functions:
    walklevel: Walk directory tree with level limit
"""


import os
from collections.abc import Generator
from pathlib import Path
from shutil import copyfile


def walklevel(
    some_dir: str, level: int = 1
) -> Generator[tuple[str, list[str], list[str]], None, None]:
    """Walk directory tree with level limit.

    Args:
        some_dir: The directory to walk through
        level: The maximum depth level to traverse (default: 1)

    Yields:
        Tuple containing (root, dirs, files) for each directory level
    """
    some_dir = some_dir.rstrip(os.path.sep)
    if Path(some_dir).is_dir():
        num_sep = some_dir.count(os.path.sep)
        for root_, dirs_, files_ in os.walk(some_dir):
            yield root_, dirs_, files_
            num_sep_this = root_.count(os.path.sep)
            if num_sep + level <= num_sep_this:
                del dirs_[:]
    else:
        ex_msg = f'Invalid directory provided {some_dir}'
        raise ValueError(ex_msg)


def main() -> None:
    """Main function to copy layout.json files from TCEx projects."""
    home = os.getenv('HOME')
    if not home:
        ex_msg = 'HOME environment variable not set'
        raise RuntimeError(ex_msg)

    src_base = f'{home}/WorkBench/010__DEVELOPMENT/'
    dst_base = 'layout_json_samples'
    filename = 'layout.json'

    projects = ['TC', 'TCPB', 'TCVA', 'TCVC', 'TCVF', 'TCVW']

    for project in projects:
        try:
            Path(dst_base) / project.lower()
            (Path(dst_base) / project.lower()).mkdir(parents=True, exist_ok=True)
            prj_dir = Path(src_base) / project

            for root, _dirs, _files in walklevel(str(prj_dir)):
                src_fqfn = Path(root) / filename
                if not src_fqfn.is_file():
                    continue

                base_name = Path(root).name
                dst_fqfn = Path(dst_base) / project.lower() / f'{base_name.lower()}-{filename}'
                copyfile(str(src_fqfn), str(dst_fqfn))
        except Exception as ex:
            ex_msg = f'Error processing project {project}: {ex}'
            raise RuntimeError(ex_msg) from ex


if __name__ == '__main__':
    main()
