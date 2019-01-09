.. _building_apps_tclib:

------------------------------------
Building Apps - Dependencies (tclib)
------------------------------------

Summary
-------

The ``tclib`` CLI tool provides a simple interface to download required Python modules in a self contained folder in the project directory.  This "lib" directory allows all dependencies to be bundled within the App. The App dependencies should be defined in the **requirements.txt** file in the project directory.

.. warning:: If you are using **macOS** and have Python installed via Homebrew, there is a `known bug <https://stackoverflow.com/questions/24257803/distutilsoptionerror-must-supply-either-home-or-prefix-exec-prefix-not-both>`__ that requires you to create a ``setup.cfg`` file in the same directory as the ``requirements.txt``. The ``setup.cfg`` file should have the following code at minimum:

  .. code-block:: python

    [install]
    prefix=

Usage
-----

To get the latest usage for ``tclib`` run ``tclib -h``.

.. IMPORTANT:: Running the ``tcinit`` command overwrites any existing lib directory.

.. code:: bash

    usage: tclib [-h] [--app_name APP_NAME] [--app_path APP_PATH]
                 [--config CONFIG] [--no_cache_dir] [--branch BRANCH]

    optional arguments:
      -h, --help           show this help message and exit
      --app_name APP_NAME  (Advanced) Fully qualified path of App.
      --app_path APP_PATH  (Advanced) Fully qualified path of App.
      --config CONFIG      (Advanced) Configuration file for gen lib. (Default:
                           tcex.json)
      --no_cache_dir       Do not use pip cache directory.
      --branch BRANCH      Build tcex from specified git branch instead of
                           downloading from PyPi.

Common Usage
~~~~~~~~~~~~

To build the "lib" directory for the current project the following is the most common command. This command can also be used to add/remove an changes made to requirements.

.. code:: bash

    tclib

If using a PIP cache it is sometimes required to tell ``pip`` to ignore the cached to pick up the latest package from pypi. Adding the ``--no_cache_dir`` flag to the command will force ``tclib`` to ignore any local cache directory.

.. code:: bash

    tclib --no_cache_dir

Using Configuration File
------------------------
By default the **tcex.json** configuration file will be loaded if it exists.  If the configuration includes the ``lib_versions`` parameter array the ``tclib`` command will use the values defined in the configuration to build the lib directories.

**Linux**

.. code:: javascript

  <...snipped>
  "lib_versions": [{
      "lib_dir": "lib_2.7.13",
      "python_executable": "~/.pyenv/versions/2.7.13/bin/python"
    },
    {
      "lib_dir": "lib_3.4.6",
      "python_executable": "~/.pyenv/versions/3.4.6/bin/python"
    },
    {
      "lib_dir": "lib_3.5.3",
      "python_executable": "~/.pyenv/versions/3.5.3/bin/python"
    },
    {
      "lib_dir": "lib_3.6.5",
      "python_executable": "~/.pyenv/versions/3.6.5/bin/python"
    }
  ],
  <snipped...>

For ease of management when building multiple Apps the tcex.json file can contain environment vars defining the Python version (e.g., $env.PY36 for ``export PY36='3.6.5'``).

.. code:: javascript

  <...snipped>
    {
      "lib_dir": "lib_$env.PY36",
      "python_executable": "~/.pyenv/versions/$env.PY36/bin/python"
    }
  <snipped...>

**Windows**

.. code:: javascript

  <...snipped>
  "lib_versions": [{
      "lib_dir": "lib_2.7.13",
      "python_executable": "~\\AppData\\Local\\Programs\\Python\\Python27\\python.exe"
    }, {
      "lib_dir": "lib_3.6.5",
      "python_executable": "~\\AppData\\Local\\Programs\\Python\\Python36\\python.exe"
    }
  ],
  <snipped...>
