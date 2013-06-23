ownerclass = 'HSFairwareAboutBox'
ownerimport = 'HSFairwareAboutBox.h'

result = Window(259, 217, "")
result.canResize = False
result.canMinimize = False
image = ImageView(result, "NSApplicationIcon")
titleLabel = Label(result, NLSTR("AppTitle"))
versionLabel = Label(result, NLSTR("AppVersion"))
copyrightLabel = Label(result, NLSTR("AppCopyright"))
registeredLabel = Label(result, "This app is registered, thanks!")
registerButton = Button(result, "Register")

owner.window = result
owner.titleTextField = titleLabel
owner.versionTextField = versionLabel
owner.copyrightTextField = copyrightLabel
owner.registeredTextField = registeredLabel
owner.registerButton = registerButton
for label in (titleLabel, versionLabel, copyrightLabel, registeredLabel):
    label.alignment = const.NSCenterTextAlignment
titleLabel.font = Font(FontFamily.Label, FontSize.RegularControl, traits=[FontTrait.Bold])
for label in (versionLabel, copyrightLabel, registeredLabel):
    label.font = Font(FontFamily.Label, FontSize.SmallControl)
    label.height = 14
registerButton.bezelStyle = const.NSRoundRectBezelStyle
registerButton.action = Action(owner, 'showRegisterDialog')

image.height = 96
image.packToCorner(Pack.UpperLeft)
image.y = result.height - 10 - image.height
image.fill(Pack.Right)
image.setAnchor(Pack.UpperLeft, growX=True)
titleLabel.packRelativeTo(image, Pack.Below, Pack.Left)
titleLabel.fill(Pack.Right)
titleLabel.setAnchor(Pack.UpperLeft, growX=True)
versionLabel.packRelativeTo(titleLabel, Pack.Below, Pack.Left)
versionLabel.fill(Pack.Right)
versionLabel.setAnchor(Pack.UpperLeft, growX=True)
copyrightLabel.packRelativeTo(versionLabel, Pack.Below, Pack.Left)
copyrightLabel.fill(Pack.Right)
copyrightLabel.setAnchor(Pack.UpperLeft, growX=True)
registeredLabel.packRelativeTo(copyrightLabel, Pack.Below, Pack.Left)
registeredLabel.fill(Pack.Right)
registeredLabel.setAnchor(Pack.UpperLeft, growX=True)
registerButton.packRelativeTo(copyrightLabel, Pack.Below, Pack.Middle)
