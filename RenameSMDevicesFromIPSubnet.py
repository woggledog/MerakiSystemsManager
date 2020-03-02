import meraki
import logging, sys, getopt, keyring, getpass

loggingEnabled = True


def main(argv):

    arg_apikey = keyring.get_password('MerakiAPI', 'personal')
    APIKeyExists = True

    if len(arg_apikey) == 0:
        writeToLog('No API key found in keychain, use passed command line arg instead...', loggingEnabled)
        APIKeyExists = False

    # initialize variables for command line arguments
    arg_network_id = ''
    # get command line arguments
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

    ## get all devices with IP address

    ourDevices = getAllSMDevices(client, arg_network_id, "ip")

    writeToLog(ourDevices,loggingEnabled)

    # for each device returned,
        # look up the Mac / serial number in device data, and key the name to be assigned.
        # if it doesn't exist, move on
        # handle any errors that might exist due to the name already having been assigned

    ourDevicesList = ourDevices["devices"]

    for ourDevice in ourDevicesList:

        # replace . with - and build dict
        deviceFieldsDict ={'name': ourDevice["ip"].replace(".", "-")}

        try:
            writeToLog(ourDevice["serialNumber"],loggingEnabled)
            writeToLog(ourDevice["ip"], loggingEnabled)
            writeToLog(deviceFieldsDict,loggingEnabled)
            writeToLog("*************",loggingEnabled)

            result = client.sm.updateNetworkSmDeviceFields(networkId=arg_network_id, deviceFields=deviceFieldsDict, serial=ourDevice["serialNumber"])
        except meraki.APIError as e:
            print(e)


def getDevices(passedClient, passedNetwork, passedSerials):

    result = "fail"
    try:
        result = passedClient.sm.getNetworkSmDevices(networkId=passedNetwork, serials=passedSerials)
    except meraki.APIError as e:
        writeToLog(e, loggingEnabled)
        writeToLog("no devices found", loggingEnabled)
    return result

def getAllSMDevices(passedClient, passedNetwork,passedParam):

    result = "fail"
    try:
        result = passedClient.sm.getNetworkSmDevices(networkId=passedNetwork,fields=passedParam)
    except meraki.APIError as e:
        writeToLog(e, loggingEnabled)
        writeToLog("no devices found", loggingEnabled)
    return result


def writeToLog(MessageToLog, toLog):
    if toLog:
        logging.warning(MessageToLog)


def printhelp():
    # prints help information

    print('This is a script to for a given CSV with serial numbers and intended names, ')
    print('rename the devices in systems manager')
    print(' ')
    print('Mandatory arguments:')
    print(' -k <api key>         : Your Meraki Dashboard API key')
    print(' -n <network ID>      : Your Meraki Network ID')


if __name__ == '__main__':
    main(sys.argv[1:])