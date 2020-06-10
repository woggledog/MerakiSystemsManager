import meraki
import logging, sys, getopt, keyring, getpass

loggingEnabled = False


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
        opts, args = getopt.getopt(argv, 'k:n:d:')
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
        elif opt == '-d':
            arg_device_id = arg

    # if arg_apikey == '' or arg_network_id == '':
    if arg_network_id == '':
        printhelp(argv)
        sys.exit(2)

    # Create Meraki Client Object and initialise
    client = meraki.DashboardAPI(api_key=arg_apikey)

    try:

        ourDevices = client.sm.getNetworkSmDevices(networkId=arg_network_id, ids=arg_device_id, fields="isSupervised,location")

        ourDevicesList = ourDevices["devices"]

        print(ourDevices)

        sys.exit(2)

        for ourDevice in ourDevicesList:
            isSupervised = ourDevice["isSupervised"]

            if isSupervised:
                print("Device is supervised")
            else:
                print("Device is NOT supervised")
                # So now we unenroll the device
                device_id = 'deviceId0'
                collect['device_id'] = device_id

               #result = client.sm.unenrollNetworkSmDevice(networkId=arg_network_id, deviceId=arg_device_id)

    except meraki.APIError as e:

        print('Error:')
        print(e.response_code)
        print('with error message :')
        print(e.context.response.raw_body)
        sys.exit(2)


def writeToLog(MessageToLog, toLog):
    if toLog:
        logging.warning(MessageToLog)


def printhelp(passedargvs):
    # prints help information

    print('This is a script .........................')
    print('')
    print('Mandatory arguments:')
    print(' -k <api key>         : Your Meraki Dashboard API key')
    print(' -n <network ID>      : Your Meraki Dashboard Network ID')
    print('')
    print('You passed:')
    print(passedargvs)


if __name__ == '__main__':
    main(sys.argv[1:])
