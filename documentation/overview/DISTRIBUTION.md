# BREEZER Distribution Guide

**How to build and distribute BREEZER IDE to your company**

---

## Platform Compatibility ⚠️

**IMPORTANT**: Each platform needs its own build!

| Build | Compatible With | File Extension |
|-------|----------------|----------------|
| **Linux build** | Linux x64 only | `.tar.gz` |
| **Windows build** | Windows 10/11 only | `.zip` |
| **macOS build** | macOS Intel/Apple Silicon | `.tar.gz` / `.dmg` |

**Cross-platform does NOT work!** Windows users need Windows build, etc.

---

## Distribution Strategies

### Strategy 1: GitHub Releases (Recommended)

**Best for:** Company-wide distribution, automatic builds

**How it works:**
1. Push code to GitHub
2. Create version tag
3. CI/CD builds all platforms automatically (30-60 min)
4. Employees download from GitHub Releases

**Setup:**

```bash
# Initial setup
cd C:\Users\msira\Downloads\breezer_sonnet
git init
git add .
git commit -m "Initial BREEZER v1.0.0"
git remote add origin https://github.com/msiraga/BREEZER_X.git
git push -u origin main

# Create first release
git tag v1.0.0 -m "BREEZER v1.0.0 - Initial Release"
git push origin v1.0.0
```

**GitHub Actions will automatically:**
- Build Linux version (on Ubuntu runner)
- Build Windows version (on Windows runner)
- Build macOS version (on macOS runner)
- Create GitHub Release
- Attach all builds

**Distribution URL:**
```
https://github.com/msiraga/BREEZER_X/releases/latest
```

**Employees get:**
- ✅ Always latest version
- ✅ All platforms available
- ✅ Consistent builds
- ✅ No build time on your machine

---

### Strategy 2: Local Docker Build

**Best for:** Air-gapped environments, no GitHub access

**Build all platforms locally:**

```bash
# Build everything (1-3 hours)
docker-compose -f docker/docker-compose.build.yml up

# Output in builds/:
# - breezer-ide-linux-x64.tar.gz
# - breezer-ide-windows-x64.zip
# - breezer-ide-darwin-x64.tar.gz
```

**Then upload to:**
- Internal file server
- SharePoint
- Network drive
- Company intranet

---

## CI/CD Workflows

### Included Workflows

**1. Release Build** (`.github/workflows/build-release.yml`)
- **Trigger**: Push to `main` branch OR git tag `v*`
- **Builds**: All 3 platforms automatically
- **Output**: Artifacts (push) OR GitHub Release (tags)

**2. Nightly Build** (`.github/workflows/nightly-build.yml`)
- **Trigger**: Daily at 2 AM UTC
- **Builds**: All 3 platforms
- **Output**: Artifacts (7-day retention)
- **Purpose**: Catch issues early

**3. Backend Tests** (`.github/workflows/test-backend.yml`)
- **Trigger**: Push to main, PRs
- **Tests**: Backend API, agents, services
- **Output**: Coverage report

### How to Trigger Builds

**Automatic release:**
```bash
git tag v1.0.1 -m "Bug fixes and improvements"
git push origin v1.0.1
# Wait 30-60 minutes → Release created
```

**Manual trigger:**
1. Go to: https://github.com/msiraga/BREEZER_X/actions
2. Select "Build BREEZER IDE"
3. Click "Run workflow"
4. Choose branch
5. Click "Run workflow" button

---

## Employee Installation Guide

### Windows

**Download:**
```
https://github.com/msiraga/BREEZER_X/releases/latest
→ breezer-ide-windows-x64.zip
```

**Install:**
```powershell
# Extract
Expand-Archive breezer-ide-windows-x64.zip -DestinationPath C:\BreezerIDE

# Run
cd C:\BreezerIDE\VSCode-win32-x64
.\Code.exe
```

**Optional - Add to PATH:**
```powershell
# Add to system PATH for 'breezer' command
$env:Path += ";C:\BreezerIDE\VSCode-win32-x64"
```

---

### Linux

**Download:**
```bash
wget https://github.com/msiraga/BREEZER_X/releases/latest/download/breezer-ide-linux-x64.tar.gz
```

**Install:**
```bash
# Extract
tar -xzf breezer-ide-linux-x64.tar.gz
sudo mv VSCode-linux-x64 /opt/breezer-ide

# Create symlink
sudo ln -s /opt/breezer-ide/code /usr/local/bin/breezer

# Run
breezer
```

---

### macOS

**Download:**
```bash
curl -LO https://github.com/msiraga/BREEZER_X/releases/latest/download/breezer-ide-darwin-x64.tar.gz
```

