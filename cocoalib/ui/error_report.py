ownerclass = 'HSErrorReportWindow'
ownerimport = 'HSErrorReportWindow.h'

result = Window(524, 470, "Error Report")
result.canClose = False
result.canResize = False
result.canMinimize = False
label1 = Label(result, "Something went wrong. How about reporting the error?")
errorTextView = TextView(result)
label2 = Label(result,
    "Error reports should be reported as Github issues. You can copy the error traceback "
    "above and paste it in a new issue (bonus point if you run a search to make sure the "
    "issue doesn't already exist). What usually really helps is if you add a description "
    "of how you got the error. Thanks!"
    "\n\n"
    "Although the application should continue to run after this error, it may be in an "
    "unstable state, so it is recommended that you restart the application."
)
sendButton = Button(result, "Go to Github")
dontSendButton = Button(result, "Close")

owner.contentTextView = errorTextView
sendButton.action = Action(owner, 'goToGithub')
sendButton.keyEquivalent = "\\r"
dontSendButton.action = Action(owner, 'close')
dontSendButton.keyEquivalent = "\\E"

label1.height = 34
errorTextView.height = 221
label2.height = 130
sendButton.width = 100
dontSendButton.width = 100

label1.moveTo(Pack.UpperLeft)
label1.fill(Pack.Right)
errorTextView.moveNextTo(label1, Pack.Below, Pack.Left)
errorTextView.fill(Pack.Right)
label2.moveNextTo(errorTextView, Pack.Below, Pack.Left)
label2.fill(Pack.Right)
sendButton.moveNextTo(label2, Pack.Below, Pack.Right)
dontSendButton.moveNextTo(sendButton, Pack.Left, Pack.Middle)
