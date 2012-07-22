ownerclass = 'IgnoreListDialog'
ownerimport = 'IgnoreListDialog.h'

result = Window(550, 350, "Ignore List")
table = TableView(result)
removeSelectedButton = Button(result, "Remove Selected")
clearButton = Button(result, "Clear")
closeButton = Button(result, "Close")

owner.ignoreListTableView = table

result.canMinimize = False
removeSelectedButton.action = Action(owner.model, 'removeSelected')
clearButton.action = Action(owner.model, 'clear')
closeButton.action = Action(result, 'performClose:')
closeButton.keyEquivalent = '\\r'
table.allowsColumnReordering = False
table.allowsColumnSelection = False
table.allowsMultipleSelection = True

removeSelectedButton.width = 142
clearButton.width = 142
closeButton.width = 84
buttonLayout = HLayout(left=[removeSelectedButton, clearButton], right=[closeButton])
buttonLayout.packToCorner(Pack.LowerLeft)
buttonLayout.fill(Pack.Right)
buttonLayout.setAnchor(Pack.Below)
table.packRelativeTo(buttonLayout, Pack.Above)
table.fill(Pack.UpperRight)
table.setAnchor(Pack.UpperLeft, growX=True, growY=True)
