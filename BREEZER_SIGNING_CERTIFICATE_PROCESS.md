# BREEZER Code Signing Certificate Process

**Project:** BREEZER IDE by RICHDALE AI  
**Purpose:** Eliminate Windows SmartScreen warnings and establish trust  
**Status:** Documentation for future implementation  
**Priority:** High (required for professional distribution)

---

## Executive Summary

Windows Defender SmartScreen blocks unsigned executables with a "Windows protected your PC" warning, requiring users to click "More info" → "Run anyway". This creates a poor first impression and reduces trust.

**Solution:** Implement EV (Extended Validation) Code Signing to:
- ✅ Eliminate SmartScreen warnings immediately
- ✅ Establish instant trust with Windows
- ✅ Professional appearance for enterprise clients
- ✅ Enable automatic updates without security warnings

**Investment:** ~$400-500/year  
**ROI:** First enterprise sale covers annual cost

---

## Why Code Signing is Critical

### Current User Experience (Unsigned)

1. User downloads `breezer-ide-windows-x64.zip`
2. Extracts and runs `BREEZER.exe`
3. **Windows SmartScreen blocks execution:**
   ```
   ┌─────────────────────────────────────────┐
   │  Windows protected your PC              │
   │                                          │
   │  Windows Defender SmartScreen prevented │
   │  an unrecognized app from starting.     │
   │  Running this app might put your PC     │
   │  at risk.                                │
   │                                          │
   │  [ More info ]        [ Don't run ]     │
   └─────────────────────────────────────────┘
   ```
4. User must click "More info" → "Run anyway"
5. **Impression:** "Is this malware?"

### Target User Experience (Signed with EV Certificate)

1. User downloads `breezer-ide-windows-x64.zip`
2. Extracts and runs `BREEZER.exe`
3. **Windows verifies signature:**
   - Sees "RICHDALE AI" as verified publisher
   - No SmartScreen warning
   - App launches immediately
4. **Impression:** Professional, trustworthy software

---

## Certificate Types Comparison

| Certificate Type | Cost (Annual) | SmartScreen Trust | Reputation Build Time | Hardware Token | Best For |
|------------------|---------------|-------------------|----------------------|----------------|----------|
| **Standard Code Signing** | $100-200 | ⚠️ Delayed | Weeks/Months | No | Internal/Beta |
| **EV Code Signing** | $400-500 | ✅ Immediate | None | Yes (USB) | **Production** |
| **Self-Signed** | Free | ❌ None | Never | No | Development only |

**Recommendation:** EV Code Signing Certificate

---

## EV Code Signing Certificate - Detailed Guide

### What is EV Code Signing?

Extended Validation (EV) Code Signing provides the highest level of trust:
- **Instant SmartScreen reputation** - No waiting for Microsoft approval
- **Requires business validation** - Proves you're a legitimate organization
- **Hardware token required** - Certificate stored on USB device (tamper-proof)
- **Strongest protection** - Cannot be exported or stolen easily

### Trusted Certificate Authorities

| Provider | Price (3 years) | Validation Time | Support Quality | Recommended |
|----------|-----------------|-----------------|-----------------|-------------|
| **DigiCert** | $474/year | 1-7 days | ⭐⭐⭐⭐⭐ | **Best choice** |
| **Sectigo (Comodo)** | $349/year | 1-5 days | ⭐⭐⭐⭐ | Good value |
| **GlobalSign** | $599/year | 2-7 days | ⭐⭐⭐⭐⭐ | Premium |
| **SSL.com** | $299/year | 1-5 days | ⭐⭐⭐ | Budget option |

**Recommendation:** DigiCert EV Code Signing Certificate
- Most trusted by Windows
- Best support
- Fastest validation
- Includes YubiKey token

---

## Procurement Process

### Prerequisites

Before purchasing, gather these documents:

