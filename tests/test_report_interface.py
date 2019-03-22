# -*- coding: utf-8 -*-
"""Test the TcEx app.."""

import os
import sys
from tcex.tcex_ti.tcex_ti import TcExTi

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import utility  # pylint: disable=C0413


tcex = utility.init_tcex(clean_data=False)
ti = TcExTi(tcex)


# def test_report_create_0():
#     """Test report creation"""
#     summary = 'report1'
#     file_name = 'report_file_name.pdf'
#     report = ti.write.report(summary, file_name)
#     response = report.create('System')
#     assert response.json().get('status') == 'Success'


# def test_report_create_1():
#     """Test report creation"""
#     summary = 'report3'
#     file_name = 'report_file_name.txt'
#     report = ti.write.report(summary, file_name)
#     response = report.create('System')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_report_update_0():
#     """Test report creation"""
#     unique_id = '142736'
#     report = ti.write.report(None, None, unique_id=unique_id)
#     file_content =  'IyEvYmluL2Jhc2gKCmNkIFVzZXJzL2JwdXJkeS1hZC9wcm9qZWN0cy90aHJlYXRjb' \
#                     '25uZWN0LWluc3RhbGxlci90aHJlYXRjb25uZWN0L2FwcApteXNxbCAtdSByb290IC' \
#                     '1wIHBhc3N3b3JkIHRocmVhdGNvbm5lY3QgPCAnREVMRVRFIEZST00gYHRocmVhdGN' \
#                     'vbm5lY3RgLmBsaWNlbnNlYDsnCi4vc2V0dXAuc2ggPCB+L0RvY3VtZW50cy9mdWxs' \
#                     'X3NlcnZlcl9pbnB1dC50eHQgIApjcCAuLi90aHJlYXRjb25uZWN0LnhtbCB+L0Rvd' \
#                     '25sb2Fkcy9lYXAvc3RhbmRhbG9uZS9jb25maWd1cmF0aW9uLwpzdGFydF9qYm9zcw' \
#                     'pzbGVlcCAzMAppZiBbIC1lIH4vRG93bmxvYWRzL2VhcC9zdGFuZGFsb25lL2RlcGx' \
#                     'veW1lbnRzL3RocmVhdGNvbm5lY3QuZWFyIF07IHRoZW4KICAgIGVjaG8gIkZ1bGwg' \
#                     'ZGVwbG95bWVudCBzdWNjZXNzZnVsIgplbHNlCiAgZWNobyAiRnVsbCBkZXBsb3ltZ' \
#                     'W50IHVuc3VjY2Vzc2Z1bCIKICBleGl0IDEKZmkKCg=='
#     response = report.file_content(file_content)
#     assert response.json().get('status') == 'Success'

# def test_report_update_1():
#     """Test report creation"""
#     unique_id = '142736'
#     report = ti.write.report(None, unique_id=unique_id)
#     response = report.attribute('Description', 'Test Description')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_report_update_2():
#     unique_id = '142736'
#     attribute_id = 933459
#     report = ti.write.report(None, unique_id=unique_id)
#     response = report.add_attribute_labels(attribute_id, 'TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_report_update_3():
#     unique_id = '142736'
#     attribute_id = 933459
#     report = ti.write.report(None, unique_id=unique_id)
#     response = report.delete_attribute_labels(attribute_id, 'TLP:AMBER')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_report_update_4():
#     unique_id = '142736'
#     attribute_id = 933459
#     report = ti.write.report(None, unique_id=unique_id)
#     response = report.delete_attribute(attribute_id)
#     assert response.json().get('status') == 'Success'

# def test_report_update_5():
#     unique_id = '142736'
#     report = ti.write.report(None, unique_id=unique_id)
#     response = report.label('TLP:AMBER')
#     print(response)
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_report_update_6():
#     unique_id = '142736'
#     report = ti.write.report(None, unique_id=unique_id)
#     response = report.delete_label('TLP:AMBER')
#     assert response.json().get('status') == 'Success'

# def test_report_delete_0():
#     unique_id = '142736'
#     report = ti.write.report(None, unique_id=unique_id)
#     response = report.delete()
#     assert response.json().get('status') == 'Success'
