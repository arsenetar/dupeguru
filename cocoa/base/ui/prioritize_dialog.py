ownerclass = 'PrioritizeDialog'
ownerimport = 'PrioritizeDialog.h'

result = Window(610, 400, "Re-Prioritize duplicates")
promptLabel = Label(result, "Add criteria to the right box and click OK to send the dupes that "
    "correspond the best to these criteria to their respective group's reference position. Read "
    "the help file for more information.")
split = SplitView(result, 2, vertical=True)
categoryPopup = Popup(split.subviews[0])
criteriaTable = ListView(split.subviews[0])
prioritizationTable = ListView(split.subviews[1])
addButton = Button(split.subviews[1], NLSTR("-->"))
removeButton = Button(split.subviews[1], NLSTR("<--"))
okButton = Button(result, "Ok")
cancelButton = Button(result, "Cancel")

owner.categoryPopUpView = categoryPopup
owner.criteriaTableView = criteriaTable
owner.prioritizationTableView = prioritizationTable

result.canMinimize = False
result.canClose = False
result.minSize = Size(result.width, result.height)
addButton.action = Action(owner.model, 'addSelected')
removeButton.action = Action(owner.model, 'removeSelected')
okButton.action = Action(owner, 'ok')
cancelButton.action = Action(owner, 'cancel')
okButton.keyEquivalent = '\\r'
cancelButton.keyEquivalent = '\\e'

# For layouts to correctly work, subviews need to have the dimensions they'll approximately have
# at runtime.
split.subviews[0].width = 260
split.subviews[0].height = 260
split.subviews[1].width = 340
split.subviews[1].height = 260
promptLabel.height *= 3 # 3 lines

leftLayout = VLayout([categoryPopup, criteriaTable], filler=criteriaTable)
middleLayout = VLayout([addButton, removeButton], width=41)
buttonLayout = HLayout([None, cancelButton, okButton])

#pack split subview 0
leftLayout.fillAll()

#pack split subview 1
prioritizationTable.fillAll()
prioritizationTable.width -= 48
prioritizationTable.moveTo(Pack.Right)
middleLayout.moveNextTo(prioritizationTable, Pack.Left, align=Pack.Middle)

# Main layout
promptLabel.packToCorner(Pack.UpperLeft)
promptLabel.fill(Pack.Right)
split.moveNextTo(promptLabel, Pack.Below)
buttonLayout.moveNextTo(split, Pack.Below)
buttonLayout.fill(Pack.Right)
split.fill(Pack.LowerRight)

promptLabel.setAnchor(Pack.UpperLeft, growX=True)
prioritizationTable.setAnchor(Pack.UpperLeft, growX=True, growY=True)
categoryPopup.setAnchor(Pack.UpperLeft, growX=True)
criteriaTable.setAnchor(Pack.UpperLeft, growX=True, growY=True)
split.setAnchor(Pack.UpperLeft, growX=True, growY=True)
buttonLayout.setAnchor(Pack.Below)
