App-Deployment Configuration File
=================================

A configuration file named ``install.json`` is used for ThreatConnect
apps written in:

-  Python
-  Java®
-  JavaScript® (Spaces)

Standard Section
----------------

The Standard section defines required and optional properties of all Apps in ThreatConnect. The required properties are properties that must be provided for any packaged App installed through the ThreatConnect platform. The optional properties provide additional information based on the type of target App.

The table below lists all of the properties of the Standard section.

+--------------------------------------------+-----------+-----------------------------------------+
| Property                                   | Required? | Allowed Values                          |
+============================================+===========+=========================================+
| `allowOnDemand <#allowondemand>`__         | TRUE      | Boolean                                 |
+--------------------------------------------+-----------+-----------------------------------------+
| `apiUserTokenParam <#apiusertokenparam>`__ | FALSE     | Boolean                                 |
+--------------------------------------------+-----------+-----------------------------------------+
| `displayName <#displayname>`__             | TRUE      | String                                  |
+--------------------------------------------+-----------+-----------------------------------------+
| `feeds <#feed-app-configuration>`__        | FALSE     | Object                                  |
+--------------------------------------------+-----------+-----------------------------------------+
| `languageVersion <#languageversion>`__     | FALSE     | String                                  |
+--------------------------------------------+-----------+-----------------------------------------+
| `listDelimiter <#listdelimiter>`__         | FALSE     | String                                  |
+--------------------------------------------+-----------+-----------------------------------------+
| `minServerVersion <#minserverversion>`__   | FALSE     | String                                  |
+--------------------------------------------+-----------+-----------------------------------------+
| `note <#note>`__                           | FALSE     | String                                  |
+--------------------------------------------+-----------+-----------------------------------------+
| `params <#parameter-array-section>`__      | TRUE      | Object                                  |
+--------------------------------------------+-----------+-----------------------------------------+
| `Playbook <#playbook-app-configuration>`__ | FALSE     | Array of objects                        |
+--------------------------------------------+-----------+-----------------------------------------+
| `programIcon <#programicon>`__             | FALSE     | String                                  |
+--------------------------------------------+-----------+-----------------------------------------+
| `programLanguage <#programlanguage>`__     | TRUE      | ``"JAVA"``, ``"PYTHON"``, or ``"NONE"`` |
+--------------------------------------------+-----------+-----------------------------------------+
| `programMain <#programmain>`__             | TRUE      | String                                  |
+--------------------------------------------+-----------+-----------------------------------------+
| `programVersion <#programversion>`__       | TRUE      | String                                  |
+--------------------------------------------+-----------+-----------------------------------------+
| `publishOutFiles <#publishoutfiles>`__     | FALSE     | Array of strings                        |
+--------------------------------------------+-----------+-----------------------------------------+
| `repeatingMinutes <#repeatingminutes>`__   | FALSE     | Array of integers                       |
+--------------------------------------------+-----------+-----------------------------------------+
| `runtimeContext <#runtimecontext>`__       | FALSE     | Array of strings                        |
+--------------------------------------------+-----------+-----------------------------------------+
| `runtimeLevel <#runtimelevel>`__           | TRUE      | ``"Organization"``,                     |
|                                            |           | ``"SpaceOrganization"``, or             |
|                                            |           | ``"System"``                            |
+--------------------------------------------+-----------+-----------------------------------------+

allowOnDemand
^^^^^^^^^^^^^

Required property that allows or disallows an App to be run on demand using the **Run Now** button when the App is configured as a Job in the ThreatConnect platform. This property only applies to Python and Java Apps.

apiUserTokenParam
^^^^^^^^^^^^^^^^^

Optional property that specifies whether or not the App should use an API user token (which allows access to the datastore)

displayName
^^^^^^^^^^^

Required property providing the name of the App as it will appear in the ThreatConnect platform

languageVersion
^^^^^^^^^^^^^^^

Optional property used solely for tracking purposes. It does **not** affect the version of Python or Java used by the Job Execution Engine to run the App.

listDelimiter
^^^^^^^^^^^^^

Optional property that sets the character used to delimit the values of **Select Many** Attributes that are passed into an App

minServerVersion
^^^^^^^^^^^^^^^^

Optional string property restricting the ThreatConnect instance from installing the App if it does not meet this version requirement. The notation is **<major>.<minor>.<patch>** (e.g., **5.4.0**).

note
^^^^

Optional property available in Playbook Apps under the **?**" tooltip when the App parameters are being edited. Use this field to describe the purpose of the app in two-three sentences.

programIcon
^^^^^^^^^^^

Optional property providing the icon that will be used to represent Central Spaces Apps

programLanguage
^^^^^^^^^^^^^^^

