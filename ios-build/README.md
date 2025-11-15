# iOS Cross-Compilation for HFST

This directory contains scripts and resources for cross-compiling the HFST (Helsinki Finite-State Transducer) library for iOS.

## Overview

The Sanaporakone iOS app requires the HFST library to load and query Finnish morphology models. This is a complex cross-compilation task involving:

1. **ICU** (International Components for Unicode) - Required by HFST
2. **OpenFST 1.7.9** - Finite-state transducer backend
3. **HFST 3.16.2** - The main morphology library

## Architecture

We're targeting:
- **iOS Devices**: ARM64 architecture
- **iOS Simulator**: x86_64 (Intel Macs) and ARM64 (Apple Silicon Macs)

## Build Strategy

### Phase 1: Dependency Compilation
1. Compile ICU for iOS
2. Compile OpenFST 1.7.9 for iOS
3. Compile HFST for iOS

### Phase 2: Library Packaging
- Create static libraries (.a files)
- Package as XCFramework for easy Xcode integration

### Phase 3: Swift Integration
- Create C/C++ bridge headers
- Create Swift wrapper for HFST API

## Minimal HFST API Required

Based on the Django app analysis, we only need:

```cpp
// Open and read FST file
HfstInputStream his("omorfi.generate.hfst");
HfstTransducer* generator = his.read();

// Perform lookups
HfstOneLevelPaths* results = generator->lookup("input_string");
```

## Dependencies

### System Requirements
- macOS with Xcode 14+ (for iOS SDK)
- Command-line tools: autoconf, automake, libtool, pkg-config
- CMake 3.20+

### Library Versions
- ICU 70.1+
- OpenFST 1.7.9 (not newer - HFST incompatible with 1.8+)
- HFST 3.16.2

## Build Scripts

- `build-icu.sh` - Cross-compile ICU for iOS
- `build-openfst.sh` - Cross-compile OpenFST for iOS
- `build-hfst.sh` - Cross-compile HFST for iOS
- `create-xcframework.sh` - Package libraries as XCFramework
