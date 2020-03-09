.. _snippets:

-------
Feature
-------

-----
Batch
-----

Initialize Batch Create
-----------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    batch = self.tcex.batch(owner="MyOwner")


Initialize Batch Delete
-----------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    batch = self.tcex.batch(owner="MyOwner", action="Delete")


Add Group Interface 1
---------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = batch.campaign(name="camp-1", first_seen="12-12-08", xid="my-unique-external-id")


Add Group Interface 2
---------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = batch.group(group_type="Campaign", name="camp-2", date_added="12-12-2008", first_seen="12-12-08", xid="my-unique-external-id")


Add Attribute
-------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti.attribute(attr_type="Description", attr_value="Example Description", displayed=True)


Add Tag
-------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti.tag(name="Crimeware")


Add Security Label
------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti.security_label(name="My Custom Label", description="My Label Description", color="ffffff")


Add Association
---------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti.association("my-unique-adversary-external-id")


Save
----

.. code-block:: python
    :linenos:
    :lineno-start: 1

    # temporarily save group to disk to preserve memory
    batch.save(ti)


Add Indicator Interface 1
-------------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = batch.file(md5="43c3609411c83f363e051d455ade78a6", rating="5.0", confidence="100")


Add Indicator Interface 2
-------------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = batch.indicator(indicator_type="File", summary="43c3609411c83f363e051d455ade78a6")
    ti.confidence = "50"
    ti.rating = "3.2"
    ti.occurrence(file_name="drop1.exe", path="C:\\\\test\\\\", date="2017-02-02")
    ti.occurrence(file_name="drop2.exe", path="C:\\\\test2\\\\", date="2017-01-01")


Submit
------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    batch_status = batch.submit_all()


---------------
Case Management
---------------

Create Case
-----------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    case_data = {
        "name": "Case Name",
        "severity": "Low",
        "status": "Open",
    }
    case = self.cm.case(**case_data)
    case.submit()

Update Case
-----------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    case = self.cm.case(id=2)
    case.name = "Updated Name"
    case.submit()

Delete Case
-----------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    case = self.cm.case(id=2)
    case.delete()

Get Case
--------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    case = self.cm.case(id=2)
    case.get()

Get Sub Artifacts
-----------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    case = self.cm.case(id=2)
    case.get(all_available_fields=True)
    for artifact in case.artifacts:
        self.tcex.log.debug(f"artifact: {artifact}")

Create Case with Artifacts
--------------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    case_data = {
        "name": "Case Name",
        "severity": "Low",
        "status": "Open",
    }

    case = self.cm.case(**case_data)

    # artifact data
    artifact_data = [
        {"summary": "asn4455", "intel_type": "indicator-ASN", "type": "ASN"},
        {"summary": "asn5544", "intel_type": "indicator-ASN", "type": "ASN"},
    ]

    # add artifacts
    for artifact in artifact_data:
        case.add_artifact(**artifact)
    case.submit()

Get Cases with TQL
------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    cases = self.tcex.cm.cases()
    cases.filter.id(TQL.Operator.EQ, case.id)

    for case in cases:
        self.tcex.log.debug(f"case: {case}")

Get Cases with Linked TQL
-------------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    cases = self.tcex.cm.cases()
    cases.filter.has_artifact.id(TQL.Operator.EQ, artifact.id)

    for case in cases:
        self.tcex.log.debug(f"case: {case}")

Create Artifact
---------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    artifact_data = {
        "case_id": 1,
        "summary": f"asn2342",
        "type": "ASN",
    }

    # create artifact
    artifact = self.tcex.cm.artifact(**artifact_data)
    artifact.submit()

Create Note
-----------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    note_data = {
        "case_id": 1,
        "text": f"sample note for test case."
    }

    # create note
    note = self.tcex.cm.note(**note_data)
    note.submit()

Add Tag
-------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    case = self.tcex.cm.case(id=1)
    case.add_tag("sample tag")
    case.submit()

Create Task
-----------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    task_data = {
        "case_id": 1,
        "description": f"a description for new task",
        "name": f"new task",
        "xid": "unique-task-xid"
    }

    # create task
    self.tcex.cm.task(**task_data)
    task.submit()

Create Workflow Event
---------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    workflow_event_data = {
        "case_id": 1,
        "summary": "workflow event summary"
    }

    # create workflow_event
    self.tcex.cm.workflow_event(**workflow_event_data)
    workflow_event.submit()

---------
DataStore
---------

Initialize Local
----------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    # when using a value of "local" the scope of the datastore is limited to this App in the current Playbook
    ds = self.tcex.datastore("local", "myDnsData")


Initialize Organization
-----------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ds = self.tcex.datastore("organization", "myDnsData")


Get
---

.. code-block:: python
    :linenos:
    :lineno-start: 1

    response = ds.get(rid="one")


Add
---

.. code-block:: python
    :linenos:
    :lineno-start: 1

    response = ds.add(rid="one", data={"one": 1})


Add (dynamic id)
----------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    response = ds.add(rid=None, data={"one": 1})


Put
---

