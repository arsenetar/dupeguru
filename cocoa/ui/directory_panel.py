ownerclass = 'DirectoryPanel'
ownerimport = 'DirectoryPanel.h'

result = Window(425, 300, "dupeGuru")
promptLabel = Label(result, "Select folders to scan and press \"Scan\".")
directoryOutline = OutlineView(result)
directoryOutline.OBJC_CLASS = 'HSOutlineView'
appModeSelector = SegmentedControl(result)
appModeLabel = Label(result, "Application Mode:")
scanTypePopup = Popup(result)
scanTypeLabel = Label(result, "Scan Type:")
addButton = Button(result, "")
removeButton = Button(result, "")
loadResultsButton = Button(result, "Load Results")
scanButton = Button(result, "Scan")
addPopup = Popup(None)
loadRecentPopup = Popup(None)

owner.outlineView = directoryOutline
owner.appModeSelector = appModeSelector
owner.scanTypePopup = scanTypePopup
owner.removeButton = removeButton
owner.loadResultsButton = loadResultsButton
owner.addButtonPopUp = addPopup
owner.loadRecentButtonPopUp = loadRecentPopup

result.autosaveName = 'DirectoryPanel'
result.canMinimize = False
result.minSize = Size(400, 270)
for label in ["Standard", "Music", "Picture"]:
    appModeSelector.addSegment(label, 80)
addButton.bezelStyle = removeButton.bezelStyle = const.NSTexturedRoundedBezelStyle
addButton.image = 'NSAddTemplate'
removeButton.image = 'NSRemoveTemplate'
for button in (addButton, removeButton):
    button.style = const.NSTexturedRoundedBezelStyle
    button.imagePosition = const.NSImageOnly
scanButton.keyEquivalent = '\\r'
appModeSelector.action = Action(owner, 'changeAppMode:')
addButton.action = Action(owner, 'popupAddDirectoryMenu:')
removeButton.action = Action(owner, 'removeSelectedDirectory')
loadResultsButton.action = Action(owner, 'popupLoadRecentMenu:')
scanButton.action = Action(None, 'startScanning')

directoryOutline.font = Font(FontFamily.System, FontSize.SmallSystem)
col = directoryOutline.addColumn('name', "Name", 100)
col.editable = False
col.autoResizable = True
col = directoryOutline.addColumn('state', "State", 85)
col.editable = True
col.autoResizable = False
col.dataCell = Popup(None, ["Normal", "Reference", "Excluded"])
col.dataCell.controlSize = const.NSSmallControlSize
directoryOutline.allowsColumnReordering = False
directoryOutline.allowsColumnSelection = False
directoryOutline.allowsMultipleSelection = True

appModeLabel.width = scanTypeLabel.width = 110
scanTypePopup.width = 248
appModeLayout = HLayout([appModeLabel, appModeSelector])
scanTypeLayout = HLayout([scanTypeLabel, scanTypePopup])

for button in (addButton, removeButton):
    button.width = 28
for button in (loadResultsButton, scanButton):
    button.width = 118

buttonLayout = HLayout([addButton, removeButton, None, loadResultsButton, scanButton])
mainLayout = VLayout([appModeLayout, scanTypeLayout, promptLabel, directoryOutline, buttonLayout], filler=directoryOutline)
mainLayout.packToCorner(Pack.UpperLeft)
mainLayout.fill(Pack.LowerRight)
directoryOutline.packRelativeTo(promptLabel, Pack.Below)

promptLabel.setAnchor(Pack.UpperLeft, growX=True)
directoryOutline.setAnchor(Pack.UpperLeft, growX=True, growY=True)
buttonLayout.setAnchor(Pack.Below)
