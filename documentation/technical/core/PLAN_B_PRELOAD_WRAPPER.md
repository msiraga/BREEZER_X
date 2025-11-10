# Plan B: Electron Preload Wrapper - DOCUMENTED (Not Implemented)

**Status:** Documented for future consideration  
**Alternative to:** Plan A (HTML Script Loading)  
**Alignment:** Matches official VS Code architecture  
**Complexity:** Medium (requires preload modification)

---

## Overview

Plan B uses Electron's native preload mechanism to load `bootstrap-window.js` before the renderer process starts, then exposes `MonacoBootstrapWindow` to the page via `contextBridge`. This is architecturally superior to Plan A and matches how official VS Code handles sandboxed renderer APIs.

---

## Why Plan B is More Robust

### Compared to Plan A

| Aspect | Plan A (HTML) | Plan B (Preload) |
|--------|---------------|------------------|
| **Upstream alignment** | Custom approach | Matches VS Code architecture |
| **Load timing** | HTML parsing order | Preload runs before renderer starts |
| **Context isolation** | Relies on global scope | Uses `contextBridge` (proper) |
| **Script mixing** | Classic + ES module | Preload context only |
| **Integrity checks** | Must disable | Can potentially keep enabled |
| **window.vscode APIs** | Intact | Explicitly preserved |

### Key Advantages

✅ **Guaranteed timing** - Preload runs **before** any renderer code  
✅ **Proper sandboxing** - Uses `contextBridge` for context isolation  
✅ **Upstream-aligned** - Matches official VS Code's preload pattern  
✅ **No HTML patching** - Cleaner separation of concerns  
✅ **Future-proof** - Less likely to break with VS Code updates  

---

## Architecture

### VS Code's Existing Preload

Official VS Code uses a preload script at:
```
resources/app/out/vs/base/parts/sandbox/electron-sandbox/preload.js
```

This preload:
- Runs before renderer starts
- Exposes `window.vscode` APIs
- Handles sandboxed renderer communication

**Our strategy:** Wrap this preload to also load bootstrap.

---

## Implementation Blueprint

### Step 1: Package Bootstrap File

**Same as Plan A:** Copy `bootstrap-window.js` to package.

```powershell
# In .github/workflows/build-release.yml (Windows job)

$bootstrapSource = "code-oss\out\bootstrap-window.js"
$bootstrapDest = "VSCode-win32-x64\resources\app\out\bootstrap-window.js"

Copy-Item -Force $bootstrapSource $bootstrapDest
Write-Host "✓ Packaged bootstrap-window.js"
```

---

### Step 2: Create Wrapper Preload

**Location:** Post-packaging step in CI/CD

**Strategy:** 
1. Rename original VS Code preload: `preload.js` → `preload.vscode.js`
2. Create new `preload.js` that wraps the original

```powershell
# Paths
$preloadDir = "VSCode-win32-x64\resources\app\out\vs\base\parts\sandbox\electron-sandbox"
$preload = Join-Path $preloadDir "preload.js"
$preloadOrig = Join-Path $preloadDir "preload.vscode.js"

# Preserve original
Move-Item -Force $preload $preloadOrig

# Create wrapper
$wrapper = @'
const path = require("path");
const { contextBridge } = require("electron");

// 1) Run VS Code's original preload (keeps window.vscode intact)
require(path.join(__dirname, "preload.vscode.js"));

// 2) Run bootstrap that defines globalThis.MonacoBootstrapWindow = { load }
// Path: electron-sandbox/ + 5x .. = out/bootstrap-window.js
require(path.join(__dirname, "..", "..", "..", "..", "..", "bootstrap-window.js"));

// 3) Expose to page (contextIsolation-safe via contextBridge)
if (globalThis.MonacoBootstrapWindow) {
  contextBridge.exposeInMainWorld("MonacoBootstrapWindow", globalThis.MonacoBootstrapWindow);
} else {
  console.error("BREEZER: bootstrap-window.js did not define MonacoBootstrapWindow");
}
'@

# Write with UTF-8 encoding (Node.js compatibility)
Set-Content -NoNewline -Encoding UTF8 -Path $preload -Value $wrapper
Write-Host "✓ Created wrapper preload"
```

**Path Analysis:**
```
preload.js location:     .../out/vs/base/parts/sandbox/electron-sandbox/
Target:                  .../out/bootstrap-window.js

Levels up needed:
1. .. → sandbox/
2. .. → parts/
3. .. → base/
4. .. → vs/
5. .. → out/

Result: 5 levels = "../../../../../bootstrap-window.js"
```