Required property describing the language runtime environment used by the ThreatConnect Job Executor. It is relevant for Apps that run on the Job Execution Engine (Python and Java Apps) and can be set to NONE for Spaces Apps.

programMain
^^^^^^^^^^^

Required property providing the entry point into the App. For Python Apps, it is the name of the ``.py`` file (or exclude the extension if running it as a module). For Java Apps, it is the main class the Job Execution Engine should use when calling the App using the Java Runtime Environment.

programVersion
^^^^^^^^^^^^^^

Required property providing the version number for the App that will be displayed in the **Installed Apps** section available to a System Administrator. ThreatConnect recommends the use of `Semantic Versioning <https://semver.org/>`_. The Semantic Version notation is **<major>.<minor>.<patch>** (e.g., **1.0.1**).

publishOutFiles
^^^^^^^^^^^^^^^

Optional field available for job-style Apps that can be scheduled to serve files. If this array is populated, the App is responsible for writing the files to the relative **tc_output_path** parameter that is passed in. This will enable HTTP-based file serving of these files as a unique URL available to the user in ThreatConnect. This parameter accepts an array of strings and can include file globs.

repeatingMinutes
^^^^^^^^^^^^^^^^

Optional property that provides a list of minute increments to display in the **Repeat Every…** section in the **Schedule** panel of the Job Wizard. This property is relevant only for Python and Java Apps for which the developer wants to control how frequently an App can be executed. If this property is not defined, the default listing is as follows: [60, 120, 240, 360, 720] .

runtimeContext
^^^^^^^^^^^^^^

Optional property enabling Spaces Apps to be context aware. (Context-aware Spaces Apps can be added to the **Details** screen of an object in the ThreatConnect platform.) Because this property is an array of strings, the App can be displayed in Spaces under multiple contexts within the ThreatConnect platform, including the **Menu** and **Search** screens. This property is only relevant to Spaces Apps.

.. note:: Context-aware Spaces Apps are passed contextual information via the URL query string when the App is displayed in the ThreatConnect platform. The details of those parameters are bewyond the scope of this document.

The available runtime contexts are:

* Address
* Adversary
* ASN
* Campaign
* CIDR
* Document
* Email
* EmailAddress
* Event
* File
* Host
* Incident
* IntrusionSet
* Menu
* Mutex
* RegistryKey
* Report
* Search
* Signature
* Tag
* Threat
* URL
* UserAgent
* Victim

runtimeLevel
^^^^^^^^^^^^

Required property which dictates how the app is used within the ThreatConnect platform, as detailed in the table below.

+-------------------+------------------------------------------------------------------------------+
| Value             | Description                                                                  |
+===================+==============================================================================+
| Organization      | This value is a Python or Java App that is run by the Job Execution Engine.  |
|                   | This type of app must be provisioned to specific organizations (or **Allow   |
|                   | All Orgs** must be selected) by the System Administrator. Once provisioned,  |
|                   | the App can be scheduled to run as part of a Job.                            |
+-------------------+------------------------------------------------------------------------------+
| SpaceOrganization | This value is a Spaces App that is run within ThreatConnect as a Space.      |
|                   | This type of App must be provisioned to specific organizations (or **Allow   |
|                   | All Orgs** must be selected) by the System Administrator. Once provisioned,  |
|                   | the App can be added as a Spaces App by any user belonging to the            |
|                   | Organization.                                                                |
+-------------------+------------------------------------------------------------------------------+
| System            | Although not commonly used, a System-level App is a Python or Java App that  |
|                   | is strictly visible by the System Administrator. This App can be scheduled   |
|                   | only in a System Job.                                                        |
+-------------------+------------------------------------------------------------------------------+

Feed App Configuration
----------------------

+--------------------------------------------------------------------+-----------+-----------------+
| Property                                                           | Required? | Allowed Values  |
+====================================================================+===========+=================+
| `attributesFile <#attributesfile>`__                               | FALSE     | String          |
+--------------------------------------------------------------------+-----------+-----------------+
| `documentStorageLimitMb <#documentstoragelimitmb>`__               | FALSE     | Integer         |
+--------------------------------------------------------------------+-----------+-----------------+
| `enableBulkJson <#enablebulkjson>`__                               | FALSE     | Boolean         |
+--------------------------------------------------------------------+-----------+-----------------+
| `indicatorLimit <#indicatorlimit>`__                               | FALSE     | Integer         |
+--------------------------------------------------------------------+-----------+-----------------+
| `jobFile <#jobfile>`__                                             | FALSE     | String          |
+--------------------------------------------------------------------+-----------+-----------------+
| `sourceCategory <#sourcecategory>`__                               | FALSE     | String          |
+--------------------------------------------------------------------+-----------+-----------------+
| `sourceDescription <#sourcedescription>`__                         | FALSE     | String          |
+--------------------------------------------------------------------+-----------+-----------------+
| `sourceName <#sourcename>`__                                       | FALSE     | String          |
+--------------------------------------------------------------------+-----------+-----------------+

