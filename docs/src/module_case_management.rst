.. include:: <isonum.txt>
.. _module_case_management:

=======================
Module: Case Management
=======================

.. important:: The Case Management module requires ThreatConnect version 6.0 or higher.

The ThreatConnect TcEx Framework provides the :py:mod:`~tcex.case_management.case_management.CaseManagement` module to create, fetch, and delete Case Management objects.

* Create - Cases, Artifacts, Notes, Tags, Tasks, Workflow Events, and Workflow Templates.
* Get - Cases, Artifacts, Artifact Type, Notes, Tags, Tasks, Workflow Events, and Workflow Templates
* Delete - Cases Artifacts, Notes, Tags, and Tasks
* Update - Not Supported

Create
======
Can create Cases, Artifacts, Notes, Tags, Tasks, Workflow Events, and Workflow Templates.

Examples
--------

Create Case:

.. code-block:: python

    case_data = {
        'name': 'Case Name',
        'severity': 'Low',
        'status': 'Open',
    }
    case = self.cm.case(**case_data)
    case.submit()

Create Artifact:

.. code-block:: python

    case = create_case()

    artifact_data = {
        'case_id': case_id,
        'intel_type': 'indicator-ASN',
        'summary': 'asn-100',
        'type': 'ASN',
    }

    # create artifact
    artifact = self.cm.artifact(**artifact_data)
    artifact.submit()

Create Note:

.. code-block:: python

    case = create_case()

    # note data
    note_data = {
        'case_id': case_id,
        'text': 'sample note for case.',
        'date_added': '2033-12-07T14:16:40-05:00',
        'edited': True,
    }

    # create note
    note = self.cm.note(**note_data)
    note.submit()

Create Tag:

.. code-block:: python

    tag_data = {
        'description': 'a description of tag',
        'name': 'Tag Name',
    }

    # create tag
    tag = self.cm.tag(**tag_data)
    tag.submit()

Create Task:

.. code-block:: python

    case = create_case()

    # task data
    task_data = {
        'case_id': case_id,
        'description': 'a description of task',
        'name': f'task-name',
        'workflow_phase': 0,
        'workflow_step': 1
    }

    # create task
    task = self.cm.task(**task_data)
    task.submit()

Create Workflow Event:

.. code-block:: python

   case = self.cm_helper.create_case()

    # workflow event data
    workflow_event_data = {
        'case_id': case_id,
        'summary': 'Workflow Event Summary'
    }

    # create workflow_event
    workflow_event = self.cm.workflow_event(**workflow_event_data)
    workflow_event.submit()

Create Workflow Template:

.. code-block:: python

    workflow_template_data = {
        'description': 'a description for workflow template',
        'name': 'Workflow Template Name',
        'version': 1,
    }

    # create workflow_template
    workflow_template = self.cm.workflow_template(**workflow_template_data)
    workflow_template.submit()

Multiple
--------
It is possible to create multiple objects at the same time as well. For example:

.. code-block:: python

   case_data = {
        'name': 'Case Name',
        'severity': 'Low',
        'status': 'Open',
    }

    # create case
    case = self.cm.case(**case_data)

    # artifact data
    artifact_data = [
        {'summary': 'asn4455', 'intel_type': 'indicator-ASN', 'type': 'ASN'},
        {'summary': 'asn5544', 'intel_type': 'indicator-ASN', 'type': 'ASN'},
    ]

    # add artifacts
    for artifact in artifact_data:
        case.add_artifact(**artifact)

    # note data
    note_data = ['A note']

    # add notes
    for note in note_data:
        case.add_note(text=note)

    # tag data
    tag_data = [{'name': 'tag-1'}, {'name': 'tag-2'}]

    # add tags
    for tag in tag_data:
        case.add_tag(**tag)

    # task data
    task_data = [{'name': 'task-1', 'description': 'task description', 'status': 'Pending'}]

    # add task
    for task in task_data:
        case.add_task(**task)

    # submit case
    case.submit()

Will create a Case with artifacts, tags, notes, and tasks all under it in one submit.

Delete
======
Can delete Cases Artifacts, Notes, Tags, and Tasks

