ownerclass = 'DeletionOptions'
ownerimport = 'DeletionOptions.h'

result = Window(450, 240, "Deletion Options")
messageLabel = Label(result, "")
linkCheckbox = Checkbox(result, "Link deleted files")
linkLabel = Label(result, "After having deleted a duplicate, place a link targeting the "
    "reference file to replace the deleted file.")
linkTypeChoice = RadioButtons(result, ["Symlink", "Hardlink"], columns=2)
directCheckbox = Checkbox(result, "Directly delete files")
directLabel = Label(result, "Instead of sending files to trash, delete them directly. This option "
    "is usually used as a workaround when the normal deletion method doesn't work.")
proceedButton = Button(result, "Proceed")
cancelButton = Button(result, "Cancel")

owner.linkButton = linkCheckbox
owner.linkTypeRadio = linkTypeChoice
owner.directButton = directCheckbox
owner.messageTextField = messageLabel

result.canMinimize = False
result.canResize = False
linkLabel.controlSize = ControlSize.Small
directLabel.controlSize = ControlSize.Small
linkTypeChoice.controlSize = ControlSize.Small
proceedButton.keyEquivalent = '\\r'
cancelButton.keyEquivalent = '\\e'
linkCheckbox.action = directCheckbox.action = linkTypeChoice.action = Action(owner, 'updateOptions')
proceedButton.action = Action(owner, 'proceed')
cancelButton.action = Action(owner, 'cancel')

linkLabel.height *= 2 # 2 lines
directLabel.height *= 3 # 3 lines
proceedButton.width = 92
cancelButton.width = 92

mainLayout = VLayout([messageLabel, linkCheckbox, linkLabel, linkTypeChoice, directCheckbox,
    directLabel])
mainLayout.packToCorner(Pack.UpperLeft)
mainLayout.fill(Pack.Right)
buttonLayout = HLayout([cancelButton, proceedButton])
buttonLayout.packToCorner(Pack.LowerRight)

# indent the labels under checkboxes a little bit to the right
for indentedView in (linkLabel, directLabel, linkTypeChoice):
    indentedView.x += 20
    indentedView.width -= 20
# We actually don't want the link choice radio buttons to take all the width, it looks weird.
linkTypeChoice.width = 170