---

### Step 3: Validation

```powershell
# Guard 1: Original preload preserved
if (!(Test-Path $preloadOrig)) {
  Write-Error "VALIDATION FAILED: Original preload not at $preloadOrig"
  exit 1
}

# Guard 2: Wrapper created
if (!(Test-Path $preload)) {
  Write-Error "VALIDATION FAILED: Wrapper preload not created"
  exit 1
}

# Guard 3: Wrapper contains critical imports
$wrapperContent = Get-Content $preload -Raw
if ($wrapperContent -notmatch 'preload\.vscode\.js') {
  Write-Error "VALIDATION FAILED: Wrapper doesn't load original preload"
  exit 1
}
if ($wrapperContent -notmatch 'bootstrap-window\.js') {
  Write-Error "VALIDATION FAILED: Wrapper doesn't load bootstrap"
  exit 1
}
if ($wrapperContent -notmatch 'contextBridge\.exposeInMainWorld') {
  Write-Error "VALIDATION FAILED: Wrapper doesn't expose to page"
  exit 1
}

# Guard 4: Bootstrap packaged
if (!(Test-Path $bootstrapDest)) {
  Write-Error "VALIDATION FAILED: bootstrap-window.js not packaged"
  exit 1
}

Write-Host "✅ All validation checks passed"
```

---

## Execution Flow

### At Build Time
1. Gulp compiles `bootstrap-window.js` → `code-oss/out/`
2. Gulp packages Windows build → `VSCode-win32-x64/`
3. **CI copies** `bootstrap-window.js` to package
4. **CI renames** original preload: `preload.js` → `preload.vscode.js`
5. **CI creates** wrapper preload as new `preload.js`
6. CI packages final artifact

### At Runtime

**Phase 1: Electron Main Process**
```javascript
// Electron's BrowserWindow configuration (unchanged)
const win = new BrowserWindow({
  webPreferences: {
    sandbox: true,
    contextIsolation: true,
    preload: path.join(appPath, 'out/vs/base/parts/sandbox/electron-sandbox/preload.js')
  }
});
```

**Phase 2: Preload Execution** (before renderer starts)
```javascript
// Our wrapper preload.js runs:

// Step 1: VS Code's preload
require("./preload.vscode.js");
// → Defines window.vscode APIs

// Step 2: Bootstrap
require("../../../../../bootstrap-window.js");
// → Defines globalThis.MonacoBootstrapWindow

// Step 3: Bridge to page
contextBridge.exposeInMainWorld("MonacoBootstrapWindow", globalThis.MonacoBootstrapWindow);
// → Page can access window.MonacoBootstrapWindow
```

**Phase 3: Renderer Process**
```javascript
// workbench.html loads
// workbench.js (ES module) runs:

const B = window.MonacoBootstrapWindow;  // ✅ Defined by preload
await B.load("vs/workbench/workbench.desktop.main", ...);  // ✅ Works
```

---

## Files Modified

### CI/CD Workflow
- **File:** `.github/workflows/build-release.yml`
- **Job:** `build-windows`
- **New Step:** "Fix Windows bootstrap loading (Preload Wrapper)"

### Package Files (Post-Build)
- `resources/app/out/bootstrap-window.js` ← **Added**
- `resources/app/out/vs/base/parts/sandbox/electron-sandbox/preload.js` ← **Replaced** (wrapper)
- `resources/app/out/vs/base/parts/sandbox/electron-sandbox/preload.vscode.js` ← **Added** (renamed original)

**No changes to:**
- `workbench.html` - Stays untouched
- `product.json` - Integrity checks can potentially stay enabled

---

## Why Not Implemented

### Plan A Already Works
- Plan A successfully resolved the blue screen
- Verified working in production
- Simple and maintainable

### When to Switch to Plan B

Consider implementing Plan B if:

1. **Upstream changes break Plan A**
   - VS Code modifies `workbench.html` structure
   - HTML parsing order becomes unreliable
   - ES module loading behavior changes

2. **Context isolation issues arise**
   - Plan A's global scope approach causes problems
   - Need stricter sandboxing for security

3. **Integrity checks become required**
   - Business/compliance requires file validation
   - Can't disable checksums in production

4. **Closer upstream alignment needed**
   - Easier merging of upstream VS Code updates
   - Want to match official architecture exactly

---

## Complete Implementation Code

### Full CI/CD Step

