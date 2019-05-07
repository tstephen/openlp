# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2019 OpenLP Developers                              #
# ---------------------------------------------------------------------- #
# This program is free software: you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by   #
# the Free Software Foundation, either version 3 of the License, or      #
# (at your option) any later version.                                    #
#                                                                        #
# This program is distributed in the hope that it will be useful,        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of         #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
# GNU General Public License for more details.                           #
#                                                                        #
# You should have received a copy of the GNU General Public License      #
# along with this program.  If not, see <https://www.gnu.org/licenses/>. #
##########################################################################
"""
Package to test the openlp.core.projectors.pjlink commands package.
"""
from unittest import TestCase, skip
from unittest.mock import call, patch

import openlp.core.projectors.pjlink
from openlp.core.projectors.pjlinkcommands import process_command
from openlp.core.projectors.constants import PJLINK_POWR_STATUS, S_ON, S_STANDBY
from openlp.core.projectors.db import Projector
from openlp.core.projectors.pjlink import PJLink
from tests.resources.projector.data import TEST1_DATA


class TestPJLinkCommands(TestCase):
    """
    Tests PJLink get status commands part 2
    """
    def setUp(self):
        """
        Initial test setup
        """
        self.pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)

    def tearDown(self):
        """
        Test reset
        """
        del(self.pjlink)

    @skip('Needs update to new setup')
    def test_projector_process_inpt_valid(self):
        """
        Test input source status shows current input
        """
        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.source = '11'
            log_debug_calls = [call('({ip}) reset_information() connect status is '
                                    'S_NOT_CONNECTED'.format(ip=pjlink.name))]
            chk_source_available = ['11', '12', '21', '22', '31', '32']
            pjlink.source_available = chk_source_available

            # WHEN: Called with input source
            process_command(projector=self.pjlink, cmd='INPT', data='21')

            # THEN: Input selected should reflect current input
            assert pjlink.source == '21', 'Input source should be set to "21"'
            mock_log.debug.assert_has_calls(log_debug_calls)

    @skip('Needs update to new setup')
    def test_projector_process_input_not_in_list(self):
        """
        Test setting input outside of available inputs

        TODO: Future test
        """
        pass

    @skip('Needs update to new setup')
    def test_projector_process_input_not_in_default(self):
        """
        Test setting input with no sources available
        TODO: Future test
        """
        pass

    @skip('Needs update to new setup')
    def test_projector_process_input_invalid(self):
        """
        Test setting input with an invalid value

        TODO: Future test
        """

    @skip('Needs update to new setup')
    def test_projector_process_inst_class_1(self):
        """
        Test saving video source available information
        """

        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.source_available = []
            log_debug_calls = [call('({ip}) reset_information() connect status is '
                                    'S_NOT_CONNECTED'.format(ip=pjlink.name)),
                               call('({ip}) Setting projector source_available to '
                                    '"[\'11\', \'12\', \'21\', \'22\', \'31\', \'32\']"'.format(ip=pjlink.name))]

            chk_data = '21 12 11 22 32 31'  # Although they should already be sorted, use unsorted to verify method
            chk_test = ['11', '12', '21', '22', '31', '32']

            # WHEN: process_inst called with test data
            pjlink.process_inst(data=chk_data)

            # THEN: Data should have been sorted and saved properly
            assert pjlink.source_available == chk_test, "Sources should have been sorted and saved"
            mock_log.debug.assert_has_calls(log_debug_calls)

    @skip('Needs update to new setup')
    def test_projector_process_lamp_invalid(self):
        """
        Test status multiple lamp on/off and hours
        """
        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.lamp = [{'Hours': 00000, 'On': True},
                           {'Hours': 11111, 'On': False}]
            log_data = [call('({ip}) process_lamp(): Invalid data "11111 1 22222 0 333A3 1"'.format(ip=pjlink.name))]

            # WHEN: Call process_command with invalid lamp data
            pjlink.process_lamp('11111 1 22222 0 333A3 1')

            # THEN: lamps should not have changed
            assert 2 == len(pjlink.lamp), 'Projector should have kept 2 lamps specified'
            assert pjlink.lamp[0]['On'] is True, 'Lamp 1 power status should have stayed TRUE'
            assert 00000 == pjlink.lamp[0]['Hours'], 'Lamp 1 hours should have been left at 00000'
            assert pjlink.lamp[1]['On'] is False, 'Lamp 2 power status should have stayed FALSE'
            assert 11111 == pjlink.lamp[1]['Hours'], 'Lamp 2 hours should have been left at 11111'
            mock_log.warning.assert_has_calls(log_data)

    @skip('Needs update to new setup')
    def test_projector_process_lamp_multiple(self):
        """
        Test status multiple lamp on/off and hours
        """
        # GIVEN: Test object
        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        pjlink.lamp = []

        # WHEN: Call process_command with invalid lamp data
        pjlink.process_lamp('11111 1 22222 0 33333 1')

        # THEN: Lamp should have been set with proper lamp status
        assert 3 == len(pjlink.lamp), 'Projector should have 3 lamps specified'
        assert pjlink.lamp[0]['On'] is True, 'Lamp 1 power status should have been set to TRUE'
        assert 11111 == pjlink.lamp[0]['Hours'], 'Lamp 1 hours should have been set to 11111'
        assert pjlink.lamp[1]['On'] is False, 'Lamp 2 power status should have been set to FALSE'
        assert 22222 == pjlink.lamp[1]['Hours'], 'Lamp 2 hours should have been set to 22222'
        assert pjlink.lamp[2]['On'] is True, 'Lamp 3 power status should have been set to TRUE'
        assert 33333 == pjlink.lamp[2]['Hours'], 'Lamp 3 hours should have been set to 33333'

    @skip('Needs update to new setup')
    def test_projector_process_lamp_single(self):
        """
        Test status lamp on/off and hours
        """

        # GIVEN: Test object
        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        pjlink.lamp = []

        # WHEN: Call process_command with invalid lamp data
        pjlink.process_lamp('22222 1')

        # THEN: Lamp should have been set with status=ON and hours=22222
        assert 1 == len(pjlink.lamp), 'Projector should have only 1 lamp'
        assert pjlink.lamp[0]['On'] is True, 'Lamp power status should have been set to TRUE'
        assert 22222 == pjlink.lamp[0]['Hours'], 'Lamp hours should have been set to 22222'

    @skip('Needs update to new setup')
    def test_projector_process_lamp_single_hours_only(self):
        """
        Test process lamp with 1 lamp reply hours only and no on/off status
        """
        # GIVEN: Test object
        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        pjlink.lamp = []

        # WHEN: Process lamp command called with only hours and no lamp power state
        pjlink.process_lamp("45")

        # THEN: Lamp should show hours as 45 and lamp power as Unavailable
        assert 1 == len(pjlink.lamp), 'There should only be 1 lamp available'
        assert 45 == pjlink.lamp[0]['Hours'], 'Lamp hours should have equalled 45'
        assert pjlink.lamp[0]['On'] is None, 'Lamp power should be "None"'

    @skip('Needs update to new setup')
    def test_projector_process_name(self):
        """
        Test saving NAME data from projector
        """
        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            chk_data = "Some Name the End-User Set IN Projector"
            log_debug_calls = [call('({ip}) Setting projector PJLink name to '
                                    '"Some Name the End-User Set IN Projector"'.format(ip=pjlink.name))]

            # WHEN: process_name called with test data
            pjlink.process_name(data=chk_data)

            # THEN: name should be set and logged
            assert pjlink.pjlink_name == chk_data, 'Name test data should have been saved'
            mock_log.debug.assert_has_calls(log_debug_calls)

    @skip('Needs update to new setup')
    def test_projector_process_powr_on(self):
        """
        Test status power to ON
        """
        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'change_status') as mock_change_status, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons') as mock_UpdateIcons:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.power = S_STANDBY

            # WHEN: process_name called with test data
            pjlink.process_powr(data=PJLINK_POWR_STATUS[S_ON])

            # THEN: Power should be set to ON
            assert pjlink.power == S_ON, 'Power should have been set to ON'
            assert mock_UpdateIcons.emit.called is True, 'projectorUpdateIcons should have been called'
            mock_send_command.assert_called_once_with('INST')
            mock_change_status.assert_called_once_with(S_ON)

    @skip('Needs update to new setup')
    def test_projector_process_powr_invalid(self):
        """
        Test process_powr invalid call
        """
        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'change_status') as mock_change_status, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons') as mock_UpdateIcons:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.power = S_STANDBY
            log_warn_calls = [call('({ip}) Unknown power response: "99"'.format(ip=pjlink.name))]

            # WHEN: process_name called with test data
            pjlink.process_powr(data='99')

            # THEN: Power should be set to ON
            assert pjlink.power == S_STANDBY, 'Power should not have changed'
            mock_UpdateIcons.emit.assert_not_called()
            mock_change_status.assert_not_called()
            mock_send_command.assert_not_called()
            mock_log.warning.assert_has_calls(log_warn_calls)

    @skip('Needs update to new setup')
    def test_projector_process_powr_off(self):
        """
        Test status power to STANDBY
        """
        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink.PJLink, 'send_command') as mock_send_command, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'change_status') as mock_change_status, \
                patch.object(openlp.core.projectors.pjlink.PJLink, 'projectorUpdateIcons') as mock_UpdateIcons:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.power = S_ON

            # WHEN: process_name called with test data
            pjlink.process_powr(data=PJLINK_POWR_STATUS[S_STANDBY])

            # THEN: Power should be set to ON
            assert pjlink.power == S_STANDBY, 'Power should have changed to S_STANDBY'
            mock_UpdateIcons.emit.assert_called_with()
            mock_change_status.assert_called_with(313)
            mock_send_command.assert_not_called()

    @skip('Needs update to new setup')
    def test_projector_process_rfil_save(self):
        """
        Test saving filter type
        """
        filter_model = 'Filter Type Test'

        # GIVEN: Test object
        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        pjlink.model_filter = None

        # WHEN: Filter model is received
        pjlink.process_rfil(data=filter_model)

        # THEN: Filter model number should be saved
        assert pjlink.model_filter == filter_model, 'Filter type should have been saved'

    @skip('Needs update to new setup')
    def test_projector_process_rfil_nosave(self):
        """
        Test saving filter type previously saved
        """
        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.model_filter = 'Old filter type'
            filter_model = 'Filter Type Test'
            log_warn_calls = [call('({ip}) Filter model already set'.format(ip=pjlink.name)),
                              call('({ip}) Saved model: "Old filter type"'.format(ip=pjlink.name)),
                              call('({ip}) New model: "Filter Type Test"'.format(ip=pjlink.name))]

            # WHEN: Filter model is received
            pjlink.process_rfil(data=filter_model)

            # THEN: Filter model number should be saved
            assert pjlink.model_filter != filter_model, 'Filter type should NOT have been saved'
            mock_log.warning.assert_has_calls(log_warn_calls)

    @skip('Needs update to new setup')
    def test_projector_process_rlmp_save(self):
        """
        Test saving lamp type
        """
        # GIVEN: Test object
        # GIVEN: Test object
        pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
        pjlink.model_lamp = None
        lamp_model = 'Lamp Type Test'

        # WHEN: Filter model is received
        pjlink.process_rlmp(data=lamp_model)

        # THEN: Filter model number should be saved
        assert pjlink.model_lamp == lamp_model, 'Lamp type should have been saved'

    @skip('Needs update to new setup')
    def test_projector_process_rlmp_nosave(self):
        """
        Test saving lamp type previously saved
        """
        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.model_lamp = 'Old lamp type'
            lamp_model = 'Lamp Type Test'
            log_warn_calls = [call('({ip}) Lamp model already set'.format(ip=pjlink.name)),
                              call('({ip}) Saved lamp: "Old lamp type"'.format(ip=pjlink.name)),
                              call('({ip}) New lamp: "Lamp Type Test"'.format(ip=pjlink.name))]

            # WHEN: Filter model is received
            pjlink.process_rlmp(data=lamp_model)

            # THEN: Filter model number should be saved
            assert pjlink.model_lamp != lamp_model, 'Lamp type should NOT have been saved'
            mock_log.warning.assert_has_calls(log_warn_calls)

    @skip('Needs update to new setup')
    def test_projector_process_snum_set(self):
        """
        Test saving serial number from projector
        """
        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:

            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.serial_no = None
            log_debug_calls = [call('({ip}) Setting projector serial number to '
                                    '"Test Serial Number"'.format(ip=pjlink.name))]
            test_number = 'Test Serial Number'

            # WHEN: No serial number is set and we receive serial number command
            pjlink.process_snum(data=test_number)

            # THEN: Serial number should be set
            assert pjlink.serial_no == test_number, 'Projector serial number should have been set'
            mock_log.debug.assert_has_calls(log_debug_calls)

    @skip('Needs update to new setup')
    def test_projector_process_snum_different(self):
        """
        Test projector serial number different than saved serial number
        """
        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.serial_no = 'Previous serial number'
            log_warn_calls = [call('({ip}) Projector serial number does not match '
                                   'saved serial number'.format(ip=pjlink.name)),
                              call('({ip}) Saved:    "Previous serial number"'.format(ip=pjlink.name)),
                              call('({ip}) Received: "Test Serial Number"'.format(ip=pjlink.name)),
                              call('({ip}) NOT saving serial number'.format(ip=pjlink.name))]
            test_number = 'Test Serial Number'

            # WHEN: No serial number is set and we receive serial number command
            pjlink.process_snum(data=test_number)

            # THEN: Serial number should be set
            assert pjlink.serial_no != test_number, 'Projector serial number should NOT have been set'
            mock_log.warning.assert_has_calls(log_warn_calls)

    @skip('Needs update to new setup')
    def test_projector_process_sver(self):
        """
        Test invalid software version information - too long
        """
        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.sw_version = None
            pjlink.sw_version_received = None
            test_data = 'Test 1 Subtest 1'
            log_debug_calls = [call('({ip}) Setting projector software version to '
                                    '"Test 1 Subtest 1"'.format(ip=pjlink.name))]

            # WHEN: process_sver called with invalid data
            pjlink.process_sver(data=test_data)

            # THEN: Version information should not change
            assert pjlink.sw_version == test_data, 'Software version should have been updated'
            mock_log.debug.assert_has_calls(log_debug_calls)

    @skip('Needs update to new setup')
    def test_projector_process_sver_changed(self):
        """
        Test invalid software version information - Received different than saved
        """
        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            test_data_old = 'Test 1 Subtest 1'
            test_data_new = 'Test 1 Subtest 2'
            log_warn_calls = [call('({ip}) Projector software version does not match '
                                   'saved software version'.format(ip=pjlink.name)),
                              call('({ip}) Saved:    "Test 1 Subtest 1"'.format(ip=pjlink.name)),
                              call('({ip}) Received: "Test 1 Subtest 2"'.format(ip=pjlink.name)),
                              call('({ip}) Updating software version'.format(ip=pjlink.name))]
            pjlink.sw_version = test_data_old

            # WHEN: process_sver called with invalid data
            pjlink.process_sver(data=test_data_new)

            # THEN: Version information should not change
            assert pjlink.sw_version == test_data_new, 'Software version should have changed'
            mock_log.warning.assert_has_calls(log_warn_calls)

    @skip('Needs update to new setup')
    def test_projector_process_sver_invalid(self):
        """
        Test invalid software version information - too long
        """
        test_data = 'This is a test software version line that is too long based on PJLink version 2 specs'
        log_warn_calls = [call('Invalid software version - too long')]

        # GIVEN: Test object
        with patch.object(openlp.core.projectors.pjlink, 'log') as mock_log:
            pjlink = PJLink(Projector(**TEST1_DATA), no_poll=True)
            pjlink.sw_version = None

            # WHEN: process_sver called with invalid data
            pjlink.process_sver(data=test_data)

            # THEN: Version information should not change
            assert pjlink.sw_version is None, 'Software version should not have changed'
            assert pjlink.sw_version_received is None, 'Received software version should not have changed'
            mock_log.warning.assert_has_calls(log_warn_calls)
