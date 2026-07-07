"""UI test configuration.

Forces the offscreen Qt platform so widget tests run headless, without
opening real windows. Must be set before any ``QApplication`` is created.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
