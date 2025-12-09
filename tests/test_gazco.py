import sys, os
# Ensure local src/ is on sys.path before installed packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import runpy
import pytest

# Dummy RfCat stub to intercept transmissions
class DummyRfCat:
    def __init__(self):
        self.transmissions = []
    def setMdmModulation(self, *args, **kwargs): pass
    def makePktFLEN(self, *args, **kwargs): pass
    def setMdmDRate(self, *args, **kwargs): pass
    def setMdmSyncMode(self, *args, **kwargs): pass
    def setFreq(self, *args, **kwargs): pass
    def setMaxPower(self): pass
    def RFxmit(self, data): self.transmissions.append(data)
    def setModeIDLE(self): pass

@pytest.fixture(autouse=True)
def stub_rfcat(monkeypatch):
    """Automatically stub out RfCat from rfcat package."""
    import rflib
    monkeypatch.setattr(rflib, 'RfCat', DummyRfCat)
    monkeypatch.setattr(rflib, 'MOD_ASK_OOK', 'OOK')
    return DummyRfCat

@pytest.fixture(autouse=True)
def stub_sleep(monkeypatch):
    """Prevent actual sleeping during tests."""
    import gazco_rf.controller as controller_module
    monkeypatch.setattr(controller_module, 'sleep', lambda x: None)


def test_send_on():
    from gazco_rf.controller import GazcoController
    ctrl = GazcoController()
    result = ctrl.send_command('on')
    assert result is True
    # Verify repeat count and payload
    expected = ctrl.commands['on']['data']
    assert all(pkt == expected for pkt in ctrl.d.transmissions)
    assert len(ctrl.d.transmissions) == ctrl.commands['on']['repeats']


def test_unknown_command(capsys):
    from gazco_rf.controller import GazcoController
    ctrl = GazcoController()
    result = ctrl.send_command('invalid')
    captured = capsys.readouterr()
    assert "Unknown command" in captured.out
    assert result is False


def test_convert_gazco_output(capsys):
    # Run the convert_gazco script as __main__ and capture its output
    runpy.run_module('gazco_rf.utils.convert_gazco', run_name='__main__')
    captured = capsys.readouterr()
    assert "PWM Key:" in captured.out
    assert "Byte string:" in captured.out

if __name__ == '__main__':
    pytest.main()
