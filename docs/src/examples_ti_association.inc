.. _examples_ti_associations:

------------------------------
Indicator to Group Association
------------------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1


    ti = self.indicator('address', owner, **kwargs)
    ti.create()

    # group to associate
    association_target = self.group('document', owner, **association_kwargs)

    ti.add_association(
      None,
      api_type=association_target.api_type,
      api_branch=association_target.api_branch,
      unique_id=association_target.unique_id
    )
