ownerclass = 'HSErrorReportWindow'
ownerimport = 'HSErrorReportWindow.h'

result = Window(524, 390, "Error Report")
result.canClose = False
result.canResize = False
result.canMinimize = False
label1 = Label(result, "Something went wrong. Would you like to send the error report to Hardcoded Software?")
errorTextView = TextView(result)
label2 = Label(result, "Although the application should continue to run after this error, it may be in an instable state, so it is recommended that you restart the application.")
sendButton = Button(result, "Send")
dontSendButton = Button(result, "Don't Send")

owner.contentTextView = errorTextView
sendButton.action = Action(owner, 'send')
sendButton.keyEquivalent = "\\r"
dontSendButton.action = Action(owner, 'dontSend')
dontSendButton.keyEquivalent = "\\E"

label1.height = 34
errorTextView.height = 221
label2.height = 51
sendButton.width = 100
dontSendButton.width = 100

label1.packToCorner(Pack.UpperLeft)
label1.fill(Pack.Right)
errorTextView.packRelativeTo(label1, Pack.Below, Pack.Left)
errorTextView.fill(Pack.Right)
label2.packRelativeTo(errorTextView, Pack.Below, Pack.Left)
label2.fill(Pack.Right)
sendButton.packRelativeTo(label2, Pack.Below, Pack.Right)
dontSendButton.packRelativeTo(sendButton, Pack.Left, Pack.Middle)
