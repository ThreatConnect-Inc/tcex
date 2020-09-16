"""Test the TcEx Utils Module."""


# pylint: disable=no-self-use
class testMitreAttackTechniques:
    """Test the TcEx Utils Module."""

    def test_mitre_technique_id_to_tc_tags(self, tcex):
        """Test the mapping between MITRE ATT&CK technique ID and TC tags.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        technique_id = 'T1001'
        assert tcex.utils.mitre_attack.technique_id_to_tags(technique_id) == [
            'T1001 - Data Obfuscation - C&C - ENT - ATT&CK'
        ]

        technique_id = 'T1055'
        assert tcex.utils.mitre_attack.technique_id_to_tags(technique_id) == [
            'T1055 - Process Injection - DEF - ENT - ATT&CK',
            'T1055 - Process Injection - PRI - ENT - ATT&CK',
        ]

        technique_id = 't1055'
        assert tcex.utils.mitre_attack.technique_id_to_tags(technique_id) == [
            'T1055 - Process Injection - DEF - ENT - ATT&CK',
            'T1055 - Process Injection - PRI - ENT - ATT&CK',
            'T1055 - Process Injection - NDT - ENT - ATT&CK',
        ]

        technique_id = 'T1055.011'
        assert tcex.utils.mitre_attack.technique_id_to_tags(technique_id) == [
            'Extra Window Memory Injection - DEF - ENT - ATT&CK',
            'Extra Window Memory Injection - PRI - ENT - ATT&CK',
            'Extra Window Memory Injection - NDT - ENT - ATT&CK',
        ]

    def test_mitre_technique_id_to_tc_tags_without_ndt_tags(self, tcex):
        """."""
        technique_id = 'T1055'
        assert tcex.utils.mitre_attack.technique_id_to_tags(technique_id, include_ndt_tag=True) == [
            'T1055 - Process Injection - DEF - ENT - ATT&CK',
            'T1055 - Process Injection - PRI - ENT - ATT&CK',
            'T1055 - Process Injection - NDT - ENT - ATT&CK',
        ]

    def test_invalid(self, tcex):
        """Test a string that is not an IP address

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        technique_id = 'T5555'
        assert tcex.utils.mitre_attack.technique_id_to_tags(technique_id) == []

        technique_id = 'not a valid technique id'
        assert tcex.utils.mitre_attack.technique_id_to_tags(technique_id) == []


# pylint: disable=no-self-use
class testMitreAttackFindTacticAbbreviation:
    """Test the TcEx Utils Module."""

    def test_mitre_tactic_name_abbreviation(self, tcex):
        """Test the mapping between mitre attack tactic names and their abbreviations

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        assert (
            tcex.utils.mitre_attack.tactic_name_abbreviation('Establish&MaintainInfrastructure')
            == 'EMI'
        )
        assert (
            tcex.utils.mitre_attack.tactic_name_abbreviation('Establish & Maintain Infrastructure')
            == 'EMI'
        )
        assert tcex.utils.mitre_attack.tactic_name_abbreviation('Execution') == 'EXE'
        assert tcex.utils.mitre_attack.tactic_name_abbreviation('CommandAndControl') == 'C&C'
        assert tcex.utils.mitre_attack.tactic_name_abbreviation('commandandcontrol') == 'C&C'
        assert tcex.utils.mitre_attack.tactic_name_abbreviation('Command And Control') == 'C&C'
        assert tcex.utils.mitre_attack.tactic_name_abbreviation('command and control') == 'C&C'
        assert tcex.utils.mitre_attack.tactic_name_abbreviation('Command-And-Control') == 'C&C'
        assert tcex.utils.mitre_attack.tactic_name_abbreviation('command-and-control') == 'C&C'
        assert tcex.utils.mitre_attack.tactic_name_abbreviation('Foobar') is None
