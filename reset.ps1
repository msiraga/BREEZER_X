# reset.ps1
Stop-Process -Name breezer-ide -Force -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force $env:APPDATA\breezer-ide -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force $env:APPDATA\Code -ErrorAction SilentlyContinue
Write-Host "BREEZER IDE user data reset" -ForegroundColor Green