"""Install JSON Validate"""
# pylint: disable=R0401
# standard library
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .install_json import InstallJson


class InstallJsonValidate:
    """Validate install.json file."""

    def __init__(self, ij: 'InstallJson'):  # pylint: disable=E0601
        """Initialize class properties."""
        self.ij = ij

    def validate_duplicate_input(self) -> list:
        """Check for duplicate input names."""
        duplicates = []
        tracker = []
        for param in self.ij.model.params:
            if param.name in tracker:
                duplicates.append(param.name)
            tracker.append(param.name)
        return duplicates

    def validate_duplicate_output(self) -> list:
        """Check for duplicate input names."""
        duplicates = []
        tracker = []
        for output in self.ij.model.playbook.output_variables or []:
            name_type = f'{output.name}-{output.type}'
            if name_type in tracker:
                duplicates.append(output.name)
            tracker.append(name_type)
        return duplicates

    def validate_duplicate_sequence(self) -> list:
        """Check for duplicate sequence numbers."""
        duplicates = []
        tracker = []
        for param in self.ij.model.params:
            if param.sequence in tracker:
                duplicates.append(param.sequence)
            tracker.append(param.sequence)
        return duplicates
