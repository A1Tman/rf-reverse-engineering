"""Offline regression tests against pre-reconciliation script bytes."""

import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import runpy
import sys
import unittest
from unittest.mock import Mock, call, patch


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = json.loads((ROOT / 'tests/fixtures/transmissions.json').read_text())
# Independent hashes recorded before replacing any standalone transmitter.
HASHES = {
    ('gazco', 'on'): '46c01c466e86c111a97e52429ad79f0994d415ec797e1105e97b03072df54c47',
    ('gazco', 'off'): 'b6f148b482cbaaaf66b72707caf68d4a7405d7e80e445cc511dfbff503a2598b',
    ('gazco', 'up'): 'bb5c3d5c11bccc188134e8ac1786f17fb1360f43920deba0fa924019f4bd84ba',
    ('gazco', 'down'): 'a10b70f0c59d9c371d2af84cad95b849ca88830cdcb4e78dc121e195d200187f',
    ('gazco', 'down_notes_19'): '4bd3ca2c9bb97ff2030c4373a0bbb3366c7950f5333d834c04f0fffa00ef9496',
    ('sonte', 'button1'): '3c8c586f09f4237e5f2ea835897928242a38896ae710b2f3527bf279acdd6a26',
    ('sonte', 'button2'): '373c716524b3507f9c5cf30f09866af6348d8a1c4f63319913b4dd698aba3631',
    ('sonte', 'original'): 'cd265150609873ff655931b08a0d8bc10240f50333b014a2d3452aeb967ac7a4',
}


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GAZCO = load('gazco_controller_test', 'gazco-fireplace/code/controller.py')
SONTE = load('sonte_controller_test', 'sonte-smart-film/code/sonte_controller.py')
CONTROLLERS = {'gazco': GAZCO.GazcoController, 'sonte': SONTE.SonteController}
WRAPPERS = {
    ('gazco', command): f'gazco-fireplace/code/scripts/gazco_{command}.py'
    for command in ('on', 'off', 'up', 'down')
}
WRAPPERS.update({
    ('sonte', 'button1'): 'sonte-smart-film/code/sonte_button1_transparent.py',
    ('sonte', 'button2'): 'sonte-smart-film/code/sonte_button2_opaque.py',
})


