# Windows Blue Screen Issue - Technical Analysis

**Project:** BREEZER IDE by RICHDALE AI  
**Based on:** Code-OSS 1.95 (VS Code fork)  
**Issue:** Windows build fails to launch - shows blue screen  
**Platforms Affected:** Windows only (Linux works perfectly)  
**Date:** November 8-9, 2025

---

## Executive Summary

The Windows build of BREEZER IDE launches but displays only a blue screen instead of the expected walkthrough UI. The Linux build works correctly with identical source code and branding. Investigation reveals a critical JavaScript bundling issue specific to the Windows `vscode-win32-x64-min` gulp task.

---

## Problem Description

### Symptoms
- **Windows:** Blue screen on launch (no UI, no errors visible)
- **Linux:** Works perfectly - shows walkthrough screen
- **macOS:** Untested but likely works (same build process as Linux)

### Error Message (DevTools Console)
```
Uncaught (in promise) TypeError: Cannot read properties of undefined (reading 'load')
at workbench.js:3
```

### Specific Error Location
```javascript
// workbench.js line 3
const B = window.MonacoBootstrapWindow;  // ← UNDEFINED on Windows
await B.load("vs/workbench/workbench.desktop.main", ...);  // ← Crashes here
```

---

## Root Cause Analysis

### The Core Issue

The `MonacoBootstrapWindow` global object is **not defined** when `workbench.js` executes on Windows.

### Expected Architecture

VS Code uses a two-phase bootstrap process:

1. **Phase 1:** `bootstrap-window.js` runs first and defines `MonacoBootstrapWindow`
   ```javascript
   // bootstrap-window.js (end of file)
   globalThis.MonacoBootstrapWindow = { load };
   ```

2. **Phase 2:** `workbench.js` uses the defined object
   ```javascript
   // workbench.js (start of file)
   const B = window.MonacoBootstrapWindow;  // Should be defined by Phase 1
   ```

### What We Discovered

#### File Size Comparison

| Platform | `workbench.js` Size | `bootstrap-window.js` Bundled? | Result |
|----------|---------------------|--------------------------------|--------|
| **Linux** | 8,853 bytes | ✅ **YES** - bundled into workbench.js | ✅ **Works** |
| **Windows** | 5,453 bytes | ❌ **NO** - missing from workbench.js | ❌ **Blue screen** |
| **Official VS Code** | 5,453 bytes | ❌ NO - loaded differently | ✅ Works (different system) |

#### Key Finding

**The Windows `vscode-win32-x64-min` gulp task fails to bundle `bootstrap-window.js` into `workbench.js`.**

- Linux build: Both files are combined into a single 8.8KB file
- Windows build: Only `workbench.js` content (5.4KB), missing bootstrap code (~3.4KB)

---

## Investigation Timeline

### Phase 1: Initial Discovery (Nov 8, ~4:00 PM)
- Confirmed blue screen on Windows
- Extracted DevTools error: `Cannot read properties of undefined (reading 'load')`
- Identified missing `window.MonacoBootstrapWindow`

### Phase 2: File Comparison (Nov 8, ~4:30 PM)
- Tested Linux build in WSL - **works perfectly**
- Compared `workbench.js` files:
  - Linux: 8,853 bytes (complete)
  - Windows: 5,453 bytes (truncated)
- **Conclusion:** Windows build is incomplete

### Phase 3: Build Analysis (Nov 8, ~5:00 PM)
- Examined GitHub Actions logs
- Found: `bootstrap-window.js` is **built correctly** (8,991 bytes in `code-oss/out/`)
- Found: `bootstrap-window.js` is **NOT packaged** into final distribution
- Found: Linux bundles bootstrap code INTO workbench.js
- Found: Windows does NOT bundle bootstrap code

### Phase 4: Attempted Fix #1 (Nov 8, ~7:00 PM)
**Approach:** Manually concatenate `bootstrap-window.js` + `workbench.js` in CI/CD

```powershell
# Read both files
$bootstrapContent = Get-Content bootstrap-window.js -Raw
$workbenchContent = Get-Content workbench.js -Raw

# Concatenate with comma separator
$fixedContent = $bootstrapContent + "," + $workbenchContent

# Write back
Set-Content -Path workbench.js -Value $fixedContent
```

