# Release Notes

## 4.0.11

-   APP-5036 - [Services] Updated message broker connection to not set tls_version
-   APP-5037 - [API] Updated V3 API to include new endpoints and/or updates to existing endpoints
-   APP-5055 - [Services] Updated Paho MQTT library and message broker reconnect logic
-   APP-5067 - [Services] Fixed issue with redis connection on each new thread
-   APP-5068 - [Batch] Added cleaner to batch submit; deduplication and merging of indicators and groups, auto truncate of attribute values, deduplication of attributes
-   APP-5072 - [Services] Applied PR #356
-   APP-5077 - [API] Updated V3 objects to allow setting a request timeout via property
-   APP-5094 - [API] Added filesystem cache dict for attribute_types, owners, owner_roles, system_roles, users, and user_groups
-   APP-5101 - [Inputs] Updated the inputs module to set the tempfile.tempdir to be the temp directory passed in by the Platform

## 4.0.10

-   APP-4969 - [Util] Updated regex patterns for playbook to support "Global" app type
-   APP-4974 - [Transform] Updated transform lastSeen mapping to look for appropriate field

## 4.0.9

-   APP-4825 - [Token] Updated token logic to handle new long-lived tokens
-   APP-4846 - [Transform] Added support for Batch API update which enables top-level associations
-   APP-4851 - [Util] Updated regex patterns for Playbook and TC variable to be more specific
-   APP-4852 - [API] Updated API logic to send query params in body when length exceeds max characters
-   APP-4866 - [Transform] Added Support for "Severity" and "Status" fields to Case
-   APP-4868 - (PREVIEW) [Transform] Added support for producing v3 API format
-   APP-4869 - [Inputs] Added strip() option to always_array input validation
-   APP-4870 - [Transform] Loosened restrictions for custom function transform definition
-   APP-4886 - [API] Updated V3 API to include new endpoints and/or updates to existing endpoints
-   APP-5100 - [Mitre] Updated MITRE tag module to add a filesystem cache property

## 4.0.8

-   APP-4717 - [API] Updated V3 API to include new endpoints (exclusionList, etc)
-   APP-4740 - Migrated to "uv" for package management
-   APP-4741 - Switched linters to "ruff" (including linting fixes)
-   APP-4743 - [API] Added support for "conditional-read-only" fields
-   APP-4744 - [API] Added support for v2 batch association changes
-   APP-4769 - [Inputs] Updated EditChoice input type to handle new value pattern
-   APP-4806 - [API] Updated stage_assignee method for cases and tasks

## 4.0.7

-   APP-4601 - [Pleb] Added jmespath custom functions to pleb to centralize functionality
-   APP-4604 - [Transform] Added standard processing functions class
-   APP-4605 - [Transform] Normalized the way null/empty values are handled in transforms (includes '')
-   APP-4620 - [Transform] Added structured/contextualized exceptions to transform
-   APP-4632 - [Transform] Added support for attribute.pinned field
-   APP-4640 - [API] Updated API hashing method to use SHA256 for FIPS compliance
-   APP-4656 - [Transform] Refactored how the custom predefined function works

## 4.0.6

-   APP-4472 - [API] Added NAICS industry classification module
-   APP-4482 - [API] Updated transforms to support new static methods
-   APP-4520 - [Util] Fixed TCEX string operations trim method
-   APP-4521 - [API] Updated support for IR endpoints
-   APP-4522 - [API] Updated batch module to support external date fields

## 4.0.5

-   APP-4442 - [Mitre] Updated MITRE module to support default value and make logging optional
-   APP-4443 - [API] Updated multiple API modules to be cached properties
-   APP-4444 - [Util] Replaced inflect package with inflection package
-   APP-4445 - [Util] Updated utils module to use inflection for case conversion

## 4.0.4

-   APP-4307 - [API] Added support for paginating indicator custom associations
-   APP-4334 - [API] Fixed issue where transform methods wasn't being called if value was not a string
-   APP-4380 - [API] Added support for external date fields to TI Transform model
-   APP-4381 - [Logging] Fixed API logging issues
-   APP-4383 - [API] Updated TC API module for changes in the V3 API
-   APP-4400 - [Input] Added support for KeyValue input type with None value
-   APP-4401 - [API] Fixed issue with Assignee model not calculating appropriate model type

## 4.0.3

-   APP-4245 - [Inputs] Added support for secure Redis (SSL and User/Pass)
-   APP-4246 - [Playbook] Removed support for AOT execution

## 4.0.2

-   APP-4155 - [API] Added Mitre Attack module for lookup by id or name
-   APP-4175 - [API] Updated API to support TC 7.3 API changes
-   APP-4187 - [Playbook] Updated inputs to support TC variable nested in a Playbook variable (Key Value List)

## 4.0.1

-   APP-4055 - [API] Updated v3 gen body to allow 0 and false in body
-   APP-4056 - [API] Updated Transforms to Support Email Group Type
-   APP-4057 - [Logging] Added lock to sensitive filter to fix concurrent update exception
-   APP-4075 - [APP] Added support for System App type
-   APP-4107 - [Config] Updated config submodule (tcex.json model) to support legacy App Builder Apps
-   APP-4108 - [API] Removed max_length and min_length from TI models

## 4.0.0

-   APP-3910 - [TcEx] Updated typing hint to Python 3.11 standards
-   APP-3911 - [TcEx] General code enhancement
-   APP-3914 - [TcEx] Restructured code for better programming interface
-   APP-3918 - [Inputs] Added App type specific models to use in app_inputs.py file in templates
-   APP-3925 - [CLI] Split CLI tools into a new project (tcex-cli)

## 3.x

### 3.0.9

-   APP-3943 - [API] Update Transforms to Support Email Group Type
-   APP-3981 - [API] Updated v3 gen body to allow 0 and false in body
-   APP-3972 - [Logging] Add lock to sensitive filter to fix concurrent update exception
-   APP-3993 - [KVStore] Added Redis password support

### 3.0.8

-   APP-3899 - [CLI] Updated error handling on CLI when downloading template files
-   APP-3900 - [CLI] Updated proxy support for CLI
-   APP-3906 - [CLI] Don't create requirements.lock file if any errors occurred during tcex deps.
-   APP-3922 - [API] Update TI Transforms to treat event_date field on some group types as a datetime transform.

### 3.0.7

-   APP-3859 - [API] Enhancements for ThreatConnect 7.x

### 3.0.6

-   APP-3857 - [CLI] Updated spectool for general improvements and fixes
-   APP-3862 - [Services] Updated request handling for Service Apps to process with a threadpool
-   APP-3863 - [API] Updated url() method in object_abc to resolve by id, xid, or summary when needed
-   APP-3866 - [API] Updated TQL as_str to use value for TQLOperators instead of name
-   APP-3867 - [CLI] Updated template commands to support nested directories
-   APP-3884 - [TcEx] Removed unused package dependencies
-   APP-3885 - [Logging] Added logging of specific environment variables

### 3.0.5

-   APP-3766 - [API] Added support for Security Labels on Attributes
-   APP-3775 - [Playbooks] Updated variable pattern regex to better handle mix variables types
-   APP-3776 - [CLI] Updated spectool for general improvements and fixes
-   APP-3805 - [API] Added TI Transforms module used to map a TI object to TC Batch or V3 format
-   APP-3810 - [Services] Added Support for Feed Service Apps
-   APP-3822 - [TcEx] Added type hints to cached_property, scoped_property, and registry to enable intellisense
-   APP-3825 - [API] Updated date format on TQL filters used in V3 api
-   APP-3826 - [Utils] Updated file operations module with more helper methods
-   APP-3827 - [Inputs] Updated sensitive.value property to address issue with latest requests module
-   APP-3831 - [API] Updated v3 base models to match TC 6.7.x documented structure
-   APP-3837 - [Decorators] Updated benchmark decorator

### 3.0.4

-   APP-3582 - [CLI] Updated spectool to automatically sort release notes by version when creating readme.md
-   APP-3586 - [CLI] Updated spectool to ignore outputPrefix for non-playbook apps
-   APP-3587 - [CLI] Updated spectool README.md generation for outputs
-   APP-3610 - [CLI] Updated spectool for general improvements and fixes
-   APP-3750 - [Batch] Updated batch_submit method to accept content as dict or string
-   APP-3751 - [API] Updated API module for new case filters (cal_score, missing_artifact_count, threat_assess_score)
-   APP-3752 - [API] Updated API module for file action and file occurrence support
-   APP-3753 - [API] Updated API module for new task filter (missing_artifact_count)
-   APP-3748 - [Inputs] Added result Limit on resolving magic variables
-   APP-3747 - [API] Added support for Group -> Victim Asset Associations
-   APP-3753 - [API] Updated API module for new task filter (missing_artifact_count)
-   APP-3754 - [API] Updated group_model to address API spec discrepancy
-   APP-3756 - [KeyValue] Added KeyValueMock, an implementation of KeyValueABC only for testing and running apps locally
-   APP-3757 - [AppConfig] Updated inputs to support external Apps (no install.json)
-   APP-3758 - [Token] Updated exit module to not invoke token thread for external Apps

### 3.0.3