class TransmissionTests(unittest.TestCase):
    def test_all_profiles_match_frozen_bytes_and_single_burst_call_order(self):
        for device, profiles in FIXTURES.items():
            for command, fixture in profiles.items():
                with self.subTest(device=device, command=command):
                    expected = bytes.fromhex(fixture['hex'])
                    self.assertEqual(hashlib.sha256(expected).hexdigest(), HASHES[device, command])
                    radio = Mock()
                    radio.RFxmit.return_value = 0
                    controller = CONTROLLERS[device](radio, modulation=0x30)
                    with contextlib.redirect_stdout(io.StringIO()):
                        self.assertTrue(controller.send_command(command))
                    self.assertEqual(radio.mock_calls, [
                        call.setMdmModulation(0x30), call.makePktFLEN(fixture['packet_length']),
                        call.setMdmDRate(fixture['baud']), call.setMdmSyncMode(0),
                        call.setFreq(fixture['frequency']), call.setMaxPower(),
                        call.RFxmit(expected), call.setModeIDLE(),
                    ])

    def test_controller_and_wrappers_import_without_rfcat_or_output(self):
        output = io.StringIO()
        paths = ['gazco-fireplace/code/controller.py', 'sonte-smart-film/code/sonte_controller.py', *WRAPPERS.values()]
        with patch.dict(sys.modules, {'rflib': None}), contextlib.redirect_stdout(output):
            for path in paths:
                runpy.run_path(str(ROOT / path), run_name='import_only')
            for controller_class in CONTROLLERS.values():
                self.assertIsNone(controller_class().d)
        self.assertEqual(output.getvalue(), '')

    def test_every_wrapper_sends_the_same_frozen_burst_as_controller(self):
        for (device, command), path in WRAPPERS.items():
            with self.subTest(path=path):
                radio = Mock()
                radio.RFxmit.return_value = 0
                rfcat = Mock(RfCat=Mock(return_value=radio), MOD_ASK_OOK=0x30)
                with patch.dict(sys.modules, {'rflib': rfcat}), patch.object(sys, 'argv', [path]), contextlib.redirect_stdout(io.StringIO()):
                    with self.assertRaises(SystemExit) as result:
                        runpy.run_path(str(ROOT / path), run_name='__main__')
                self.assertEqual(result.exception.code, 0)
                radio.RFxmit.assert_called_once_with(bytes.fromhex(FIXTURES[device][command]['hex']))

    def test_all_dry_runs_and_help_do_not_load_rfcat(self):
        for device, module in [('gazco', GAZCO), ('sonte', SONTE)]:
            for command, fixture in FIXTURES[device].items():
                output = io.StringIO()
                with patch.dict(sys.modules, {'rflib': None}), contextlib.redirect_stdout(output):
                    self.assertEqual(module.main([command, '--dry-run']), 0)
                self.assertIn(fixture['hex'], output.getvalue())
            with patch.dict(sys.modules, {'rflib': None}), contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as result:
                module.main(['--help'])
            self.assertEqual(result.exception.code, 0)
        for path in WRAPPERS.values():
            with patch.dict(sys.modules, {'rflib': None}), patch.object(sys, 'argv', [path, '--dry-run']), contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as result:
                runpy.run_path(str(ROOT / path), run_name='__main__')
            self.assertEqual(result.exception.code, 0)

    def test_invalid_commands_rejected_before_hardware_creation(self):
        for module, controller_class in [(GAZCO, GAZCO.GazcoController), (SONTE, SONTE.SonteController)]:
            rfcat = Mock()
            with patch.dict(sys.modules, {'rflib': rfcat}), contextlib.redirect_stderr(io.StringIO()):
                self.assertFalse(controller_class().send_command('invalid'))
                with self.assertRaises(SystemExit) as result:
                    module.main(['invalid'])
            self.assertEqual(result.exception.code, 2)
            rfcat.RfCat.assert_not_called()

    def test_status_success_and_failures_are_not_reported_as_target_success(self):
        for status, expected in [(None, True), (0, True), (1, False), (208, False), ('0', False), (b'\0', False), (0.0, False)]:
            with self.subTest(status=status):
                radio = Mock()
                radio.RFxmit.return_value = status
                controller = GAZCO.GazcoController(radio, modulation=0x30)
                output = io.StringIO()
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(controller.send_command('on'), expected)
                radio.setModeIDLE.assert_called_once_with()
                self.assertEqual('submitted' in output.getvalue(), expected)

    def test_failures_and_interruption_idle_once_without_retrying(self):
        for method, error in [('setFreq', RuntimeError('configuration failure')), ('RFxmit', RuntimeError('transport failure')), ('RFxmit', KeyboardInterrupt())]:
            with self.subTest(method=method, error=type(error)):
                radio = Mock()
                getattr(radio, method).side_effect = error
                controller = SONTE.SonteController(radio, modulation=0x30)
                with contextlib.redirect_stderr(io.StringIO()):
                    if isinstance(error, KeyboardInterrupt):
                        with self.assertRaises(KeyboardInterrupt):
                            controller.send_command('original')
                    else:
                        self.assertFalse(controller.send_command('original'))
                radio.setModeIDLE.assert_called_once_with()
                self.assertLessEqual(radio.RFxmit.call_count, 1)

    def test_idle_failure_makes_operation_unsuccessful(self):
        radio = Mock()
        radio.RFxmit.return_value = 0
        radio.setModeIDLE.side_effect = RuntimeError('idle failure')
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
            self.assertFalse(GAZCO.GazcoController(radio, modulation=0x30).send_command('on'))
        self.assertNotIn('submitted', output.getvalue())

    def test_cli_reports_transmit_error_as_nonzero(self):
        radio = Mock()
        radio.RFxmit.return_value = 208
        rfcat = Mock(RfCat=Mock(return_value=radio), MOD_ASK_OOK=0x30)
        with patch.dict(sys.modules, {'rflib': rfcat}), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(SONTE.main(['original']), 1)

    def test_profiles_are_immutable(self):
        with self.assertRaises(TypeError):
            GAZCO.GazcoController.profiles['on'] = None
        with self.assertRaises(AttributeError):
            GAZCO.GazcoController.profiles['on'].data = b''


if __name__ == '__main__':
    unittest.main()