```yaml
- name: Fix Windows bootstrap loading (Preload Wrapper)
  run: |
    Write-Host "=== Implementing Preload Wrapper Solution ==="
    Write-Host "Strategy: Wrap VS Code's preload to load bootstrap + expose via contextBridge"
    
    # Paths
    $artifactRoot = "VSCode-win32-x64\resources\app\out"
    $preloadDir   = Join-Path $artifactRoot "vs\base\parts\sandbox\electron-sandbox"
    $preload      = Join-Path $preloadDir "preload.js"
    $preloadOrig  = Join-Path $preloadDir "preload.vscode.js"
    $bootstrapSrc = "code-oss\out\bootstrap-window.js"
    $bootstrapDest = Join-Path $artifactRoot "bootstrap-window.js"
    
    Write-Host "`n=== Step 1: Validate inputs ==="
    
    # Check preload exists
    if (!(Test-Path $preload)) {
      Write-Error "Expected VS Code preload at: $preload"
      exit 1
    }
    Write-Host "✓ Found VS Code preload.js"
    
    # Check bootstrap was compiled
    if (!(Test-Path $bootstrapSrc)) {
      Write-Error "bootstrap-window.js not compiled at: $bootstrapSrc"
      exit 1
    }
    Write-Host "✓ Found compiled bootstrap-window.js ($((Get-Item $bootstrapSrc).Length) bytes)"
    
    Write-Host "`n=== Step 2: Preserve original VS Code preload ==="
    Move-Item -Force $preload $preloadOrig
    Write-Host "✓ Renamed preload.js → preload.vscode.js"
    
    Write-Host "`n=== Step 3: Create wrapper preload ==="
    
    $wrapper = @'
const path = require("path");
const { contextBridge } = require("electron");

// 1) Run VS Code's original preload (keeps window.vscode intact)
require(path.join(__dirname, "preload.vscode.js"));

// 2) Run bootstrap that defines globalThis.MonacoBootstrapWindow = { load }
require(path.join(__dirname, "..", "..", "..", "..", "..", "bootstrap-window.js"));

// 3) Expose to page (contextIsolation-safe via contextBridge)
if (globalThis.MonacoBootstrapWindow) {
  contextBridge.exposeInMainWorld("MonacoBootstrapWindow", globalThis.MonacoBootstrapWindow);
} else {
  console.error("BREEZER: bootstrap-window.js did not define MonacoBootstrapWindow");
}
'@
    
    Set-Content -NoNewline -Encoding UTF8 -Path $preload -Value $wrapper
    Write-Host "✓ Created wrapper preload.js"
    
    Write-Host "`n=== Step 4: Copy bootstrap-window.js to package ==="
    Copy-Item -Force $bootstrapSrc $bootstrapDest
    Write-Host "✓ Copied bootstrap-window.js ($((Get-Item $bootstrapDest).Length) bytes)"
    
    Write-Host "`n=== Step 5: Validate the fix ==="
    
    if (!(Test-Path $preloadOrig)) {
      Write-Error "VALIDATION FAILED: Original preload not preserved"
      exit 1
    }
    Write-Host "✓ Guard 1: Original VS Code preload preserved"
    
    if (!(Test-Path $preload)) {
      Write-Error "VALIDATION FAILED: Wrapper preload not created"
      exit 1
    }
    
    $wrapperContent = Get-Content $preload -Raw
    if ($wrapperContent -notmatch 'preload\.vscode\.js') {
      Write-Error "VALIDATION FAILED: Wrapper doesn't load original preload"
      exit 1
    }
    if ($wrapperContent -notmatch 'bootstrap-window\.js') {
      Write-Error "VALIDATION FAILED: Wrapper doesn't load bootstrap"
      exit 1
    }
    if ($wrapperContent -notmatch 'contextBridge\.exposeInMainWorld') {
      Write-Error "VALIDATION FAILED: Wrapper doesn't expose to page"
      exit 1
    }
    Write-Host "✓ Guard 2: Wrapper preload contains all critical imports"
    
    if (!(Test-Path $bootstrapDest)) {
      Write-Error "VALIDATION FAILED: bootstrap-window.js not packaged"
      exit 1
    }
    Write-Host "✓ Guard 3: bootstrap-window.js packaged in app"
    
    Write-Host "`n=== Architecture Summary ==="
    Write-Host "   Preload chain:"
    Write-Host "   1. Electron loads: preload.js (wrapper)"
    Write-Host "   2. Wrapper runs:  preload.vscode.js (VS Code APIs)"
    Write-Host "   3. Wrapper runs:  bootstrap-window.js (MonacoBootstrapWindow)"
    Write-Host "   4. Wrapper bridges: window.MonacoBootstrapWindow (contextBridge)"
    Write-Host "   5. Page executes:   workbench.js (uses window.MonacoBootstrapWindow)"
    
    Write-Host "`n✅ Preload wrapper solution implemented successfully!"
    
    Write-Host "`n=== Step 6: Recreate Windows artifact ==="
    Remove-Item builds\breezer-ide-windows-x64.zip -Force
    Compress-Archive -Path VSCode-win32-x64 -DestinationPath builds\breezer-ide-windows-x64.zip
    Write-Host "✅ Windows artifact recreated"
