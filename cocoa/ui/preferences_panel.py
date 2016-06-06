appmode = args.get('appmode', 'standard')
dialogHeights = {
    'standard': 325,
    'music': 345,
    'picture': 255,
}

result = Window(410, dialogHeights[appmode], "dupeGuru Preferences")
tabView = TabView(result)
basicTab = tabView.addTab("Basic")
advancedTab = tabView.addTab("Advanced")
thresholdSlider = Slider(basicTab.view, 1, 100, 80)
thresholdLabel = Label(basicTab.view, "Filter hardness:")
moreResultsLabel = Label(basicTab.view, "More results")
fewerResultsLabel = Label(basicTab.view, "Fewer results")
thresholdValueLabel = Label(basicTab.view, "")
fontSizeCombo = Combobox(basicTab.view, ["11", "12", "13", "14", "18", "24"])
fontSizeLabel = Label(basicTab.view, "Font Size:")
if appmode in ('standard', 'music'):
    wordWeightingBox = Checkbox(basicTab.view, "Word weighting")
    matchSimilarWordsBox = Checkbox(basicTab.view, "Match similar words")
elif appmode == 'picture':
    matchDifferentDimensionsBox = Checkbox(basicTab.view, "Match pictures of different dimensions")
mixKindBox = Checkbox(basicTab.view, "Can mix file kind")
removeEmptyFoldersBox = Checkbox(basicTab.view, "Remove empty folders on delete or move")
checkForUpdatesBox = Checkbox(basicTab.view, "Automatically check for updates")
if appmode == 'standard':
    ignoreSmallFilesBox = Checkbox(basicTab.view, "Ignore files smaller than:")
    smallFilesThresholdText = TextField(basicTab.view, "")
    smallFilesThresholdSuffixLabel = Label(basicTab.view, "KB")
elif appmode == 'music':
    tagsToScanLabel = Label(basicTab.view, "Tags to scan:")
    trackBox = Checkbox(basicTab.view, "Track")
    artistBox = Checkbox(basicTab.view, "Artist")
    albumBox = Checkbox(basicTab.view, "Album")
    titleBox = Checkbox(basicTab.view, "Title")
    genreBox = Checkbox(basicTab.view, "Genre")
    yearBox = Checkbox(basicTab.view, "Year")
    tagBoxes = [trackBox, artistBox, albumBox, titleBox, genreBox, yearBox]

regexpCheckbox = Checkbox(advancedTab.view, "Use regular expressions when filtering")
ignoreHardlinksBox = Checkbox(advancedTab.view, "Ignore duplicates hardlinking to the same file")
debugModeCheckbox = Checkbox(advancedTab.view, "Debug mode (restart required)")
customCommandLabel = Label(advancedTab.view, "Custom command (arguments: %d for dupe, %r for ref):")
customCommandText = TextField(advancedTab.view, "")
copyMoveLabel = Label(advancedTab.view, "Copy and Move:")
copyMovePopup = Popup(advancedTab.view, ["Right in destination", "Recreate relative path", "Recreate absolute path"])

resetToDefaultsButton = Button(result, "Reset To Defaults")
thresholdSlider.bind('value', defaults, 'values.minMatchPercentage')
thresholdValueLabel.bind('value', defaults, 'values.minMatchPercentage')
fontSizeCombo.bind('value', defaults, 'values.TableFontSize')
mixKindBox.bind('value', defaults, 'values.mixFileKind')
removeEmptyFoldersBox.bind('value', defaults, 'values.removeEmptyFolders')
checkForUpdatesBox.bind('value', defaults, 'values.SUEnableAutomaticChecks')
regexpCheckbox.bind('value', defaults, 'values.useRegexpFilter')
ignoreHardlinksBox.bind('value', defaults, 'values.ignoreHardlinkMatches')
debugModeCheckbox.bind('value', defaults, 'values.DebugMode')
customCommandText.bind('value', defaults, 'values.CustomCommand')
copyMovePopup.bind('selectedIndex', defaults, 'values.recreatePathType')
if appmode in ('standard', 'music'):
    wordWeightingBox.bind('value', defaults, 'values.wordWeighting')
    matchSimilarWordsBox.bind('value', defaults, 'values.matchSimilarWords')
    disableWhenContentScan = [thresholdSlider, wordWeightingBox, matchSimilarWordsBox]
    for control in disableWhenContentScan:
        vtname = 'vtScanTypeMusicIsNotContent' if appmode == 'music' else 'vtScanTypeIsNotContent'
        prefname = 'values.scanTypeMusic' if appmode == 'music' else 'values.scanTypeStandard'
        control.bind('enabled', defaults, prefname, valueTransformer=vtname)
    if appmode == 'standard':
        ignoreSmallFilesBox.bind('value', defaults, 'values.ignoreSmallFiles')
        smallFilesThresholdText.bind('value', defaults, 'values.smallFileThreshold')
    elif appmode == 'music':
        for box in tagBoxes:
            box.bind('enabled', defaults, 'values.scanTypeMusic', valueTransformer='vtScanTypeIsTag')
        trackBox.bind('value', defaults, 'values.scanTagTrack')
        artistBox.bind('value', defaults, 'values.scanTagArtist')
        albumBox.bind('value', defaults, 'values.scanTagAlbum')
        titleBox.bind('value', defaults, 'values.scanTagTitle')
        genreBox.bind('value', defaults, 'values.scanTagGenre')
        yearBox.bind('value', defaults, 'values.scanTagYear')
