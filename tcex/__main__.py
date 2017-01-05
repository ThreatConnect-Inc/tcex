import os
import sys
import inspect

def main():
    # use this if you want to include modules from a subfolder
    lib_path = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], "lib")))
    for root, directories, files in os.walk(lib_path):
        while len(directories) > 0:
            module = os.path.join(root, directories.pop(0))
            if 'PYTHONPATH' in os.environ:
                os.environ['PYTHONPATH'] = '{}{}{}'.format(module, os.pathsep, os.environ['PYTHONPATH'])
            else:
                os.environ['PYTHONPATH'] = '{}'.format(module)

    # os.environ['LD_LIBRARY_PATH'] = ''
    sys.argv[0] = sys.executable
    sys.argv[1] = '{}.py'.format(sys.argv[1])
    os.execv('{}'.format(sys.executable), sys.argv)

if __name__ == '__main__':
    main()