@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT=%~dp0.."
pushd "%ROOT%"

if not exist "icon.ico" (
  echo [ERROR] icon.ico not found in project root.
  popd
  exit /b 1
)

echo [INFO] Cleaning old portable artifacts...
if exist "build" rmdir /s /q "build"
if exist "dist\Teleflow_v4.exe" del /f /q "dist\Teleflow_v4.exe"

echo [INFO] Building portable executable with PyInstaller...
pyinstaller --noconfirm --clean --noconsole --onefile --name "Teleflow_v4" --icon "icon.ico" --add-data "icon.ico;." main.py
if errorlevel 1 (
  echo [ERROR] PyInstaller portable build failed.
  popd
  exit /b 1
)

if not exist "dist\Teleflow_v4.exe" (
  echo [ERROR] Portable executable not produced.
  popd
  exit /b 1
)

if defined SIGN_CERT_SHA1 (
  echo [INFO] Signing portable executable...
  signtool sign /sha1 "%SIGN_CERT_SHA1%" /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 "dist\Teleflow_v4.exe"
  if errorlevel 1 (
    echo [ERROR] Code signing failed for portable executable.
    popd
    exit /b 1
  )

  echo [INFO] Verifying signature...
  signtool verify /pa "dist\Teleflow_v4.exe"
  if errorlevel 1 (
    echo [ERROR] Signature verification failed for portable executable.
    popd
    exit /b 1
  )
) else (
  echo [WARN] SIGN_CERT_SHA1 is not set. Portable build is unsigned.
)

echo [OK] Portable build ready: dist\Teleflow_v4.exe
popd
exit /b 0
