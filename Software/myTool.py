import argparse
import Chameleon
import sys
import datetime

# From Device.py
COMMAND_VERSION = "VERSION"
COMMAND_UPLOAD = "UPLOAD"
COMMAND_DOWNLOAD = "DOWNLOAD"
COMMAND_SETTING = "SETTING"
COMMAND_UID = "UID"
COMMAND_GETUID = "GETUID"
COMMAND_IDENTIFY = "IDENTIFY"
COMMAND_DUMPMFU = "DUMP_MFU"
COMMAND_CONFIG = "CONFIG"
COMMAND_LOG_DOWNLOAD = "LOGDOWNLOAD"
COMMAND_LOG_CLEAR = "LOGCLEAR"
COMMAND_LOGMODE = "LOGMODE"
COMMAND_LBUTTON = "LBUTTON"
COMMAND_LBUTTONLONG = "LBUTTON_LONG"
COMMAND_RBUTTON = "RBUTTON"
COMMAND_RBUTTONLONG = "RBUTTON_LONG"
COMMAND_GREEN_LED = "LEDGREEN"
COMMAND_RED_LED = "LEDRED"
COMMAND_THRESHOLD = "THRESHOLD"
COMMAND_UPGRADE = "upgrade"

STATUS_CODE_OK = 100
STATUS_CODE_OK_WITH_TEXT = 101
STATUS_CODE_WAITING_FOR_XMODEM = 110
STATUS_CODE_FALSE = 120
STATUS_CODE_TRUE = 121
STATUS_CODE_UNKNOWN_COMMAND = 200
STATUS_CODE_UNKNOWN_COMMAND_USAGE = 201
STATUS_CODE_INVALID_PARAMETER = 202

STATUS_CODES_SUCCESS = [
    STATUS_CODE_OK,
    STATUS_CODE_OK_WITH_TEXT,
    STATUS_CODE_WAITING_FOR_XMODEM,
    STATUS_CODE_FALSE,
    STATUS_CODE_TRUE
]

STATUS_CODES_FAILURE = [
    STATUS_CODE_UNKNOWN_COMMAND,
    STATUS_CODE_UNKNOWN_COMMAND_USAGE,
    STATUS_CODE_INVALID_PARAMETER
]

LINE_ENDING = "\r"
SUGGEST_CHAR = "?"
SET_CHAR = "="
GET_CHAR = "?"

# Chameleon Variables
#verboseFunc = verboseLog
verboseFunc = None
PORT = '/dev/ttyACM0'

# Instantiate device object and connect
CHAMELEON = Chameleon.Device(verboseFunc)

# Measurement in seconds
DEFAULT_SERIAL_TIMEOUT = CHAMELEON.serial.timeout

# Custom const variables
MY_LOG = True   # Enable custom logging


def verboseLog(text):
    formatString = "[{}] {}"
    timeString = datetime.datetime.utcnow()
    print(formatString.format(timeString, text), sys.stderr)

def myLog(text):
    if (MY_LOG):
        print(text)
    

# From Device.py line 154
def readResponse():
    # Read response to command, if any
    response = CHAMELEON.serial.readline().decode('ascii').rstrip()
    CHAMELEON.verboseLog("Response: {}".format(response))
    return response

# From Device.py line 126
def writeCmd(cmd):
    # Execute command
    cmdLine = cmd + LINE_ENDING
    CHAMELEON.serial.write(cmdLine.encode('ascii'))

    # Get status response
    status = CHAMELEON.serial.readline().decode('ascii').rstrip()
    myLog('[{}] status: {}'.format(cmd, status))

    if (len(status) == 0):
        CHAMELEON.verboseLog("Executing <{}>: Timeout".format(cmd))
        return None
    else:
        CHAMELEON.verboseLog("Executing <{}>: {}".format(cmd, status))

    statusCode, statusText = status.split(":")
    statusCode = int(statusCode)

    result = {'statusCode': statusCode, 'statusText': statusText, 'response': None}

    if (statusCode == STATUS_CODE_OK_WITH_TEXT):
        result['response'] =  readResponse()
    elif (statusCode == STATUS_CODE_TRUE):
        result['response'] = True
    elif (statusCode == STATUS_CODE_FALSE):
        result['response'] = False

    return result


