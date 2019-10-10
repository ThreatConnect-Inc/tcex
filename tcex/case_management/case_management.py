# -*- coding: utf-8 -*-
from .artifacts import Artifacts


class CaseManagement(object):
    def artifacts(self):
        return Artifacts()

    def artifact_types(self):
        return

    def cases(self):
        return

    def notes(self):
        return

    def tasks(self):
        return

    def workflow_events(self):
        return

    def workflow_templates(self):
        return

    def tags(self):
        return


# artifact = self.tcex.v3.cm.add_artifact(count, date_observed)
#
# this will return a tiny artifact object using the __stub__ feature.
#
# then the user would
#
# artifact.submit()
