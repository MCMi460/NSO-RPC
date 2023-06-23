import sys
from qtpy.QtCore import qVersion

try:
    qt_version = qVersion()
    if qt_version.startswith('6'):
        from .qt6_layout import *
    elif qt_version.startswith('5'):
        from .qt5_layout import *
    else:
        print(f"Unsupported Qt version: {qt_version}")
        sys.exit(1)
except (ImportError, TypeError) as e:
    print(f"Error importing Qt modules: {e}")
    sys.exit(1)