**Result:**
- ✅ File size increased: 5,453 → 23,211 bytes
- ✅ Build logs show "Successfully fixed!"
- ❌ **Still blue screen**

### Phase 5: Syntax Error Discovery (Nov 8, ~11:00 PM)
**Problem:** Sourcemap comments causing syntax errors

**Bad concatenation:**
```javascript
}());
//# sourceMappingURL=data:application/json;base64...
,/*!----- SECOND FILE -----  // ← Syntax error! Comma after sourcemap
```

**Should be:**
```javascript
}()),  // ← Comma BEFORE sourcemap
//# sourceMappingURL=...
/*!----- SECOND FILE -----
```

### Phase 6: Attempted Fix #2 (Nov 9, ~10:00 AM)
**Approach:** Strip sourcemap comments before concatenation

```powershell
# Strip sourcemaps
$bootstrapContent = $bootstrapContent -replace '//# sourceMappingURL=.*$', ''
$workbenchContent = $workbenchContent -replace '//# sourceMappingURL=.*$', ''

# Concatenate
$fixedContent = $bootstrapContent.TrimEnd() + "," + $workbenchContent
```

**Status:** Build pending...

---

## Technical Deep Dive

### VS Code Bootstrap Architecture

#### Normal Flow (How it should work)
1. Electron main process starts
2. Loads `workbench.html`
3. `workbench.html` loads `workbench.js` as ES module
4. `workbench.js` expects `MonacoBootstrapWindow` to exist
5. Uses `MonacoBootstrapWindow.load()` to bootstrap the workbench

#### Linux Build (Working)
```javascript
// workbench.js contains BOTH:

// PART 1: bootstrap-window.js code (defines MonacoBootstrapWindow)
(function () {
    // ... bootstrap code ...
    globalThis.MonacoBootstrapWindow = { load };
}()),  // ← Note the comma

// PART 2: workbench.js code (uses MonacoBootstrapWindow)
(async function(){
    const B = window.MonacoBootstrapWindow;  // ← NOW DEFINED!
    await B.load(...);
})();
```

#### Windows Build (Broken)
```javascript
// workbench.js contains ONLY:

// PART 2: workbench.js code (MISSING PART 1!)
(async function(){
    const B = window.MonacoBootstrapWindow;  // ← UNDEFINED!
    await B.load(...);  // ← CRASH!
})();
```

### Why This Happens

The `vscode-win32-x64-min` gulp task is supposed to:
1. Compile TypeScript to JavaScript
2. Minify the code
3. Bundle dependencies
4. Package the application

**Hypothesis:** The minification or bundling step on Windows is:
- Not recognizing the dependency on `bootstrap-window.js`
- Or treating it as a separate module instead of bundling it
- Or encountering a Windows-specific path issue (backslashes vs forward slashes)

---

## Attempted Solutions

### Solution 1: Manual Concatenation in CI/CD ❌
**Status:** Implemented but FAILED

**What we did:**
- Added post-build step in GitHub Actions
- Manually read both files
- Concatenated with comma separator
- Rewrote `workbench.js`
- Recreated the distribution ZIP

**Why it failed:**
- Sourcemap comments interfered with concatenation
- Created syntax error: `, //# sourceMappingURL=...`
- JavaScript parser couldn't handle it

### Solution 2: Strip Sourcemaps Before Concatenation ⏳
**Status:** Currently testing

**What we're doing:**
- Strip `//# sourceMappingURL=...` from both files
- Trim whitespace
- Concatenate cleanly
- Test if syntax error is resolved

**Potential issues:**
- May still have other syntax incompatibilities
- May be missing other initialization code
- May have IIFE scope conflicts

---

## Current Status

### Build Information
- **Latest Run:** https://github.com/msiraga/BREEZER_X/actions/runs/19197389752
- **Artifact:** `breezer-ide-windows` (141 MB)
- **workbench.js Size:** 23,211 bytes (after fix)
- **Status:** Blue screen persists

### What Works
- ✅ Branding applied correctly
- ✅ Telemetry disabled
- ✅ Application launches (no crash)
- ✅ Window appears with correct title
- ✅ File size looks correct (23KB)