attributesFile
^^^^^^^^^^^^^^

Optional property that provides the name of the CSV file with any of the custom Attributes required for the feed

documentStorageLimitMb
^^^^^^^^^^^^^^^^^^^^^^

Optional property that sets the Document storage limit

enableBulkJson
^^^^^^^^^^^^^^

Optional property that turns on or off the bulk JSON capability

indicatorLimit
^^^^^^^^^^^^^^

Optional property that sets the Indicator limit

jobFile
^^^^^^^

Optional property that providea the name of the JSON file that is used to set up and run the Job that pulls in content from the feed

sourceCategory
^^^^^^^^^^^^^^

Optional property that specifies how the source should be categorized

sourceDescription
^^^^^^^^^^^^^^^^^

Optional property that provides the source's description as it will appear in ThreatConnect

sourceName
^^^^^^^^^^

Optional property that provides the name of the source in which the feed's content will be created

Parameter Array Section
-----------------------

The Parameter Array section of the **install.json** file is the mechanism used by the Job Execution Engine and the Spaces framework to pass configuration data at runtime. For Java and Python Apps, the entries defined in this section dictate the **Parameters** panel of the Job Wizard in the ThreatConnect platform. Spaces Apps have their own configuration screen as part of the user’s Space for each App.

.. note:: In Python, parameters are called by using the **--param <value>** syntax handled by the **argparse** library. For Java Apps, the System-environment arguments are passed by using the **-Dparam=<value>** syntax. Discussion of App argument parsing is beyond the scope of this document.

The table below highlights the Parameter array properties (the **params** array).

+-------------------------------------------------------+-----------+------------------------------+
| Property                                              | Required? | Allowed Values               |
+=======================================================+===========+==============================+
| `allowMultiple <#allowmultiple>`__                    | FALSE     | Boolean                      |
+-------------------------------------------------------+-----------+------------------------------+
| `default <#default>`__                                | FALSE     | Boolean or Integer or String |
+-------------------------------------------------------+-----------+------------------------------+
| `encrypt <#encrypt>`__                                | FALSE     | Boolean                      |
+-------------------------------------------------------+-----------+------------------------------+
| `hidden <#hidden>`__                                  | FALSE     | Boolean                      |
+-------------------------------------------------------+-----------+------------------------------+
| `label <#label>`__                                    | TRUE      | String                       |
+-------------------------------------------------------+-----------+------------------------------+
| `name <#name>`__                                      | TRUE      | String                       |
+-------------------------------------------------------+-----------+------------------------------+
| `note <#note-parameter>`__                            | FALSE     | String                       |
+-------------------------------------------------------+-----------+------------------------------+
| `PlaybookDataType <#playbookdatatype>`__              | FALSE     | Array                        |
+-------------------------------------------------------+-----------+------------------------------+
| `required <#required>`__                              | FALSE     | Boolean                      |
+-------------------------------------------------------+-----------+------------------------------+
| `sequence <#sequence>`__                              | FALSE     | Integer                      |
+-------------------------------------------------------+-----------+------------------------------+
| `type <#type>`__                                      | TRUE      | String                       |
+-------------------------------------------------------+-----------+------------------------------+
| `validValues <#validvalues>`__                        | FALSE     | Array                        |
+-------------------------------------------------------+-----------+------------------------------+
| `viewRows <#viewrows>`__                              | FALSE     | Integer                      |
+-------------------------------------------------------+-----------+------------------------------+

allowMultiple
^^^^^^^^^^^^^

The value of this optional property is automatically set to **true** if the **MultiChoice** type is used. If a String type is used, this flag allows the user to define multiple values in a single input field delimited by a pipe ("|") character.

default
^^^^^^^

Optional property that is the default value pre-populated for new Jobs or Spaces. The purpose of a default value is to provide the user with a guidance while allowing edits based on preference.

encrypt
^^^^^^^

Optional property that designates a parameter as an encrypted value. Parameters defined as encrypted will be managed by the Keychain feature that encrypts password while at rest. This flag should be used with the String type and will render a password input textbox in the Job and Spaces configuration.

hidden
^^^^^^

If this optional property is set to **true**, this parameter will be hidden from the Job Wizard. Hidden parameters allow the developer to persist parameters between Job executions without the need to render the values in the Job Wizard. This option is valid only for Python and Java Apps. Further details on persisting parameters directly from the app are beyond the scope of this document.

label
^^^^^

Required property providing a description of the parameter displayed in the ThreatConnect platform Job Wizard or Spaces Configuration dialog box

name
^^^^

Required property that is the internal parameter name taken from the Job Wizard and passed to the App at runtime. It is the effective command-line argument name passed to the App.

