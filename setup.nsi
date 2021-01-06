;==============================================================================
; dupeGuru Installer Script for Windows via NSIS
;
; When calling makensis use the following:
; makensis /DVERSIONMAJOR=x /DVERSIONMINOR=x /DVERSIONPATCH=x /DBITS=x \
;   /DSOURCEPATH=x
; NOTE:
; If SOURCEPATH is not set it will default to build (uses subdir based on app).
;==============================================================================

; Compression Setting
SetCompressor /SOLID lzma
; General Headers
!include "FileFunc.nsh"

;==============================================================================
; Configuration Defines
;==============================================================================

; Environment Defines
!verbose push
!verbose 4
!ifndef VERSIONMAJOR
  !echo "VERSIONMAJOR is NOT defined"
!endif
!ifndef VERSIONMINOR
  !echo "VERSIONMINOR is NOT defined"
!endif
!ifndef VERSIONPATCH
  !echo "VERSIONPATCH is NOT defined"
!endif
!ifndef BITS
  !echo "BITS is NOT defined"
!endif
!ifndef SOURCEPATH
  !echo "SOURCEPATH is NOT defined"
  !define SOURCEPATH "dist"
!endif
!ifndef VERSIONMAJOR | VERSIONMINOR | VERSIONPATCH | BITS | SOURCEPATH
  !error "Command line Defines missing use /DDEFINE=VALUE to define before script"
!endif
!verbose pop

; Application Specific Defines
!define APPNAME "dupeGuru"
!define COMPANYNAME "Hardcoded Software"
!define DESCRIPTION "dupeGuru is a tool to find duplicate files on your computer."
!define APPLICENSE "LICENSE"           ; License is not in build directory
!define APPICON "images\dgse_logo.ico" ; nor is the icon
!define DISTDIR "dist"
!define HELPURL "https://github.com/arsenetar/dupeguru/issues"
!define UPDATEURL "https://dupeguru.voltaicideas.net/" 
!define ABOUTURL "https://dupeguru.voltaicideas.net/"

; Static Defines
!define UNINSTALLREGBASE "Software\Microsoft\Windows\CurrentVersion\Uninstall"

; Derived Defines
!define BASEREGKEY "Software\${COMPANYNAME}\${APPNAME}" ;without root key
!define VENDORREGKEY "Software\${COMPANYNAME}" ;without root key
!define UNINSTALLREG "${UNINSTALLREGBASE}\${APPNAME}" ;without root key
!define INSTPATH "${COMPANYNAME}\${APPNAME}" ;without programs / appdata

; Global vars
var StartMenuFolder
var InstallSize

;==============================================================================
; Plugin Setup
;==============================================================================

; MultiUser Plugin - Allow single user or all install based on execution level
!define MULTIUSER_EXECUTIONLEVEL Highest
!define MULTIUSER_MUI
!define MULTIUSER_INSTALLMODE_COMMANDLINE
!define MULTIUSER_INSTALLMODE_INSTDIR "${INSTPATH}" ; without programs /appdata
; allow for next run of installer to automatically find install path and type
!define MULTIUSER_INSTALLMODE_INSTDIR_REGISTRY_KEY "${BASEREGKEY}"
!define MULTIUSER_INSTALLMODE_INSTDIR_REGISTRY_VALUENAME "InstallPath"
!define MULTIUSER_INSTALLMODE_DEFAULT_REGISTRY_KEY "${BASEREGKEY}"
!define MULTIUSER_INSTALLMODE_DEFAULT_REGISTRY_VALUENAME "InstallType"
!if ${BITS} == "64"
  !define MULTIUSER_USE_PROGRAMFILES64
!endif
!include MultiUser.nsh
    
; Modern UI 2
!include MUI2.nsh
!define MUI_ICON "${APPICON}"
!define MUI_ABORTWARNING
!define MUI_UNABORTWARNING

;==============================================================================
; NSIS Variables
;==============================================================================

Name "${APPNAME}"
!system 'mkdir "${DISTDIR}"'
OutFile "${DISTDIR}\${APPNAME}_win${BITS}_${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONPATCH}.exe"
Icon "${APPICON}"

;==============================================================================
; Pages
;==============================================================================

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "${APPLICENSE}"
!insertmacro MULTIUSER_PAGE_INSTALLMODE
!insertmacro MUI_PAGE_DIRECTORY

; values for start menu page
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "SHCTX" ; uses shell context 
!define MUI_STARTMENUPAGE_REGISTRY_KEY "${BASEREGKEY}" 
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder

!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
  
;==============================================================================
; Languages
;==============================================================================
 
!insertmacro MUI_LANGUAGE "English" ;first language is the default language
!insertmacro MUI_LANGUAGE "French"
!insertmacro MUI_LANGUAGE "German"
!insertmacro MUI_LANGUAGE "Greek"
!insertmacro MUI_LANGUAGE "Italian"
!insertmacro MUI_LANGUAGE "Korean"
!insertmacro MUI_LANGUAGE "Polish"
!insertmacro MUI_LANGUAGE "Russian"
!insertmacro MUI_LANGUAGE "Spanish"
!insertmacro MUI_LANGUAGE "Ukrainian"
!insertmacro MUI_LANGUAGE "Vietnamese"
!insertmacro MUI_LANGUAGE "Dutch"
!insertmacro MUI_LANGUAGE "Czech"
;!insertmacro MUI_LANGUAGE "Chinese" ; no NSIS builtin support
;!insertmacro MUI_LANGUAGE "Brazilian" ; no NSIS builtin support
;!insertmacro MUI_LANGUAGE "Armenian" ; requires UNICODE