elif appmode == 'picture':
    matchDifferentDimensionsBox.bind('value', defaults, 'values.matchScaled')
    thresholdSlider.bind('enabled', defaults, 'values.scanTypePicture', valueTransformer='vtScanTypeIsFuzzy')

result.canResize = False
result.canMinimize = False
thresholdValueLabel.formatter = NumberFormatter(NumberStyle.Decimal)
thresholdValueLabel.formatter.maximumFractionDigits = 0
allLabels = [thresholdValueLabel, moreResultsLabel, fewerResultsLabel,
    thresholdLabel, fontSizeLabel, customCommandLabel, copyMoveLabel]
allCheckboxes = [mixKindBox, removeEmptyFoldersBox, checkForUpdatesBox, regexpCheckbox,
    ignoreHardlinksBox, debugModeCheckbox]
if appmode == 'standard':
    allLabels += [smallFilesThresholdSuffixLabel]
    allCheckboxes += [ignoreSmallFilesBox, wordWeightingBox, matchSimilarWordsBox]
elif appmode == 'music':
    allLabels += [tagsToScanLabel]
    allCheckboxes += tagBoxes + [wordWeightingBox, matchSimilarWordsBox]
elif appmode == 'picture':
    allCheckboxes += [matchDifferentDimensionsBox]
for label in allLabels:
    label.controlSize = ControlSize.Small
fewerResultsLabel.alignment = TextAlignment.Right
for checkbox in allCheckboxes:
    checkbox.font = thresholdValueLabel.font
resetToDefaultsButton.action = Action(defaults, 'revertToInitialValues:')

thresholdLabel.width = fontSizeLabel.width = 94
fontSizeCombo.width = 66
thresholdValueLabel.width = 25
resetToDefaultsButton.width = 136
if appmode == 'standard':
    smallFilesThresholdText.width = 60
    smallFilesThresholdSuffixLabel.width = 40
elif appmode == 'music':
    for box in tagBoxes:
        box.width = 70

tabView.packToCorner(Pack.UpperLeft)
tabView.fill(Pack.Right)
resetToDefaultsButton.packRelativeTo(tabView, Pack.Below, align=Pack.Right)
tabView.fill(Pack.Below, margin=14)
tabView.setAnchor(Pack.UpperLeft, growX=True, growY=True)
thresholdLayout = HLayout([thresholdLabel, thresholdSlider, thresholdValueLabel], filler=thresholdSlider)
thresholdLayout.packToCorner(Pack.UpperLeft)
thresholdLayout.fill(Pack.Right)
# We want to give the labels as much space as possible, and we only "know" how much is available
# after the slider's fill operation.
moreResultsLabel.width = fewerResultsLabel.width = thresholdSlider.width // 2
moreResultsLabel.packRelativeTo(thresholdSlider, Pack.Below, align=Pack.Left, margin=6)
fewerResultsLabel.packRelativeTo(thresholdSlider, Pack.Below, align=Pack.Right, margin=6)
fontSizeCombo.packRelativeTo(moreResultsLabel, Pack.Below)
fontSizeLabel.packRelativeTo(fontSizeCombo, Pack.Left)

if appmode == 'music':
    tagsToScanLabel.packRelativeTo(fontSizeCombo, Pack.Below)
    tagsToScanLabel.fill(Pack.Left)
    tagsToScanLabel.fill(Pack.Right)
    trackBox.packRelativeTo(tagsToScanLabel, Pack.Below)
    trackBox.x += 10
    artistBox.packRelativeTo(trackBox, Pack.Right)
    albumBox.packRelativeTo(artistBox, Pack.Right)
    titleBox.packRelativeTo(trackBox, Pack.Below)
    genreBox.packRelativeTo(titleBox, Pack.Right)
    yearBox.packRelativeTo(genreBox, Pack.Right)
    viewToPackCheckboxesUnder = titleBox
else:
    viewToPackCheckboxesUnder = fontSizeCombo

if appmode == 'standard':
    checkboxesToLayout = [wordWeightingBox, matchSimilarWordsBox, mixKindBox, removeEmptyFoldersBox,
        ignoreSmallFilesBox]
elif appmode == 'music':
    checkboxesToLayout = [wordWeightingBox, matchSimilarWordsBox, mixKindBox, removeEmptyFoldersBox,
        checkForUpdatesBox]
elif appmode == 'picture':
    checkboxesToLayout = [matchDifferentDimensionsBox, mixKindBox, removeEmptyFoldersBox,
        checkForUpdatesBox]
checkboxLayout = VLayout(checkboxesToLayout)
checkboxLayout.packRelativeTo(viewToPackCheckboxesUnder, Pack.Below)
checkboxLayout.fill(Pack.Left)
checkboxLayout.fill(Pack.Right)

if appmode == 'standard':
    smallFilesThresholdText.packRelativeTo(ignoreSmallFilesBox, Pack.Below, margin=4)
    checkForUpdatesBox.packRelativeTo(smallFilesThresholdText, Pack.Below, margin=4)
    checkForUpdatesBox.fill(Pack.Right)
    smallFilesThresholdText.x += 20
    smallFilesThresholdSuffixLabel.packRelativeTo(smallFilesThresholdText, Pack.Right)

advancedLayout = VLayout(advancedTab.view.subviews[:])
advancedLayout.packToCorner(Pack.UpperLeft)
advancedLayout.fill(Pack.Right)
