# Contributing

This repository preserves the analysis and recorded transmissions for the
author's Gazco fireplace and Sonte smart film remotes. Changes should make the
work easier to reproduce without losing the evidence behind its choices.

## Work offline first

Python 3.10 or newer is sufficient for the controller dry runs and tests.
They use the standard library and do not require RfCat, a dongle, or access to
the maintainer's private repositories. From the repository root:

<!-- offline-smoke -->
```bash
python gazco-fireplace/code/controller.py on --dry-run
python sonte-smart-film/code/sonte_controller.py button1 --dry-run
```

Run the checks used in CI:

```bash
python -m unittest discover -s tests -v
python tools/check_documentation.py
```

CI runs these on Python 3.10, 3.11, and 3.12. The optional conversion utilities
need `bitstring`; actual transmission needs a compatible RfCat installation.
See the [installation guide](README.md#quick-start) for those separate paths.

## Preserve transmission evidence

- Keep logical command bits, PWM units, byte alignment, recorded padding, and
  the RFcat FLEN setting distinct. Explain their units in examples.
- Change a recorded profile only with evidence explaining the difference.
  Include the source capture or historical reference and the exact old/new
  bytes, settings, and expected effect.
- The repetitions and gaps are already encoded in each complete burst. Use
  the shared sender; do not add host-side repetition loops or sleeps.
- Do not silently rewrite the independent fixtures to match an implementation
  change. They preserve the pre-reconciliation reference bytes and hashes.
- Keep unresolved choices explicit, including ON padding, DOWN ten versus
  nineteen frames, and Sonte `original`'s unassigned physical meaning.

The implementation and evidence are described in
[TRANSMISSIONS.md](TRANSMISSIONS.md). `rf_signals.py` checks numeric transmit
status and attempts IDLE cleanup. Legacy libraries returning `None` remain
compatible but cannot expose firmware errors they discard internally. A
successful send means submission, not target acknowledgement.

## Test failures as well as successful submissions

Use injected fake radios. This example runs from `gazco-fireplace/code` and
does not import RfCat or open hardware:

```python
from unittest.mock import Mock
from controller import GazcoController

radio = Mock()
radio.RFxmit.return_value = 208
controller = GazcoController(radio=radio, modulation=0x30)
assert controller.send_command('on') is False
radio.RFxmit.assert_called_once_with(controller.profiles['on'].data)
radio.setModeIDLE.assert_called_once_with()
```

The existing tests cover exact bytes and settings, wrapper/controller agreement,
invalid commands before hardware access, nonzero statuses, configuration and
transport exceptions, interruption, and cleanup failures. Add a focused
regression that reproduces the behavior being changed. The code does not
implement a duty-cycle regulator; do not document or test a fictitious one.

## Documentation and hardware reports

Use commands and paths present in this repository. Mark runnable offline
Python CLI examples with `<!-- offline-smoke -->` immediately before their
`bash` block when they use `--dry-run` or `--help`; the documentation checker
executes those with radio imports blocked. It also checks local Markdown links.
Do not mark hardware commands, installation commands, or shell pipelines for
this check.

Preserve the author's historical account and dates. Distinguish those reports
from current software tests, new hardware observations, and protocol hypotheses.
For a hardware result, record device/firmware versions, profile, capture method,
and observed response. State explicitly when hardware has not been tested.
Do not infer emissions compliance or device acknowledgement from a successful
Python return value. Work only with equipment you are authorized to use.

## Submitting a change

Keep related fixes, documentation, and regression tests together in a coherent
change. Describe the problem, resulting behavior, evidence, checks performed,
and any remaining uncertainty. Run the offline checks before submission and
avoid unrelated formatting or profile changes.

This repository's contribution process applies here; it does not authorize
submitting changes to the original RfCat project. Contributions are under the
[MIT license](LICENSE.md). For bugs, include the command, Python/OS versions,
expected and observed behavior, and a minimal capture or fake-radio reproduction
where possible. Do not include credentials or unrelated private data.