note Parameter
^^^^^^^^^^^^^^

Optional parameter-description field available in Playbook Apps under the **?** tooltip when the App parameters are being edited. Use this field to describe the purpose of the parameter in two-three sentences.

PlaybookDataType
^^^^^^^^^^^^^^^^

Optional property restricting the data type of incoming Playbook variables. This is different than the ``type`` property that controls the UI input type. The PlaybookDataType can be any standard or custom type and is expected to be an array of strings.

As of ThreatConnect 5.4, the standard Playbook types supported by the Python and Java SDK are:

* String
* StringArray
* Binary
* BinaryArray
* KeyValue
* KeyValueArray
* TCEntity
* TCEntityArray
* TCEnhancedEntity
* TCEnhancedEntityArray

required
^^^^^^^^

Optional property designating this parameter as a required field that must be populated to save the Job or Playbook App

sequence
^^^^^^^^

Optional number used to control the ordering of the parameters in the Job Wizard or Spaces Configuration dialog box. If it is not defined, the order of the parameters in the **install.json** file is used.

type
^^^^

Required property to enable the UI to display relevant components and allow the Job Executor to adapt how parameters are passed to an App at runtime. The table below lists the available types and how they affect elements within the platform.

+-------------+------------------------------------------------------------------------------------+
| Type        | Description                                                                        |
+=============+====================================================================================+
| String      | This type renders an HTML Input textbox in the Job Wizard or Spaces Configuration  |
|             | dialog box. This allows the user to enter free-form text as a parameter. Values    |
|             | are passed as a String to Python and Java Apps.                                    |
+-------------+------------------------------------------------------------------------------------+
| Choice      | This type renders an HTML Select option in the Job Wizard or Spaces Configuration  |
|             | dialog box. This allows the user to select predefined text values as a parameter.  |
|             | (See the description of the **validValues"** string array property in 3.) Values   |
|             | are passed as a String to Python and Java Apps.                                    |
+-------------+------------------------------------------------------------------------------------+
| MultiChoice | This type renders an HTML Multi-Checkbox Select option in the Job Wizard or Spaces |
|             | Configuration dialog box. This allows the user to select multiple predefined text  |
|             | values as a parameter. (See the description of the **validValues** string array    |
|             | property in 3.) The same parameter is passed multiple times for a Python App.      |
|             | Python Apps should use the argparse **action='append'** option to receive the      |
|             | parameters as an array. Java and Spaces Apps will receive the parameter as a       |
|             | single value separated by a pipe character. Values are passed as a String to       |
|             | Python and Java Apps. This selection must be used together with the                |
|             | **allowMultiple** flag defined as **true**.                                        |
+-------------+------------------------------------------------------------------------------------+
| Boolean     | This type renders an HTML Checkbox option in the Job Wizard or Spaces              |
|             | Configuration dialog box. This allows the user to turn on a flag as a parameter.   |
|             | Values are passed as a **--flag** style parameter to Python Apps. (See the         |
|             | **action='store_true'** option in the argparse module.) Java and Spaces Apps       |
|             | receive the actual Boolean value **true** or **false**. These Apps should parse    |
|             | the string to resolve the Boolean flag value.                                      |
+-------------+------------------------------------------------------------------------------------+

validValues
^^^^^^^^^^^

Optional property to be used with the **Choice** and **MultiChoice** types to restrict the possible values a user can select. For example, to define a **loggingLevel** parameter, this field could have the following values: ["CRITICAL", "ERROR", "WARN", "INFO", "DEBUG", "TRACE"].

viewRows
^^^^^^^^

Optional property for Playbook Apps to control the height of the display in the input parameter, and it expects an integer value. A value of 1 is default (and will show a text input element) and anything greater than 1 displays a textarea input when editing the Playbook App in ThreatConnect.

Playbook App Configuration
--------------------------

+---------------------------------------------------------------------+-----------+----------------+
| Property                                                            | Required? | Allowed Values |
+=====================================================================+===========+================+
| `outputVariables <#outputvariables>`__                              | FALSE     | Array          |
+---------------------------------------------------------------------+-----------+----------------+
| `retry <#retry>`__                                                  | FALSE     | Object         |
+---------------------------------------------------------------------+-----------+----------------+

outputVariables
^^^^^^^^^^^^^^^

Optional ``outputVariables`` property that specifies the variables that a Playbook App will provide for downstream Playbooks

+---------------------------------------------------------------------+-----------+----------------+
| Property                                                            | Required? | Allowed Values |
+=====================================================================+===========+================+
| `name <#output-variable-name>`__                                    | TRUE      | String         |
+---------------------------------------------------------------------+-----------+----------------+
| `type <#output-variable-type>`__                                    | TRUE      | String         |
+---------------------------------------------------------------------+-----------+----------------+

Output Variable Name
""""""""""""""""""""

Required property that provides the name of the output variable that is accessible to downstream Apps

Output Variable Type
""""""""""""""""""""

Required property that specifies the type of the output variable. The valid types are:

* Binary
* BinaryArray
* KeyValue
* KeyValueArray
* String
* StringArray
* TCEntity
* TCEntityArray

retry
^^^^^

Optional ``retry`` property that can be used to allow a Playbook to retry its execution in case of failure

+---------------------------------------------------------------------+-----------+----------------+
| Property                                                            | Required? | Allowed Values |
+=====================================================================+===========+================+
| `allowed <#allowed>`__                                              | FALSE     | Boolean        |
+---------------------------------------------------------------------+-----------+----------------+
| `defaultDelayMinutes <#defaultdelayminutes>`__                      | FALSE     | Integer        |
+---------------------------------------------------------------------+-----------+----------------+
| `defaultMaxRetries <#defaultmaxretries>`__                          | FALSE     | Integer        |
+---------------------------------------------------------------------+-----------+----------------+

allowed
"""""""

Optional property that specifies whether or not the Playbook App can retry its execution

defaultDelayMinutes
"""""""""""""""""""

Optional property that specifies the number of minutes between each new retry in case of failure. This property assumes that the ``allowed`` property is set **true** to allow the App to retry.

defaultMaxRetries
"""""""""""""""""

Optional property that specifies the maximum number of times the Playbook App can retry in case of failure. This property assumes that the ``allowed`` property is set **true** to allow the app to retry

Variable Expression
-------------------

The variable-expression feature enables developers to reference **$**
style variables in the **install.json** file and have the ThreatConnect
platform resolve the values when displayed in the Job Wizard or Spaces
Configuration dialog box. The external-variables component can go one
step further by resolving the value at the time a Job executes. Variable
expressions are allowed only in the **params** section of the
**install.json** file.

Internal Variables
^^^^^^^^^^^^^^^^^^

Internal variables are predefined (reserved) variables that can be
explicitly declared in the **install.json** file. Apps declaring these
variables direct the Job Wizard and Spaces Configuration dialog box
to convert the variables into literal values. Internal variables should
be used only with the **Choice** and **MultiChoice** types. They should
be defined in the **validValues** property.

Example of a validValues parameter definition:

.. code:: json

    {
       "name": "owner",
       "label": "Owner",
       "type": "Choice",
       "validValues": ["${OWNERS}"]
    }

The variables listed in the table below are internal variables
understood by the ThreatConnect platform.

+------------+------------------+------------------------------+-------------------------------------------------------------------------------------+
| Variable   | Resolves As Type | Example of Usage             | Description                                                                         |
+============+==================+==============================+=====================================================================================+
| OWNERS     | String Array     | ``["${OWNERS}"]``            | The OWNERS variable resolves to the available owners to which the current user has  |
|            |                  |                              | access. Since this determination is dynamically resolved at runtime, the owners     |
|            |                  |                              | rendered depend on the user. This variable is useful when an App needs to have a    |
|            |                  |                              | defined owner passed as a parameter. The string value of the owner(s) is passed as  |
|            |                  |                              | an argument to the App.                                                             |
+------------+------------------+------------------------------+-------------------------------------------------------------------------------------+
| ATTRIBUTES | String Array     | ``["${ATTRIBUTES}"]`` or     | The ATTRIBUTES variable resolves to available Attributes in the current             |
|            |                  | ``["${ATTRIBUTES:<type>}"]`` | organization. This variable has a second, optional component, **:<type>**, that     |
|            |                  |                              | further refines the attributes resolved to the specific Indicator or Group type     |
|            |                  |                              | (e.g., **["${ATTRIBUTES:Address}"]**). The string value of the Attribute(s) is      |
|            |                  |                              | passed as an argument to the App.                                                   |
+------------+------------------+------------------------------+-------------------------------------------------------------------------------------+
| INDICATORS | String Array     | ``["${INDICATOR_TYPES}"]``   | The INDICATOR_TYPES variable resolves to all of the Indicator types available in    |
|            |                  |                              | the given instance of ThreatConnect. The string value of the Indicator type(s) is   |
|            |                  |                              | passed as an argument to the app.                                                   |
+------------+------------------+------------------------------+-------------------------------------------------------------------------------------+

When the ``$ATTRIBUTES`` internal variable is used with a ``:<type>`` suffix, the type can be any of the Indicator, Group, Task, or Victim types in the ThreatConnect platform:

* Address: ``["${ATTRIBUTES:Address}"]``
* Adversary: ``["${ATTRIBUTES:Adversary}"]``
* ASN: ``["${ATTRIBUTES:ASN}"]``
* Campaign: ``["${ATTRIBUTES:Campaign}"]``
* CIDR: ``["${ATTRIBUTES:CIDR}"]``
* Document: ``["${ATTRIBUTES:Document}"]``
* Email: ``["${ATTRIBUTES:Email}"]``
* EmailAddress: ``["${ATTRIBUTES:EmailAddress}"]``
* Event: ``["${ATTRIBUTES:Event}"]``
* File: ``["${ATTRIBUTES:File}"]``
* Host: ``["${ATTRIBUTES:Host}"]``
* Incident: ``["${ATTRIBUTES:Incident}"]``
* IntrusionSet: ``["${ATTRIBUTES:IntusionSet}"]``
* Mutex: ``["${ATTRIBUTES:Mutex}"]``
* RegistryKey: ``["${ATTRIBUTES:RegistryKey}"]``
* Report: ``["${ATTRIBUTES:Report}"]``
* Adversary: ``["${ATTRIBUTES:Adversary}"]``
* Signature: ``["${ATTRIBUTES:Signature}"]``
* Task: ``["${ATTRIBUTES:Task}"]``
* Threat: ``["${ATTRIBUTES:Threat}"]``
* URL: ``["${ATTRIBUTES:URL}"]``
* UserAgent: ``["${ATTRIBUTES:URL}"]``
* Victim: ``["${ATTRIBUTES:Victim}"]``

External Variables
^^^^^^^^^^^^^^^^^^^

External variables offer the user an additional level of convenience by
directing the Job Wizard and Spaces Configuration dialog box to take
advantage of the Variables feature.

.. note:: The Variables feature in the ThreatConnect platform allows any user to create variable key/value pairs. Once created, these values can be selected by the user in the Job Wizard or Spaces Configuration dialog box to reduce the need to copy and paste keys and plain-text data.

Since the variable names are not known by the App developer, the generic
form of the variables is referenced instead in a **<level:type>**
format.

For example, to allow users to select one of their plain-text
variables from Organization and User levels, the **install.json** file
would reference them as follows:

.. code:: json

    "validValues": ["{USER:TEXT}", "${ORGANIZATION:TEXT}"]

The left-hand component of the variable is the level. The level can be
any of the options listed in the table below.

+--------------+-----------------------------------------------------------------------------------+
| Level Option | Description                                                                       |
+==============+===================================================================================+
| User         | This option displays the list of the user’s variables in the Job Wizard or Spaces |
|              | Configuration dialog box.                                                         |
+--------------+-----------------------------------------------------------------------------------+
| Organization | This option displays the list of organization variables available to the current  |
|              | user in the Job wizard or Spaces Configuration dialog box.                        |
+--------------+-----------------------------------------------------------------------------------+
| System       | This option displays the list of System variables available to the current user   |
|              | in the Job Wizard or Spaces Configuration dialog box.                             |
+--------------+-----------------------------------------------------------------------------------+

Multiple external-variable expressions can be included in string array form.

install.json Schema
-------------------

.. code-block:: json

    {
      "additionalProperties": false,
      "properties": {
        "allowOnDemand": {
          "type": "boolean"
        },
        "apiUserTokenParam": {
          "type": "boolean"
        },
        "displayName": {
          "type": "string"
        },
        "feeds": {
          "items": {
            "additionalProperties": false,
            "properties": {
              "attributesFile": {
                "type": "string"
              },
              "enableBulkJson": {
                "type": "boolean"
              },
              "documentStorageLimitMb": {
                "type": "integer"
              },
              "indicatorLimit": {
                "type": "integer"
              },
              "jobFile": {
                "type": "string"
              },
              "sourceCategory": {
                "type": "string"
              },
              "sourceDescription": {
                "type": "string"
              },
              "sourceName": {
                "type": "string"
              }
            }
          }
        },
        "languageVersion": {
          "type": "string"
        },
        "listDelimiter": {
          "type": "string"
        },
        "minServerVersion": {
          "type": "string"
        },
        "note": {
          "type": "string"
        },
        "params": {
          "items": {
            "additionalProperties": false,
            "properties": {
              "allowMultiple": {
                "type": "boolean"
              },
              "default": {
                "type": [
                  "boolean",
                  "integer",
                  "string"
                ]
              },
              "encrypt": {
                "type": "boolean"
              },
              "hidden": {
                "type": "boolean"
              },
              "label": {
                "type": "string"
              },
              "name": {
                "type": "string"
              },
              "note": {
                "type": "string"
              },
              "PlaybookDataType": {
                "items": {
                  "enum": [
                    "Any",
                    "Binary",
                    "BinaryArray",
                    "KeyValue",
                    "KeyValueArray",
                    "String",
                    "StringArray",
                    "TCEntity",
                    "TCEntityArray"
                  ]
                },
                "type": "array"
              },
              "required": {
                "type": "boolean"
              },
              "sequence": {
                "type": "integer"
              },
              "type": {
                "enum": [
                  "Boolean",
                  "Choice",
                  "KeyValueList",
                  "MultiChoice",
                  "String",
                  "StringMixed"
                ],
                "type": "string"
              },
              "validValues": {
                "type": "array"
              },
              "viewRows": {
                "type": "integer"
              }
            },
            "required": [
              "label",
              "name",
              "type"
            ],
            "type": "object"
          },
          "type": "array",
          "uniqueItems": true
        },
        "Playbook": {
          "properties": {
            "outputVariables": {
              "items": {
                "additionalProperties": false,
                "properties": {
                  "name": {
                    "type": "string"
                  },
                  "type": {
                    "enum": [
                      "Binary",
                      "BinaryArray",
                      "KeyValue",
                      "KeyValueArray",
                      "String",
                      "StringArray",
                      "TCEntity",
                      "TCEntityArray"
                    ],
                    "type": "string"
                  }
                },
                "required": [
                  "name",
                  "type"
                ],
                "type": "object"
              },
              "type": "array",
              "uniqueItems": true
            },
            "retry": {
              "additionalProperties": false,
              "properties": {
                "allowed": {
                  "type": "boolean"
                },
                "defaultDelayMinutes": {
                  "type": "integer"
                },
                "defaultMaxRetries": {
                  "type": "integer"
                }
              },
              "type": "object"
            }
          },
          "type": "object"
        },
        "programIcon": {
          "type": "string"
        },
        "programLanguage": {
          "type": "string"
        },
        "programMain": {
          "type": "string"
        },
        "programVersion": {
          "type": "string"
        },
        "publishOutFiles": {
          "type": "array"
        },
        "repeatingMinutes": {
          "type": "array"
        },
        "runtimeContext": {
          "type": "array"
        },
        "runtimeLevel": {
          "type": [
            "array",
            "string"
          ]
        }
      },
      "required": [
        "allowOnDemand",
        "displayName",
        "params",
        "programLanguage",
        "programMain",
        "programVersion",
        "runtimeLevel"
      ],
      "type": "object"
    }

Example JSON File
-----------------

This section provides an example of an **install.json** file for a
Python App. The key elements are described with line-number references
in 8, below the example.

Example **install.json** file for a Python app:

.. code-block:: json
    :linenos:
    :lineno-start: 1

    {
     "programVersion": "1.0.0",
     "programLanguage": "PYTHON",
     "programMain": "auto_enrich",
     "languageVersion": "2.7",
     "runtimeLevel": "Organization",
     "allowOnDemand": true,
     "params": [{
      "name": "api_access_id",
      "label": "Local ThreatConnect API Access ID",
      "sequence": 1,
      "required": true,
      "validValues": ["${USER:TEXT}", "${ORGANIZATION:TEXT}"]
     }, {
      "name": "api_secret_key",
      "label": "Local ThreatConnect API Secret Key",
      "sequence": 2,
      "encrypt": true,
      "required": true,
      "validValues": ["${USER:KEYCHAIN}", "${ORGANIZATION:KEYCHAIN}"]
     }, {
      "name": "owner",
      "label": "Destination Owner",
      "sequence": 3,
      "required": true,
      "type": "choice",
      "validValues": ["${OWNERS}"]
     }, {
      "name": "remote_api_access_id",
      "label": "Remote ThreatConnect API Access ID",
      "sequence": 4,
      "required": true,
      "validValues": ["${USER:TEXT}", "${ORGANIZATION:TEXT}"]
     }, {
      "name": "remote_api_secret_key",
      "label": "Remote ThreatConnect API Secret Key",
      "sequence": 5,
      "encrypt": true,
      "required": true,
      "validValues": ["${USER:KEYCHAIN}", "${ORGANIZATION:KEYCHAIN}"]
     }, {
      "name": "remote_api_path",
      "label": "Remote ThreatConnect API Path",
      "sequence": 6,
      "required": true,
      "default": "https://api.threatconnect.com",
      "validValues": ["${USER:TEXT}", "${ORGANIZATION:TEXT}"]
     }, {
      "name": "remote_owner",
      "label": "Remote Owner",
      "sequence": 7,
      "required": true
     }, {
      "name": "apply_threat_assess_rating",
      "label": "Apply ThreatAssessRating from Remote Owner",
      "type": "Boolean",
      "sequence": 8
     }, {
      "name": "apply_rating",
      "label": "Apply Rating from Remote Owner if ThreatAssessRating is not Available ",
      "type" : "Boolean",
      "sequence" : 9
     }, {
      "name": "apply_threat_assess_confidence",
      "label": "Apply ThreatAssessConfidence from Remote Owner",
      "type": "Boolean",
      "sequence": 10
     }, {
      "name": "apply_confidence",
      "label": "Apply Confidence from Remote Owner if ThreatAssessConfidence is not Available",
      "type" : "Boolean",
      "sequence": 11
     }, {
      "name": "apply_tags",
      "label": "Apply Tags from Remote Owner",
      "type": "Boolean",
      "sequence": 12
     }, {
      "name": "apply_auto_enrich_tag",
      "label": "Apply 'AutoEnriched' Tag",
      "type": "Boolean",
      "sequence": 13
     }, {
      "name": "apply_proxy_tc",
      "label": "Apply Proxy to Local API Connection",
      "type": "Boolean",
      "sequence": 14,
      "default": false
     }, {
      "name": "apply_proxy_ext",
      "label": "Apply Proxy to Remote API Connection",
      "type": "Boolean",
      "sequence": 15,
      "default": false
     }, {
      "name": "logging",
      "label": "Logging Level",
      "sequence": 16,
      "default": "info",
      "type": "choice",
      "validValues": ["debug", "info", "warning", "error", "critical"]
     }]
    }

+-------------+------------------------------------------------------------------------------------+
| Line Number | Description                                                                        |
+=============+====================================================================================+
| 2           | The **programVersion** is 1.0.0. This value is rendered in the Apps listing for    |
|             | System Administrators.                                                             |
+-------------+------------------------------------------------------------------------------------+
| 4           | The **programMain** will direct the Job Executor to run this App as a main module. |
+-------------+------------------------------------------------------------------------------------+
| 6           | The **runtimeLevel** for this App is **Organization**. This App will allow Jobs    |
|             | to be configured only for an organization (assuming that the System Administrator  |
|             | has provisioned the organization).                                                 |
+-------------+------------------------------------------------------------------------------------+
| 8           | This line is the start of the **params** array. The contents in this array are     |
|             | solely for parameter definitions.                                                  |
+-------------+------------------------------------------------------------------------------------+
| 9–13        | This parameter describes the **api_access_id** argument for the App. The App will  |
|             | be passed an argument called **--api_access_id** at execution time. The label in   |
|             | the Job Wizard will be **Local ThreatConnect API Access ID**. Since the sequence   |
|             | is defined as **1**, this parameter will be the first parameter displayed in the   |
|             | Job Wizard. This parameter is required, and the user can benefit from user- and    |
|             | organization-level plain-text variables, if defined. Otherwise, the user is        |
|             | allowed to enter free-form text (the default type if no variables are defined).    |
+-------------+------------------------------------------------------------------------------------+
| 35–40       | This parameter describes the **remote_api_secret_key** argument for the App. The   |
|             | App will be passed an argument called **--remote_api_secret_key** at execution     |
|             | time. The label in the Job Wizard will be **Remote ThreatConnect API Secret Key**. |
|             | This parameter will be the fifth parameter in the Job Wizard **Parameters** panel. |
|             | Since the parameter is set to **encrypt**, the input field will be displayed as a  |
|             | password with a masked value. Encrypted parameters will also be stored in          |
|             | encrypted form in the database. At runtime, the decrypted password will be passed  |
|             | to the App. Finally, the user can benefit from user- and organization-level        |
|             | keychain variables, if defined. Otherwise, the user is allowed to enter free-form  |
|             | password text.                                                                     |
+-------------+------------------------------------------------------------------------------------+
| 65–68       | This parameter describes the **apply_threat_assess_confidence** Boolean argument   |
|             | for the App. The App will be passed an argument called                             |
|             | **--apply_threat_assess_confidence** at execution time, only if the user selects   |
|             | this value in the Job Wizard. The Job Wizard will display a label called **Apply   |
|             | ThreatAssessRating from Remote Owner**, along with a checkbox. The argparse style  |
|             | flag (without an argument) and the checkbox displayed in the Job Wizard are        |
|             | dictated by the Boolean type in the parameter definition. This parameter will be   |
|             | the eigth parameter in the Job Wizard **Parameters** panel.                        |
+-------------+------------------------------------------------------------------------------------+
| 98–103      | This parameter describes the **logging** argument for the App. The App will be     |
|             | passed a parameter named **--logging** with a string argument. The                 |
|             | **Logging Level** label will be displayed in the Job Wizard. This parameter will   |
|             | be the sixteenth (and last) parameter in the Job Wizard **Parameters** panel. The  |
|             | type for this parameter is **Choice**, and the definition dictates that a valid    |
|             | value for this parameter is one of **debug**, **info**, **warning**, **error**,    |
|             | or **critical**. The user will not be able to edit this drop-down list, and the    |
|             | default value for new Jobs will be logging-level info.                             |
+-------------+------------------------------------------------------------------------------------+

Java® and JavaScript® are registered trademarks of the Oracle Corporation.
