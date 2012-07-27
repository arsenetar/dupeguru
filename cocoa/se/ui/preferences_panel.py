result = Window(410, 345, "dupeGuru Preferences")
tabView = TabView(result)
basicTab = tabView.addTab("Basic")
advancedTab = tabView.addTab("Advanced")
scanTypePopup = Popup(basicTab.view, ["Filename", "Content", "Folders"])
scanTypeLabel = Label(basicTab.view, "Scan Type:")
thresholdSlider = Slider(basicTab.view, 1, 100, 80)
# XXX add a number formatter to this
thresholdLabel = Label(basicTab.view, "Filter hardness:")
moreResultsLabel = Label(basicTab.view, "More results")
fewerResultsLabel = Label(basicTab.view, "Fewer results")
thresholdValuelabel = Label(basicTab.view, "")
fontSizeCombo = Combobox(basicTab.view, ["11", "12", "13", "14", "18", "24"])
fontSizeLabel = Label(basicTab.view, "Font Size:")
wordWeightingBox = Checkbox(basicTab.view, "Word weighting")
matchSimilarWordsBox = Checkbox(basicTab.view, "Match similar words")
mixKindBox = Checkbox(basicTab.view, "Can mix file kind")
removeEmptyFoldersBox = Checkbox(basicTab.view, "Remove empty folders on delete or move")
ignoreSmallFilesBox = Checkbox(basicTab.view, "Ignore files smaller than:")
smallFilesThresholdText = TextField(basicTab.view, "")
smallFilesThresholdSuffixLabel = Label(basicTab.view, "KB")
checkForUpdatesBox = Checkbox(basicTab.view, "Automatically check for updates")

regexpCheckbox = Checkbox(advancedTab.view, "Use regular expressions when filtering")
ignoreHardlinksBox = Checkbox(advancedTab.view, "Ignore duplicates hardlinking to the same file")
debugModeCheckbox = Checkbox(advancedTab.view, "Debug mode (restart required)")
customCommandLabel = Label(advancedTab.view, "Custom command (arguments: %d for dupe, %r for ref):")
customCommandText = TextField(advancedTab.view, "")
copyMoveLabel = Label(advancedTab.view, "Copy and Move:")
copyMovePopup = Popup(advancedTab.view, ["Right in destination", "Recreate relative path", "Recreate absolute path"])

resetToDefaultsButton = Button(result, "Reset To Defaults")

scanTypePopup.bind('selectedIndex', defaults, 'values.scanType')
thresholdSlider.bind('value', defaults, 'values.minMatchPercentage')
thresholdValuelabel.bind('value', defaults, 'values.minMatchPercentage')
fontSizeCombo.bind('value', defaults, 'values.TableFontSize')
wordWeightingBox.bind('value', defaults, 'values.wordWeighting')
matchSimilarWordsBox.bind('value', defaults, 'values.matchSimilarWords')
mixKindBox.bind('value', defaults, 'values.mixFileKind')
removeEmptyFoldersBox.bind('value', defaults, 'values.removeEmptyFolders')
ignoreSmallFilesBox.bind('value', defaults, 'values.ignoreSmallFiles')
smallFilesThresholdText.bind('value', defaults, 'values.smallFileThreshold')
checkForUpdatesBox.bind('value', defaults, 'values.SUEnableAutomaticChecks')
regexpCheckbox.bind('value', defaults, 'values.useRegexpFilter')
ignoreHardlinksBox.bind('value', defaults, 'values.ignoreHardlinkMatches')
debugModeCheckbox.bind('value', defaults, 'values.DebugMode')
customCommandText.bind('value', defaults, 'values.CustomCommand')
copyMovePopup.bind('selectedIndex', defaults, 'values.recreatePathType')
disableWhenContentScan = [thresholdSlider, wordWeightingBox, matchSimilarWordsBox]
for control in disableWhenContentScan:
    control.bind('enabled', defaults, 'values.scanType', valueTransformer='vtScanTypeIsNotContent')

result.canResize = False
result.canMinimize = False
allLabels = [scanTypeLabel, thresholdValuelabel, moreResultsLabel, fewerResultsLabel,
    thresholdLabel, fontSizeLabel, smallFilesThresholdSuffixLabel, customCommandLabel,
    copyMoveLabel]
for label in allLabels:
    label.controlSize = ControlSize.Small
fewerResultsLabel.alignment = TextAlignment.Right
allCheckboxes = [wordWeightingBox, matchSimilarWordsBox, mixKindBox, removeEmptyFoldersBox,
    ignoreSmallFilesBox, checkForUpdatesBox, regexpCheckbox, ignoreHardlinksBox, debugModeCheckbox]
for checkbox in allCheckboxes:
    checkbox.font = scanTypeLabel.font
resetToDefaultsButton.action = Action(defaults, 'revertToInitialValues:')

scanTypeLabel.width = thresholdLabel.width = fontSizeLabel.width = 94
fontSizeCombo.width = 66
thresholdValuelabel.width = 25
resetToDefaultsButton.width = 136
smallFilesThresholdText.width = 60
smallFilesThresholdSuffixLabel.width = 40

tabView.packToCorner(Pack.UpperLeft)
tabView.fill(Pack.Right)
resetToDefaultsButton.packRelativeTo(tabView, Pack.Below, align=Pack.Right)
tabView.fill(Pack.Below, margin=14)
tabView.setAnchor(Pack.UpperLeft, growX=True, growY=True)
scanTypePopup.packToCorner(Pack.UpperRight)
scanTypeLabel.packRelativeTo(scanTypePopup, Pack.Left)
scanTypePopup.fill(Pack.Left)
thresholdSlider.packRelativeTo(scanTypePopup, Pack.Below)
thresholdValuelabel.packRelativeTo(thresholdSlider, Pack.Right)
thresholdSlider.fill(Pack.Right)
# We want to give the labels as much space as possible, and we only "know" how much is available
# after the slider's fill operation.
moreResultsLabel.width = fewerResultsLabel.width = thresholdSlider.width // 2
moreResultsLabel.packRelativeTo(thresholdSlider, Pack.Below, align=Pack.Left, margin=6)
fewerResultsLabel.packRelativeTo(thresholdSlider, Pack.Below, align=Pack.Right, margin=6)
thresholdLabel.packRelativeTo(thresholdSlider, Pack.Left)
fontSizeCombo.packRelativeTo(moreResultsLabel, Pack.Below)
fontSizeLabel.packRelativeTo(fontSizeCombo, Pack.Left)

checkboxLayout = VLayout([wordWeightingBox, matchSimilarWordsBox, mixKindBox, removeEmptyFoldersBox,
    ignoreSmallFilesBox])
checkboxLayout.packRelativeTo(fontSizeCombo, Pack.Below)
checkboxLayout.fill(Pack.Left)
checkboxLayout.fill(Pack.Right)

smallFilesThresholdText.packRelativeTo(ignoreSmallFilesBox, Pack.Below, margin=4)
checkForUpdatesBox.packRelativeTo(smallFilesThresholdText, Pack.Below, margin=4)
checkForUpdatesBox.fill(Pack.Right)
smallFilesThresholdText.x += 20
smallFilesThresholdSuffixLabel.packRelativeTo(smallFilesThresholdText, Pack.Right)

advancedLayout = VLayout(advancedTab.view.subviews[:])
advancedLayout.packToCorner(Pack.UpperLeft)
advancedLayout.fill(Pack.Right)
