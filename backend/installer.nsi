; LEUIT NSIS Installer Script
!include "MUI2.nsh"

Name "LEUIT"
OutFile "LeuitApp-Setup-1.0.0.exe"
InstallDir "$PROGRAMFILES\LEUIT"
InstallDirRegKey HKCU "Software\LEUIT" ""
RequestExecutionLevel admin

!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  File /r "D:\Project\Leuit\backend\dist\LeuitApp\*"
  
  WriteRegStr HKCU "Software\LEUIT" "" $INSTDIR
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  CreateDirectory "$SMPROGRAMS\LEUIT"
  CreateShortcut "$SMPROGRAMS\LEUIT\LEUIT.lnk" "$INSTDIR\LeuitApp.exe"
  CreateShortcut "$DESKTOP\LEUIT.lnk" "$INSTDIR\LeuitApp.exe"
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\*"
  RMDir /r "$INSTDIR"
  Delete "$SMPROGRAMS\LEUIT\LEUIT.lnk"
  Delete "$DESKTOP\LEUIT.lnk"
  RMDir "$SMPROGRAMS\LEUIT"
  DeleteRegKey HKCU "Software\LEUIT"
SectionEnd
