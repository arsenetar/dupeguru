SetCompressor /SOLID lzma

; General Defines
    !define REGKEY "Software\Hardcoded Software\dupeGuru"
    !define INSTPATH "Hardcoded Software\dupeGuru"
    var StartMenuFolder

    ; todo include a way to point between x64 and x32 builds via env
    ; need to also change between PROGRAMS64 and PROGRAMS
;--------------------------------

;MultiUser

    !define MULTIUSER_EXECUTIONLEVEL Highest
    !define MULTIUSER_MUI
    !define MULTIUSER_INSTALLMODE_COMMANDLINE
    !define MULTIUSER_INSTALLMODE_INSTDIR "${INSTPATH}"
    !define MULTIUSER_INSTALLMODE_INSTDIR_REGISTRY_KEY "${REGKEY}"
    !define MULTIUSER_INSTALLMODE_INSTDIR_REGISTRY_VALUENAME "InstallPath"
    !define MULTIUSER_INSTALLMODE_DEFAULT_REGISTRY_KEY "${REGKEY}"
    !define MULTIUSER_INSTALLMODE_DEFAULT_REGISTRY_VALUENAME "InstallType"
    !include MultiUser.nsh
    
;--------------------------------

;--------------------------------
;Modern UI 2

    !include "MUI2.nsh"
    !define MUI_ICON "images\dgse_logo.ico"

;--------------------------------

;General

    ;Name and file
    Name "dupeGuru"
    OutFile "DupeGuruInstaller.exe"

;--------------------------------

;Interface Settings

    !define MUI_ABORTWARNING
    !define !define MUI_UNABORTWARNING
    
;--------------------------------
;Pages

    !insertmacro MUI_PAGE_WELCOME
    !insertmacro MUI_PAGE_LICENSE LICENSE
    !insertmacro MULTIUSER_PAGE_INSTALLMODE
    
    !insertmacro MUI_PAGE_DIRECTORY

    !define MUI_STARTMENUPAGE_REGISTRY_ROOT "SHCTX" 
    !define MUI_STARTMENUPAGE_REGISTRY_KEY "${REGKEY}" 
    !define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
    !insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder
    !insertmacro MUI_PAGE_INSTFILES
    !insertmacro MUI_PAGE_FINISH
  
    !insertmacro MUI_UNPAGE_CONFIRM
    !insertmacro MUI_UNPAGE_INSTFILES
  
;--------------------------------
;Languages
 
  !insertmacro MUI_LANGUAGE "English" ;first language is the default language

;--------------------------------

;Reserve Files
 
  ;If you are using solid compression, files that are required before
  ;the actual installation should be stored first in the data block,
  ;because this will make your installer start faster.
 
  !insertmacro MUI_RESERVEFILE_LANGDLL
  ReserveFile /nonfatal "${NSISDIR}\Plugins\*.dll"
 
;--------------------------------

;Installer Sections

Section "DupeGuru" SecDupeGuru

  SetOutPath "$INSTDIR"
  
  ;Files to install
  File /r "build\dupeguru-win64bit\*"
  File "images\dgse_logo.ico" ; image for ?

  ;Store installation folder
  WriteRegStr SHCTX "${REGKEY}" "Path" $INSTDIR

  ;Uninstall Entry
  WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\dupeGuru" \
                 "DisplayName" "dupeGuru"
  WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\dupeGuru" \
                 "UninstallString" "$\"$INSTDIR\uninstall.exe$\" /$MultiUser.InstallMode"
  WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\dupeGuru" "QuietUninstallString" \
                 "$\"$INSTDIR\uninstall.exe$\" /$MultiUser.InstallMode /S"
  ;todo add the rest of the keys needed here
  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    
    ;Create shortcuts
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    CreateShortcut "$SMPROGRAMS\$StartMenuFolder\dupeGuru.lnk" "$INSTDIR\dupeGuru.exe"
    CreateShortcut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  
  !insertmacro MUI_STARTMENU_WRITE_END

SectionEnd

;--------------------------------
;Descriptions


;--------------------------------
;Uninstaller Section

Section "Uninstall"

  ;ADD YOUR OWN FILES HERE...
  !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
  RMDir /r "$SMPROGRAMS\$StartMenuFolder"
  Delete "$INSTDIR\Uninstall.exe"

  RMDir /r "$INSTDIR"
  ; todo delete vendor dir and keys if empty
  DeleteRegKey SHCTX "${REGKEY}"
  DeleteRegKey SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\dupeGuru"

SectionEnd

Function .onInit
  !insertmacro MULTIUSER_INIT
  !insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd

Function un.onInit
  !insertmacro MULTIUSER_UNINIT
  !insertmacro MUI_UNGETLANGUAGE
FunctionEnd