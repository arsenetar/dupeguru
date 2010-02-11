/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>

/* ResultsChangedNotification happens on major changes, which requires a complete reload of the data*/
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