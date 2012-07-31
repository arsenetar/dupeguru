wnerclass = 'ResultWindow'
ownerimport = 'ResultWindow.h'

result = Window(557, 400, "dupeGuru Results")
toolbar = result.createToolbar('ResultsToolbar')
table = TableView(result)
table.OBJC_CLASS = 'HSTableView'
statsLabel = Label(result, "")
contextMenu = Menu("")

#Setup toolbar items
toolbar.displayMode = const.NSToolbarDisplayModeIconOnly
directoriesToolItem = toolbar.addItem('Directories', "Directories", image='folder32')
actionToolItem = toolbar.addItem('Action', "Action")
filterToolItem = toolbar.addItem('Filter', "Filter")
optionsToolItem = toolbar.addItem('Options', "Options")
quicklookToolItem = toolbar.addItem('QuickLook', "Quick Look")
toolbar.defaultItems = [actionToolItem, optionsToolItem, quicklookToolItem, directoriesToolItem,
    toolbar.flexibleSpace(), filterToolItem]
actionPopup = Popup(None)
actionPopup.pullsdown = True
actionPopup.bezelStyle = const.NSTexturedRoundedBezelStyle
actionPopup.arrowPosition = const.NSPopUpArrowAtBottom
item = actionPopup.menu.addItem("") # First item is invisible
item.hidden = True
item.image = 'NSActionTemplate'
actionPopup.width = 44
actionToolItem.view = actionPopup
filterField = SearchField(None, "Filter")
filterField.action = Action(owner, 'filter')
filterField.sendsWholeSearchString = True
filterToolItem.view = filterField
filterToolItem.minSize = Size(80, 22)
filterToolItem.maxSize = Size(300, 22)
quickLookButton = Button(None, "")
quickLookButton.bezelStyle = const.NSTexturedRoundedBezelStyle
quickLookButton.image = 'NSQuickLookTemplate'
quickLookButton.width = 44
quickLookButton.action = Action(owner, 'toggleQuicklookPanel')
quicklookToolItem.view = quickLookButton
optionsSegments = SegmentedControl(None)
optionsSegments.segmentStyle = const.NSSegmentStyleCapsule
optionsSegments.trackingMode = const.NSSegmentSwitchTrackingSelectAny
optionsSegments.font = Font(FontFamily.System, 11)
optionsSegments.addSegment("Details", 57)
optionsSegments.addSegment("Dupes Only", 82)
optionsSegments.addSegment("Delta", 48)
optionsSegments.action = Action(owner, 'changeOptions')
optionsToolItem.view = optionsSegments

# Popuplate menus
actionPopup.menu.addItem("Send Marked to Trash...", action=Action(owner, 'trashMarked'))
actionPopup.menu.addItem("Move Marked to...", action=Action(owner, 'moveMarked'))
actionPopup.menu.addItem("Copy Marked to...", action=Action(owner, 'copyMarked'))
actionPopup.menu.addItem("Remove Marked from Results", action=Action(owner, 'removeMarked'))
actionPopup.menu.addSeparator()
for menu in (actionPopup.menu, contextMenu):
    menu.addItem("Remove Selected from Results", action=Action(owner, 'removeSelected'))
    menu.addItem("Add Selected to Ignore List", action=Action(owner, 'ignoreSelected'))
    menu.addItem("Make Selected Reference", action=Action(owner, 'switchSelected'))
    menu.addSeparator()
    menu.addItem("Open Selected with Default Application", action=Action(owner, 'openSelected'))
    menu.addItem("Reveal Selected in Finder", action=Action(owner, 'revealSelected'))
    menu.addItem("Rename Selected", action=Action(owner, 'renameSelected'))

# Doing connections
owner.filterField = filterField
owner.matches = table
owner.optionsSwitch = optionsSegments
owner.optionsToolbarItem = optionsToolItem
owner.stats = statsLabel
table.bind('rowHeight', defaults, 'values.TableFontSize', valueTransformer='vtRowHeightOffset')

# Rest of the setup
result.minSize = Size(340, 340)
result.autosaveName = 'MainWindow'
statsLabel.alignment = TextAlignment.Center
table.alternatingRows = True
table.menu = contextMenu
table.allowsColumnReordering = True
table.allowsColumnResizing = True
table.allowsColumnSelection = False
table.allowsEmptySelection = False
table.allowsMultipleSelection = True
table.allowsTypeSelect = True
table.gridStyleMask = const.NSTableViewSolidHorizontalGridLineMask
table.setAnchor(Pack.UpperLeft, growX=True, growY=True)
statsLabel.setAnchor(Pack.LowerLeft, growX=True)

# Layout
# It's a little weird to pack with a margin of -1, but if I don't do that, I get too thick of a
# border on the upper side of the table.
table.packToCorner(Pack.UpperLeft, margin=-1)
table.fill(Pack.Right, margin=0)
statsLabel.packRelativeTo(table, Pack.Below, margin=6)
statsLabel.fill(Pack.Right, margin=0)
table.fill(Pack.Below, margin=5)
