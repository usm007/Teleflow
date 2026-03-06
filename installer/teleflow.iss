[Setup]
AppId={{B8DA0AC8-95A2-430F-B28E-142A3AAB8B9A}
AppName=Teleflow
AppVersion=4.0.0
AppPublisher=Teleflow
DefaultDirName={autopf}\Teleflow
DefaultGroupName=Teleflow
DisableProgramGroupPage=yes
OutputDir=..\release
OutputBaseFilename=Teleflow_v4_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\Teleflow_v4.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "..\dist\Teleflow_v4\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Teleflow"; Filename: "{app}\Teleflow_v4.exe"
Name: "{autodesktop}\Teleflow"; Filename: "{app}\Teleflow_v4.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Teleflow_v4.exe"; Description: "Launch Teleflow"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
