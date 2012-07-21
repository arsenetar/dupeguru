ownerclass = 'DetailsPanel'
ownerimport = 'DetailsPanel.h'

result = Panel(451, 146, "Details of Selected File")
table = TableView(result)

owner.detailsTable = table

result.style = PanelStyle.Utility
result.xProportion = 0.2
result.yProportion = 0.4
result.canMinimize = False
result.autosaveName = 'DetailsPanel'
result.minSize = Size(result.width, result.height)

table.dataSource = owner
table.allowsColumnReordering = False
table.allowsColumnSelection = False
table.allowsMultipleSelection = False
table.font = Font(FontFamily.System, FontSize.SmallSystem)
table.rowHeight = 14
table.editable = False
col = table.addColumn('0', "Attribute", 70)
col.autoResizable = True
col = table.addColumn('1', "Selected", 198)
col.autoResizable = True
col = table.addColumn('2', "Reference", 172)
col.autoResizable = True

table.x = 0
table.y = 0
table.width = result.width
table.height = result.height
table.setAnchor(Pack.UpperLeft, growX=True, growY=True)
