# HFST iOS Cross-Compilation Status

## ✅ What Has Been Completed

I've successfully completed the research and preparation phase for porting Sanaporakone to iOS:

### 1. **Comprehensive Codebase Analysis**
- ✅ Analyzed Django application structure
- ✅ Identified core business logic in `generate/generator.py`
- ✅ Mapped out HFST usage patterns
- ✅ Determined minimal API requirements

### 2. **HFST Dependency Analysis**
- ✅ Downloaded and examined HFST source code (v3.16.2)
- ✅ Identified build system: GNU Autotools
- ✅ Mapped dependency chain:
  - **ICU 50+** (Unicode support) - REQUIRED
  - **OpenFST 1.7.9** (FST backend) - REQUIRED
  - **SFST 1.4.6g** (optional, can disable)
  - **foma** (optional, can disable)

### 3. **Cross-Compilation Strategy**
- ✅ Created comprehensive build script (`build-all-ios.sh`)
- ✅ Targets: ARM64 (devices), x86_64 (Intel simulator), ARM64 (Apple Silicon simulator)
- ✅ Produces XCFramework for easy Xcode integration

### 4. **C++/Swift Integration Layer**
- ✅ Created C wrapper (`HFSTWrapper.cpp`)
- ✅ Created Objective-C bridging header (`HFST-Bridging-Header.h`)
- ✅ Created Swift wrapper class (`HFSTGenerator.swift`)

## ⚠️ Critical Limitation: macOS Required

**I cannot complete the actual compilation from this Linux environment.**

iOS cross-compilation REQUIRES:
- macOS with Xcode 14+ installed
- iOS SDK (only available on macOS)
- Apple toolchain (clang, ld, etc.)
- Code signing certificates

The build script I created (`build-all-ios.sh`) **must be run on a Mac**.

## 🔧 What You Need to Do Next

### Step 1: Run Build Script on macOS

```bash
cd ios-build
./build-all-ios.sh
```

This will:
1. Download ICU, OpenFST, and HFST sources
2. Cross-compile each for iOS (device + simulator)
3. Create `HFST.xcframework` ready for Xcode

**Expected Issues:**
- The script is complex and untested
- Dependency build configurations may need adjustment
- You may need to install: `autoconf`, `automake`, `libtool`, `pkg-config`
- Install via Homebrew: `brew install autoconf automake libtool pkg-config`

### Step 2: Create Xcode Project

1. Create new iOS App project
2. Drag `HFST.xcframework` into project
3. Add `HFSTWrapper.cpp` to project
4. Add `HFST-Bridging-Header.h` as bridging header
5. Add `HFSTGenerator.swift` to project
6. Bundle `omorfi.generate.hfst` (25MB) in app resources

### Step 3: Port Business Logic

The core generation logic from `generate/generator.py` is simple:

**Python (current):**
```python
def generate_simple_verb(word, person, tense):
    spec = f"[VOICE=ACT][MOOD=INDV][TENSE={tense}][PERS={person}]"
    return omorfi_instance.generate(f"[WORD_ID={word}][UPOS=VERB]{spec}")
```

**Swift (iOS):**
```swift
func generateSimpleVerb(word: String, person: String, tense: String) throws -> String {
    let spec = "[VOICE=ACT][MOOD=INDV][TENSE=\(tense)][PERS=\(person)]"
    let input = "[WORD_ID=\(word)][UPOS=VERB]\(spec)"
    let results = try generator.lookup(input)
    return results.first?.output ?? ""
}
```

## 🎯 Feasibility Assessment

### ✅ HIGHLY FEASIBLE (if build succeeds):

**Why I'm optimistic:**
1. HFST has minimal dependencies (just ICU + OpenFST)
2. Both ICU and OpenFST are mature, portable C++ libraries
3. The API surface area needed is tiny (just file loading + lookup)
4. No runtime code generation or JIT required
5. The FST model is a static binary (platform-agnostic data)
6. Similar projects have successfully cross-compiled FST libraries

### ⚠️ EXPECTED CHALLENGES:

1. **Build Script Debugging**
   - My script is untested on actual macOS
   - May need flag adjustments for C++17 compatibility
   - OpenFST 1.7.9 is old, may have build issues with modern Xcode

2. **Binary Size**
   - HFST library: ~5-10 MB
   - ICU: ~25-30 MB
   - OpenFST: ~2-5 MB
   - `omorfi.generate.hfst`: 25 MB
   - **Total app size increase: ~60-70 MB**

3. **Memory Usage**
   - Loading 25MB FST into memory
   - May want to use memory-mapped file I/O

4. **Startup Time**
   - Loading FST at app launch may take 1-2 seconds
   - Solution: Load asynchronously with splash screen

## 📋 Alternative Approach (if cross-compilation fails)

If the build script doesn't work, consider:

### Option A: Use HFST Python Bindings via Pyto
- Run Python code on iOS using Pyto app framework
- Bundle `libhfst` Python wheel
- **Pros:** Faster to implement
- **Cons:** Larger app size, less native feel

### Option B: Reimplement FST Lookup in Swift
- Parse the `.hfst` binary format manually
- Implement minimal FST lookup algorithm
- **Pros:** No dependencies, smaller binary
- **Cons:** Very complex, 2-3 weeks of work, error-prone

### Option C: Server-Based Approach
- Keep Django backend, make iOS app a client
- **Pros:** Simple iOS app
- **Cons:** Requires internet (violates offline requirement)

## 🎪 My Recommendation

**Try the cross-compilation first.** Here's why:

1. It's the "right" solution architecturally
2. Best performance and user experience
3. True offline support
4. If it works, you're done in days, not weeks
5. The build complexity is front-loaded - once built, it's just a library

**Risk mitigation:**
- Budget 1-2 days for build script debugging
- If build fails after 2 days, pivot to Option B (manual FST implementation)

## 📞 Next Steps

1. **Try running `build-all-ios.sh` on your Mac**
2. **Report any build errors** - I can help debug configure/make issues
3. **If successful**, proceed with Xcode integration
4. **If blocked**, we can explore alternatives

## 💡 Key Insight

The actual iOS app will be **simple**. All the complexity is in:
1. Getting HFST to compile for iOS (one-time effort)
2. Creating the bridge layer (already done)

Once you have `HFST.xcframework`, the rest is straightforward Swift/SwiftUI development.

---

**Bottom line: This is doable, but I need you to run the build on macOS to proceed further.**