-   APP-3489 - [CLI] Fixed issue with invalid tuple in help string
-   APP-3522 - [Session] Fixed issue in TC session method for passing boolean values (verify)
-   APP-3498 - [CLI] Fixed CLI file_hash reference error
-   APP-3532 - [CLI] Update spectool command to manage package name
-   APP-3533 - [CLI] Multiple fixes and tweaks to spectool
-   APP-3544 - [CLI] Updated spectool to exclude serviceConfig inputs from layout.json file
-   APP-3549 - [CLI] Updated spectool to exclude hidden inputs from layout.json file

### 3.0.2

-   APP-3456 - [Batch] Added support for the following group types: Attack Pattern, Course of Action, Malware, Tactic, and Tool
-   APP-3459 - [CLI] Added support for deprecated_apps in spectool when generating install.json
-   APP-3468 - [Pleb] Fix ScopedProperty to properly invoke it's wrapped function
-   APP-3470 - [Logging] Update logging filter to handle empty sensitive values
-   APP-3471 - [Session] Updated external session to better support Retry-After for non compliant API providers
-   APP-3472 - [CLI] Updated package command to add runtimeVariables to features in install.json
-   APP-3473 - [Playbooks] Added a feature to playbooks module to write additional data to KV store for test validation

### 3.0.1

-   APP-3432 - [CLI] Fixed issue where numeric values are getting stripped from input name during validation
-   APP-3433 - [CLI] Fixed issue where class names are getting improperly title cased when generating app_inputs.py
-   APP-3434 - [CLI] Added validation to spectool to ensure input names are unique
-   APP-3443 - [CLI] Fixed logging issue on error message for validate feature
-   APP-3448 - [AppConfig] Added entry to spec file for storing local notes
-   APP-3450 - [CM] Updated Case Management as_entity method
-   APP-3451 - [Inputs] Add Case Management field types to use in app_inputs.py file
-   APP-3452 - [Inputs] Added support for only_fields (replacing only_value) parameter on entity_input validation
-   APP-3453 - [CM] Updated CM logic to better handle JsonNode types defined by TC OPTIONS endpoint
-   APP-3454 - [CLI] Fixed issue with Retry entry when generating spec files

### 3.0.0

> New docs site: https://threatconnect.readme.io/docs/overview