#### 1. Business Verification Documents
- **Company registration certificate** (Articles of Incorporation)
- **Business license** (if applicable)
- **Tax ID / EIN** (Employer Identification Number)
- **D&B DUNS Number** (recommended but not always required)

#### 2. Personal Verification Documents (for authorized signer)
- **Government-issued photo ID** (Passport or Driver's License)
- **Proof of employment** (company email, business card)
- **Authorization letter** (if not company owner)

#### 3. Contact Information
- **Company address** (physical, not PO Box)
- **Phone number** (verified via call-back)
- **Company email** (must match domain)
- **Official website** (if available)

### Step-by-Step Purchase (DigiCert Example)

#### Phase 1: Order Certificate (Day 0)

1. **Visit DigiCert:**
   ```
   https://www.digicert.com/signing/code-signing-certificates
   → Select "EV Code Signing Certificate"
   → Add to cart: ~$474/year
   ```

2. **Complete Order Form:**
   ```
   Organization Name:    RICHDALE AI
   Organization Unit:    Development
   Street Address:       [Your business address]
   City:                 [City]
   State/Province:       [State]
   Postal Code:          [ZIP]
   Country:              [Country]
   
   Phone Number:         [Verified phone]
   Email:                admin@richdale.ai (or similar)
   ```

3. **Authorized Representative:**
   ```
   Full Name:           [Your name]
   Job Title:           [CEO/CTO/Owner]
   Email:               [Your company email]
   Phone:               [Direct line]
   ```

4. **Submit Order** → Receive order confirmation email

#### Phase 2: Validation (Days 1-7)

1. **Document Verification Email:**
   - DigiCert sends automated email requesting documents
   - Upload via secure portal:
     - Company registration
     - Tax ID
     - Photo ID of authorized representative

2. **Phone Verification Call:**
   - DigiCert calls your business phone
   - Confirms you authorized the certificate
   - 2-5 minute verification call

3. **Business Validation:**
   - DigiCert verifies business exists in public records
   - Checks DUNS database (if available)
   - May call company directly

4. **Validation Complete:**
   - Receive email confirmation
   - Certificate issuance begins

#### Phase 3: Token Delivery & Setup (Days 5-10)

1. **Hardware Token Ships:**
   - DigiCert sends YubiKey or similar USB token
   - Contains your certificate (cannot be exported)
   - Arrives via tracked mail

2. **Certificate Installation:**
   ```powershell
   # Insert USB token
   # Windows automatically detects certificate
   
   # Verify installation:
   certutil -store MY
   
   # Look for: "RICHDALE AI" certificate with EV OID
   ```

3. **Test Signing:**
   ```powershell
   # Test sign a dummy executable
   signtool sign /tr http://timestamp.digicert.com /td SHA256 /fd SHA256 /a test.exe
   
   # Should succeed without errors
   ```

---

## Implementation in CI/CD Pipeline

### Challenge: USB Token in Cloud Build

**Problem:** EV certificates require hardware USB token, but GitHub Actions is a cloud environment with no physical access.

**Solutions:**

#### Option A: Azure Key Vault (Recommended for Enterprise)

DigiCert offers **cloud-based EV signing** via Azure Key Vault:

**Advantages:**
- ✅ No physical token needed
- ✅ Works in CI/CD
- ✅ Secure cloud storage
- ✅ Audit logging

**Setup:**
1. Purchase DigiCert EV certificate with **Azure Key Vault** option
2. Certificate stored in Azure
3. Sign via Azure API

**Cost:** +$100/year premium vs USB token

**Implementation:**
```yaml
# .github/workflows/build-release.yml

- name: Sign Windows Executable
  env:
    AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
    AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
    AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
    AZURE_KEYVAULT_URL: ${{ secrets.AZURE_KEYVAULT_URL }}
  run: |
    # Install AzureSignTool
    dotnet tool install --global AzureSignTool
    
    # Sign executable via Azure Key Vault
    AzureSignTool sign `
      --azure-key-vault-url "$env:AZURE_KEYVAULT_URL" `
      --azure-key-vault-client-id "$env:AZURE_CLIENT_ID" `
      --azure-key-vault-client-secret "$env:AZURE_CLIENT_SECRET" `
      --azure-key-vault-tenant-id "$env:AZURE_TENANT_ID" `
      --azure-key-vault-certificate "BREEZER-CodeSign-Cert" `
      --timestamp-rfc3161 "http://timestamp.digicert.com" `
      --timestamp-digest sha256 `
      --file-digest sha256 `
      --verbose `
      "VSCode-win32-x64\BREEZER.exe"
    
    Write-Host "✓ Signed BREEZER.exe with EV certificate"
```

#### Option B: Self-Hosted Runner with USB Token

**Setup:**
1. Dedicate a Windows machine in your office
2. Install GitHub Actions self-hosted runner
3. Keep USB token plugged in
4. Configure runner to handle Windows builds

**Advantages:**
- ✅ Uses standard USB token (no Azure premium)
- ✅ Full control over signing environment

**Disadvantages:**
- ❌ Requires dedicated hardware
- ❌ Must be always-on
- ❌ Physical security responsibility

**Implementation:**
```yaml
# .github/workflows/build-release.yml

build-windows:
  runs-on: self-hosted  # Your machine with USB token
  
  steps:
    # ... build steps ...
    
    - name: Sign BREEZER.exe
      run: |
        # Token is physically connected to machine
        $certThumbprint = "YOUR_CERT_THUMBPRINT_HERE"
        
        signtool sign `
          /sha1 $certThumbprint `
          /tr http://timestamp.digicert.com `
          /td SHA256 `
          /fd SHA256 `
          "VSCode-win32-x64\BREEZER.exe"
```

#### Option C: Manual Signing (Temporary Solution)

**Process:**
1. CI/CD builds unsigned executable
2. Download artifact locally
3. Sign on machine with USB token
4. Re-upload signed version

**Use case:** Until cloud signing is set up

---

## Complete Signing Implementation

### Prerequisites Setup

1. **Install Windows SDK** (contains signtool.exe):
   ```powershell
   # Download and install Windows SDK
   # Or use Chocolatey:
   choco install windows-sdk-10-version-2004-all
   
   # Verify signtool location:
   Get-ChildItem "C:\Program Files (x86)\Windows Kits\10\bin\" -Recurse -Filter "signtool.exe"
   ```

2. **Add to GitHub Secrets:**
   ```
   AZURE_TENANT_ID          → [Azure AD Tenant ID]
   AZURE_CLIENT_ID          → [Service Principal Client ID]
   AZURE_CLIENT_SECRET      → [Service Principal Secret]
   AZURE_KEYVAULT_URL       → https://your-vault.vault.azure.net/
   CODE_SIGNING_CERT_NAME   → BREEZER-CodeSign-Cert
   ```

### Full CI/CD Signing Step

```yaml
- name: Install AzureSignTool
  run: |
    dotnet tool install --global AzureSignTool --version 4.0.1
    Write-Host "✓ Installed AzureSignTool"

- name: Sign BREEZER Executable
  env:
    AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
    AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
    AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
    AZURE_KEYVAULT_URL: ${{ secrets.AZURE_KEYVAULT_URL }}
    CERT_NAME: ${{ secrets.CODE_SIGNING_CERT_NAME }}
  run: |
    Write-Host "=== Code Signing BREEZER.exe with EV Certificate ==="
    
    $exePath = "VSCode-win32-x64\BREEZER.exe"
    
    # Verify executable exists
    if (!(Test-Path $exePath)) {
      Write-Error "BREEZER.exe not found at $exePath"
      exit 1
    }
    
    $originalSize = (Get-Item $exePath).Length
    Write-Host "Original executable: $originalSize bytes"
    
    # Sign via Azure Key Vault
    AzureSignTool sign `
      --azure-key-vault-url "$env:AZURE_KEYVAULT_URL" `
      --azure-key-vault-client-id "$env:AZURE_CLIENT_ID" `
      --azure-key-vault-client-secret "$env:AZURE_CLIENT_SECRET" `
      --azure-key-vault-tenant-id "$env:AZURE_TENANT_ID" `
      --azure-key-vault-certificate "$env:CERT_NAME" `
      --timestamp-rfc3161 "http://timestamp.digicert.com" `
      --timestamp-digest sha256 `
      --file-digest sha256 `
      --description "BREEZER IDE by RICHDALE AI" `
      --description-url "https://github.com/msiraga/BREEZER_X" `
      --verbose `
      $exePath
    
    if ($LASTEXITCODE -ne 0) {
      Write-Error "Code signing failed!"
      exit 1
    }
    
    # Verify signature
    Write-Host "`nVerifying signature..."
    $signCheck = Get-AuthenticodeSignature $exePath
    
    if ($signCheck.Status -eq "Valid") {
      Write-Host "✓ Signature valid"
      Write-Host "  Signer: $($signCheck.SignerCertificate.Subject)"
      Write-Host "  Thumbprint: $($signCheck.SignerCertificate.Thumbprint)"
      Write-Host "  Valid from: $($signCheck.SignerCertificate.NotBefore)"
      Write-Host "  Valid until: $($signCheck.SignerCertificate.NotAfter)"
    } else {
      Write-Error "Signature verification failed: $($signCheck.Status)"
      exit 1
    }
    
    $signedSize = (Get-Item $exePath).Length
    Write-Host "`nSigned executable: $signedSize bytes (added $($signedSize - $originalSize) bytes for signature)"
    
    Write-Host "`n✅ BREEZER.exe successfully signed with EV certificate!"

- name: Recreate signed artifact
  run: |
    Write-Host "Recreating Windows artifact with signed executable..."
    Remove-Item builds\breezer-ide-windows-x64.zip -Force
    Compress-Archive -Path VSCode-win32-x64 -DestinationPath builds\breezer-ide-windows-x64.zip
    Write-Host "✅ Signed artifact ready for distribution"
```

---

## Verification & Testing

### Verify Signature Locally

```powershell
# Method 1: PowerShell
Get-AuthenticodeSignature "BREEZER.exe" | Format-List *

# Expected output:
# Status              : Valid
# SignerCertificate   : [Subject]
#                       CN=RICHDALE AI
#                       ...

# Method 2: signtool
signtool verify /pa /v "BREEZER.exe"

# Expected output:
# Successfully verified: BREEZER.exe

# Method 3: Windows Explorer
# Right-click BREEZER.exe → Properties → Digital Signatures tab
# Should show: "RICHDALE AI" with valid signature
```

### Test SmartScreen Behavior

**Before Signing:**
```powershell
# Download unsigned build
# Run BREEZER.exe
# Result: SmartScreen blocks with "Windows protected your PC"
```

**After Signing:**
```powershell
# Download signed build
# Run BREEZER.exe
# Result: Launches immediately, no warnings
```

### Certificate Expiration Monitoring

```powershell
# Check certificate validity
$cert = Get-AuthenticodeSignature "BREEZER.exe"
$daysUntilExpiry = ($cert.SignerCertificate.NotAfter - (Get-Date)).Days

if ($daysUntilExpiry -lt 30) {
  Write-Warning "Certificate expires in $daysUntilExpiry days!"
}
```

---

## Cost Analysis

### Initial Setup Costs

| Item | Cost | One-Time/Recurring |
|------|------|-------------------|
| EV Code Signing Certificate (DigiCert) | $474 | Annual |
| Azure Key Vault Premium | $100 | Annual (optional) |
| Business validation documents | $0-50 | One-time |
| **Total Year 1** | **$574-624** | - |
| **Renewal (Year 2+)** | **$474-574** | Annual |

### Cost-Benefit ROI

**Scenario 1: Enterprise Sales**
- First enterprise client: $5,000-50,000 contract
- Code signing cost: $574/year
- **ROI: 870% to 8,600%**

**Scenario 2: Consumer Downloads**
- Conversion rate without signing: ~40% (60% drop-off due to warning)
- Conversion rate with signing: ~90%
- **2.25x improvement in adoption**

**Scenario 3: Support Cost Reduction**
- Support tickets about "Is this safe?": ~10-20/month
- Support cost per ticket: ~$15 (time)
- Annual savings: ~$1,800-3,600
- **Pays for itself 3-6x over**

---

## Timeline

### Procurement & Setup Timeline

| Phase | Duration | Key Activities |
|-------|----------|----------------|
| **Document Preparation** | 1-2 days | Gather business docs, IDs, verification info |
| **Certificate Order** | 1 hour | Submit order on DigiCert website |
| **Validation Process** | 1-7 days | DigiCert verifies business and identity |
| **Token Delivery** | 3-5 days | Hardware token ships via mail |
| **Azure Key Vault Setup** | 1-2 days | Configure Azure, import certificate |
| **CI/CD Integration** | 1-2 days | Implement signing step, test builds |
| **Testing & Verification** | 1 day | Test signed builds, verify SmartScreen |
| **Total** | **7-21 days** | From purchase to production |

---

## Maintenance & Renewal

### Annual Renewal Process

**Timeline: 30-45 days before expiration**

1. **Renewal Notification** (Day -45)
   - DigiCert sends renewal reminder
   - Check for any business info changes

2. **Revalidation** (Day -30)
   - DigiCert may require updated documents
   - Usually faster than initial validation

3. **Payment** (Day -15)
   - Pay renewal fee (~$474)
   - New certificate issued

4. **Update Azure Key Vault** (Day -7)
   - Import renewed certificate
   - Test signing with new cert

5. **Update CI/CD** (Day 0)
   - Switch to new certificate thumbprint/name
   - Deploy signed build

### Certificate Expiration Alerts

**Add to monitoring:**
```powershell
# Check in CI/CD or scheduled task
$cert = Get-AuthenticodeSignature "BREEZER.exe"
$expiryDate = $cert.SignerCertificate.NotAfter
$daysLeft = ($expiryDate - (Get-Date)).Days

if ($daysLeft -lt 60) {
  # Send alert email/Slack notification
  Write-Warning "Code signing certificate expires in $daysLeft days on $expiryDate"
}
```

---

## Security Best Practices

### Protecting the Certificate

**For USB Token (Physical Security):**
- 🔒 Store in locked drawer when not in use
- 🔒 Limit physical access to authorized personnel only
- 🔒 Use self-hosted runner in secure, monitored location
- 🔒 Log all signing operations

**For Azure Key Vault:**
- 🔒 Use Azure AD service principal with minimal permissions
- 🔒 Enable audit logging for all key vault operations
- 🔒 Rotate client secrets every 90 days
- 🔒 Use IP restrictions if possible
- 🔒 Monitor for unusual signing activity

### Secret Management in GitHub

```yaml
# Store in GitHub Secrets (Settings → Secrets and variables → Actions)
# NEVER commit these to git:

AZURE_TENANT_ID          # Azure AD tenant
AZURE_CLIENT_ID          # Service principal
AZURE_CLIENT_SECRET      # Rotate every 90 days
AZURE_KEYVAULT_URL       # Key vault endpoint
CODE_SIGNING_CERT_NAME   # Certificate name in vault
```

### Incident Response

**If certificate is compromised:**
1. **Immediately revoke** certificate via DigiCert portal
2. **Contact DigiCert** support for emergency replacement
3. **Rotate all secrets** (Azure credentials, GitHub secrets)
4. **Audit logs** to identify scope of compromise
5. **Notify users** if signed malware was distributed

---

## Alternative: Microsoft Store Distribution

### For Consumer Edition

Instead of (or in addition to) code signing, consider Microsoft Store:

**Advantages:**
- ✅ Built-in trust (no signing needed)
- ✅ Automatic updates
- ✅ One-time $19 registration fee
- ✅ Reach Windows users easily

**Disadvantages:**
- ❌ Microsoft approval process (1-3 days)
- ❌ 15% revenue share if charging
- ❌ Microsoft Store policies/restrictions

**When to use:**
- Consumer/Community edition
- Supplementary distribution channel
- Want automatic updates

**Not a replacement for code signing:**
- Enterprise clients may want direct download
- Store doesn't build developer brand
- Code signing still needed for direct distribution

---

## Troubleshooting

### Common Issues

#### Issue: "No certificates were found that met all given criteria"

**Cause:** Certificate not found in store or wrong thumbprint

**Solution:**
```powershell
# List all certificates
certutil -store MY

# Verify correct thumbprint
Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Subject -like "*RICHDALE*" }
```

#### Issue: "Timestamp server not responding"

**Cause:** DigiCert timestamp server temporarily down

**Solution:**
```powershell
# Try alternative timestamp servers:
# Primary: http://timestamp.digicert.com
# Backup: http://timestamp.comodoca.com
# Backup: http://timestamp.sectigo.com
```

#### Issue: Signed executable still shows SmartScreen warning

**Cause:** Using Standard (not EV) certificate or missing timestamp

**Solution:**
- Verify certificate is EV (check for EV OID in certificate)
- Ensure timestamp is included in signature
- Wait 24-48 hours for SmartScreen to recognize new certificate

#### Issue: Azure Key Vault authentication fails in CI/CD

**Cause:** Incorrect service principal permissions

**Solution:**
```bash
# Grant signing permission to service principal
az keyvault set-policy \
  --name YOUR_KEYVAULT_NAME \
  --spn YOUR_CLIENT_ID \
  --certificate-permissions get \
  --key-permissions sign
