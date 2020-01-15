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

    # if arg_apikey == '' or arg_network_id == '':
    if arg_network_id == '':
        printhelp(argv)
        sys.exit(2)

    # Create Meraki Client Object and initialise
    client = meraki.DashboardAPI(api_key=arg_apikey)

    try:
        result = client.sm.getNetworkSmDevices(networkId=arg_network_id)
        print(result)
    except APIException as e:
        print('Error:')
        print(e.response_code)
        print('with error message :')
        print(e.context.response.raw_body)


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