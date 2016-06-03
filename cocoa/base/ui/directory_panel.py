ownerclass = 'DirectoryPanel'
ownerimport = 'DirectoryPanel.h'

result = Window(425, 300, "dupeGuru")
promptLabel = Label(result, "Select folders to scan and press \"Scan\".")
directoryOutline = OutlineView(result)
directoryOutline.OBJC_CLASS = 'HSOutlineView'
scanTypePopup = Popup(result)
scanTypeLabel = Label(result, "Scan Type:")
addButton = Button(result, "")
removeButton = Button(result, "")
loadResultsButton = Button(result, "Load Results")
scanButton = Button(result, "Scan")
addPopup = Popup(None)
loadRecentPopup = Popup(None)

owner.outlineView = directoryOutline
owner.scanTypePopup = scanTypePopup
owner.removeButton = removeButton
owner.loadResultsButton = loadResultsButton
owner.addButtonPopUp = addPopup
owner.loadRecentButtonPopUp = loadRecentPopup

result.autosaveName = 'DirectoryPanel'
result.canMinimize = False
result.minSize = Size(370, 270)
addButton.bezelStyle = removeButton.bezelStyle = const.NSTexturedRoundedBezelStyle
addButton.image = 'NSAddTemplate'
removeButton.image = 'NSRemoveTemplate'
for button in (addButton, removeButton):
    button.style = const.NSTexturedRoundedBezelStyle
    button.imagePosition = const.NSImageOnly
scanButton.keyEquivalent = '\\r'
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

scanTypeLabel.width = 90
scanTypeLayout = HLayout([scanTypeLabel, scanTypePopup], filler=scanTypePopup)

for button in (addButton, removeButton):
    button.width = 28
for button in (loadResultsButton, scanButton):
    button.width = 118

buttonLayout = HLayout([addButton, removeButton, None, loadResultsButton, scanButton])
bottomLayout = VLayout([None, scanTypeLayout, buttonLayout])
promptLabel.packToCorner(Pack.UpperLeft)
promptLabel.fill(Pack.Right)
directoryOutline.packRelativeTo(promptLabel, Pack.Below)
bottomLayout.packRelativeTo(directoryOutline, Pack.Below, margin=8)
directoryOutline.fill(Pack.LowerRight)
bottomLayout.fill(Pack.Right)

promptLabel.setAnchor(Pack.UpperLeft, growX=True)
directoryOutline.setAnchor(Pack.UpperLeft, growX=True, growY=True)
scanTypeLayout.setAnchor(Pack.Below)
buttonLayout.setAnchor(Pack.Below)
