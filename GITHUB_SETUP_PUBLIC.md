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

### 3. Setup Authentication

**Generate a Personal Access Token (PAT):**

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - ✅ `repo` (full control of private repositories)
   - ✅ `workflow` (update GitHub Actions workflows)
4. Click "Generate token"
5. **Copy the token** (starts with `ghp_...`)

**⚠️ IMPORTANT: Never commit tokens to Git!**

---

### 4. Push to GitHub

**Option A: Using Credential Manager (Recommended)**

```bash
# Configure Git to use Windows Credential Manager
git config --global credential.helper wincred

# Push (will prompt for credentials)
git push -u origin main

# Enter:
# Username: your-github-username
# Password: ghp_YourPersonalAccessToken
```

**Option B: Environment Variable**

```powershell
# Set PAT as environment variable (current session only)
$env:GITHUB_TOKEN = "ghp_YourPersonalAccessToken"

# Push using token
git push https://$env:GITHUB_TOKEN@github.com/msiraga/BREEZER_X.git main
```

---

### 5. Check Build Status

**View builds:**
```
https://github.com/msiraga/BREEZER_X/actions
```

**What happens automatically:**
1. Code uploads to GitHub ✅
2. GitHub Actions triggers ✅
3. Builds Linux, Windows, macOS (30-60 min) ✅
4. Artifacts available for download ✅

---

## Automatic Builds on Every Push

```bash
# Make changes
git add .
git commit -m "Updated feature X"

# Push - triggers automatic build
git push origin main

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

## Security Best Practices

### ✅ DO:
- Store PAT in Windows Credential Manager
- Use environment variable for scripts
- Rotate PAT every 90 days
- Use fine-grained tokens when possible

### ❌ DON'T:
- Commit PAT to repository
- Share PAT publicly
- Use PAT in files tracked by Git
- Hard-code tokens in scripts

---

## Troubleshooting

### Push fails with authentication error

**Solution:**
```bash
# Ensure credential helper is configured
git config --global credential.helper wincred

# Or use PAT directly (one-time)
git push https://ghp_YourToken@github.com/your-repo.git main
```

### Build fails in GitHub Actions

**Check:**
1. View logs: https://github.com/msiraga/BREEZER_X/actions
2. Common issues:
   - Node.js out of memory → Already configured
   - Missing dependencies → Should auto-install
   - Deprecated actions → Update to latest versions

---

## Quick Reference

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

© 2025 RICHDALE AI
