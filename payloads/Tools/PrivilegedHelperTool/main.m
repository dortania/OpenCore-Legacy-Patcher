/*
    ------------------------------------------------
    OpenCore Legacy Patcher Privileged Helper Tool
    ------------------------------------------------
    Designed as an alternative to an XPC service,
    this tool is used to run commands as root.
    ------------------------------------------------
    Server and client must have the same signing
    certificate in order to run commands.
    ------------------------------------------------
*/

#import <Foundation/Foundation.h>
#import <Security/Security.h>
#include <libproc.h>

#define UTILITY_VERSION "1.0.0"

#define VALID_CLIENT_TEAM_ID @"S74BDJXQMD"

#define OCLP_PHT_ERROR_MISSING_ARGUMENTS           160
#define OCLP_PHT_ERROR_SET_UID_MISSING             161
#define OCLP_PHT_ERROR_SET_UID_FAILED              162
#define OCLP_PHT_ERROR_SELF_PATH_MISSING           163
#define OCLP_PHT_ERROR_PARENT_PATH_MISSING         164
#define OCLP_PHT_ERROR_SIGNING_INFORMATION_MISSING 165
#define OCLP_PHT_ERROR_INVALID_TEAM_ID             166
#define OCLP_PHT_ERROR_INVALID_CERTIFICATES        167
#define OCLP_PHT_ERROR_COMMAND_MISSING             168
#define OCLP_PHT_ERROR_COMMAND_FAILED              169
#define OCLP_PHT_ERROR_CATCH_ALL                   170


NSDictionary *getSigningInformationFromPath(NSString *path) {
    SecStaticCodeRef codeRef;
    OSStatus status = SecStaticCodeCreateWithPath((__bridge CFURLRef)[NSURL fileURLWithPath:path], kSecCSDefaultFlags, &codeRef);
    if (status != errSecSuccess) {
        return nil;
    }

    CFDictionaryRef codeDict = NULL;
    status = SecCodeCopySigningInformation(codeRef, kSecCSSigningInformation, &codeDict);
    if (status != errSecSuccess) {
        return nil;
    }

    return (__bridge NSDictionary *)codeDict;
}

NSString *getParentProcessPath() {
    char pathbuf[PROC_PIDPATHINFO_MAXSIZE];
    if (proc_pidpath(getppid(), pathbuf, sizeof(pathbuf)) <= 0) {
        return nil;
    }
    NSString *path = [NSString stringWithUTF8String:pathbuf];
    return path;
}

NSString *getProcessPath() {
    NSString *path = [[NSBundle mainBundle] executablePath];
    return path;
}

BOOL isSBitSet(NSString *path) {
    NSFileManager *fileManager = [NSFileManager defaultManager];
    NSDictionary *attributes = [fileManager attributesOfItemAtPath:path error:nil];
    if (attributes == nil) {
        return NO;
    }
    return (attributes.filePosixPermissions & S_ISUID) != 0;
}


int main(int argc, const char * argv[]) {
    @autoreleasepool {
        // We simply return if no arguments are passed
        if (argc < 2) {
            return OCLP_PHT_ERROR_MISSING_ARGUMENTS;
        }

        if (argc == 2 && (strcmp(argv[1], "--version") == 0 || strcmp(argv[1], "-v") == 0)) {
            printf("%s\n", UTILITY_VERSION);
            return 0;
        }

        // Verify whether we can run as root
        NSString *processPath = getProcessPath();
        if (processPath == nil) {
            return OCLP_PHT_ERROR_SELF_PATH_MISSING;
        }

        if (!isSBitSet(processPath)) {
            return OCLP_PHT_ERROR_SET_UID_MISSING;
        }

        setuid(0);
        if (getuid() != 0) {
            return OCLP_PHT_ERROR_SET_UID_FAILED;
        }

        NSString *parentProcessPath = getParentProcessPath();
        if (parentProcessPath == nil) {
            return OCLP_PHT_ERROR_PARENT_PATH_MISSING;
        }

        NSDictionary *processSigningInformation = getSigningInformationFromPath(processPath);
        NSDictionary *parentProcessSigningInformation = getSigningInformationFromPath(parentProcessPath);

        if (processSigningInformation == nil || parentProcessSigningInformation == nil) {
            return OCLP_PHT_ERROR_SIGNING_INFORMATION_MISSING;
        }

        #ifdef DEBUG
        // Skip Team ID check in debug mode
        // DO NOT USE IN PRODUCTION
        #else
        // Check Team ID
        if (![processSigningInformation[@"teamid"] isEqualToString:VALID_CLIENT_TEAM_ID] || ![parentProcessSigningInformation[@"teamid"] isEqualToString:VALID_CLIENT_TEAM_ID]) {
            return OCLP_PHT_ERROR_INVALID_TEAM_ID;
        }

        // Check Certificates
        if (![processSigningInformation[@"certificates"] isEqualToArray:parentProcessSigningInformation[@"certificates"]]) {
            return OCLP_PHT_ERROR_INVALID_CERTIFICATES;
        }
        #endif

        NSString *command = nil;
        NSArray *arguments = @[];
        if (argc == 2) {
            command = [NSString stringWithUTF8String:argv[1]];
        } else {
            command = [NSString stringWithUTF8String:argv[1]];
            for (int i = 2; i < argc; i++) {
                arguments = [arguments arrayByAddingObject:[NSString stringWithUTF8String:argv[i]]];
            }
        }

        // Verify command exists
        if (![[NSFileManager defaultManager] fileExistsAtPath:command]) {
            return OCLP_PHT_ERROR_COMMAND_MISSING;
        }

        NSTask *task = [[NSTask alloc] init];
        [task setLaunchPath:command];
        [task setArguments:arguments];
        [task launch];
        [task waitUntilExit];
        return [task terminationStatus];
    }
    return OCLP_PHT_ERROR_CATCH_ALL; // Should never reach here
}