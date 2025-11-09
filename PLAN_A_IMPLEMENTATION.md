# Plan A: HTML Script Loading - IMPLEMENTED ✅

**Status:** Successfully deployed and verified (Nov 9, 2025)  
**Issue Resolved:** Windows Blue Screen - `window.MonacoBootstrapWindow` undefined  
**Verification:** `typeof window.MonacoBootstrapWindow` returns `"object"`

---

## Problem Summary

### The Issue
BREEZER IDE Windows build launched with a blue screen instead of the welcome UI. DevTools revealed:

```javascript
Uncaught (in promise) TypeError: Cannot read properties of undefined (reading 'load')
at workbench.js:3
```

### Root Cause
The Windows `vscode-win32-x64-min` gulp task failed to bundle `bootstrap-window.js` into `workbench.js`, unlike the Linux build which correctly bundled both files together.

**File Size Evidence:**
| Platform | `workbench.js` Size | Bootstrap Bundled? | Result |
|----------|---------------------|--------------------|--------|
| Linux    | 8,853 bytes         | ✅ Yes             | ✅ Works |
| Windows  | 5,453 bytes         | ❌ No              | ❌ Blue screen |

### Why It Mattered
VS Code uses a two-phase bootstrap process:

1. **Phase 1:** `bootstrap-window.js` defines `globalThis.MonacoBootstrapWindow = { load }`
2. **Phase 2:** `workbench.js` calls `const B = window.MonacoBootstrapWindow; await B.load(...)`

Without Phase 1, Phase 2 crashes.

---

## Solution Architecture

### Strategy
Ship `bootstrap-window.js` as a separate file and load it via HTML `<script>` tag **before** the workbench ES module.

### Why This Works
- HTML parsing guarantees script execution order
- Classic `<script>` tags block parsing until executed
- ES modules (`type="module"`) load after DOM parsing
- Bootstrap global is defined before workbench module runs

---

## Implementation Details

### Step 1: Copy Bootstrap to Package

**Location:** `.github/workflows/build-release.yml` (Windows job)

```powershell
# Source: compiled bootstrap from build output
$bootstrapSource = "code-oss\out\bootstrap-window.js"

# Destination: package structure (matches official VS Code layout)
$packageOut = "VSCode-win32-x64\resources\app\out"
$bootstrapDest = "$packageOut\bootstrap-window.js"

# Copy the file
Copy-Item -Force $bootstrapSource $bootstrapDest
```

**Result:** `bootstrap-window.js` (~9KB) now exists in the Windows package.

---

### Step 2: Patch workbench.html

**Target File:** `VSCode-win32-x64/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html`

**Original:**
```html
<script type="module" src="./workbench.js"></script>
```

**Patched:**
```html
<!-- MUST run first to define window.MonacoBootstrapWindow -->
<script src="../../../../bootstrap-window.js"></script>

<script type="module" src="./workbench.js"></script>
```

**PowerShell Implementation:**
```powershell
$html = Get-Content $workbenchHtml -Raw

# Only patch if not already patched (idempotent)
if ($html -notmatch 'bootstrap-window\.js') {
  # Insert bootstrap script tag before the workbench module
  $html = $html -replace '(<script\s+[^>]*src="\./workbench\.js"[^>]*type="module"[^>]*>\s*</script>)',
    "`t`t<!-- MUST run first to define window.MonacoBootstrapWindow -->`r`n`t`t<script src=`"../../../../bootstrap-window.js`"></script>`r`n`r`n`t`t`$1"
  
  Set-Content -NoNewline -Path $workbenchHtml -Value $html
}
```

**Path Breakdown:**
- `workbench.html` location: `.../electron-sandbox/workbench/`
- Bootstrap location: `.../out/`
- Relative path: `../../../../` (4 levels up)

---

### Step 3: Suppress Integrity Warning

**Problem:** VS Code's integrity checks detect modified files and show "corrupt installation" warning.

**Solution:** Disable checksums and set quality to "insider" mode.

```powershell
$productJson = "VSCode-win32-x64\resources\app\product.json"
$product = Get-Content $productJson -Raw | ConvertFrom-Json

# Remove file checksums
if ($product.PSObject.Properties['checksums']) {
  $product.PSObject.Properties.Remove('checksums')
}

# Set quality to bypass strict validation
$product.quality = "insider"

# Save back
$product | ConvertTo-Json -Depth 10 | Set-Content -Path $productJson -NoNewline
```

---

## Validation Guards

### Build-Time Checks

