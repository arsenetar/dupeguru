ownerclass = 'ProgressController'
ownerimport = 'ProgressController.h'

result = Window(323, 143, "Work in progress...")
result.canClose = result.canResize = result.canMinimize = False
descLabel = Label(result, "Work in progress, please wait.")
progress = ProgressIndicator(result)
statusLabel = Label(result, "Status: Working...")
cancelButton = Button(result, "Cancel")

owner.window = result
owner.cancelButton = cancelButton
owner.descText = descLabel
owner.statusText = statusLabel
owner.progressBar = progress
result.properties['delegate'] = owner
statusLabel.font = Font(FontFamily.Label, FontSize.SmallControl)
cancelButton.keyEquivalent = '\\E'
cancelButton.action = Action(owner, 'cancel')

descLabel.packToCorner(Pack.UpperLeft)
descLabel.fill(Pack.Right)
descLabel.setAnchor(Pack.UpperLeft, growX=True)
progress.packRelativeTo(descLabel, Pack.Below, Pack.Left)
progress.fill(Pack.Right)
progress.setAnchor(Pack.UpperLeft, growX=True)
statusLabel.packRelativeTo(progress, Pack.Below, Pack.Left)
statusLabel.fill(Pack.Right)
statusLabel.setAnchor(Pack.UpperLeft, growX=True)
cancelButton.packToCorner(Pack.LowerRight)
cancelButton.setAnchor(Pack.LowerRight)
