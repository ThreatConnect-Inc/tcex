.. _building_apps_commands:

tcinit
------

This CLI tool provides a simple interface to kick start a new project from a template and to keep framework files up to date.  There are several template that supported specific use cases. Most templates are working Apps that can be easily modified to the developers use case.

tclib
-----

This CLI tool provides a simple interface to download required Python modules in a self contained folder in the project directory.  This "lib" directory allows all dependencies to be bundled within the App.

tcprofile
---------

This CLI tool provides a simple interface to create testing profiles.  The profiles can be used to perform local testing of the App before deploying to ThreatConnect.  Multiple profiles can be create and grouped to allow testing of different data inputs and outputs.

tcrun
-----

This CLI tool provides a simple interface to run the App locally using the profiles created using the ``tcprofile`` command.  If the profile has validation rules defined the ``tcrun`` command will validate the output variables as defined in the validation rules.

tcpackage
---------

This CLI tool provides a simple interface to package the App so that it can be easily deployed to the ThreatConnect Platform.
