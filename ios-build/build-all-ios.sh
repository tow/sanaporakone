#!/bin/bash
#
# Cross-compile HFST and dependencies for iOS
# Must be run on macOS with Xcode installed
#

set -e  # Exit on error

# Configuration
IOS_SDK_VERSION="17.0"  # Adjust based on your Xcode version
MIN_IOS_VERSION="15.0"
BUILD_DIR="$(pwd)/build"
PREFIX_DIR="$(pwd)/ios-libs"
SRC_DIR="$(pwd)/sources"

# Architectures
ARM64_DEVICE="arm64"
X86_64_SIM="x86_64"
ARM64_SIM="arm64"  # For Apple Silicon simulator

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    log_error "This script must be run on macOS with Xcode installed"
    log_error "iOS cross-compilation requires the iOS SDK which is only available on macOS"
    exit 1
fi

# Check if Xcode is installed
if ! command -v xcodebuild &> /dev/null; then
    log_error "Xcode is not installed or xcodebuild is not in PATH"
    log_error "Please install Xcode from the App Store"
    exit 1
fi

# Get Xcode paths
XCODE_PATH=$(xcode-select -p)
log_info "Using Xcode at: $XCODE_PATH"

# SDK paths
IOS_SDK_PATH=$(xcrun --sdk iphoneos --show-sdk-path)
IOS_SIM_SDK_PATH=$(xcrun --sdk iphonesimulator --show-sdk-path)

log_info "iOS SDK: $IOS_SDK_PATH"
log_info "iOS Simulator SDK: $IOS_SIM_SDK_PATH"

# Create directories
mkdir -p "$BUILD_DIR" "$PREFIX_DIR" "$SRC_DIR"

# Download sources
log_info "Downloading source packages..."

cd "$SRC_DIR"

# Download ICU if needed
if [ ! -d "icu" ]; then
    log_info "Downloading ICU..."
    ICU_VERSION="74-2"
    curl -L "https://github.com/unicode-org/icu/releases/download/release-74-2/icu4c-74_2-src.tgz" -o icu.tgz
    tar -xzf icu.tgz
    mv icu icu-src
fi

# Download OpenFST if needed
if [ ! -d "openfst-1.7.9" ]; then
    log_info "Downloading OpenFST 1.7.9..."
    curl -L "http://www.openfst.org/twiki/pub/FST/FstDownload/openfst-1.7.9.tar.gz" -o openfst.tgz
    tar -xzf openfst.tgz
fi

# Clone HFST if needed
if [ ! -d "hfst" ]; then
    log_info "Cloning HFST..."
    git clone https://github.com/hfst/hfst.git
fi

cd ..

