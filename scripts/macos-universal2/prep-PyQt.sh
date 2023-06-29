#!/bin/bash
# Provided by @spotlightishere on Github
# https://github.com/MCMi460/NSO-RPC/pull/86#issuecomment-1605700512

alias python3=python3.10

# Download and unpack
python3 -m pip download --only-binary=:all: --platform=macosx_13_0_x86_64 PyQt6_Qt6
python3 -m pip download --only-binary=:all: --platform=macosx_13_0_arm64 PyQt6_Qt6
python3 -m wheel unpack PyQt6_*arm64.whl --dest arm64
python3 -m wheel unpack PyQt6_*x86_64.whl --dest x86_64

# We'll use x86_64 as our basis.
# As of writing, PyQt6_Qt6 specifies a minimum of 10.14 for x86_64, and 11.0 for arm64.
# We'll reuse this tag; it should be updated if this ever changes in the future.
python3 -m wheel tags --platform-tag macosx_10_14_universal2 PyQt6_*x86_64.whl
python3 -m wheel unpack PyQt6_*universal2.whl --dest universal

# https://stackoverflow.com/a/46020381
merge_frameworks() {
  # Remove the leading universal/ from this path.
  binary_path="${1##universal/}"
  lipo -create -arch x86_64 "x86_64/$binary_path" "arm64/$binary_path" -output "universal/$binary_path"
}
export -f merge_frameworks

# Iterate through all frameworks and libraries, and lipo together
find universal -perm +111 -type f -exec sh -c 'merge_frameworks "$1"' _ {} \;
python3 -m wheel pack universal/PyQt6_*

# Finally, install our universal python3.10 -m wheel.
python3 -m pip install PyQt6_*universal2.whl --force-reinstall