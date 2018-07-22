.. _building_apps_modules:

Running ``tclib`` will download/install all required Python dependencies defined in the Apps **requirements.txt** file to a local ``lib_<version>`` directory.

.. note:: Typically calling ``tclib`` with no arguments is the most common use case.  If building an App for distribution then using a configuration file to define the lib structure is preferable.  The alternative is to run tclib using each Python version the App should support.

.. warning:: If you are using **macOS** and have Python installed via Homebrew, there is a `known bug <https://stackoverflow.com/questions/24257803/distutilsoptionerror-must-supply-either-home-or-prefix-exec-prefix-not-both>`__ that requires you to create a ``setup.cfg`` file in the same directory as the ``requirements.txt``. The ``setup.cfg`` file should have the following code at minimum:

  .. code-block:: python

    [install]
    prefix=

Usage
-----

.. code:: bash

    usage: tclib [-h] [--app_name APP_NAME] [--app_path APP_PATH]
                 [--config CONFIG] [--no_cache_dir] [--tcex_develop]

    optional arguments:
      -h, --help           show this help message and exit
      --app_name APP_NAME  Fully qualified path of App.
      --app_path APP_PATH  Fully qualified path of App.
      --config CONFIG      Configuration file for gen lib. (Default: tcex.json)
      --no_cache_dir       Do not use pip cache directory.
      --tcex_develop       Replace tcex version in config with github develop branch.

Using Configuration File
------------------------
By default the **tcex.json** configuration file will be loaded if it exists.  If the configuration includes the ``lib_versions`` parameter array the ``tclib`` command will use the values defined in the configuration to build the lib directories.  For ease of management when building multiple Apps the tcex.json file can contain environment vars defining the Python version (e.g., $env.PY36 for ``export PY36='3.6.5'``).

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
      "lib_dir": "lib_$env.PY36",
      "python_executable": "~/.pyenv/versions/$env.PY36/bin/python"
    }
  ],
  <snipped...>

**Windows**

.. code:: javascript

  <...snipped>
  "lib_versions": [{
      "lib_dir": "lib_2.7.13",
      "python_executable": "~\\AppData\\Local\\Programs\\Python\\Python27\\python.exe"
    }, {
      "lib_dir": "lib_3.6.2",
      "python_executable": "~\\AppData\\Local\\Programs\\Python\\Python36\\python.exe"
    }
  ],
  <snipped...>