### What Doesn't Work
- ❌ UI doesn't render (blue screen)
- ❌ No visible error in main window
- ❌ DevTools required to see JavaScript error

---

## Comparison with Official VS Code

### Official VS Code 1.95.3
- `workbench.js`: 5,453 bytes (same as our broken Windows build)
- **Does NOT bundle bootstrap-window.js**
- **Uses a different loading mechanism**

### Key Difference
Official VS Code likely:
- Loads `bootstrap-window.js` separately via preload script
- Or uses Electron's context bridge differently
- Or has additional bundling configuration we're missing

---

## Questions for Engineering Team

1. **Build System:**
   - Why does Linux `vscode-linux-x64-min` bundle bootstrap-window.js but Windows `vscode-win32-x64-min` doesn't?
   - Are there platform-specific gulp configurations we're missing?

2. **JavaScript Bundling:**
   - Is manual concatenation the right approach?
   - Should we modify the gulp task instead?
   - Are there other dependencies that need bundling?

3. **Official VS Code Comparison:**
   - How does official VS Code load bootstrap-window.js on Windows?
   - Is there a preload script configuration we're missing?
   - Should we examine their official build scripts?

4. **Alternative Approaches:**
   - Can we use the non-minified gulp task (`vscode-win32-x64` without `-min`)?
   - Can we copy the Linux build process exactly for Windows?
   - Can we patch `workbench.html` to load bootstrap-window.js explicitly?

---

## Recommended Next Steps

### Immediate Actions
1. **Test latest build** (with sourcemap stripping)
   - Download artifact from: https://github.com/msiraga/BREEZER_X/actions/runs/19197389752
   - Verify `workbench.js` syntax is valid
   - Check DevTools for new error messages

2. **Compare gulp tasks**
   - Download official VS Code 1.95.3 source
   - Compare `gulpfile.vscode.js` between Linux and Windows tasks
   - Look for platform-specific bundling configurations

3. **Test non-minified build**
   - Try using `vscode-win32-x64` instead of `vscode-win32-x64-min`
   - Check if non-minified version works
   - Compare file sizes and structure

### Alternative Approaches

#### Option A: Fix the Gulp Task
**Modify the build process to bundle bootstrap-window.js correctly**

Pros:
- ✅ Proper long-term solution
- ✅ Matches Linux build behavior
- ✅ No manual post-processing needed

Cons:
- ❌ Requires deep understanding of gulp/webpack
- ❌ May break other things
- ❌ Time-consuming

#### Option B: Use Preload Script
**Load bootstrap-window.js via Electron preload script**

Pros:
- ✅ Matches official VS Code pattern
- ✅ Cleaner separation of concerns

Cons:
- ❌ Requires Electron configuration changes
- ❌ May not work with current setup

#### Option C: Modify workbench.html
**Add explicit script tag to load bootstrap-window.js**

```html
<script src="../../../base/parts/sandbox/electron-sandbox/bootstrap-window.js"></script>
<script src="./workbench.js" type="module"></script>
```

Pros:
- ✅ Simple and explicit
- ✅ Easy to understand

Cons:
- ❌ File doesn't exist in packaged app
- ❌ Would need to copy file during packaging
- ❌ May conflict with module loading

---

## Files and Locations

### Key Files
```
VSCode-win32-x64/
├── resources/
│   └── app/
│       ├── out/
│       │   ├── bootstrap-window.js         ❌ Missing in package
│       │   └── vs/
│       │       └── code/
│       │           └── electron-sandbox/
│       │               └── workbench/
│       │                   ├── workbench.js     ⚠️ Incomplete (5.4KB → 23KB after fix)
│       │                   └── workbench.html   ✅ Correct
│       └── product.json                    ✅ Correct (branding applied)
└── BREEZER.exe                            ✅ Launches but blue screen
```

### Build Artifacts
```
code-oss/
├── out/                                   # TypeScript compilation output
│   └── bootstrap-window.js               ✅ Exists (8.9KB)
├── out-build/                            # Minified output
│   └── bootstrap-window.js               ✅ Exists (8.9KB)
└── out-vscode/                           # Final bundled output
    └── vs/
        └── code/
            └── electron-sandbox/
                └── workbench/
                    └── workbench.js      ⚠️ Missing bootstrap code
```

