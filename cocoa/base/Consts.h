/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>

#define DuplicateSelectionChangedNotification @"DuplicateSelectionChangedNotification"
/* ResultsChangedNotification happens on major changes, which requires a complete reload of the data*/
#define ResultsChangedNotification @"ResultsChangedNotification"
/* ResultsChangedNotification happens on minor changes, which requires buffer flush*/
#define ResultsUpdatedNotification @"ResultsUpdatedNotification"
#define ResultsMarkingChangedNotification @"ResultsMarkingChangedNotification"
#define RegistrationRequired @"RegistrationRequired"
#define JobStarted @"JobStarted"
#define JobInProgress @"JobInProgress"

#define jobLoad @"job_load"
#define jobScan @"job_scan"
#define jobCopy @"job_copy"
#define jobMove @"job_move"
#define jobDelete @"job_delete"

#define DEMO_MAX_ACTION_COUNT 10
#define LIMIT_DESC @"In the demo version, only 10 duplicates per session can be sent to Trash, moved or copied."