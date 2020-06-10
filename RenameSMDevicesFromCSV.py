import meraki # install from https://developer.cisco.com/meraki/api/#!python-meraki/meraki-dashboard-api-python-library
import logging, sys, getopt, keyring, getpass, csv

# keyring allows you to store your MerakiAPI key in your Mac's keychain securely, so you don't have to leave it in your code

loggingEnabled = False


def main(argv):

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

    # we now open the CSV file
    with open('RenameSMDevices.csv', 'rt') as csvfile:
        deviceData = dict(csv.reader(csvfile))

    writeToLog(deviceData, loggingEnabled)

    # Create Meraki Client Object and initialise
    client = meraki.DashboardAPI(api_key=arg_apikey)

    # get serial numbers from CSV and create string from this

    serialnumsSTR = ''

    for device in deviceData.keys():
        serialnumsSTR = serialnumsSTR + device + ","

    # remove trailing , from string
    serialnumsSTR = serialnumsSTR[:-1]

    writeToLog(serialnumsSTR, loggingEnabled)

    # get all devices that actually exist. If a Mac / serial doesn't exist, it won't be in this list
    ourDevices = getDevices(client, arg_network_id, serialnumsSTR)


    # for each device returned,
        # look up the Mac / serial number in device data, and key the name to be assigned.
        # if it doesn't exist, move on
        # handle any errors that might exist due to the name already having been assigned

    ourDevicesList = ourDevices["devices"]

    for ourDevice in ourDevicesList:

        deviceFieldsDict ={'name': deviceData.get(ourDevice["serialNumber"])}

        try:
            result = client.sm.updateNetworkSmDeviceFields(networkId=arg_network_id, deviceFields=deviceFieldsDict, serial=ourDevice["serialNumber"])

            # result = client.networks.createOrganizationNetwork()
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