```

---

## Next Steps

### Immediate Actions

1. **Decision:** Choose Azure Key Vault vs Self-Hosted Runner
2. **Budget Approval:** $574/year for certificate
3. **Document Gathering:** Prepare business verification documents

### Implementation Phases

**Phase 1: Procurement (Week 1-2)**
- [ ] Purchase DigiCert EV Code Signing Certificate
- [ ] Submit business verification documents
- [ ] Complete phone verification

**Phase 2: Setup (Week 2-3)**
- [ ] Receive and test hardware token (if USB) OR
- [ ] Configure Azure Key Vault (if cloud)
- [ ] Test signing locally

**Phase 3: CI/CD Integration (Week 3)**
- [ ] Add signing step to Windows workflow
- [ ] Configure GitHub Secrets
- [ ] Test signed build in CI/CD

**Phase 4: Verification (Week 4)**
- [ ] Download signed build
- [ ] Test on fresh Windows machine
- [ ] Verify no SmartScreen warning
- [ ] Document for team

---

## Related Documentation

- **Build Workflow:** `.github/workflows/build-release.yml`
- **Windows Distribution:** `AFTER_BUILD.md`
- **Project Summary:** `PROJECT_MEMORY.md`

---

## Support Contacts

### DigiCert Support
- **Phone:** 1-801-701-9600
- **Email:** support@digicert.com
- **Portal:** https://www.digicert.com/account/login.php

### Azure Key Vault Support
- **Docs:** https://docs.microsoft.com/en-us/azure/key-vault/
- **Support:** Azure Portal → Help + Support

---

**Document Version:** 1.0  
**Last Updated:** November 9, 2025  
**Owner:** RICHDALE AI Development Team  
**Status:** Planning (Not Yet Implemented)
