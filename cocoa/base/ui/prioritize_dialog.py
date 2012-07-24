ownerclass = 'PrioritizeDialog'
ownerimport = 'PrioritizeDialog.h'

result = Window(610, 400, "Re-Prioritize duplicates")
promptLabel = Label(result, "Add criteria to the right box and click OK to send the dupes that "
    "correspond the best to these criteria to their respective group's reference position. Read "
    "the help file for more information.")
categoryPopup = Popup(result)
criteriaTable = ListView(result)
prioritizationTable = ListView(result)
addButton = Button(result, "-->")
removeButton = Button(result, "<--")
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

promptLabel.height *= 3 # 3 lines

leftLayout = VLayout([categoryPopup, criteriaTable], width=262, filler=criteriaTable)
middleLayout = VLayout([addButton, removeButton], width=41)
buttonLayout = HLayout([None, cancelButton, okButton])

promptLabel.packToCorner(Pack.UpperLeft)
promptLabel.fill(Pack.Right)
leftLayout.packRelativeTo(promptLabel, Pack.Below)
middleLayout.packRelativeTo(leftLayout, Pack.Right, align=Pack.Above)
prioritizationTable.packRelativeTo(middleLayout, Pack.Right, align=Pack.Above)
buttonLayout.packRelativeTo(leftLayout, Pack.Below)
buttonLayout.fill(Pack.Right)
leftLayout.fill(Pack.Below)
middleLayout.packRelativeTo(leftLayout, Pack.Right, align=Pack.Middle)
prioritizationTable.fill(Pack.Below, goal=leftLayout.y)
prioritizationTable.fill(Pack.Right)

promptLabel.setAnchor(Pack.UpperLeft, growX=True)
prioritizationTable.setAnchor(Pack.UpperLeft, growX=True, growY=True)
buttonLayout.setAnchor(Pack.Below)