**Install:**
```bash
# Extract
tar -xzf breezer-ide-darwin-x64.tar.gz

# Move to Applications
sudo mv VSCode-darwin-x64/Code.app /Applications/BREEZER.app

# Run
open /Applications/BREEZER.app
```

---

## Update Strategy

### Version Scheme

Use semantic versioning:
- **v1.0.0** - Initial release
- **v1.0.1** - Bug fixes
- **v1.1.0** - New features
- **v2.0.0** - Breaking changes

### Release Process

```bash
# 1. Update version
# Edit: backend/main.py, ide-build/branding/product.json

# 2. Commit changes
git add .
git commit -m "Release v1.1.0"

# 3. Create tag
git tag v1.1.0 -m "BREEZER v1.1.0
- New feature X
- Bug fix Y
- Improved Z"

# 4. Push
git push origin main
git push origin v1.1.0

# 5. Wait for CI/CD
# Check: https://github.com/msiraga/BREEZER_X/actions

# 6. Notify employees
# Email: "BREEZER v1.1.0 released!"
```

### Auto-Update (Future)

Add to VSCode extension:
```typescript
// Check for updates
async function checkForUpdates() {
  const response = await fetch(
    'https://api.github.com/repos/msiraga/BREEZER_X/releases/latest'
  );
  const latest = await response.json();
  
  if (latest.tag_name > currentVersion) {
    vscode.window.showInformationMessage(
      `BREEZER ${latest.tag_name} is available!`,
      'Download'
    ).then(action => {
      if (action === 'Download') {
        vscode.env.openExternal(latest.html_url);
      }
    });
  }
}
```

---

## Private Distribution (No GitHub)

### Option 1: Internal Git Server

Use GitLab/Gitea/Azure DevOps with similar CI/CD:

```yaml
# .gitlab-ci.yml
build-windows:
  stage: build
  tags: [windows]
  script:
    - docker-compose -f docker/docker-compose.build.yml up build-windows
  artifacts:
    paths:
      - builds/
```

### Option 2: Build Server

Setup dedicated build machine:

```bash
# Cron job on build server
0 2 * * * cd /builds/breezer && git pull && docker-compose -f docker/docker-compose.build.yml up
```

### Option 3: Manual Builds

Build locally, upload to file server:

```bash
# Build
docker-compose -f docker/docker-compose.build.yml up

# Upload
scp builds/* fileserver:/share/breezer/releases/v1.0.0/
```

---

## Build Performance

| Platform | First Build | Cached Build | Parallel |
|----------|-------------|--------------|----------|
| **Linux** | 20-40 min | 8-15 min | ✅ Yes |
| **Windows** | 30-60 min | 10-20 min | ✅ Yes |
| **macOS** | 30-60 min | 10-20 min | ✅ Yes |
| **All 3** | 1-3 hours | 25-50 min | ✅ Yes |

**Tips for faster builds:**
- Use GitHub Actions (free for private repos)
- Keep Docker layer cache
- Build only changed platforms

---

## Security Considerations

### Signed Builds

**Windows:**
```powershell
# Sign with code signing certificate
signtool sign /f cert.pfx /p password /t http://timestamp.digicert.com Code.exe
```

**macOS:**
```bash
# Sign with Apple Developer ID
codesign --sign "Developer ID" --deep BREEZER.app
```

### Checksum Verification

Generate checksums for employees:

```bash
# SHA256 checksums
sha256sum breezer-ide-*.{zip,tar.gz} > checksums.txt

# Employees verify:
sha256sum -c checksums.txt
```

---

## Troubleshooting

### Build fails in CI/CD

**Check:**
1. GitHub Actions logs
2. Node.js memory limits
3. Docker daemon status

**Fix:**
```yaml
# Increase memory in workflow
env:
  NODE_OPTIONS: --max_old_space_size=8192
```

### Employees can't download

**Solutions:**
- Use direct links (not "latest")
- Mirror to internal server
- Create .zip/.tar.gz manually

### Version conflicts

**Prevention:**
- Use strict version tags
- Test before release
- Provide rollback instructions

---

## Summary

**Recommended Setup:**

1. **For 1-10 users**: Local Docker builds
2. **For 10-100 users**: GitHub Actions + Releases
3. **For 100+ users**: Internal build server + CDN

**Distribution Timeline:**

```
Day 1:  Setup GitHub repository
Day 2:  First local build + test
Day 3:  Tag v1.0.0 → CI/CD builds
Day 4:  Distribute to pilot group (5-10 users)
Week 2: Full company rollout
```

---

© 2025 RICHDALE AI
