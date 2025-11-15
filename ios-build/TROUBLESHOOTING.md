# HFST iOS Build Troubleshooting Guide

This document contains solutions to common problems encountered when cross-compiling HFST for iOS.

## Build Environment Issues

### "Xcode is not installed"
```
brew install --cask xcode
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -license accept
```

### "Cannot find SDK"
```bash
# List available SDKs
xcodebuild -showsdks

# If iOS SDK missing, install Xcode command-line tools
xcode-select --install
```

### "autoconf not found"
```bash
brew install autoconf automake libtool pkg-config
```

## ICU Build Issues

### "Cross-compiling failed"
ICU requires a host build first. The script handles this, but if it fails:

```bash
cd sources/icu-src/source
./configure --prefix=$(pwd)/../../icu-host/install
make -j$(sysctl -n hw.ncpu)
make install
```

### "Unable to find cross-build"
Ensure the `--with-cross-build` path points to the host build directory.

## OpenFST Build Issues

### "C++17 not supported"
OpenFST 1.7.9 requires C++17. Check your Xcode version:

```bash
clang++ --version  # Should be LLVM 13+ (Xcode 14+)
```

### "Undefined symbols for architecture arm64"
This usually means linker flags are wrong. Check:
- Is `-arch arm64` in CFLAGS and LDFLAGS?
- Is `-isysroot` pointing to correct SDK?

### "Library depends on unavailable symbols"
OpenFST might be trying to use features not available on iOS. Try:

```bash
# In openfst configure:
--disable-bin          # Don't build command-line tools
--disable-shared       # Static linking only
--enable-compact-fsts  # Smaller binary size
```

## HFST Build Issues

### "configure: error: ICU-50 or newer is required"
ICU headers aren't found. Check:

```bash
export PKG_CONFIG_PATH="${INSTALL_PREFIX}/lib/pkgconfig"
pkg-config --modversion icu-uc
```

### "Cannot find fst/fstlib.h"
OpenFST headers not found:

```bash
export CPPFLAGS="-I${INSTALL_PREFIX}/include"
export LDFLAGS="-L${INSTALL_PREFIX}/lib"
```

### "Undefined reference to pthread_*"
Add pthread to LDFLAGS:

```bash
export LDFLAGS="${LDFLAGS} -lpthread"
```

### "Symbol not found: _libhfst_*"
The library built but symbols are missing. This is usually because backends were disabled. Check configure output:

```bash
-- Building hfst-3.16.2:
    * libhfst with sfst: no
    *         with openfst: yes    <-- Should be 'yes'
    *         with foma: no
```

## XCFramework Creation Issues

### "Missing required architecture"
You need all three builds:
- arm64-apple-ios (device)
- x86_64-apple-iossimulator (Intel simulator)
- arm64-apple-iossimulator (Apple Silicon simulator)

Check that all three PREFIX directories exist:
```bash
ls ios-libs/
# Should show: arm64/ x86_64/ arm64-sim/
```

### "Header files missing"
Ensure headers were installed:

```bash
ls ios-libs/arm64/include/hfst/
# Should show HfstTransducer.h, etc.
```

## Runtime Issues (in Xcode)

### "Image not found: libhfst.dylib"
You built a dynamic library instead of static. HFST must be static for iOS:

```bash
# In HFST configure:
--enable-static --disable-shared
```

### "Symbol not found: _hfst_generator_create"
The bridging header isn't working. Check:
1. Is `HFSTWrapper.cpp` added to Xcode target?
2. Is bridging header path set in Build Settings?
3. Is the header using `extern "C"`?

### "Thread 1: Fatal error: Unexpectedly found nil"
Generator creation failed. Enable debugging:

```swift
if let errorMsg = String(cString: hfst_get_last_error()) {
    print("HFST Error: \(errorMsg)")
}
```

### "File not found: omorfi.generate.hfst"
The HFST model isn't in the app bundle. In Xcode:
1. Add `omorfi.generate.hfst` to project
2. Check it's in "Copy Bundle Resources" build phase
3. Access it:
```swift
Bundle.main.path(forResource: "omorfi.generate", ofType: "hfst")
```

## Performance Issues

### "App launch is slow (>3 seconds)"
Loading the 25MB FST at startup is slow. Solutions:

1. **Async loading:**
```swift
class HFSTManager {
    var generator: HFSTGenerator?

    func loadAsync() {
        DispatchQueue.global(qos: .userInitiated).async {
            // Load HFST
            DispatchQueue.main.async {
                // Update UI
            }
        }
    }
}
```

2. **Lazy loading:** Only load when first needed

3. **Memory-mapped I/O:** (Advanced) Modify HFST to use mmap instead of loading entire file

### "App uses too much memory"
The FST is loaded into RAM. If this is a problem:
- Use memory-mapped file I/O
- Compress the FST model (may slow lookups)
- Profile with Xcode Instruments to find actual usage

## Build Script Modifications

### If build-all-ios.sh fails completely:

Try building each component manually:

```bash
# 1. Build ICU
cd sources/icu-src/source
./configure --host=arm64-apple-ios \
    --prefix=/path/to/install \
    --enable-static --disable-shared \
    --with-cross-build=/path/to/host-build

# 2. Build OpenFST
cd sources/openfst-1.7.9
./configure --host=arm64-apple-ios \
    --prefix=/path/to/install \
    --enable-static --disable-shared

# 3. Build HFST
cd sources/hfst
./configure --host=arm64-apple-ios \
    --prefix=/path/to/install \
    --enable-static --disable-shared \
    --with-openfst --without-foma --without-sfst
```

## Getting Help

If you encounter errors not listed here:

1. **Check configure logs:**
```bash
cat build-arm64/config.log | grep -i error
```

2. **Check make output:**
```bash
make V=1  # Verbose mode shows full commands
```

3. **Minimal test:**
Create a simple C++ file to test if HFST works:

```cpp
#include <hfst/HfstTransducer.h>
#include <iostream>

int main() {
    std::cout << "HFST Headers Found!" << std::endl;
    return 0;
}
```

Compile:
```bash
clang++ -std=c++17 -I/path/to/hfst/include test.cpp
```

## Last Resort: Simplified Build

If all else fails, try building HFST with minimal features:

```bash
./configure \
    --enable-static \
    --disable-shared \
    --without-foma \
    --without-sfst \
    --with-openfst \
    --disable-all-tools \
    --disable-python-bindings \
    --disable-fstbinary \
    --disable-readline
```

This disables everything except core FST lookup functionality.
