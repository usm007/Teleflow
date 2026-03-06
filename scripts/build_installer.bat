@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT=%~dp0.."
if defined ISCC (
  set "ISCC=%ISCC%"
) else (
  set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
)

pushd "%ROOT%"

if not exist "teleflow.spec" (
  echo [ERROR] teleflow.spec not found in project root.
  popd
  exit /b 1
)

if not exist "%ISCC%" (
  echo [ERROR] Inno Setup compiler not found at "%ISCC%".
  echo [HINT] Install Inno Setup 6 or set environment variable ISCC to your compiler path.
  popd
  exit /b 1
)

echo [INFO] Cleaning old installer artifacts...
if exist "build" rmdir /s /q "build"
if exist "dist\Teleflow_v4" rmdir /s /q "dist\Teleflow_v4"
if exist "release" rmdir /s /q "release"

echo [INFO] Building onedir payload with PyInstaller spec...
pyinstaller --noconfirm --clean teleflow.spec
if errorlevel 1 (
  echo [ERROR] PyInstaller onedir build failed.
  popd
  exit /b 1
)

if not exist "dist\Teleflow_v4\Teleflow_v4.exe" (
  echo [ERROR] Onedir payload executable missing.
  popd
  exit /b 1
)

if defined SIGN_CERT_SHA1 (
  echo [INFO] Signing onedir app executable...
  signtool sign /sha1 "%SIGN_CERT_SHA1%" /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 "dist\Teleflow_v4\Teleflow_v4.exe"
  if errorlevel 1 (
    echo [ERROR] Code signing failed for onedir executable.
    popd
    exit /b 1
  )
)

echo [INFO] Building installer via Inno Setup...
"%ISCC%" "installer\teleflow.iss"
if errorlevel 1 (
  echo [ERROR] Installer build failed.
  popd
  exit /b 1
)

if defined SIGN_CERT_SHA1 (
  if exist "release\Teleflow_v4_Setup.exe" (
    echo [INFO] Signing installer executable...
    signtool sign /sha1 "%SIGN_CERT_SHA1%" /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 "release\Teleflow_v4_Setup.exe"
    if errorlevel 1 (
      echo [ERROR] Code signing failed for installer executable.
      popd
      exit /b 1
    )

    echo [INFO] Verifying installer signature...
    signtool verify /pa "release\Teleflow_v4_Setup.exe"
    if errorlevel 1 (
      echo [ERROR] Signature verification failed for installer executable.
      popd
      exit /b 1
    )
  )
) else (
  echo [WARN] SIGN_CERT_SHA1 is not set. Installer build is unsigned.
)

echo [OK] Installer build ready: release\Teleflow_v4_Setup.exe
popd
exit /b 0
