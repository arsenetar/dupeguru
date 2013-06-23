ownerclass = 'HSFairwareReminder'
ownerimport = 'HSFairwareReminder.h'

result = Window(528, 253, "%@ is Fairware")
result.canClose = False
result.canResize = False
result.canMinimize = False
demoPromptLabel = Label(result, NLSTR("<demo prompt>"))
tryButton = Button(result, "Try")
enterKeyButton = Button(result, "Enter Key")
buyButton = Button(result, "Buy")
fairwareButton = Button(result, "Fairware?")

owner.demoPromptTextField = demoPromptLabel
result.initialFirstResponder = tryButton
demoPromptLabel.font = Font(FontFamily.Label, FontSize.SmallControl)
tryButton.action = Action(owner, 'closeDialog')
tryButton.keyEquivalent = "\\r"
enterKeyButton.action = Action(owner, 'showEnterCode')
buyButton.action = Action(owner, 'buy')
fairwareButton.action = Action(owner, 'moreInfo')

for button in (tryButton, enterKeyButton, buyButton, fairwareButton):
    button.width = 113
demoPromptLabel.height = 185

demoPromptLabel.packToCorner(Pack.UpperLeft)
demoPromptLabel.fill(Pack.Right)
tryButton.packRelativeTo(demoPromptLabel, Pack.Below, Pack.Left)
enterKeyButton.packRelativeTo(tryButton, Pack.Right, Pack.Middle)
buyButton.packRelativeTo(enterKeyButton, Pack.Right, Pack.Middle)
fairwareButton.packRelativeTo(buyButton, Pack.Right, Pack.Middle)