```

---

## Troubleshooting

### Issue: Blue screen persists

**Check DevTools Console:**
```javascript
typeof window.MonacoBootstrapWindow  // undefined?
```

**Possible Causes:**
1. **Preload didn't run** - Check Electron main process configuration
2. **Bootstrap path wrong** - Verify 5 levels of `..` navigation
3. **contextBridge failed** - Check for context isolation errors in console

**Debug Steps:**
1. Add `console.log()` to wrapper preload to verify execution
2. Check if `preload.vscode.js` exists alongside `preload.js`
3. Verify `bootstrap-window.js` exists at `resources/app/out/`

### Issue: window.vscode undefined

**Cause:** Original VS Code preload not loading

**Fix:**
- Verify `preload.vscode.js` exists
- Check wrapper calls `require("./preload.vscode.js")` correctly
- Ensure original preload was renamed, not deleted

### Issue: Build validation fails

**Check which guard failed:**
- Guard 1 → Original preload not preserved
- Guard 2 → Wrapper missing critical imports
- Guard 3 → Bootstrap file not packaged

---

## Comparison: Plan A vs Plan B

### Plan A (Current - HTML Patching)
```
Browser loads workbench.html
  ↓
HTML parser executes <script src="bootstrap-window.js">
  ↓ (defines globalThis.MonacoBootstrapWindow)
HTML parser loads <script type="module" src="workbench.js">
  ↓ (uses window.MonacoBootstrapWindow)
UI renders
```

**Timing:** HTML parsing order (synchronous)  
**Scope:** Global window object  
**Pros:** Simple, no Electron knowledge needed  
**Cons:** Script mixing, must disable integrity checks

### Plan B (Alternative - Preload Wrapper)
```
Electron main process starts
  ↓
Preload runs (before renderer)
  ↓
Wrapper → preload.vscode.js (window.vscode)
  ↓
Wrapper → bootstrap-window.js (globalThis.MonacoBootstrapWindow)
  ↓
Wrapper → contextBridge.expose (window.MonacoBootstrapWindow)
  ↓
Renderer starts → workbench.html → workbench.js
  ↓ (uses window.MonacoBootstrapWindow)
UI renders
```

**Timing:** Preload (before renderer starts)  
**Scope:** Exposed via contextBridge  
**Pros:** Upstream-aligned, proper sandboxing, cleaner  
**Cons:** Slightly more complex, requires Electron knowledge

---

## Migration Path (If Needed)

### From Plan A to Plan B

1. **Remove Plan A steps:**
   - Delete HTML patching code
   - Keep integrity suppression (still useful)

2. **Add Plan B step:**
   - Replace "Fix Windows bootstrap loading (Plan A)" 
   - With "Fix Windows bootstrap loading (Preload Wrapper)"

3. **Test:**
   - Build artifact
   - Verify `preload.vscode.js` exists
   - Verify wrapper `preload.js` created
   - Test launch - should work identically

4. **Validate:**
   ```javascript
   typeof window.MonacoBootstrapWindow  // "object"
   typeof window.vscode  // "object"
   ```

---

## Related Documentation

- **Implemented Solution:** `PLAN_A_IMPLEMENTATION.md`
- **Problem Analysis:** `WINDOWS_BLUE_SCREEN_ISSUE.md`
- **Build Workflow:** `.github/workflows/build-release.yml`

---

## References

- **Electron Preload:** https://www.electronjs.org/docs/latest/tutorial/tutorial-preload
- **Context Bridge:** https://www.electronjs.org/docs/latest/api/context-bridge
- **VS Code Sandbox:** https://github.com/microsoft/vscode/issues/sandbox

---

**Document Version:** 1.0  
**Last Updated:** November 9, 2025  
**Status:** Documented (Not Implemented)  
**Recommendation:** Keep as contingency plan if Plan A needs replacement
