#import <Cocoa/Cocoa.h>

#define DuplicateSelectionChangedNotification @"DuplicateSelectionChangedNotification"
#define ResultsChangedNotification @"ResultsChangedNotification"
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