Examples
--------

Delete Case:

.. code-block:: python

    case = self.cm.case(id=case_id)

    # delete the case
    case.delete()

Delete Artifact:

.. code-block:: python

    artifact = self.cm.artifact(id=artifact_id)

    # delete the artifact
    artifact.delete()



Delete Note:

.. code-block:: python

    note = self.cm.note(id=note.id)

    # delete the note
    note.delete()

Delete Tag:

.. code-block:: python

    tag = self.cm.tag(id=tag_id)

    # delete the tag
    tag.delete()

Delete Task:

.. code-block:: python

    task = self.cm.task(id=task_id)

    # delete the task
    task.delete()

Multiple
--------

For safety reasons there is no call to delete multiple Case Management objects
all at once but a similar affect can be done from iterating over the items you wish to delete.
For example:

.. code-block:: python

    tasks = self.cm.tasks()
    tasks.filter.case_id(TQL.Operator.EQ, case_id)
    tasks.filter.automated(TQL.Operator.EQ, True)

    for task in tasks:
        task.delete()

Will delete all tasks under the Case with the id case_id and that was not automatically generated.

Get
===
Can retrieve Cases, Artifacts, Artifact Type, Notes, Tags, Tasks, Workflow Events, and Workflow Templates

Examples
--------
Retrieve a Single Case:

.. code-block:: python

    # retrieve case for asserts
    case = self.cm.case(id=case_id)
    case.get()

Retrieve multiple Cases:

.. code-block:: python

    for c in self.cm.cases():
        self.tcex.log.debug(c)

Retrieve a Single Artifact:

.. code-block:: python

    # retrieve case for asserts
    artifact = self.cm.case(id=case_id)
    artifact.get()

Retrieve multiple Artifacts:

.. code-block:: python

    for a in self.cm.artifacts():
        self.tcex.log.debug(a)

Retrieve a Single Artifact Type:

.. code-block:: python

    artifact_type = self.cm.artifact_type(id=1)
    artifact_type.get()

Retrieve multiple Artifact Types:

.. code-block:: python

    for at in self.cm.artifact_types():
        self.tcex.log.debug(at)

Retrieve a Single Note:

.. code-block:: python

    # retrieve case for asserts
    note = self.cm.case(id=note_id)
    note.get()

Retrieve multiple Notes:

.. code-block:: python

    for n in self.cm.notes():
        self.tcex.log.debug(n)

Retrieve a Single Tag:

.. code-block:: python

    # retrieve case for asserts
    tag = self.cm.tag(id=case_id)
    tag.get()

Retrieve multiple Tags:

.. code-block:: python

    for t in self.cm.tags():
        self.tcex.log.debug(t)

Retrieve a Single Task:

.. code-block:: python

    # retrieve case for asserts
    task = self.cm.task(id=case_id)
    task.get()

Retrieve multiple Tasks:

.. code-block:: python

    for t in self.cm.tasks():
        self.tcex.log.debug(t)

Retrieve a Single Workflow Event:

.. code-block:: python

    # retrieve case for asserts
    workflow_event = self.cm.workflow_event(id=workflow_event_id)
    workflow_event.get()

Retrieve multiple Workflow Events:

.. code-block:: python

    for we in self.cm.workflow_events():
        self.tcex.log.debug(we)

Retrieve a Single Workflow Template:

.. code-block:: python

    workflow_template = self.cm.workflow_template(id=workflow_template.id)
    workflow_template.get()

Retrieve multiple Workflow Templates:

.. code-block:: python

    for wt in self.cm.workflow_templates():
        self.tcex.log.debug(wt)


Filters
-------

Each of the different Case Management object types has a variety of filters available to them under their filters object.
To apply a filter to a object call the appropriate method and provide it with the desired operator and intended value.
For example to retrieve all artifacts under a specific case the follow filter can be applied:

.. code-block:: python

    artifacts = self.cm.artifacts()
    artifacts.filter.has_case_id(TQL.Operator.EQ, case_id)
    for artifact in artifacts:
        self.tcex.log.debug(artifact)
