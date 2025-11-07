# BREEZER GitHub Setup Guide

**Push BREEZER to GitHub for automatic builds**

---

## Step-by-Step Guide

### 1. Initialize Git Repository

```bash
cd C:\Users\msira\Downloads\breezer_sonnet

# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial BREEZER platform by RICHDALE AI"
```

---

### 2. Add GitHub Remote

```bash
# Add remote repository
git remote add origin https://github.com/msiraga/BREEZER_X.git

# Verify
git remote -v
```

---

### 3. Push to GitHub Using PAT

**Your Personal Access Token (PAT):**
```
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
```

**⚠️ IMPORTANT: Never commit this token!**

**Configure Git to use PAT:**

```bash
# Option A: Store in Git credential manager (Windows)
git config --global credential.helper wincred

# Option B: Use PAT in URL (one-time)
git remote set-url origin https://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@github.com/msiraga/BREEZER_X.git
```

---

### 4. Push to GitHub

```bash
# Set main as default branch
git branch -M main

# Push
git push -u origin main
```

**What happens next:**
1. Code uploads to GitHub ✅
2. GitHub Actions automatically triggers ✅
3. Builds Linux, Windows, macOS (30-60 min) ✅
4. Artifacts available for download ✅

---

### 5. Check Build Status

**View builds:**
```
https://github.com/msiraga/BREEZER_X/actions
```

**Download builds:**
```
https://github.com/msiraga/BREEZER_X/actions
→ Click latest workflow run
→ Scroll to "Artifacts"
→ Download:
  - breezer-ide-linux
  - breezer-ide-windows
  - breezer-ide-darwin
```

---

## Automatic Builds on Every Push

**Now configured to build automatically when you push!**

```bash
# Make changes
git add .
git commit -m "Updated feature X"

# Push - triggers automatic build
git push origin main

# Wait 30-60 minutes
# Check: https://github.com/msiraga/BREEZER_X/actions
```

---

## Creating Official Releases

**For versioned releases (v1.0.0, v1.1.0, etc.):**

```bash
# Tag the release
git tag v1.0.0 -m "BREEZER v1.0.0 - Initial Release"

# Push tag
git push origin v1.0.0
```

**This creates:**
- GitHub Release at: https://github.com/msiraga/BREEZER_X/releases
- Downloadable builds attached
- Release notes

---

## PAT Security Best Practices

### ✅ DO:
- Store PAT in Windows Credential Manager
- Use environment variable: `$env:GITHUB_TOKEN`
- Rotate PAT every 90 days

### ❌ DON'T:
- Commit PAT to repository
- Share PAT publicly
- Use PAT in scripts committed to Git

### Secure Storage

**Windows Credential Manager:**
```powershell
# Store PAT securely
cmdkey /generic:git:https://github.com /user:msiraga /pass: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

# Git will use it automatically
git push origin main
```

**Or use environment variable:**
```powershell
# Set for current session
$env:GITHUB_TOKEN = "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"

# Use in Git commands
git push https://$env:GITHUB_TOKEN@github.com/msiraga/BREEZER_X.git main
```

---

## Verify Setup

### Check Remote

```bash
git remote -v
```

**Should show:**
```
origin  https://github.com/msiraga/BREEZER_X.git (fetch)
origin  https://github.com/msiraga/BREEZER_X.git (push)
```

### Check GitHub Actions

1. Go to: https://github.com/msiraga/BREEZER_X/settings/actions
2. Ensure "Actions" is enabled
3. Check workflow permissions

---

## Workflow Triggers Summary

| Trigger | What Happens | Output |
|---------|--------------|--------|
| **Push to main** | Builds all platforms | Artifacts (30 days) |
| **Tag v**** | Builds + creates release | GitHub Release |
| **Daily 2 AM** | Nightly build | Artifacts (7 days) |
| **Pull Request** | Tests only | Test results |

---

## Quick Reference Commands

```bash
# Push code (triggers build)
git push origin main

# Create release
git tag v1.0.0 -m "Release notes"
git push origin v1.0.0

# Check status
git status

# View remote
git remote -v

# Pull latest
git pull origin main
```

---

## Next Steps After Push

1. **Monitor build**: https://github.com/msiraga/BREEZER_X/actions
2. **Download artifacts** when build completes
3. **Test builds** on each platform
4. **Create v1.0.0 release** when ready
5. **Share release link** with employees

---

## Troubleshooting

### Push fails with authentication error

**Solution:**
```bash
# Use PAT in URL
git push https://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@github.com/msiraga/BREEZER_X.git main
```

### Build fails in GitHub Actions

**Check:**
1. View logs: https://github.com/msiraga/BREEZER_X/actions
2. Common issues:
   - Node.js out of memory → Already configured with 8GB
   - Missing dependencies → Should auto-install
   - Timeout → Increase in workflow if needed

### Can't download artifacts

**Ensure:**
1. You're logged into GitHub
2. Build completed successfully
3. Artifact retention period hasn't expired

---

**You're ready to push!** Just run:

```bash
git push -u origin main
```

And watch the magic happen at:
```
https://github.com/msiraga/BREEZER_X/actions
```

---

© 2025 RICHDALE AI
