import meraki # install from https://developer.cisco.com/meraki/api/#!python-meraki/meraki-dashboard-api-python-library
import logging, sys, getopt, keyring, getpass, csv

# keyring allows you to store your MerakiAPI key in your Mac's keychain securely, so you don't have to leave it in your code

loggingEnabled = True

def main(argv):

    print(meraki.__version__)

    # when you put your API key in the keychain, it will be referenced via name and instance, so you can store multiple keys in there
    arg_apikey = keyring.get_password('MerakiAPI', 'personal')
    APIKeyExists = True

    if len(arg_apikey) == 0:
        writeToLog('No API key found in keychain, use passed command line arg instead...', loggingEnabled)
        APIKeyExists = False

    # initialize variables for command line arguments
    arg_network_id = ''
    # get command line arguments. This script needs at the very minimum a network ID
    try:
        opts, args = getopt.getopt(argv, 'k:n:')
    except getopt.GetOptError:
        if not APIKeyExists:
            printhelp(argv)
            sys.exit(2)

    for opt, arg in opts:
        if opt == '-k':
            if not APIKeyExists:
                arg_apikey = arg
        elif opt == '-n':
            arg_network_id = arg

    if arg_network_id == '':
        printhelp(argv)
        sys.exit(2)

    # Create Meraki Client Object and initialise
    client = meraki.DashboardAPI(api_key=arg_apikey)

    with open('AddTagToDevicesFromCSV.csv', 'rt') as csvfile:
        deviceData = dict(csv.reader(csvfile))

    for tagItem, deviceString in deviceData.items():
        try:
            serialArray = returnArrayForGivenStringWithDelimiter(deviceString,"*")
            response = client.sm.modifyNetworkSmDevicesTags(networkId=arg_network_id, updateAction='add',
                                                            tags=[tagItem], serials=serialArray)

        except meraki.APIError as e:
            print(e)


def returnArrayForGivenStringWithDelimiter(passedString,delimiter):
    splitStringDict = passedString.split(delimiter)
    return(splitStringDict)


def getDevices(passedClient, passedNetwork, passedSerials):

    result = "fail"
    try:
        writeToLog(passedSerials,loggingEnabled)
        result = passedClient.sm.getNetworkSmDevices(networkId=passedNetwork, serials=passedSerials)
        writeToLog("These devices were found", loggingEnabled)
        writeToLog(result, loggingEnabled)
        writeToLog("******************", loggingEnabled)


    except meraki.APIError as e:
        writeToLog(e, loggingEnabled)
        writeToLog("no devices found", loggingEnabled)
    return result


def writeToLog(MessageToLog, toLog):
    if toLog:
        logging.warning(MessageToLog)


def printhelp():
    # prints help information

    print('This is a script to, for a given CSV with serial numbers, delimited by a * and intended tags, ')
    print('tag the devices devices in systems manager')
    print(' ')
    print('Mandatory arguments:')
    print(' -k <api key>         : Your Meraki Dashboard API key, unless you use keychain')
    print(' -n <network ID>      : Your Meraki Network ID')


if __name__ == '__main__':
    main(sys.argv[1:])