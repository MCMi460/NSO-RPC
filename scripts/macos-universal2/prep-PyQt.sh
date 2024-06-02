#!/bin/bash
set -e

# Provided by @spotlightishere on Github
# https://github.com/MCMi460/NSO-RPC/pull/86#issuecomment-1605700512

# Within GitHub Actions and similar, we should use the Python.org
# copy of Python 3.11 available. This permits a universal2 framework for py2app.
# (Otherwise, GitHub's default runners include a single architecture version.)
if [[ "$CI" == "true" ]]; then
  shopt -s expand_aliases
  alias python3=/Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11
fi

# If we already have a universal2 wheel available, install and process no further.
# https://stackoverflow.com/a/6364244
if compgen -G "./PyQt6_*universal2.whl"; then
  python3 -m pip install PyQt6_*universal2.whl --force-reinstall
  exit 0
fi

# Download and unpack
python3 -m pip download --only-binary=:all: --platform=macosx_13_0_x86_64 PyQt6_Qt6
python3 -m pip download --only-binary=:all: --platform=macosx_13_0_arm64 PyQt6_Qt6
python3 -m wheel unpack PyQt6_Qt6*arm64.whl --dest arm64
python3 -m wheel unpack PyQt6_Qt6*x86_64.whl --dest x86_64

# We'll use x86_64 as our basis.
# As of writing, PyQt6_Qt6 specifies a minimum of 10.14 for x86_64, and 11.0 for arm64.
# We'll reuse this tag; it should be updated if this ever changes in the future.
python3 -m wheel tags --platform-tag macosx_10_14_universal2 PyQt6_Qt6*x86_64.whl
python3 -m wheel unpack PyQt6_Qt6*universal2.whl --dest universal

# https://stackoverflow.com/a/46020381
merge_frameworks() {
  # Remove the leading universal/ from this path.
  binary_path="${1##universal/}"
  lipo -create -arch x86_64 "x86_64/$binary_path" "arm64/$binary_path" -output "universal/$binary_path"
}
export -f merge_frameworks

# Iterate through all frameworks and libraries, and lipo together.
find universal -perm +111 -type f -exec sh -c 'merge_frameworks "$1"' _ {} \;

# We can now debloat our created universal wheel by removing
# frameworks and libraries irrelevant to NSO-RPC.
debloat_paths=(
  "Qt6/lib/QtQuick3DRuntimeRender.framework"
  "Qt6/lib/QtQuickParticles.framework"
  "Qt6/lib/QtSpatialAudio.framework"
  "Qt6/lib/QtShaderTools.framework"
  "Qt6/lib/QtQuickTest.framework"
  "Qt6/lib/QtBluetooth.framework"
  "Qt6/lib/QtDesigner.framework"
  "Qt6/lib/QtQuick.framework"
  "Qt6/lib/QtHelp.framework"
  "Qt6/lib/QtPdf.framework"
  "Qt6/lib/QtQml.framework"
  "Qt6/plugins/sqldrivers"
  "Qt6/plugins/multimedia"
  "Qt6/qml"
)

for debloat_path in "${debloat_paths[@]}"; do
  rm -rf universal/PyQt6_Qt6*/PyQt6/$debloat_path
done

# Finally, pack and install our universal2 wheel.
python3 -m wheel pack universal/PyQt6_*
python3 -m pip install PyQt6_*universal2.whl --force-reinstall
