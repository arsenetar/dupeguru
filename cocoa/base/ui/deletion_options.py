ownerclass = 'DeletionOptions'
ownerimport = 'DeletionOptions.h'

result = Window(450, 215, "Deletion Options")
messageLabel = Label(result, "")
hardlinkCheckbox = Checkbox(result, "Hardlink deleted files")
hardlinkLabel = Label(result, "After having deleted a duplicate, place a hardlink targeting the "
    "reference file to replace the deleted file.")
directCheckbox = Checkbox(result, "Directly delete files")
directLabel = Label(result, "Instead of sending files to trash, delete them directly. This option "
    "is usually used as a workaround when the normal deletion method doesn't work.")
proceedButton = Button(result, "Proceed")
cancelButton = Button(result, "Cancel")

owner.hardlinkButton = hardlinkCheckbox
owner.directButton = directCheckbox
owner.messageTextField = messageLabel

result.canMinimize = False
result.canResize = False
hardlinkLabel.controlSize = const.NSSmallControlSize
directLabel.controlSize = const.NSSmallControlSize
proceedButton.keyEquivalent = '\\r'
cancelButton.keyEquivalent = '\\e'
hardlinkCheckbox.action = directCheckbox.action = Action(owner, 'updateOptions')
proceedButton.action = Action(owner, 'proceed')
cancelButton.action = Action(owner, 'cancel')

hardlinkLabel.height *= 2 # 2 lines
directLabel.height *= 3 # 3 lines
proceedButton.width = 92
cancelButton.width = 92

messageLabel.packToCorner(Pack.UpperLeft)
hardlinkCheckbox.packRelativeTo(messageLabel, Pack.Below)
hardlinkLabel.packRelativeTo(hardlinkCheckbox, Pack.Below)
directCheckbox.packRelativeTo(hardlinkLabel, Pack.Below)
directLabel.packRelativeTo(directCheckbox, Pack.Below)
for view in (messageLabel, hardlinkCheckbox, hardlinkLabel, directCheckbox, directLabel):
    view.fill(Pack.Right)
proceedButton.packToCorner(Pack.LowerRight)
cancelButton.packRelativeTo(proceedButton, Pack.Left)

# indent the labels under checkboxes a little bit to the right
for label in (hardlinkLabel, directLabel):
    label.x += 20
    label.width -= 20