---

## Environment Details

### Build Environment (GitHub Actions)
- **Runner:** `windows-latest` (Windows Server 2022)
- **Node.js:** 20.18.0
- **npm:** 10.8.2
- **Memory:** 8GB (via `NODE_OPTIONS: --max-old-space-size=8192`)

### Gulp Tasks Used
```bash
npm run compile              # Compile TypeScript
npm run gulp vscode-win32-x64-min  # Build and package for Windows
```

### Working Environment (Linux in WSL)
- **Distribution:** Ubuntu (via WSL2)
- **Same Node.js version:** 20.18.0
- **Same gulp task:** `vscode-linux-x64-min`
- **Result:** ✅ Works perfectly

---

## Logs and Evidence

### GitHub Actions Build Log Excerpts

#### Bootstrap File Created ✅
```
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---           11/8/2025 11:59 AM           8991 bootstrap-window.js
```

#### Fix Applied ✅
```
Original workbench.js size: 5453 bytes
Fixed workbench.js size: 23211 bytes
Windows workbench.js successfully fixed! Size increased by 17758 bytes
```

#### Artifact Created ✅
```
Artifact breezer-ide-windows has been successfully uploaded!
Final size is 141501958 bytes
Artifact ID is 4508482828
```

### File Content Comparison

#### Linux workbench.js (First 100 chars)
```javascript
"use strict";
/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
```

#### Windows workbench.js BEFORE fix (First 100 chars)
```javascript
/*!--------------------------------------------------------
 * Copyright (C) Microsoft Corporation. All rights reserved.
 *--------------------------------------------------------*/(async function(){
```

#### Windows workbench.js AFTER fix (First 100 chars)
```javascript
"use strict";
/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Microsoft Corporation. All rights reserved.
```

**Status:** ✅ Content now starts correctly (like Linux)

---

## References

### Official VS Code Source
- **Repository:** https://github.com/microsoft/vscode
- **Version:** 1.95.3
- **Bootstrap Window Source:** https://github.com/microsoft/vscode/blob/1.95.3/src/vs/base/parts/sandbox/electron-sandbox/bootstrap-window.ts
- **Workbench Source:** https://github.com/microsoft/vscode/blob/1.95.3/src/vs/code/electron-sandbox/workbench/workbench.ts
- **Gulpfile:** https://github.com/microsoft/vscode/blob/1.95.3/build/gulpfile.vscode.js

### Our Repository
- **Main Repo:** https://github.com/msiraga/BREEZER_X
- **Build Workflow:** `.github/workflows/build-release.yml`
- **Branding Script (Windows):** `ide-build/scripts/apply-branding.ps1`
- **Branding Script (Linux):** `ide-build/scripts/apply-branding.sh`

### Related Issues
- None found in official VS Code repository
- This appears to be specific to our fork/build process

---

## Contact

**For questions or collaboration on this issue:**
- Repository: https://github.com/msiraga/BREEZER_X/issues
- Project: BREEZER IDE by RICHDALE AI
- Document Version: 1.0 (November 9, 2025)

---

## Appendix A: Full Error Stack Trace

```
[14844:1108/151635.424:INFO:CONSOLE(3)] 
"Uncaught (in promise) TypeError: Cannot read properties of undefined (reading 'load')", 
source: vscode-file://vscode-app/c:/BREEZER/VSCode-win32-x64/resources/app/out/vs/code/electron-sandbox/workbench/workbench.js (3)
```

## Appendix B: DevTools Console Access

To view the error:
1. Launch BREEZER.exe
2. Press `Ctrl+Shift+I` to open DevTools
3. Click **Console** tab
4. Error will be visible

## Appendix C: File Size Evolution

| Stage | Size | Status |
|-------|------|--------|
| Original Windows build | 5,453 bytes | ❌ Broken |
| After concatenation (v1) | 23,211 bytes | ❌ Syntax error |
| After sourcemap strip (v2) | TBD | ⏳ Testing |
| Working Linux build | 8,853 bytes | ✅ Reference |

---

*End of Document*