def writeCmdLoop(cmd, timeout=1.0):
    """Write command to Chameleon via Serial

    Args:
        cmd (str):
            The command to be sent to Chameleon
        timeout (float, optional): 
            Serial timeout during the execution. Defaults to 1.0 second. 
            The timeout value will be reset to original value after the execution

    Returns:
        str : A string of data if serial returns STATUS_CODE_OK_WITH_TEXT
        bool: True if serial returns STATUS_CODE_TRUE. False if STATUS_CODE_FALSE
        None: Returns None if the serial does not receive a status code within
            the timeout period

    """

    # Set serial timeout to 1 second for faster output
    myLog('[config] Setting serial timeout to {} second(s)'.format(timeout))
    CHAMELEON.serial.timeout = timeout

    # Execute command
    cmdLine = cmd + LINE_ENDING
    CHAMELEON.serial.write(cmdLine.encode('ascii'))

    # Get status response
    status = CHAMELEON.serial.readline().decode('ascii').rstrip()
    myLog('[{}] status: {}'.format(cmd, status))

    if (len(status) == 0):
        CHAMELEON.verboseLog("Executing <{}>: Timeout".format(cmd))
        return None
    else:
        CHAMELEON.verboseLog("Executing <{}>: {}".format(cmd, status))

    statusCode, statusText = status.split(":")
    statusCode = int(statusCode)

    result = {'statusCode': statusCode, 'statusText': statusText, 'response': None}

    if (statusCode == STATUS_CODE_OK_WITH_TEXT):
        r = ''
        while True:
            t = readResponse()
            myLog('[{}] |{}|'.format(cmd, t))
            if (len(t) == 0):
                break
            r += t + '\n'
        result['response'] = r
    elif (statusCode == STATUS_CODE_TRUE):
        result['response'] = True
    elif (statusCode == STATUS_CODE_FALSE):
        result['response'] = False
        
    myLog('[config] Setting serial timeout back to default ({} second(s))'
        .format(DEFAULT_SERIAL_TIMEOUT)
    )
    CHAMELEON.serial.timeout = DEFAULT_SERIAL_TIMEOUT
    
    return result

# For some reason, the communication port keep receving garbage response
# This method helps turning it off by setting LOGMODE=OFF
def fixGarbageResponse():
    myLog('')
    myLog('[FIX] Fixing garbage responses by setting LOGMODE=OFF')
    if (CHAMELEON.isConnected()):
        result = writeCmd(CHAMELEON, '{}=OFF'.format(COMMAND_LOGMODE))
        myLog('[FIX] {}'.format(result))
    else:
        print('[FIX] Connection is not established')


def testCmdId():
    success = []
    fail = []
    for i in range(52, 54):
        result = writeCmdLoop('SEND {}'.format(i))
        if (result['statusCode'] in STATUS_CODES_SUCCESS):
            myLog('[{}] {}'.format(i, result))
            myLog('')
            success.append(i)
        else:
            fail.append(i)
    print('success: {}'.format(success))
    print('fail   : {}'.format(fail))

def main():
    cmds = [COMMAND_GETUID, COMMAND_LOGMODE+'?', COMMAND_IDENTIFY]

    if (CHAMELEON.connect(PORT)):
        myLog('[conn] Connected to {} successfully!'.format(PORT))

        testCmdId()


    #     for cmd in cmds:
    #         myLog('')
    #         result = writeCmd(cmd)
    #         myLog('[{}] {}'.format(cmd, result))
    else:
        print('[conn] Unable to establish communication on {}'.format(port))
        sys.exit(2)


    myLog('')
    myLog('[CMD] Finish executing all commands')
    
    # Goodbye
    CHAMELEON.disconnect()
    myLog('[conn] Disconnected successfully!')


    sys.exit(0)



if __name__ == "__main__":
    main()