.. code-block:: python
    :linenos:
    :lineno-start: 1

    response = ds.put(rid="one", data={"one": 1})


Delete
------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    response = ds.delete(rid="one")


Search
------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    search = {"query": {"match_all": {}}}
    response = ds.get(rid="_search", data=search)


----
Exit
----

Set exit message
----------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    self.exit_message = f"Created {indicator_count} indicators."


Set exit code
-------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    # set the exit code and allow App to continue to process
    self.tcex.playbook.exit_code = 1


Exit with error
---------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    # exit the App immediately with the provided exit message
    self.tcex.playbook.exit(code=1, msg="Failed to add indicators to Owner.")


-------
General
-------

Action Method
-------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    @IterateOnArg(arg="input_arg")
    @OnException(exit_msg="Failed to run "do something" operation.")
    @OnSuccess(exit_msg="Successfully ran "do something" operation.")
    @Output(attribute="return_outputs")
    def do_action(self, input_arg):
        """Perform an action on interator_input and append return value to self.return_outputs."""
        return input_arg


Get variable type
-----------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    var_type = self.tcex.playbook.variable_type(variable=self.args.input)


-------
Logging
-------

Debug
-----

.. code-block:: python
    :linenos:
    :lineno-start: 1

    self.tcex.log.debug("debug logging")


Info
----

.. code-block:: python
    :linenos:
    :lineno-start: 1

    self.tcex.log.info("info logging")


Warning
-------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    self.tcex.log.warning("warning logging")


Error
-----

.. code-block:: python
    :linenos:
    :lineno-start: 1

    self.tcex.log.error("error logging")


-------
Metrics
-------

Add Metrics
-----------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    metrics = self.tcex.metric(name="My Metric", description="Indicator Count", data_type="Sum", interval="Daily", keyed=False)
    metrics.add(value=42, date="2008-12-12T12:12:12")


Add Keyed Metrics
-----------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    metrics = self.tcex.metric(name="My Metric By Owner", description="Indicator Count by Owner", data_type="Sum", interval="Daily", keyed=True)
    metrics.add_keyed(value=42, key="MyOrg", date="2008-12-12T12:12:12", return_value=True)


-------------
Notifications
-------------

Send to Recipients
------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    notification = self.tcex.notification()
    notification.recipients(notification_type="My notification", recipients="myuser@example.com", priority="High")
    status = notification.send(message="High alert send to recipients.")


Sent to Organization
--------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    notification = self.tcex.notification()
    notification.org(notification_type="My notification", priority="High")
    status = notification.send(message="High alert send to organization.")


-------------------
Threat Intelligence
-------------------

Get Group by Id
---------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    parameters = {
        "includes": ["additional", "attributes", "labels", "tags"]
    }
    ti = self.tcex.ti.group(group_type="Adversary", owner="MyOrg", unique_id=416)
    response = ti.single(params=parameters)


Get Groups
----------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    parameters = {
        "includes": ["additional", "attributes", "labels", "tags"]
    }
    groups = self.tcex.ti.group(group_type="Adversary", owner="MyOrg")
    for group in groups.many(params=parameters):
        self.tcex.log.debug(f"group: {group}")


Get Tags
--------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    for tag in ti.tags():
        self.tcex.log.debug(f"tag: {tag}")


Get Attributes
--------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    for attribute in ti.attributes():
        self.tcex.log.debug(f"attribute: {attribute}")


Get Associations
----------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    for association in ti.indicator_associations():
        self.tcex.log.debug(f"association: {association}")


Create Group
------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.group(group_type="Campaign", name="camp-3", owner="MyOrg", first_seen="2019-04-02")
    response = ti.create()


Add Tag
-------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    response = ti.add_tag(name="Crimeware")


Add Attribute
-------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    response = ti.add_attribute(attribute_type="Description", attribute_value="Example Description.")


Add Security Label
------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    response = ti.add_label(label="TLP:GREEN")


Add Association
---------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    group_assoc = self.tcex.ti.group(group_type="Campaign", unique_id=417)
    response = ti.add_association(target=group_assoc)


Update Group
------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.group(group_type="Campaign", first_seen="2019-04-03", unique_id=417)
    response = ti.update()


Delete Group
------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.group(group_type="Campaign", unique_id=419)
    response = ti.delete()


Get Indicatory by Value
-----------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    parameters = {
        "includes": ["additional", "attributes", "labels", "tags"]
    }
    ti = self.tcex.ti.indicator(indicator_type="Address", owner="MyOrg", unique_id="127.0.0.1")
    response = ti.single(params=parameters)


Get Indicators
--------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    parameters = {
        "includes": ["additional", "attributes", "labels", "tags"]
    }
    indicators = self.tcex.ti.indicator(indicator_type="Address", owner="MyOrg")
    for indicator in indicators.many(params=parameters):
        self.tcex.log.debug(f"indicator: {indicator}")


Create Indicator
----------------

.. code-block:: python
    :linenos:
    :lineno-start: 1

    ti = self.tcex.ti.indicator(indicator_type="Address", owner="MyOrg", ip="12.13.14.15")
    response = ti.create()
