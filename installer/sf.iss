#define MyAppName "SimpleFighter"
#define MyAppVersion "7.9"
#define MyAppPublisher "tsatria03"
#define MyAppURL "https://tsatria03.itch.io/SimpleFighter"
#define MyAppExeName "sf.exe"

[Setup]
AppId={{64477427-9EAA-4A52-905B-269D21D008DA}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
OutputDir=.
OutputBaseFilename=SimpleFighter_windows_installer_password_is_SpfBuilder
Password=SpfBuilder
Encryption=yes
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"
Name: "startmenuicon"; Description: "Create a Start Menu shortcut"; GroupDescription: "Additional icons:"

[Files]
Source: "C:\Users\tsatr\OneDrive\Documents\GitHub\SimpleFighter\releases\windows\SimpleFighter_windows_portable_password_is_SpfBuilder\sf\*"; \
  DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startmenuicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; \
  Flags: nowait postinstall skipifsilent unchecked;