;==============================================================================
; Reserve Files
;==============================================================================
 
; If you are using solid compression, files that are required before
; the actual installation should be stored first in the data block,
; because this will make your installer start faster.
 
!insertmacro MUI_RESERVEFILE_LANGDLL
ReserveFile /nonfatal "${NSISDIR}\Plugins\*.dll" ;reserve if needed
 
;==============================================================================
; Installer Sections
;==============================================================================

Section "!Application" AppSec
  SetOutPath "$INSTDIR" ; set from result of installer pages
  
  ; Files to install
  File /r "${SOURCEPATH}\${APPNAME}-win${BITS}\*"
 
  ; Create Start Menu Items
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    CreateShortcut "$SMPROGRAMS\$StartMenuFolder\${APPNAME}.lnk" "$INSTDIR\${APPNAME}-win${BITS}.exe"
    CreateShortcut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  !insertmacro MUI_STARTMENU_WRITE_END

  ; Store installation folder
  WriteRegStr SHCTX "${BASEREGKEY}" "InstallPath" $INSTDIR
  WriteRegStr SHCTX "${BASEREGKEY}" "InstallType" $MultiUser.InstallMode

  ; get installed size
  Push $R0
  Push $R1
  Push $R2
  ${GetSize} "$INSTDIR" "/S=0K" $R0 $R1 $R2 ; look into locate
  IntFmt $InstallSize "0x%08X" $R0
  Pop $R2
  Pop $R1
  Pop $R0

  ; Uninstall Entry 
  WriteRegStr SHCTX "${UNINSTALLREG}" "DisplayName" "${APPNAME} ${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONPATCH}"
  WriteRegStr SHCTX "${UNINSTALLREG}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONPATCH}"
  WriteRegStr SHCTX "${UNINSTALLREG}" "DisplayIcon" "$INSTDIR\${APPNAME}.exe"
  WriteRegDWORD SHCTX "${UNINSTALLREG}" "VersionMajor" ${VERSIONMAJOR}
  WriteRegDWORD SHCTX "${UNINSTALLREG}" "VersionMinor" ${VERSIONMINOR}
  WriteRegDWORD SHCTX "${UNINSTALLREG}" "VersionPatch" ${VERSIONPATCH}
  WriteRegStr SHCTX "${UNINSTALLREG}" "Comments" "${APPNAME} installer"
  WriteRegStr SHCTX "${UNINSTALLREG}" "InstallLocation" "$INSTDIR"
  WriteRegStr SHCTX "${UNINSTALLREG}" "Publisher" "${COMPANYNAME}"
  WriteRegStr SHCTX "${UNINSTALLREG}" "Contact" "${HELPURL}"
  WriteRegStr SHCTX "${UNINSTALLREG}" "HelpLink" "${HELPURL}"
  WriteRegStr SHCTX "${UNINSTALLREG}" "URLUpdateInfo" "${UPDATEURL}"
  WriteRegStr SHCTX "${UNINSTALLREG}" "URLInfoAbout" "${ABOUTURL}"
  WriteRegDWORD SHCTX "${UNINSTALLREG}" "NoModify" 1
  WriteRegDWORD SHCTX "${UNINSTALLREG}" "NoRepair" 1
  WriteRegDWORD SHCTX "${UNINSTALLREG}" "EstimatedSize" $InstallSize
  WriteRegStr SHCTX "${UNINSTALLREG}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\" /$MultiUser.InstallMode"
  WriteRegStr SHCTX "${UNINSTALLREG}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /$MultiUser.InstallMode /S"

  ; Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

;==============================================================================
; Descriptions
;==============================================================================
; Add descriptions as needed

;==============================================================================
; Uninstaller Sections
;==============================================================================

Section "Uninstall"
  ; Remove Start Menu Folder
  !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
  RMDir /r "$SMPROGRAMS\$StartMenuFolder"

  ; Remove Files & Folders in Install Folder
  RMDir /r "$INSTDIR\core"
  RMDir /r "$INSTDIR\help"
  RMDir /r "$INSTDIR\PyQt5"
  RMDir /r "$INSTDIR\qt"
  RMDir /r "$INSTDIR\locale"
  Delete "$INSTDIR\*.exe"
  Delete "$INSTDIR\*.dll"
  Delete "$INSTDIR\*.pyd"
  Delete "$INSTDIR\*.zip"
  Delete "$INSTDIR\*.manifest"
  
  ; Remove Install Folder if empty
  RMDir "$INSTDIR"

  ; Remove registry keys and vendor keys (if empty)
  DeleteRegKey  SHCTX "${BASEREGKEY}"
  DeleteRegKey /ifempty SHCTX "${VENDORREGKEY}"
  DeleteRegKey SHCTX "${UNINSTALLREG}"
SectionEnd

;==============================================================================
; Functions
;==============================================================================

Function .onInit
  !if ${BITS} == "64"
    SetRegView 64
  !else
    SetRegView 32
  !endif
  !insertmacro MULTIUSER_INIT
  ; it appears that the languages shown may not always be filtered correctly
  !define MUI_LANGDLL_ALLLANGUAGES
  !insertmacro MUI_LANGDLL_DISPLAY 
FunctionEnd

Function un.onInit
  !if ${BITS} == "64"
    SetRegView 64
  !else
    SetRegView 32
  !endif
  !insertmacro MULTIUSER_UNINIT
  !insertmacro MUI_UNGETLANGUAGE
FunctionEnd