# Function to build for a specific architecture and SDK
build_for_arch() {
    local ARCH=$1
    local SDK=$2
    local SDK_PATH=$3
    local TARGET_NAME="${ARCH}-apple-ios"

    log_info "Building for ${ARCH} (${SDK})..."

    # Set up environment
    export CC="$(xcrun --sdk $SDK --find clang)"
    export CXX="$(xcrun --sdk $SDK --find clang++)"
    export CPP="$(xcrun --sdk $SDK --find cpp)"
    export LD="$(xcrun --sdk $SDK --find ld)"
    export AR="$(xcrun --sdk $SDK --find ar)"
    export RANLIB="$(xcrun --sdk $SDK --find ranlib)"
    export STRIP="$(xcrun --sdk $SDK --find strip)"

    export CFLAGS="-arch ${ARCH} -isysroot ${SDK_PATH} -mios-version-min=${MIN_IOS_VERSION} -fembed-bitcode"
    export CXXFLAGS="${CFLAGS} -std=c++17"
    export LDFLAGS="-arch ${ARCH} -isysroot ${SDK_PATH}"

    local INSTALL_PREFIX="${PREFIX_DIR}/${ARCH}"

    # Build ICU
    log_info "Building ICU for ${ARCH}..."
    cd "${SRC_DIR}/icu-src/source"

    # ICU needs a host build first (for tools)
    if [ ! -d "../../icu-host/source" ]; then
        log_info "Building ICU host tools..."
        mkdir -p ../../icu-host
        cd ../../icu-host
        ../icu-src/source/configure --prefix="$(pwd)/install" --enable-static --disable-shared
        make -j$(sysctl -n hw.ncpu)
        make install
        cd ../icu-src/source
    fi

    # Cross-compile ICU
    mkdir -p "build-${ARCH}"
    cd "build-${ARCH}"

    ../configure \
        --host="${TARGET_NAME}" \
        --prefix="${INSTALL_PREFIX}" \
        --enable-static \
        --disable-shared \
        --with-cross-build="$(pwd)/../../icu-host/source" \
        --disable-samples \
        --disable-tests

    make -j$(sysctl -n hw.ncpu)
    make install

    # Build OpenFST
    log_info "Building OpenFST for ${ARCH}..."
    cd "${SRC_DIR}/openfst-1.7.9"
    mkdir -p "build-${ARCH}"
    cd "build-${ARCH}"

    ../configure \
        --host="${TARGET_NAME}" \
        --prefix="${INSTALL_PREFIX}" \
        --enable-static \
        --disable-shared \
        --enable-compact-fsts \
        --enable-const-fsts \
        --enable-far \
        --enable-ngram-fsts \
        --disable-bin

    make -j$(sysctl -n hw.ncpu)
    make install

    # Build HFST
    log_info "Building HFST for ${ARCH}..."
    cd "${SRC_DIR}/hfst"

    # Generate configure if needed
    if [ ! -f "configure" ]; then
        ./autogen.sh
    fi

    mkdir -p "build-${ARCH}"
    cd "build-${ARCH}"

    export PKG_CONFIG_PATH="${INSTALL_PREFIX}/lib/pkgconfig"
    export CPPFLAGS="-I${INSTALL_PREFIX}/include ${CFLAGS}"
    export LDFLAGS="-L${INSTALL_PREFIX}/lib ${LDFLAGS}"

    ../configure \
        --host="${TARGET_NAME}" \
        --prefix="${INSTALL_PREFIX}" \
        --enable-static \
        --disable-shared \
        --with-openfst \
        --without-foma \
        --without-sfst \
        --enable-no-tools \
        --disable-python-bindings

    make -j$(sysctl -n hw.ncpu)
    make install

    cd "$BUILD_DIR"
}

# Build for each architecture
log_info "Starting multi-architecture build..."

# Device (ARM64)
build_for_arch "$ARM64_DEVICE" "iphoneos" "$IOS_SDK_PATH"

# Simulator (x86_64 - Intel Macs)
build_for_arch "$X86_64_SIM" "iphonesimulator" "$IOS_SIM_SDK_PATH"

# Simulator (ARM64 - Apple Silicon Macs)
build_for_arch "$ARM64_SIM" "iphonesimulator" "$IOS_SIM_SDK_PATH"

# Create XCFramework
log_info "Creating XCFramework..."

XCFRAMEWORK_DIR="${PREFIX_DIR}/HFST.xcframework"
rm -rf "$XCFRAMEWORK_DIR"

xcodebuild -create-xcframework \
    -library "${PREFIX_DIR}/${ARM64_DEVICE}/lib/libhfst.a" \
    -headers "${PREFIX_DIR}/${ARM64_DEVICE}/include" \
    -library "${PREFIX_DIR}/${X86_64_SIM}/lib/libhfst.a" \
    -headers "${PREFIX_DIR}/${X86_64_SIM}/include" \
    -library "${PREFIX_DIR}/${ARM64_SIM}/lib/libhfst.a" \
    -headers "${PREFIX_DIR}/${ARM64_SIM}/include" \
    -output "$XCFRAMEWORK_DIR"

log_info "✅ Build complete!"
log_info "XCFramework created at: $XCFRAMEWORK_DIR"
log_info ""
log_info "Next steps:"
log_info "1. Drag HFST.xcframework into your Xcode project"
log_info "2. Add it to 'Frameworks, Libraries, and Embedded Content'"
log_info "3. Create a bridging header to use HFST from Swift"
