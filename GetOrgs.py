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
    try:
        opts, args = getopt.getopt(argv, 'k:')
    except getopt.GetOptError:
        if not APIKeyExists:
            printhelp(argv)
            sys.exit(2)

    for opt, arg in opts:
        if opt == '-k':
            if not APIKeyExists:
                arg_apikey = arg

    try:

        # Create Meraki Client Object and initialise
        client = meraki.DashboardAPI(api_key=arg_apikey)

        # Get Orgs for API Key
        orgs = client.organizations.getOrganizations()
        writeToLog(orgs, loggingEnabled)
        for org in orgs:
            organization_id = (org['id'].encode())
            organization_name = (org['name'].encode())
            writeToLog(organization_id, loggingEnabled)
            writeToLog(organization_name, loggingEnabled)
            writeToLog(' ', loggingEnabled)

    except APIException as e:
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
