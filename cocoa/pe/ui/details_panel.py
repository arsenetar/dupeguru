ownerclass = 'DetailsPanelPE'
ownerimport = 'DetailsPanelPE.h'

result = Panel(593, 398, "Details of Selected File")
table = TableView(result)
split = SplitView(result, 2, vertical=True)
leftSplit, rightSplit = split.subviews
selectedLabel = Label(leftSplit, "Selected")
selectedImage = ImageView(leftSplit, 'NSApplicationIcon')
leftSpinner = ProgressIndicator(leftSplit)
referenceLabel = Label(rightSplit, "Reference")
referenceImage = ImageView(rightSplit, 'NSApplicationIcon')
rightSpinner = ProgressIndicator(rightSplit)

owner.detailsTable = table
owner.dupeImage = selectedImage
owner.dupeProgressIndicator = leftSpinner
owner.refImage = referenceImage
owner.refProgressIndicator = rightSpinner
table.dataSource = owner

result.style = PanelStyle.Utility
result.xProportion = 0.6
result.yProportion = 0.6
result.canMinimize = False
result.autosaveName = 'DetailsPanel'
result.minSize = Size(451, 240)

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
table.height = 165

sides = [
    (leftSplit, selectedLabel, selectedImage, leftSpinner),
    (rightSplit, referenceLabel, referenceImage, rightSpinner),
]
for subSplit, label, image, spinner in sides:
    label.alignment = TextAlignment.Center
    spinner.style = const.NSProgressIndicatorSpinningStyle
    spinner.controlSize = const.NSSmallControlSize
    spinner.displayedWhenStopped = False
    
    label.packToCorner(Pack.UpperLeft, margin=0)
    label.fill(Pack.Right, margin=0)
    label.setAnchor(Pack.UpperLeft, growX=True)
    image.packRelativeTo(label, Pack.Below)
    image.fill(Pack.LowerRight, margin=0)
    image.setAnchor(Pack.UpperLeft, growX=True, growY=True)
    spinner.y = label.y
    spinner.x = subSplit.width - 30
    spinner.setAnchor(Pack.UpperRight)

table.packToCorner(Pack.UpperLeft, margin=0)
table.fill(Pack.Right, margin=0)
table.setAnchor(Pack.UpperLeft, growX=True)

split.packRelativeTo(table, Pack.Below)
split.fill(Pack.LowerRight, margin=0)
split.setAnchor(Pack.UpperLeft, growX=True, growY=True)

