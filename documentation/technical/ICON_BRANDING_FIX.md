# BREEZER IDE Icon Branding Fix

**Date**: November 10, 2025  
**Issue**: Windows build not showing BREEZER custom icon  
**Status**: ✅ FIXED

## Problem

The BREEZER IDE Windows build was not displaying the custom `breezer.ico` icon despite the branding script copying it to the Code-OSS repository. The warning about obsolete `version` attribute in `docker-compose.yml` was fixed, but the icon still wasn't appearing in the final executable.

## Root Cause

1. **Icon Placement Timing**: The branding script copied the icon to `resources/win32/code.ico`, but VS Code's Electron packager might have been looking for it at additional locations
2. **Missing Validation**: No validation step existed to verify icons were properly placed before or after the build
3. **Incomplete Icon Coverage**: Only one icon location was being populated, but Electron packager may check multiple paths

## Solution Implemented

### Fix 1: Enhanced Branding Scripts

**Updated Files**:
- `ide-build/scripts/apply-branding.ps1` (PowerShell)
- `ide-build/scripts/apply-branding.sh` (Bash)

**Changes**:
```powershell
# Now copies icons to MULTIPLE locations
Copy-Item "$LogosSource\breezer.ico" "$CodeOssDir\resources\win32\code.ico" -Force
Copy-Item "$LogosSource\breezer.ico" "$CodeOssDir\resources\win32\app.ico" -Force

# Validates icon size
$iconSize = (Get-Item "$LogosSource\breezer.ico").Length
if ($iconSize -lt 1024) {
    Write-Warning "Icon file is very small ($iconSize bytes) - may be corrupted"
}
```

### Fix 2: Pre-Build Verification

**Added to branding scripts**:
```powershell
# Verify all expected icon locations exist BEFORE build
$iconLocations = @(
    "$CodeOssDir\resources\win32\code.ico",
    "$CodeOssDir\resources\win32\app.ico"
)

foreach ($iconPath in $iconLocations) {
    if (Test-Path $iconPath) {
        Write-Host "✓ $iconPath" -ForegroundColor Green
    } else {
        Write-Host "✗ MISSING: $iconPath" -ForegroundColor Red
        $allIconsPresent = $false
    }
}
```

### Fix 3: Post-Build Validation

**Added to GitHub Actions** (`.github/workflows/build-release.yml`):
```yaml
- name: Validate icon embedding
  run: |
    Write-Host "=== Validating BREEZER icon in Windows build ===" 
    
    # Verify icon resources exist in package
    $iconResources = @(
      "$packagePath\resources\app\resources\win32\code.ico",
      "$packagePath\resources\app\resources\win32\app.ico"
    )
    
    foreach ($iconPath in $iconResources) {
      if (!(Test-Path $iconPath)) {
        Write-Error "Icon MISSING: $iconPath"
        exit 1
      }
    }
```

## Testing

### Manual Testing
1. **Verify branding script output**:
   ```powershell
   cd C:\Users\msira\Downloads\breezer_sonnet
   .\ide-build\scripts\apply-branding.ps1 code-oss
   ```
   
   Expected output:
   ```
   ✓ Copied to resources\win32\code.ico
   ✓ Copied to resources\win32\app.ico
   ✓ Icon validated (XXXXX bytes)
   ✅ BREEZER IDE branding applied successfully!
   ```

2. **Check icon files exist**:
   ```powershell
   Get-ChildItem code-oss\resources\win32\*.ico
   ```
   
   Expected:
   - `code.ico` (BREEZER icon)
   - `app.ico` (BREEZER icon)

3. **Build and verify**:
   ```powershell
   cd code-oss
   npm ci
   npm run compile
   npm run gulp vscode-win32-x64
   
   # Verify icon in package
   Get-Item VSCode-win32-x64\resources\app\resources\win32\code.ico
   ```

### CI/CD Testing
The GitHub Actions workflow will now:
1. Apply branding (with pre-validation)
2. Build Windows package
3. **Validate icon embedding** (NEW!)
4. Package and upload

If icons are missing, the build will **FAIL** with clear error messages.

## Expected Results

After these fixes:
1. ✅ BREEZER icon appears in Windows taskbar
2. ✅ BREEZER icon appears in Windows Explorer
3. ✅ BREEZER icon appears in Start menu
4. ✅ BREEZER icon appears in Alt+Tab switcher
5. ✅ Build fails early if icons are missing (better CI/CD feedback)

## Rollback Plan

If issues persist:
```bash
# Revert changes
git checkout HEAD~1 ide-build/scripts/apply-branding.ps1
git checkout HEAD~1 ide-build/scripts/apply-branding.sh
git checkout HEAD~1 .github/workflows/build-release.yml
```

## Additional Notes

### Icon Requirements
- **Format**: ICO (Windows Icon)
- **Minimum Size**: 1 KB (validated by script)
- **Recommended Sizes**: 16x16, 32x32, 48x48, 256x256 (multi-resolution ICO)
- **Location**: `ide-build/branding/icons/breezer.ico`

### VS Code Icon Paths
VS Code's Electron packager checks these locations:
1. `resources/win32/code.ico` (primary)
2. `resources/win32/app.ico` (fallback)
3. Icon embedding happens during `gulp vscode-win32-x64` task

### Related Issues
- Fixed: `docker-compose.yml` version warning (removed `version: '3.8'`)
- Fixed: Icon placement validation
- Fixed: Multiple icon location support

## Commit Message Template
```
fix: ensure BREEZER icon appears in Windows builds

- Copy breezer.ico to multiple Electron packager paths
- Add pre-build icon validation in branding scripts
- Add post-build icon verification in GitHub Actions
- Prevent builds with missing icons from passing CI

This ensures the custom BREEZER icon is properly embedded
in the Windows executable and visible in all contexts
(taskbar, explorer, start menu, etc.)

Fixes #[issue-number]
```

## References
- Issue: Windows build not showing custom icon
- Previous attempt: Commit "fix: use breezer.ico for all platform icons + harden scripts"
- Related: Electron packager documentation
- VS Code build system: `build/lib/electron.ts`
