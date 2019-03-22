# -*- coding: utf-8 -*-
"""Test the TcEx app.."""

import os
import sys
from tcex.tcex_ti.tcex_ti import TcExTi

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import utility  # pylint: disable=C0413


tcex = utility.init_tcex(clean_data=False)
ti = TcExTi(tcex)

# def test_event_create_0():
#     """Test adversary creation"""
#     summary = 'event-000'
#     event = ti.write.event(summary)
#     response = event.create('System')
#     assert response.json().get('status') == 'Success'

# def test_event_create_1():
#     """Test adversary creation"""
#     summary = 'event-001'
#     event = ti.write.event(summary, status='Needs Review')
#     response = event.create('System')
#     assert response.json().get('status') == 'Success'

# def test_event_update_0():
#     weblink: 'https://127.0.0.1/auth/event/event.xhtml?event=142722'
# event_id = 142722
# summary = 'event-002'
# event = ti.write.event(summary, id=event_id)
# response = event.update()
# assert response.json().get('status') == 'Success'

# def test_event_update_1():
#     event_id = 142722
#     event = ti.write.event(None, id=event_id)
#     response = event.tag('test_tag_1')
#     assert response.json().get('status') == 'Success'

# def test_event_update_2():
#     event_id = 142722
#     event = ti.write.event(None, id=event_id)
#     response = event.delete_tag('test_tag_1')
#     assert response.json().get('status') == 'Success'

# def test_event_update_3():
#     event_id = 142722
#     event = ti.write.event(None, id=event_id)
#     response = event.attribute('Description', 'Test_Description')
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_event_update_4():
#     event_id = 142722
#     attribute_id = 933455
#     event = ti.write.event(None, id=event_id)
#     response = event.delete_attribute(attribute_id)
#     print(response.json())
#     assert response.json().get('status') == 'Success'

# def test_event_update_5():
#     event_id = 142722
#     attribute_id = 933456
#     event = ti.write.event(None, id=event_id)
#     response = event.attribute_labels(attribute_id, 'TLP:AMBER')
#     # Returns a 404 if the security label doesnt exist.
#     print(response)
#     assert response.json().get('status') == 'Success'

# def test_event_update_6():
#     event_id = 142722
#     attribute_id = 933456
#     event = ti.write.event(None, id=event_id)
#     response = event.delete_attribute_labels(attribute_id, 'TLP:AMBER')
#     print(response)
#     assert response.json().get('status') == 'Success'
