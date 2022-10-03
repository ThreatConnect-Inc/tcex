"""Tool to copy all layout.json files from App to testing directory."""
# standard library
import os
from shutil import copyfile


def walklevel(some_dir, level=1):
    """."""
    some_dir = some_dir.rstrip(os.path.sep)
    if os.path.isdir(some_dir):
        num_sep = some_dir.count(os.path.sep)
        for root_, dirs_, files_ in os.walk(some_dir):
            yield root_, dirs_, files_
            num_sep_this = root_.count(os.path.sep)
            if num_sep + level <= num_sep_this:
                del dirs_[:]
    else:
        print(f'Invalid directory provided {some_dir}')


home = os.getenv('HOME')
src_base = f'{home}/WorkBench/010__DEVELOPMENT/'
dst_base = 'layout_json_samples'
filename = 'layout.json'
for project in ['TC', 'TCPB', 'TCVA', 'TCVC', 'TCVF', 'TCVW']:
    os.makedirs(os.path.join(dst_base, project.lower()), exist_ok=True)
    prj_dir = os.path.join(src_base, project)

    for root, dirs, files in walklevel(prj_dir):
        src_fqfn = os.path.join(root, filename)
        if not os.path.isfile(src_fqfn):
            continue

        base_name = os.path.basename(root)
        dst_fqfn = os.path.join(dst_base, project.lower(), f'{base_name.lower()}-{filename}')
        copyfile(src_fqfn, dst_fqfn)