-   APP-2294 - [TI] Added support for V3 TI API
-   APP-3403 - [TI] Added support for Last Modified field on Groups (TC >=6.5.0)
-   APP-3028 - [CM] Updated Case Manage V3 modules to use datamodels for consistency with TI module
-   APP-3402 - [CM] Added support for CM/TI links (TC >=6.5.0)
-   APP-2296 - [Inputs] Changed inputs model logic to use datamodels for all App types
-   APP-3146 - [Inputs] Added support to mask sensitive App inputs/outputs
-   APP-2486 - [CLI] Replace old CLI commands with single "tcex" command
-   APP-3408 - [CLI] Added spectool feature to CLI command
-   APP-2385 - [Utils] Updated datetime methods to use Arrow (https://github.com/arrow-py/arrow) package
-   APP-2485 - [Batch] Updated writer/submit methods for better support
-   APP-3411 - [Services] Added support for UpdateTriggerValue message in service Apps (TC >=6.5.0)
-   APP-2488 - [TI] Moved common TI methods to new ti_utils module
-   APP-2434 - [TcEx] Added support for protecting sensitive values in Apps and framework
-   APP-2489 - [TcEx] Added typing hints to public methods
-   APP-3346 - [TcEx] Added support for exit code of 4 (hard fail/no retry) for playbook Apps
-   APP-3347 - [TcEx] Change message.tc (exit message) behavior to rewrite file on each execution
-   APP-2660 - [AppConfig] Updated install.json module to fully support all feature types
-   APP-3353 - [AppConfig] Added support for new deprecatesApps and output.encrypt fields in the install.json
-   APP-3389 - [AppConfig] Added support for Action based retries in Playbook Apps
-   APP-3014 - [API] Updated path structure of all TC API module code
-   APP-2487 - [Docs] Moved all documentation to hosted site
-   APP-3343 - [STIX] Moved STIX module to new repo
-   APP-2292 - [Testing] Moved App testing framework to new repo
-   APP-2295 - [Templates] Moved App templates to new repo

## 2.x

### 2.0.28

-   APP-3325 - [Token] - Added proxy support to token renewal (ENV Server).

### 2.0.27

-   ESUP-212 - [CM] - Added support for both the read-only and readOnly properties.
-   APP-3200 - [CM] - Added support for PDF download in the CM module.

### 2.0.26

-   APP-3130 - [TI] - Added ability to iterate over all Tags currently in system.
-   APP-3149 - [Inputs] - Added support for resolving FILE, TEXT, and KEYCHAIN values [TC 6.4].
-   APP-3147 - [CM] - Updated artifact_filter property to excluded when using the to_dict method.
-   APP-3184 - [Session] Updated user agent on TC and external sessions to be include TcEx version and App name/version.
-   APP-3185 - [CLI] Added timeout to tclib when running the pip install command (App Builder).
-   APP-3187 - [CM] Updated CM module for new fields and filters.

### 2.0.25

-   APP-3069 - [Batch] Added support for new group types.
-   APP-3133 - [Dep] Limited tzlocal dependency < 3.0.
-   APP-2981 - [CM] Added support for attributes.

### 2.0.24

-   APP-3016 [Session] Updated tc_session to better evaluate the auth method.
-   APP-3017 [Testing] Added support for TCBatch to the testing framework.
-   APP-3023 [CLI] Updated tcpackage command to remove any nested zip files in a project.

### 2.0.23

-   APP-2942 [TI] - Added support for 6 new group types (supported in TC 6.3).
-   APP-2943 [CLI] - Updated tcpackage to fix issue with erroneous excludes.
-   APP-2944 [STIX] - Added support for Email Subject indicator type in STIX module.
-   APP-2958 [CLI] - Updated the tcvalidate command to support the new EditChoice input type (supported in TC 6.3).

### 2.0.22

-   APP-2662 [STIX] Added several STIX object mapping types in model.py.
-   APP-2665 [Testing] Updated session recording to fix issue in STIX module.
-   APP-2711 [STIX] Updated STIX parser to only support single pattern indicators.
-   APP-2712 [TcEx] Updated adding of signal handler to catch when added to non-main thread.
-   APP-2717 [TI] Updated pagination logic for TI module.

### 2.0.21

-   APP-2475 [Batch] Fixed batch method signature in tcex.py.
-   APP-2476 [Batch] Fixed tag and security label write mode properties in batch submit module.

### 2.0.20

-   APP-76 [Batch] Added tagWriteType and securityLabelWriteType to batch module (settings).
-   APP-2469 [Batch] Added batch writer and batch submit modules to support Web API Service Apps.
-   APP-2329 [STIX] Updated module to parse `threat-actor` from STIX object.
-   APP-2437 [STIX] Updated module to write https url indicator to batch files.
-   APP-2438 [STIX] Updated module to parse objects with multiple simultaneous patterns.
-   APP-2462 [CLI] Updated `tcpackage` CLI command to retain smtpSettings feature.
-   APP-2463 [Service] Improved API Service response body handling.
-   APP-2467 [Service] Added broker test message for Service Apps when heartbeats are missed.
-   APP-2457 [Session] Updated session methods to use default_args instead of args.
-   APP-2465 [Session] Added methods for sessions for multiprocess support in Apps.
-   APP-2466 [TcEx] Updated signal handling logic to not exit with error when thread is not MainThread.
-   APP-2464 [TI] Updated TI module to work in forked instance.
-   APP-2305 [Testing] Added hash_eq operator to testing framework.
-   APP-2459 [Testing] Updated testing framework to properly support Apps using multi-choice inputs and permutations.

### 2.0.19

-   APP-2044 - [Testing] When generating test profiles with --negative, environments will be copied from base profile and "negative" appended.
-   APP-2128 - [Playbook] Accept any iterable for array types when creating outputs.
-   APP-2129 - [Playbook] Enhance add_output() to add None values to array types when append=True.
-   APP-2130 - [CM] Add forward-reference type hints.
-   APP-2140 - [CLI] Add missing file for API Service template.
-   APP-2186 - [KVStore] Add parameter to disable decoding of value read by read().
-   APP-2219 - [CLI] update tctest to allow user to re-enter choice inputs if they enter a bad value.
-   APP-2228 - [CLI] Add several validations for feed job apps.
-   APP-2179 - [Service] Add support for Acknowledge commands.
-   APP-2180 - [Input] Updated resolved_args method to properly handle resolving arguments that come in as a list.
-   APP-1940 - [Profile] Updated merge_inputs method to resolve playbook variables for permutation check.

### 2.0.18

-   APP-1829 - [Session] Added logic to use http instead of https for proxy.
-   APP-2044 - [Testing] Enhance tctest --negative to copy environments from base profile and add 'negative'.

### 2.0.17

-   Update setup.py package_data to include STIX parser lark file.
-   APP-1829 - [Session] Added logic to attempt to handle "[SSL: WRONG_VERSION_NUMBER] wrong version number" error new to urllib3.

### 2.0.16

-   APP-1807, APP-1801 - [STIX] Remove dependency on Dendrol and replace with lark parser.

### 2.0.15

-   APP-891 - [STIX] Added additional support for consuming and producing STIX documents.
-   APP-1212 - [Testing] fixed output deletion issue for skipped test when --merge_outputs is used.
-   APP-1244 - [Testing] Added the is_json operator to assist in testing validation.
-   APP-1406 - [Testing] Fixed testing issue centered around the `validation_criteria` field present during bulk tests.
-   APP-1407 - [Testing] Fixed issue encountered when `validation_criteria` is set in a test profile (apps that use batch).
-   APP-1413 - [Testing] Converts option inputs that have a value of null to use #App:1234:null!String.
-   APP-1641 - [Batch] Fixed issue that batch delete that prevented single submission or last submission from working.
-   APP-1642 - [Service] Increased tc_svc_broker_conn_timeout arg to 60 to address disconnect issue in API service.
-   APP-1643 - [Template] Added "no-commit-to-branch" feature to the pre-commit configuration.
-   APP-1760 - [KVStore] Updated module to support new endpoint for PLAT-1237 in support of service Apps running on MEO.

### 2.0.14

-   APP-1394 - [Batch] Updated batch data processing to handle max sizes appropriately.

### 2.0.13

-   APP-1296 - [Session] Updated external session retry to accept a URL for retry mount.
-   APP-1366 - [Batch] Fixed issue in batch where self.\_file_threads was not getting updated appropriately.

### 2.0.12

-   APP-1126 - [Logger] Compress backup log files and increase backup count to 25.
-   APP-1127 - [Batch] Fixed issue with recursion when having a large number of associations.
-   APP-1128 - [Batch] Updated DEBUG feature to assist in testing batch module..
-   APP-1129 - [Batch] Added support for batch_max_size to truncate the batch job at ~75Mb.
-   APP-1130 - [Batch] Removed file_contents getter and setter method.
-   APP-1131 - [Session] Updated request_to_curl method in Utils module to truncate body and not write body to disk.
-   APP-1262 - [AppFeature] Update advanced_request module to take output_prefix as an arg.
-   APP-1263 - [Session] Updated session module to only log curl command when request receives an invalid response or enabled globally.
-   APP-1264 - [Logger] - Updated logger modules to set default encoding to "UTF-8" when no value set at the OS level.
-   APP-1266 - [Utils] Update utils datetime module to include a chunk_date_range method to be used in job Apps that need to break request into smaller time-frames.
-   APP-1267 - [Batch] Add batch callback method to batch module to allow downloading/processing of data while batch job polls for status.
-   APP-1268 - Update the default temp directory to use an OS appropriate value.
-   APP-1272 - [AppConfig] Removed feature to update install.json and layout.json for advanced_request.
-   APP-1280 - [Session] Add ability to mask the body when logging curl command.

### 2.0.11

-   APP-1107 - Added MITRE ATTACK Utils methods to return the properly formatted tag value.
-   APP-1119 - Updated to batch module to handle recursion issue with integrations that have a large number of group associations.

### 2.0.10

-   APP-890 - Added discoverTypes to Ready command for API Services.
-   APP-939 - Restructured Service module to better support API Services.
-   APP-943, APP-1027, App-1036 - Updated ReadArg and IterateArgs decorators for better transform and validator support.
-   APP-944 - Added rate limit and 429 (too-many-requests) in external session module.
-   APP-964 - Updated inputs module to allow duplicate args (advanced request requirement).
-   SUP-8557 - Updated how the Threat Intelligence module was adding observations to ThreatConnect objects.
-   APP-865, APP-1021, APP-1030, APP-1086 - Added minor enhancements.

#### Testing framework

-   APP-921 - Updated default operator rule for test cases.
-   APP-926 - Updated profile generation to not add String type to all inputs.
-   APP-935 - Updated tcinit to include custom_feature.py when missing.
-   APP-936 - Updated test handling when incorrect stage data is provided.

### 2.0.9

-   APP-849 - Updated request_to_curl method to handle proxy values properly.
-   APP-852 - Moved jmespath package from dev dependencies to standard dependencies.

### 2.0.8

-   APP-796 - Updated Advanced Request Method to always write output variable.
-   APP-813 - Updated datastore and cache modules; renamed ttl_minute to ttl_seconds, added handling of 0 or null ttl_second value.
-   APP-815 - Updated session_external to not raise RetryError.
-   APP-816 - Updated tcinit to not fail when no tcex.json file is present.

### 2.0.7

-   APP-780 - Added truncate method to Utils module.
-   APP-786 - Updated logger to address TypeError exception.
-   APP-789 - Updated pre-commit configuration for App templates.
-   APP-790 - Added new Advance Request feature for App that utilize a remote API.
-   APP-791 - Updated session and session_external to not require an instance of tcex.
-   APP-792 - Updated services module to support sending failed message on ack.
-   APP-793 - Updated session to not create curl logs when sending API logs.

#### Testing framework

-   APP-77 - Added mechanism to tell if Webhook service Apps fired in testing framework.
-   APP-88 - Added "magic" variable expansion for tctest interactive mode.
-   APP-715 - Updated validation for tags to be case insensitive in testing framework.
-   APP-746 - Updated to address issue with email validation in testing framework.
-   APP-769 - Added rargs property to profile for custom methods in testing framework.

### 2.0.6

-   APP-79 - Added curl command to the log file at debug level to assist in troubleshooting.
-   APP-80 - Added support for **comment** in testing profile.
-   APP-87 - Added check for invalid values in profile for Boolean inputs.
-   APP-102 - Added pytest fixture for testing sessions.
-   APP-557 - Added update logic for profiles to convert static String inputs to Staged KVStore variables.
-   APP-561 - Updated pre-commit template file to support large files on commit.
-   APP-676 - Updated --interactive mode to support all input types.
-   APP-677 - Added --negative flag to tctest command to auto-generate negative test profiles.
-   APP-78, APP-82, APP-83, APP-84, APP-85, APP-86, APP-87, APP-106, APP-219 - Enhanced testing framework.

### 2.0.5

-   Updated testing framework to decouple App version of TcEx and testing version.
-   Updated deepdiff validation method to better handle OrderedDicts.
-   Added simple caching to env_store.
-   Added session recording & playback for testing framework.
-   Added automatic staging of inputs to kvstore for testing framework.
-   Added additional support for batch in testing framework.

### 2.0.4

-   Updated decorator method logging.
-   Updated testing framework validation template to support dynamic output variable.
-   Updated testing framework validation template to validate output variable consistency.
-   Updated profile module to support variable from env store server.
-   Updated OnException decorator to log traceback.
-   Multiple enhancement and fixes to testing framework.

### 2.0.3

-   Added `is_variable()` method to Playbook module.
-   Updated ReadArgs decorator to return None when arg doesn't exist.
-   Updated ReadArgs to not log input value.
-   Added new Permutations class to app_config_object module.
-   Added new Profile and ProfileInteractive Classes to app_config_object module.
-   Added new TcexJson Class to app_config_object module.
-   Moved all testing template generation/download logic to consolidated templates.py file.
-   Added schema management to InstallJson class.
-   Added schema management to LayoutJson class.
-   Multiple updates for App testing framework.
    -   Updated testing framework to support permutations for Service Apps
    -   Added **--replace_exit_message** CLI flag for pytest to replace outputs for test cases
    -   Added **--replace_outputs** CLI flag for pytest to replace outputs for test cases
    -   Added **--merge_outputs** CLI flag for pytest to merge new outputs with existing outputs for test cases
    -   Profile schema is now managed and old profiles will be automatically updated
    -   Changed default run method for Service Apps to be subprocess instead of thread.
-   Updated **tcinit** CLI command.
    -   Removed **--action** CLI arg
    -   Added **--update** CLI arg to enable updates of non-customized template files
    -   Added **--migrate** CLI arg to enable migration of non-compliant PB Apps
    -   Added **--layouts** CLI arg to allow for dynamic creation of example layout.json based on install.json
    *   The **tcinit** command now store the template in the tcex.json file to allow easier updates
-   Updated **tcpackage** CLI command.
    -   Moved logic that updates the install.json to the InstallJson class
    -   Updated to use InstallJson and LayoutJson objects
-   Updated **tctest** CLI command.
    -   Added **--interactive** flag to allow for dynamic creation of testing profile.
    -   Updated to use new Profile Class and Template Classes
-   Updated **tcvalidate** CLI command.
    -   Updated to use InstallJson and LayoutJson objects
    -   Updated validation logic for layout.json
-   Multiple updates to App templates to remove subprocess.
    -   Added `run()` method to run.py template for job and playbook Apps
    -   Added app_lib.py dependencies for all App types
    -   Updated **main**.py to call run method of run.py
-   Added logging of TcEx path.
-   Updated Utils Class to no longer require tcex instance.

### 2.0.2

-   Updated requirement for stdlib-list to >= 0.6.0 to support Python 3.8.
-   Updated test cases to call setup/teardown instead of start/done.
-   Added pydocstyle as a development dependency.
-   Removed isort from App template pre-commit file.
-   Multiple updates for templates and testing logic for Service Apps.
-   Issue-103 - added support for ThreatConnect ThreatIntelligence File Actions.
-   Issue-107 - added check for missing config file for external Apps.
-   Issue-110 - added example for associations using Threat Intelligence Module.
-   Issue-111 - updated trace logger method for Python 3.8.x changes.

### 2.0.1

-   Updated bin module to delete reference to removed profile and run files.
-   Updated setup.py for long_description.
-   Updated README.md to include all dependencies.

### 2.0.0

-   Added support for ThreatConnect Case Management.
-   Added support for ThreatConnect Service Apps.
-   Updated templates to support changes in tcex 2.0.
-   Updated code to support Python 3.6+, removing support for all older versions of Python.
-   Removed old tcrun and tcprofile commands.
-   Breaking Change: Multiple updates to `playbook` module logic.
-   Breaking Change: Moved datetime methods in tcex.utils.xxx to tcex.utils.datetime.xxx.
-   Breaking Change: Reworked App decorators to improve usability.
-   Breaking Change: Renamed `start()` and `done()` methods in templates to `setup()` and `teardown()`.
-   Breaking Change: Removed `tcex.s()` method.
-   Breaking Change: Removed `tcex.data_filter` property and module.
-   Breaking Change: Removed `tcex.request` property and module.
-   Breaking Change: Removed `tcex.resources` property and module.
-   Breaking Change: Removed `tcex.safetag()` method.
-   Breaking Change: Removed `tcex.safeurl()` method.
-   Breaking Change: Updated `tcex.safe_indicator()` method input params.
-   Breaking Change: Updated `tcex.safe_url()` method input params.
-   Breaking Change: Updated `tcex.safe_tag()` method input params.

## 1.x

### 1.1.8

-   Improved support for TI module to support creating files given a unique_id.
-   Updates to playbook modules to remove logging affecting environment servers.

### 1.1.7

-   Updates to testing framework for custom validation.
-   Updates to the docs for multiple modules.
-   Multiple updates to testing framework.

### 1.1.6

-   Updated deleted() method of TI module to yield results instead of returning raw response.
-   Updates to testing framework for custom methods when testing profiles.
-   Updated inputs to ensure args provided via sys.argv take precedent over all other args.
-   Added new service_id arg for service Apps.
-   Added POC of session_external. Python requests session with auto-proxy configuration.
-   Updated excludes for tcpackage command for pytest report folders.

### 1.1.5

-   Updated validation module to handle local imports and shared modules.

### 1.1.4

-   Added additional support for v2 API endpoints.
-   Added support for new appId field in the install.json.
-   Updated validation command to better handle packages with nested modules.
-   Updated PB module to handle execution with no requested output variables.
-   Updated PB module to handle null values in BinaryArray.
-   Updated TI modules to better handle conversion to and from TCEntity.
-   Updated external App template to allow passing configuration in on TcEx() initialization.
-   Multiple updates for testing framework.

### 1.1.3

-   Added cache handler to logging module.
-   Updated args module to use dict input over sys.argv when possible.
-   Updated args module replaced required args with a default value when possible.
-   Updated testing module for args changes and more.
-   Updated logging add handler calls in multiple modules.
-   Renamed args module to inputs.
-   Removed reference to args in logging module.

### 1.1.2

-   Updates to token and args modules to better support testing framework and external Apps.
-   Added kwargs on tcex init for external Apps.
-   Updates to testing templates.

### 1.1.1

-   Moved registration of default token to default_args method to address issue with secure params.
-   Updated template files.
-   Updated build process for wheel files.
-   Updated permutations generation to include hidden inputs.

### 1.1.0

-   Restructured tcex modules into individual directories.
-   Added services module for service Apps.
-   Added token module to manage tokens for all types of Apps.
-   Moved token renewal from session to new token module.
-   Updated multiple module to simplify testing.

### 1.0.7

-   Updated logging formatter for issue in py2.
-   Updated test_case to automatically create profile output.

### 1.0.6

-   Reworked logging for the TcEx framework to provide better flexibility.
-   Updated logging of batch sizes to not log when there is not content.
-   Moved the logging of App info to the args call.
-   Added trace logging level (unsupported in platform currently).
-   Added new testing module using pytest.

### 1.0.5

-   Updated arg parsing to better handle delimited input strings for secureParams/AOT input.
-   Updated TI module to better handle filters and retrieving generic indicator/group types.
-   Updated logging initialization to ensure user provided log path is available before adding file handler.

### 1.0.4

-   Updated datastore module to prevent creating of empty record on index creation.
-   Updated batch module to support additional debugging features.

### 1.0.3

-   Updated playbook read for `\s` replacement issue in Python 3.7.
-   Updated utils `unix_time_to_datetime()` method to handle unix timestamps with milliseconds that are not floats.
-   Updated TI module with changes for indicators data.
-   Updated tcinit for temporary proxy fields names.

### 1.0.2

-   Updated **read_embedded** to escape newline characters in embedded string values

### 1.0.1

-   Updated **install.json** schema validation to ensure that **displayName** contains a minimum of three characters
-   Updated **read_embedded** to cast data value to a string
-   Made minor updates to the TI module

### 1.0.0

-   Added new Threat Intel (TI) module to interact with ThreatConnect REST API
-   Added support of "\s" characters to be replaced automatically with a space (" ") character on user string input in Playbook Apps
-   Added templates for external Apps
-   Updated **read_embedded method** to deserialize nested variables before replacement
-   Updated Utils module to better handle datetime timezone conversions

## 0.x

### 0.9.13

-   Updated **ReadArg** decorator to support `fail_on` parameter
-   Updated **IterateOnArg** decorator to support `fail_on` parameter and removed `fail_on_empty`
-   Updated `Datastore` module to support no ID for POST and GET methods

### 0.9.12

-   Added new **FailOnInput** decorator
-   Changed **FailOn** decorator to **FailOnError** with arg input changes to enable
-   Added additional logging to **IterateOnArg** decorator

### 0.9.11

-   Reverted change to Playbook module `read()` method for null value returned when Array is True

### 0.9.10

-   Updated App templates to call `parse_args()` from **init** method
-   Updated `IterateOnArg` decorator to take an addition default value
-   Updated `IterateOnArg` to exit or log when no data is retrieved from Redis
-   Updated `TcExRun` module to detect v3 profile args section by either optional or required field
-   Updated `TcExProfile` module to use new **layout.json** output logic and always display output variables unless display value exists and return negative validation

### 0.9.9

-   Added new `Cache` module
-   Added new `DataStore` module
-   Updated App templates to ignore or exclude definitions
-   Updated `tcprofile` **permutation_id** to handle 0 index
-   Updated `tcpackage` command to not add **commitHash** if value is None
-   Updated `tcvalidate` command to handle permission errors when using **pkg_resources**
-   Updated **install.json** schema to include **commitHash**

### 0.9.8

-   Fixed issue with `sqlite` being imported while not required for Apps
-   Updated `tcprofile` to better support App bundle projects

### 0.9.7

-   Updated :py:mod:`~tcex.tcex_args` module to parse injected params using a **=** separator instead of a space+ Updated `tcprofile` command to support permutations logic for Apps with **layout.json** conditional input parameters
-   Updated `tcprofile` command to update the profile schema to **v3**. Note that **app.arg** is now **app.arg.optional** and **app.arg.required**.
-   Updated `tcrun` arg parsing logic to use a **=** separator instead of a space
-   Updated Batch module to support new 5.8+ merge of file hash feature

### 0.9.6

-   Added a fix for `tcvalidate` output display statement validation
-   Updated **install.json** schema file
-   Updated `tclib` to error when environment variables are not available
-   Updated Batch module to handle **xid** as **str** for **py2** Apps

### 0.9.5

-   Enabled **package_data** in **setup.py** for JSON schema files

### 0.9.4

-   Switched from **setup.py package_data** to **MANIFEST.in** for JSON schema files

### 0.9.3

-   Added new `tcvalidate` command for App Builder
-   Added validation of **layout.json** schema, inputs, and outputs
-   Migrated JSON validation files from App to TcEx

### 0.9.2

-   Added new `FailOn` App decorator
-   Updated **run.py** in Playbook templates to handle **TypeError** on incorrect action
-   Updated `tcpackage` command to suggest proper fix for missing modules
-   Updated `tcrun` to handle null value in args

### 0.9.1

-   Fixed issue in `tcpackage` with handling errors
-   Updated `tcpackage` command to validate import module for **.py** file in project-root directory
-   Updated `tcpackage` moving **install.json** validation to top level
-   Updated `tcpackage` to support `--ignore_validation` arg. Using this flag will cause the command to not exit on validation errors.
-   Updated **install.json** schema file to support new `feedDeployer` Boolean field
-   Updated `run.py` template file to ensure proper paths are set for an App

### 0.9.0

-   Updated all optional args in Batch module for Group/Indicator objects to kwargs. This will allow easier updates for new values in the future.
-   Updated the decode arg on the read Binary/BinaryArray methods to be False by default. When set to True, the `read()` method cannot be used in some use cases.
-   Updated the Group and Indicator object in the Batch module to only produce random and unique xids when an xid is not provided. These objects will no longer produce a unique and reproducible xid.
-   Added new App templates and updated templates with new files and content
-   Added :py:mod:`~tcex.tcex_args` module to include all args related methods from the :py:mod:`~tcex.tcex` module
-   Updated :py:meth:`~tcex.tcex.TcEx.request` method to include proxy settings
-   Updated `tcprofile` to include an epilog with command instructions on environment setup **(> tcprofile -h)**
-   Updated `tcprofile` to split the args section to support "default" args and "app" args
-   Updated `tcinit` to support templates instead of types
-   Updated `tcinit` to include an epilog with template definitions **(> tcinit -h)**
-   Updated `tcinit` to download additional files required for building Apps
-   Updated `tcrun` to support update args schema in profiles
-   Removed `tcex.jobs()` module
-   Removed `tcex.request_external()` method
-   Removed `tcex.authorization()` method
-   Removed `tcex.authorization_hmac()` method
-   Removed `tcex._authorization_token_renew()` method
-   Updated **all** code to standard formatting and structure
-   Updated and restructured Documents

### 0.8.27

-   Added decorator to provide common methods for Playbook Apps.
-   Added logic to `tcpackage` to do basic syntax validation of `.py` and `.json` files
-   Added :py:meth:`~tcex.tcex_playbook.TcExPlaybook.add_output` and :py:meth:`~tcex.tcex_playbook.TcExPlaybook.write_output` methods to provide an alternative way to write Playbook output data
-   Added access to resolved args
-   Updated `tclib` logic for **lib_latest** symbolic link

### 0.8.26

-   Updated `tcinit` to include **migration** as an action to help convert non-App Builder compliant Apps
-   Updated Utils module for additional method to determine local timezone
-   Updated Utils module to output correct **total_weeks** value

### 0.8.25

-   Updated `tcinit` command CLI option `--upgrade` to download additional files
-   Updated `tcrun` command to use **dockerImage** parameter from **install.json** or profile
-   Updated `tcrun` command to support new **autoclear** value in profile
-   Updated `tclib` to create a symbolic link to the latest Python lib directory
-   Updated `tcpackage` command to add **commitHash** value to **install.json**
-   Updated :py:mod:`~tcex.tcex` module to log **commitHash** value
-   Updated the `.gitignore` file for App templates

### 0.8.24

-   Fixed GH issue #(60)
-   Updated App templates. Added **tc_action** logic to handle launching **action** methods in the App class
-   Added `--docker` flag to `tcrun` command to launch App in docker container

### 0.8.23

-   Updated Batch module to handle Attribute values of False
-   Added `read_array` method to Playbook module
-   Updated App templates to include **start** and **done** methods
-   Update **tcprofile** to create the **tcex.d** directory automatically

### 0.8.22

-   Removed `__slots__` on Batch module due to issues with Python 2
-   Updated **tcinit** and corresponding App templates

### 0.8.21

-   Added PDF method to Resource module for supported Group types
-   Added **task_id** method for Task class
-   Added **date_added** property to Indicator and Groups objects
-   Added **last_modified** property to Indicator objects
-   Updated **tcrun** for handling Binary/BinaryArray validation

### 0.8.20

-   Fixed deletion in Batch module for TC instances < 5.7

### 0.8.19

-   Removed **app.lock** logic
-   Updated **file_content** logic for Documents and Reports
-   Added `add_file()` method for batch Group objects
-   Added **playbook_triggers_enabled** parameter to Batch module (requires ThreatConnect 5.7)

### 0.8.18

-   Made minor change to batch poll
-   Updated Batch module `close()` method to check for xids-saved file existence before deletion

### 0.8.17

-   Added **app.lock** file to temp directory to ensure single execution

### 0.8.16

-   Removed debugging flag from Batch module and replaced with logic to control debug externally
-   Updated batch-poll method logic to poll more frequently
-   Update Resource module to allow the addition of a body when reading from the datastore

### 0.8.15

-   Added signal handler to tcex to gracefully handle interrupts
-   Added new `tcinit` command to download files required for a new App or update files in an existing App
-   Updated batch-poll method to automatically calculate poll interval. **REMOVED** interval-method parameter
-   Updated Batch module to raise error on batch-status poll timeout
-   Updated \***\*main**.py\*\* to version 1.0.2
-   Moved and added supporting file to **app_init** directory

### 0.8.14

-   Added :py:meth:`~tcex.tcex_batch_v2.TcExBatch.close` method to allow cleanup of temp files when batch job is done
-   Added global overrides for **halt_on_error** in Batch module
-   Fixed issue with token renewal not failing properly on error
-   Updated logging method to ensure all messages are logged to file
-   Updated logging method to skip API logging during token renewal
-   Changed tcrun to not use shell on Windows systems

### 0.8.13

-   Updated Batch module to use Submit Job/Submit Data for deletes
-   Replaced **tcex_develop** arg with branch arg for tclib command
-   Added :py:meth:`~tcex.tcex_batch_v2.TcExBatch.generate_xid` method to help generate a unique and/or reproducible xid
-   Added default value for Email score in Batch module

### 0.8.12

-   Added active property to Indicator type objects
-   Updated :py:meth:`~tcex.tcex_batch_v2.TcExBatch.save` method be best effort
-   Updated :py:meth:`~tcex.tcex_batch_v2.TcExBatch.submit_file` to handle None value being returned
-   Updated `attribute()` methods to handle unique values when using a formatter
-   Fixed issue with **--unmask** arg not working on tcrun command

### 0.8.11

-   Merged AOT feature in prep for 5.7
-   Added :py:meth:`~tcex.tcex.TcEx.install_json` method to load **install.json**, which is used in the injection method to determine the structure on the param values
-   Added :py:meth:`~tcex.tcex_batch_v2.TcExBatch.save` method to save batch data to disk to reduce memory usage of the App
-   Updated the logic in :py:meth:`~tcex.tcex.TcEx.default_args` method to handle both injecting secureParams and AOT params depending, on selected feature.
-   Updated :py:meth:`~tcex.tcex.TcEx.inject_params` method to be public and generic and to allow params to be injected manually
-   Updated :py:mod:`~tcex.tcex_redis` module to support additional Redis methods required for AOT
-   Updated :py:meth:`~tcex.tcex_playbook.TcExPlaybook.read_binary` and :py:meth:`~tcex.tcex_playbook.TcExPlaybook.read_binary_array` methods to support b64decode and decode params
-   Updated :py:meth:`~tcex.tcex_batch_v2.Report` module to make the Report file name optional for updates in 5.7
-   Updated examples in Documents
-   Fixed validation issues in tcrun

### 0.8.10

-   Updated **submit_create_and_upload** method to clear raw list after submission
-   Rewrote **results_tc** method to handle updates to key/value pairs
-   Updated tcrun to automatically create required directories
-   Updated tclib to support building tcex develop version with **--tcex_develop** CLI flag

### 0.8.9

-   Rewrote tcrun and tcprofile commands
-   Removed tcdata commands
-   Changed logging of unsupported args to only show when App retrieves args
-   Changed **read_binary_array** method to decode Redis data automatically

### 0.8.8

-   Updated :py:meth:`~tcex.tcex.TcEx.exit` methods to treat exit code of 3 as non-failure
-   Updated v2 Batch createAndUpload

### 0.8.7

-   Updated secure params injection to handle pipe-delimited multiple-choice values

### 0.8.6

-   Fixed issue with API logging not working when secure params are enabled
-   Fixed issue with API logging timestamp precision

### 0.8.5

-   Updated tcdata for Playbook variable creation during staging testing data
-   Updated tcex logging for level and removal of stream logger once API logger is initialized

### 0.8.4

-   Updated tcdata to handle binary array
-   Updated tclib command to support environment variables in **tcex.json** file
-   Added initial functionality for v2 Batch **create and upload**

### 0.8.3

-   Updated regex for Playbook variables

### 0.8.2

-   Updated Tcdata module for local testing
-   Updated Batch v2 API

### 0.8.1

-   Updated secureParams loading order
-   Updated :py:mod:`~tcex.tcex_logger` module
-   Updated :py:mod:`~tcex.tcex` module to only import modules when required
-   Moved :py:meth:`~tcex.tcex_utils.TcExUtils.inflect` to the Utils module
-   Updated documents for Metrics, Notifications, and Batch

### 0.8.0

-   Added **tcex.session** to provide access to the ThreatConnect API using Requests' native interface
-   Added :py:mod:`~tcex.tcex_batch_v2` module to replace the Jobs module starting in ThreatConnect 5.6
-   Added msg to :py:meth:`~tcex.tcex.TcEx.exit` methods
-   Changed :py:meth:`~tcex.tcex.TcEx.exit_code` method to a property with a setter
-   Changed :py:meth:`~tcex.tcex.TcEx.request` property to a method
-   Updated multiple methods to use :py:mod:`~tcex.tcex_session` instead of :py:mod:`~tcex.tcex_request`
-   Renamed Logger module to be consistent with other modules
-   Removed second arg from :py:meth:`~tcex.tcex.TcEx.expand_indicators` method
-   Removed owner parameter from :py:mod:`~tcex.tcex_resources.Datastore` module
-   Added deprecation warning for the following methods: :py:meth:`~tcex.tcex.TcEx.bulk_enabled`, :py:meth:`~tcex.tcex.TcEx.job`, :py:meth:`~tcex.tcex.TcEx.request_tc`, :py:meth:`~tcex.tcex.TcEx.epoch_seconds`, and :py:meth:`~tcex.tcex.TcEx.to_string`. These methods will be removed in version 0.9.0.
-   Cleaned up code, comments, and documentation
-   Added error code/message for all RuntimeError exceptions

### 0.7.21

-   Fixed issue with newstr when using quote() method in :py:meth:`~tcex.tcex.TcEx.safe_indicator`

### 0.7.20

-   Updated logging to log App name and other data
-   Added Notifications module for ThreatConnect 5.6+

### 0.7.19

-   Updated secure params injection to treat string value of True as Boolean/flag
-   Updated secure params to handle unicode values in py2
-   Updated Jobs module to use batch settings from args on init and to allow programmatic override of batch settings
-   Updated token renewal to handle issue with newstr

### 0.7.18

-   Updated Jobs module to not call safetag method when using Resource module
-   Updated Intrusion Set class in Resource module
-   Updated Group list to include new Group types
-   Added `upload()` and `download()` methods to Report class in resource module.
-   Added Task as a group type.
-   Added new secure params feature

### 0.7.17

-   Updated Utils module for handling naive datetime in py2
-   Added **to_bool()** method back to Utils module

### 0.7.16

-   Updated utils datetime methods to not require a timezone
-   Updated Tag class to urlencode tag value so slashes are supported
-   Updated safetag method to strip **^** from tag values
-   Changed modules dependency to use latest version instead of restricting to current version
-   Added Event, Intrusion Set, and Report Group types in preparation for TC > 5.6.0
-   Added metrics module to create and add metrics to ThreatConnect.
-   Added **deleted** endpoint for Indicators.

### 0.7.15

-   Updated Jobs module to delete by name when using replace for Groups
-   Updated token renewal to log more information on failure
-   Updated Playbooks read-binary array to better handle null values

### 0.7.14

-   Updated file Indicator class for proper handling of Attributes, Tags, and Labels
-   Updated :py:meth:`~tcex.tcex.TcEx.expand_indicators` method to use a new regex to handle more formats for file hashes and custom Indicators

### 0.7.13

-   Fixed issue with embedded variable matching during exact variable check

### 0.7.12

-   Updated :py:mod:`~tcex.tcex_resources.Resource` for py2 unicode issue in ipAddress module

### 0.7.11

-   Updated :py:mod:`~tcex.tcex_resources.Resource` module to automatically handle files hashes in format "md5 : sha1 : sha256"
-   Updated :py:mod:`~tcex.tcex_resources.Resource` module to reformat ipv6 addresses to same format as TC

### 0.7.10

-   Updated \***\*main**.py\*\* template with better logic to detect Python lib directory version
-   Updated regex patterns for variable matching in Playbook module
-   Updated Playbook module function in handling variables

### 0.7.9

-   Updated :py:meth:`~tcex.tcex_playbook.TcExPlaybook.read_embedded` method to better support embedded variables
-   Added **--report** arg to `tcrun` to output a JSON Report of profiles and run data
-   Added new JSON string comparison operator (jc/json compare) to `tcdata` to compare two JSON strings (requires DeepDiff to be installed locally)

### 0.7.8

-   Added **KeyValueArray** operator to `tcdata`, which allows searching for a single key/value entry in array
-   Updated functionality to replace non-quoted embedded variable to handle duplicate variables in **KeyValueArray**

### 0.7.7

-   Added new string comparison operator (sc) to `tcdata` that strips all white space before eq comparison
-   Added new functionality to :py:mod:`~tcex.tcex_playbook.TcExPlaybook` to replace non-quoted embedded variables in **Read KeyValueArrays**
-   Updated **Create KeyValue/KeyValueArray** methods to not JSON load when passed a string
-   Added :py:meth:`~tcex.tcex_utils.TcExUtils.any_to_datetime` method to return **datetime.datetime** object
-   Added :py:meth:`~tcex.tcex_utils.TcExUtils.timedelta` method to return delta object from two provided datetime expressions

### 0.7.6

-   Fixed issue with _newstr_ and dynamic-class generation

### 0.7.5

-   Updated all TcEx framework command-line interface (CLI) commands to use utf-8 encoding by default
-   Replaced usage of unicode with built-in str (Python 2/3 compatible
-   Replaced usage of long with built-in int (Python 2/3 compatible)
-   Update usage of **urllib.quote** to be Python 2/3 compatible

### 0.7.4

-   Updated :py:meth:`~tcex.tcex_resources.Resource.association_custom` to handle boolean values that are passed as strings
-   Updated :py:meth:`~tcex.tcex.TcEx._resource` method to handle boolean returned as strings from the API
-   Updated `tcdata` to properly delete Indicators when using `--clear` arg
-   Update the Log module to use **tcex** instead of **tcapp**

### 0.7.3

-   Added :py:mod:`~tcex.tcex_utils.TcExUtils` module with date functions to handle common date-use cases
-   Added DeepDiff functionality to `tcdata` for validating unsorted dictionaries and list
-   Updated `tcdata` to pull item from lists by index for easier comparison
-   Updated :py:meth:`~tcex.tcex_playbook.TcExPlaybook.read` method to allow disabling of automatically resolving embedded variables
-   Updated :py:meth:`~tcex.tcex_resources.Resource.association_custom` method to support file actions
-   Updated :py:meth:`~tcex.tcex_resources.File.file_action` method as alias to :py:meth:`~tcex.tcex_resources.Resource.association_custom`

### 0.7.2

-   Updated `tcdata` command for issue on sorting list in Python 3
-   Added update for **tcex.json** file to allow the App version to be specified instead of using **programVersion** from **install.json**

### 0.7.1

-   Added stub support for **associatedGroup** in Batch Indicator JSON
-   Updated the TcEx Job module to better handle Document uploads in Python 3
-   Updated TcEx Resource module to support query parameter list in the **add_payload()** method
-   Updated TcEx Request module to support query parameter list in the **add_payload()** method
-   Updated `tclib` to remove the old lib directory before creating the lib directory

### 0.7.0

-   Updated the TcEx framework to only build custom Indicator classes when working with custom Indicators
-   Updated TcEx Jobs module Group add logic to fix issue with skipping existing Groups
-   Updated TcEx Jobs module to handle **associatedGroup** passed as string or int when using **/v2**

> Important:: Breaking change to any App that uses the Direct Access method with a Custom Indicator type.

### 0.6.3

-   Fixed issue in `tcdata` when validating that data is not string type
-   Updated `tcprofile` to set type check to binary on binary data

### 0.6.2

-   Updated Playbook **create_binary** and **create_binary** array for to better support py3.
-   Updated `tcdata` to support Security Labels in staged data
-   Updated `tcdata` to support adding associations
-   Updated `tcdata` to support variable reference **#App:4768:tc.address!TCEntity::value** during validation

### 0.6.1

-   Updated `tcdata` to validate string as **string_types** for "is type" check using six modules
-   Added fix for code font not matching line numbers in the documents

### 0.6.0

-   Added :py:mod:`~tcex.tcex_resources.CustomMetric` module to :py:mod:`~tcex.tcex_resources.Resource` module
-   Renamed `_args` variable in **tcex.py** to `default_args`
-   Renamed `_parser` variable in **tcex.py** to `parser`
-   Cleaned up code (removed any Python 2.5-specific code)

### 0.5.23

-   Replaced use of `str()` in TcEx Playbook module
-   Updated `tcrun` to pass **data_owner** for each action on `tcdata`
-   Updated `tcdata` to stage TC data via `/v2` instead of batch
-   Updated `tcdata` write entity out as variable

### 0.5.22

-   Updated `tcprofile` to support new parameters
-   Updated `tcdata` to properly handle older **tcex.json** files
-   Updated :py:meth:`~tcex.tcex_playbook.TcExPlaybook.read_embedded` method to handle unicode error
-   Added additional logging to TcEx Job for logging API response

### 0.5.21

-   Added :py:meth:`~tcex.tcex.TcEx.job` association feature to handle Group-> Indicator and Group-> Group associations
-   Added :py:meth:`~tcex.tcex.TcEx.safe_group_name` method to ensure Group meets the required length
-   Added `tcdata` initial feature to stage Groups and Indicators in ThreatConnect
-   Updated `tcrun` to use new parameter for logging
-   Updated :py:meth:`~tcex.tcex.TcEx.job` to support upload of file to Document Group

### 0.5.20

-   Updated token renewal URL
-   Updated `tcprofile` to include **api_default_org, tc_proxy_external, tc_proxy_host, tc_proxy_port, tcp_proxy_password, tc_proxy_tc, tc_proxy_username**
-   Updated `tcprofile` changing **tc_playbook_db_path** and **tc_playbook_db_port** parameters to environment variables by default
-   Updated `tcprofile` changing **logging** to **tc_log_level**
-   Updated `tclib` to check for **requirements.txt**

### 0.5.19

-   Updated **tcex.playbook**, tcrun, and tcdata to support deleting data from Redis from previous runs

### 0.5.18

-   Updated `tcrun` to handle issue where **install_json** is not defined in the **tcex.json** file so that script name was improperly being set

### 0.5.17

-   Updated **create_output()** method to fix issue when using output variables of the same name and different type

### 0.5.16

-   Updated `tcrun` to not check for the program main file for Java Apps

### 0.5.15

-   Updated `tcrun` to support running Java Apps
-   Added support for **install_json** profile parameter to **tcex.json**. This should be included in all **tcex.json** files going forward.
-   Added support for **java_path** config parameter to **tcex.json** for custom Java path. Default behavior is to use the default version of Java from user path.
-   Added support for **class_path** profile parameter to **tcex.json** for custom Java paths. By default, `./target/` will be used as the **class_pass** value.
-   Updated `tcpackage` to grab minor version from **programVersion** in **install.json**. If no **programVersion** is found, the default version of an App is 1.0.0.
-   Cleaned up PEP8

### 0.5.14

-   Updated :py:meth:`~tcex.tcex_resources.Bulk.json` method to use proper entity value
-   Updated `tcprofile` to use default env values for API credentials
-   Added Groups parameter to **tcex.json** so that a profile can be part of multiple Groups

### 0.5.13

-   Added additional exclude values for IDE directories
-   Added **app_name** parameter to **tcex.json** for App built on system where App directory is not the App name
-   Updated `tcpackage` to use new **app_name**, if it exists, and to default back to App directory name
-   Updated `tcprofile` to only output Redis variable for Playbook Apps
-   Updated `tclib` to have default config value for instance where there is not **tcex.json** file

### 0.5.12

-   Update Building Apps section of the documentation
-   Updated required module versions (requests, python-dateutil, and Redis)
-   Fixed issue with sleep parameter being ignored in `tcrun`.
-   Updated `tclib` to automatically read **tcex.json**
-   Updated `tcpackage` to output Apps zip files with **.tcx** extension

### 0.5.11

-   Added support for binary data type in `tcdata` for staging

### 0.5.10

-   Added platform for docker support

### 0.5.9

-   Added platform check for subprocess calls
-   Added additional error logging for `tcrun` command

### 0.5.8

-   Added better support for build and test commands on Windows platform

### 0.5.7

-   Removed pip as a dependency

### 0.5.6

-   Updated `tcdata` to support multiple operators for validation
-   Added `tcprofile` command to automatically build testing profiles from **install.json**
-   Updated `tcrun` to create log, out, and temp directories for testing output
-   Updated `tcpackage` to exclude **.pyc** files and \***\*pycache\*\*** directory

### 0.5.5

-   Updated `tcpackage` to append version number to zip file
-   Added a **bundle_name** parameter to **tcex.json** file for systems where the directory name does not represent the App name

### 0.5.4

-   Updated tcdata for issue with bytes string in Python 3

### 0.5.3

-   Added new tcdata, tclib, tcpackage, and tcrun commands for App testing and packaging (The app.py will be deprecated in the future.)
-   Updated `__main__.py` for new lib directory structure created with pip (replaced easy_install)
-   Changed method so that Apps are now built with `requirements.txt` instead of `setup.py`

### 0.5.2

-   Updated :py:meth:`~tcex.tcex_resources.Resource.association_custom` method to support DELETE/POST methods
-   Added :py:meth:`~tcex.tcex.TcEx._association_types` method to load Custom Association types from API
-   Added `indicator_types_data` property with full Indicator Type data
-   Added `indicator_associations_types_data` property with full Indicator Association Type data

### 0.5.1

-   Update **playbookdb** variable name
-   Updated \***\*main**.py\*\* template for proper exit code

### 0.5.0

-   Added support for output variable of the same name, but different types
-   Added support for new **TCKeyValueAPI** DB types in Playbook Apps. This is a seamless change to the Apps.
-   Updated :py:meth:`~tcex.tcex.TcEx.authorization` method to return properly formatted header when no **token_expires** is provided
-   Added automatic authorization to :py:meth:`~tcex.tcex.TcEx.request_tc` method
-   Updated documentation for Request module

### 0.4.11

-   Changed proxy variable to proxies in :py:meth:`~tcex.tcex.TcEx.request_external` method
-   Changed proxy variable to proxies in :py:meth:`~tcex.tcex.TcEx.request_tc` method
-   Added :py:meth:`~tcex.tcex_resources.Task.assignees` method for Tasks
-   Added :py:meth:`~tcex.tcex_resources.Task.escalatees` method for Tasks
-   Added 201 as valid status code for Task

### 0.4.10

-   Added :py:meth:`~tcex.tcex_resources.Resource.victims` method to :py:mod:`~tcex.tcex_resources.Resource` module
-   Added :py:meth:`~tcex.tcex_resources.Resource.victim_assets` method to :py:mod:`~tcex.tcex_resources.Resource` module
-   Added :py:meth:`~tcex.tcex_resources.Indicator.observations` methods to :py:mod:`~tcex.tcex_resources.Resource` module
-   Added :py:meth:`~tcex.tcex_resources.Indicator.observation_count` methods to :py:mod:`~tcex.tcex_resources.Resource` module
-   Added :py:meth:`~tcex.tcex_resources.Indicator.observed` methods to :py:mod:`~tcex.tcex_resources.Resource` module
-   Changed private `_copy()` method to public :py:meth:`~tcex.tcex_resources.Resource.copy` in the :py:mod:`~tcex.tcex_resources.Resource` module
-   Updated :py:meth:`~tcex.tcex_resources.File.occurrence` method Indicator parameter to be optional
-   Added :py:meth:`~tcex.tcex_resources.Host.resolution` methods to :py:mod:`~tcex.tcex_resources.Resource` module to retrieve DNS resolutions on Host Indicators

### 0.4.9

-   Added :py:meth:`~tcex.tcex_resources.Signature.download` method to download Signature data
-   Added **urlencoding** to proxy user and password

### 0.4.7

-   Added :py:meth:`~tcex.tcex.TcEx.job` method to allow multiple jobs to run in an App
-   Update :py:meth:`~tcex.tcex.TcEx.s` method to fix issues in Python 3

### 0.4.6

-   Updated :py:meth:`~tcex.tcex_playbook.TcExPlaybook.create_binary_array` method to properly handle binary array data
-   Updated :py:meth:`~tcex.tcex_playbook.TcExPlaybook.read_binary_array` method to properly handle binary array data

### 0.4.5

-   Updated :py:meth:`~tcex.tcex_resources.Indicator.indicator_body` to support missing hashes
-   Added :py:meth:`~tcex.tcex_resources.Indicator.false_positive` endpoint for Indicators
-   Merged pull requests for better native Python 3 support
-   Added Campaign to Group types
-   Increased request timeout to 300 second.

### 0.4.4

-   Updated :py:meth:`~tcex.tcex_playbook.TcExPlaybook.read_embedded` method logic for null values and better support of mixed values

### 0.4.3

-   Updated TcEx Job module for file hashes updates using **v2/indicators/files**

### 0.4.2

-   Updated :py:mod:`~tcex.tcex_job.TcExJob` module for file hashes updates using `v2/indicators/files`

### 0.4.2

-   Updated :py:meth:`~tcex.tcex_playbook.TcExPlaybook.read_embedded` method to support different formatting dependent on the parent variable type
-   Updated :py:mod:`~tcex.tcex_resources.Resource` module to address issue in which copying the instance causes errors with request instance in Python 3
-   Updated T**cExLocal** :py:meth:`~tcex.tcex_local.TcExLocal.run` method to better format error output

### 0.4.1

-   Added :py:meth:`~tcex.tcex_resources.Datastore.add_payload` method to :py:mod:`~tcex.tcex_resources.DataStore` class
-   Fixed issue with :py:mod:`~tcex.tcex_job.TcExJob` module in which batch Indicator POST with chunking would fail after first chunk
-   Added :py:meth:`~tcex.tcex.TcEx.safe_indicator` method to urlencode and cleaned up Indicator before associations, etc.
-   Updated :py:meth:`~tcex.tcex.TcEx.expand_indicators` method to use a regex instead of split for better support of custom Indicators
-   Updated :py:mod:`~tcex.tcex_job.TcExJob._process_indicators_v2` to better handle custom Indicator types
-   Updated :py:meth:`~tcex.tcex_playbook.TcExPlaybook.read_embedded` method to strip off double quote from JSON string on mixed types and to decode escaped strings
-   Updated :py:mod:`~tcex.tcex_resources.Resource` module so that all Indicator are URL encoded before adding to the URI
-   Updated :py:meth:`~tcex.tcex_resources.Indicator.Indicator_body` method to only include items in the JSON body if not None.
-   Updated :py:meth:`~tcex.tcex_resources.Indicator.indicators` method to handle extra white spaces on the boundary
-   Added additional standard args of `api_default_org` and `tc_in_path`

### 0.4.0

-   Updated :py:mod:`~tcex.tcex_resources.Resource` module. All `_pivot()` and `associations()` methods now take an instance of Resource and return a copy of the current Resource instance. Other methods such as `security_label()` and `tags()` now return a copy of the current Resource instance.
-   Added :py:mod:`~tcex.tcex_resources.Tag` Resource class
-   Added :py:meth:`~tcex.tcex.TcEx.resource` method to get instance of Resource instance
-   Added :py:mod:`~tcex.tcex_resources.Datastore` Resource class to the :py:mod:`~tcex.tcex_resources.Resource` module
-   Updated :py:mod:`~tcex.tcex_job.TcExJob` module for changes in the :py:mod:`~tcex.tcex_resources.Resource` module

### 0.3.7

-   Added logic around retrieving Batch errors to handle 404
-   Added new :py:meth:`~tcex.tcex_playbook.TcExPlaybook.exit` method for Playbook Apps (exit code of 3 to 1 for partial success)

### 0.3.6

-   Added :py:mod:`~tcex.tcex_job.TcExJob.group_results` and :py:mod:`~tcex.tcex_job.TcExJob.indicator_results` properties to :py:mod:`~tcex.tcex_job.TcEx Job` module
-   Added :py:meth:`~tcex.tcex.TcEx.request_external` and :py:meth:`~tcex.tcex.TcEx.request_tc` methods
-   Updated :py:meth:`~tcex.tcex_playbook.TcExPlaybook.read_embedded` method with a better regex for matching variables
-   Updated :py:meth:`~tcex.tcex_playbook.TcExPlaybook` module with better error handling with JSON loads
-   Updated **TcExLocal** :py:meth:`~tcex.tcex_local.TcExLocal.run` method to sleep after subprocess executes the first time

### 0.3.5

-   Updated :py:mod:`~tcex.tcex_job.TcEx Job` module to allow Indicators to be added via `/v2/indicators/<type>`
-   Updated structure for Attributes/Tags on Groups to use singular version (Attribute/Tag) in Jobs modules to match format used for Indicators
-   Added custom case_preference and parsable properties to :py:mod:`~tcex.tcex_resources.Resource` module
-   Added logic to cleanup temporary JSON bulk file. When logging is **debug**, a compressed copy of the file will remain.

### 0.3.4

-   Fixed issue in :py:mod:`~tcex.tcex_resources` module with pagination stopping before all results are retrieved

### 0.3.3

-   Added :py:meth:`~tcex.tcex.TcEx.s` method to replace the :py:meth:`~tcex.tcex.TcEx.to_string` method (handle bad unicode in Python 2 and still support Python 3)
-   Updated :py:meth:`~tcex.tcex_playbook.TcExPlaybook.read_embedded` method to better handle embedded vars

### 0.3.2

-   Added :py:meth:`~tcex.tcex_resources.Resource.indicators` method to allow iteration over Indicator values in Indicator response JSON

### 0.3.1

-   Updated :py:meth:`~tcex.tcex_request.TcExRequest.set_basic_auth` method to use proper unicode method
-   Updated :py:mod:`~tcex.tcex_playbook` create and read methods to warn when None value is passed

### 0.3.0

-   Added :py:meth:`~tcex.tcex_request.TcExRequest.json` method that accepts a dictionary and automatically sets content-type and body
-   Updated :py:meth:`~tcex.tcex.TcEx.safeurl` and :py:meth:`~tcex.tcex.TcEx.safetag` to use :py:meth:`~tcex.tcex.TcEx.to_string`
-   Update :py:meth:`~tcex.tcex_request.TcExRequest.set_basic_auth` for Python 2/3 compatibility

### 0.2.11

-   Updated :py:meth:`~tcex.tcex_request.TcExRequest.add_payload` method to not force the value to string
-   Updated :py:meth:`~tcex.tcex_request.TcExRequest.files` method
-   Added :py:meth:`~tcex.tcex_request.TcExRequest.set_basic_auth` method for instance where normal method does not work

### 0.2.10

-   Added :py:meth:`~tcex.tcex_request.TcExRequest.files` property to :py:mod:`~tcex.tcex_request` module

### 0.2.9

-   Fixed issue with boolean parameters having an extra space at the end

### 0.2.8

-   Updated :py:meth:`~tcex.tcex_local.TcExLocal._parameters` method to build a list for **subprocess.popen** instead of a string
-   Updated **install.json** schema to support **note** field

### 0.2.7

-   Removed hiredis as a dependency
-   Added hvac as a dependency for vault-credential storage
-   Added ability to use vault as a credential store for local testing
-   Fixed args wrapper for Windows (' to ")

### 0.2.6

-   Added sleep option for test profiles that take time to complete

### 0.2.5

-   Updated :py:mod:`~tcex.tcex_local` module to change **tc.json** profiles to list instead of dictionary to maintain order of profiles
-   Added feature to :py:mod:`~tcex.tcex_local` to read environment variables for value in **tc.json** (e.g., $evn.my_api_key)

### 0.2.4

-   Handled None type returned by Redis module

### 0.2.3

-   Added :py:meth:`~tcex.tcex.TcEx.to_string` method to replace old `uni()` method (handled Python 2/3 encoding for Apps)

### 0.2.2

-   Updated string/unicode/bytes issue between Python 2 and 3

### 0.2.1

-   Updated :py:mod:`~tcex.tcex_local` module for Python 2/3 support
-   Updated binary methods in :py:mod:`~tcex.tcex_playbook` module for Python 2/3 support

### 0.2.0

-   Reworked :py:mod:`~tcex.tcex_local` :py:meth:`~tcex.tcex_local.TcExLocal.run` logic to support updated **tc.json** schema
-   Changed **--test** arg to **--profile** in :py:meth:`~tcex.tcex_local.TcExLocal._required_arguments`
-   Added **script** field to **tc.json** that matches **--script** arg to support predefined script names
-   Added **Group** field to **tc.json** that matches **--group** arg in :py:meth:`~tcex.tcex_local.TcExLocal._required_arguments` to support running multiple profiles
-   Added `inflect <https://pypi.python.org/pypi/inflect>`\_ requirement to version 0.2.5
-   Changed python-dateutil requirement to version 2.6.10
-   Changed requests requirement to version 2.13.0

### 0.1.6

-   Added accepted status code of 201 for Custom Indicator POST on dynamic class creation

### 0.1.5

-   Added :py:meth:`~tcex.tcex_resources.Indicator.entity_body` method to :py:mod:`~tcex.tcex_resources` for generating Indicator body
-   Added :py:meth:`~tcex.tcex_resources.Indicator.indicator_body` method to :py:mod:`~tcex.tcex_resources` for generating Indicator body

### 0.1.4

-   Fixed issue with Job :py:meth:`~tcex.tcex_job.TcExJob.group_cache` method

### 0.1.3

-   Updated :py:mod:`~tcex.tcex_job.TcExJob` module to use new pagination functionality in :py:mod:`~tcex.tcex_resources` module
-   Updated and labeled :py:meth:`~tcex.tcex_resources.Resource.paginate` method as deprecated

### 0.1.2

-   Updated **tcex_local** for additional parameter support during build process

### 0.1.1

-   Updated **tcex_local** for exit code when app.py is called (maven build issue)
-   Added new log event for proxy settings

### 0.1.0

-   Reworked iterator logic in :py:mod:`~tcex.tcex_resources` module

### 0.0.12

-   Updated documentation
-   Changed :py:mod:`~tcex.tcex_resources` to allow iteration over the instance to retrieve paginated results
-   Updated support-persistent args when running App locally
-   Updated Playbook module for Python 3
-   Added logging of platform for debugging purposes
-   Updated Pep 8

### 0.0.11

-   Updated :py:meth:`~tcex.tcex_job.TcExJob.file_occurrence` in the :py:mod:`~tcex.tcex_job.TcEx Job` module
-   Added :py:mod:`~tcex.tcex_data_filter` module access via `tcex.data_filter(data)`
-   Added :py:meth:`~tcex.tcex.TcEx.epoch_seconds` method to return epoch seconds with optional delta period
-   Added `python-dateutil==2.4.2` as a Python dependency

### 0.0.10

-   Added :py:meth:`~tcex.tcex_resources.Resource.paginate` method to :py:mod:`~tcex.tcex_resources` module
-   Updated :py:meth:`~tcex.tcex_job.TcExJob.group_cache` module to use :py:meth:`~tcex.tcex_resources.Resource.paginate` method

### 0.0.9

-   Updated :py:mod:`~tcex.tcex_job.TcExJob` module for :py:mod:`~tcex.tcex_resources` modules renamed methods and changes

### 0.0.8

-   Changed logging level logic to use `logging` over `tc_logging_level`, if it exists
-   Added App version logging attempt

### 0.0.7

-   Updated :py:meth:`~tcex.tcex.TcEx._resources` method to handle TC version without custom Indicators
-   Updated logging to better debug API request failures
-   Updated package command to create lib directory with Python version (e.g., lib_3.6.0)
-   Updated logging the Logging Level, Python, and TcEx versions for additional debugging

### 0.0.6

-   Updated open call for bytes issue on Python 3

### 0.0.5

-   Updated to **setup.py** for Python 3 support

### 0.0.4

-   Updated Campaign Resource type Class
-   Added `building_apps` section to documentation

### 0.0.3

-   Added :py:meth:`~tcex.tcex_resources.Campaign` Class
-   Updated documentation

### 0.0.2

-   Updated `setup.py` for build

### 0.0.1

-   Initial Public Release