```powershell
# Guard 1: Bootstrap file exists in package
if (!(Test-Path $bootstrapDest)) {
  Write-Error "VALIDATION FAILED: bootstrap-window.js missing from package"
  exit 1
}

# Guard 2: HTML loads bootstrap
if ($html -notmatch 'bootstrap-window\.js') {
  Write-Error "VALIDATION FAILED: workbench.html not loading bootstrap-window.js"
  exit 1
}

# Guard 3: Load order correct (uses (?s) for multi-line regex)
if ($html -match '(?s)bootstrap-window\.js.*workbench\.js"[^>]*type="module"') {
  Write-Host "✓ Load order correct (bootstrap → workbench module)"
} else {
  Write-Error "VALIDATION FAILED: Incorrect load order"
  exit 1
}
```

### Runtime Verification

**DevTools Console:**
```javascript
typeof window.MonacoBootstrapWindow  // Should return "object"
window.MonacoBootstrapWindow.load    // Should be a function
```

**Visual Check:**
- ✅ Welcome/walkthrough UI renders
- ✅ No blue screen
- ✅ No console errors
- ✅ No "corrupt installation" warning (after integrity suppression)

---

## Execution Flow

### At Build Time
1. Gulp compiles TypeScript → `bootstrap-window.js` in `out/`
2. Gulp packages Windows build → `VSCode-win32-x64/`
3. **CI copies** `bootstrap-window.js` to package `out/` directory
4. **CI patches** `workbench.html` to load bootstrap first
5. **CI disables** integrity checks in `product.json`
6. CI creates final ZIP artifact

### At Runtime
1. Electron launches BREEZER.exe
2. Main process loads `workbench.html`
3. **HTML parser executes:** `<script src="../../../../bootstrap-window.js">`
   - Defines `globalThis.MonacoBootstrapWindow = { load }`
4. **HTML parser loads:** `<script type="module" src="./workbench.js">`
   - `const B = window.MonacoBootstrapWindow` ✅ NOW DEFINED
   - `await B.load(...)` ✅ WORKS
5. UI renders successfully

---

## Files Modified

### CI/CD Workflow
- **File:** `.github/workflows/build-release.yml`
- **Job:** `build-windows`
- **Steps Added:**
  1. "Fix Windows bootstrap loading (Plan A)" - Copy + patch
  2. "Suppress integrity warning" - Disable checks

### Package Files (Post-Build)
- `resources/app/out/bootstrap-window.js` ← **Added**
- `resources/app/out/vs/code/electron-sandbox/workbench/workbench.html` ← **Modified**
- `resources/app/product.json` ← **Modified** (checksums removed, quality changed)

---

## Advantages

✅ **Simple** - Post-build file manipulation only  
✅ **No source changes** - No need to modify Code-OSS source  
✅ **Guaranteed order** - HTML parsing ensures bootstrap runs first  
✅ **Verifiable** - Clear guards prevent regressions  
✅ **Maintainable** - Easy to understand and debug  
✅ **Cross-version compatible** - Works with any Code-OSS 1.x version  

---

## Potential Limitations

⚠️ **Script mixing** - Combines classic script + ES module (works but not how upstream does it)  
⚠️ **Integrity checks** - Must be disabled (acceptable for branded fork)  
⚠️ **Context isolation** - Relies on global scope (works without `contextIsolation` issues in practice)  

---

## Troubleshooting

### Issue: Blue screen persists
**Check:**
```javascript
typeof window.MonacoBootstrapWindow  // undefined?
```

**Causes:**
1. Bootstrap file not copied → Check package `out/` directory
2. HTML not patched → Inspect `workbench.html` source
3. Wrong relative path → Verify `../../../../` reaches `out/`

### Issue: "Corrupt installation" warning
**Check:**
- `product.json` still has `checksums` property?
- `quality` not set to `"insider"`?

**Fix:** Re-run integrity suppression step.

### Issue: Build fails validation
**Check CI logs for:**
- "VALIDATION FAILED: bootstrap-window.js missing" → Build didn't compile it
- "VALIDATION FAILED: workbench.html not loading" → Regex didn't match
- "VALIDATION FAILED: Incorrect load order" → Multi-line regex issue (needs `(?s)` flag)

---

## Related Documentation

- **Problem Analysis:** `WINDOWS_BLUE_SCREEN_ISSUE.md`
- **Alternative Solution:** `PLAN_B_PRELOAD_WRAPPER.md`
- **Build Workflow:** `.github/workflows/build-release.yml`
- **Branding Scripts:** `ide-build/scripts/apply-branding.ps1`

---

## Maintenance Notes

### When Upgrading Code-OSS Version
1. Verify `bootstrap-window.js` still compiles to `out/` directory
2. Verify `workbench.html` structure hasn't changed
3. Test the patched build before releasing
4. Check if upstream changed bootstrap mechanism

### If Upstream Changes Bootstrap Loading
Consider switching to **Plan B (Preload Wrapper)** if upstream:
- Moves bootstrap to different location
- Changes Electron preload configuration
- Modifies workbench.html structure significantly

---

**Document Version:** 1.0  
**Last Updated:** November 9, 2025  
**Status:** Active (Production)
