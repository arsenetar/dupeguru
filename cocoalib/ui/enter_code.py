ownerclass = 'HSFairwareReminder'
ownerimport = 'HSFairwareReminder.h'

result = Window(450, 185, "Enter Key")
result.canClose = False
result.canResize = False
result.canMinimize = False
titleLabel = Label(result, "Enter your key")
promptLabel = Label(result, "Type the key you received when you contributed to %@, as well as the e-mail used as a reference for the purchase.")
regkeyLabel = Label(result, "Registration key:")
regkeyField = TextField(result, "")
regemailLabel = Label(result, "Registration e-mail:")
regemailField = TextField(result, "")
contributeButton = Button(result, "Contribute")
cancelButton = Button(result, "Cancel")
submitButton = Button(result, "Submit")

owner.codePromptTextField = promptLabel
owner.codeTextField = regkeyField
owner.emailTextField = regemailField
result.initialFirstResponder = regkeyField

titleLabel.font = Font(FontFamily.Label, FontSize.RegularControl, traits=[FontTrait.Bold])
smallerFont = Font(FontFamily.Label, FontSize.SmallControl)
for control in (promptLabel, regkeyLabel, regemailLabel):
    control.font = smallerFont
regkeyField.usesSingleLineMode = regemailField.usesSingleLineMode = True
contributeButton.action = Action(owner, 'contribute')
cancelButton.action = Action(owner, 'cancelCode')
cancelButton.keyEquivalent = "\\E"
submitButton.action = Action(owner, 'submitCode')
submitButton.keyEquivalent = "\\r"

for button in (contributeButton, cancelButton, submitButton):
    button.width = 100
regkeyLabel.width = 128
regemailLabel.width = 128
promptLabel.height = 32

titleLabel.packToCorner(Pack.UpperLeft)
titleLabel.fill(Pack.Right)
promptLabel.packRelativeTo(titleLabel, Pack.Below, Pack.Left)
promptLabel.fill(Pack.Right)
regkeyField.packRelativeTo(promptLabel, Pack.Below, Pack.Right)
regkeyLabel.packRelativeTo(regkeyField, Pack.Left, Pack.Middle)
regkeyField.fill(Pack.Left)
regemailField.packRelativeTo(regkeyField, Pack.Below, Pack.Right)
regemailLabel.packRelativeTo(regemailField, Pack.Left, Pack.Middle)
regemailField.fill(Pack.Left)
contributeButton.packRelativeTo(regemailLabel, Pack.Below, Pack.Left)
submitButton.packRelativeTo(regemailField, Pack.Below, Pack.Right)
cancelButton.packRelativeTo(submitButton, Pack.Left, Pack.Middle)
