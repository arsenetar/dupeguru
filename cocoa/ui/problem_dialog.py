ownerclass = 'ProblemDialog'
ownerimport = 'ProblemDialog.h'

result = Window(480, 310, "Problems!")
messageLabel = Label(result, "There were problems processing some (or all) of the files. The cause "
    "of these problems are described in the table below. Those files were not removed from your "
    "results.")
problemTable = TableView(result)
revealButton = Button(result, "Reveal")
closeButton = Button(result, "Close")

owner.problemTableView = problemTable

result.canMinimize = False
result.minSize = Size(300, 300)
closeButton.keyEquivalent = '\\r'
revealButton.action = Action(owner.model, 'revealSelected')
closeButton.action = Action(result, 'performClose:')

messageLabel.height *= 3 # 3 lines
revealButton.width = 150
closeButton.width = 98

messageLabel.packToCorner(Pack.UpperLeft)
messageLabel.fill(Pack.Right)
problemTable.packRelativeTo(messageLabel, Pack.Below)
problemTable.fill(Pack.Right)
revealButton.packRelativeTo(problemTable, Pack.Below)
closeButton.packRelativeTo(problemTable, Pack.Below, align=Pack.Right)
problemTable.fill(Pack.Below)

messageLabel.setAnchor(Pack.UpperLeft, growX=True)
problemTable.setAnchor(Pack.UpperLeft, growX=True, growY=True)
revealButton.setAnchor(Pack.LowerLeft)
closeButton.setAnchor(Pack.LowerRight)
