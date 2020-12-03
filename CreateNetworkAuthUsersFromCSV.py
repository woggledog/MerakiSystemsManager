import meraki
import logging, sys, getopt, keyring, getpass, csv
import pandas as pd


#orgs = client.organizations.getOrganizations()
#networks = client.networks.getOrganizationNetworks("800607")


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
        opts, args = getopt.getopt(argv, 'k:o:')
    except getopt.GetOptError:
        if not APIKeyExists:
            printhelp(argv)
            sys.exit(2)

    for opt, arg in opts:
        if opt == '-k':
            if not APIKeyExists:
                arg_apikey = arg
        elif opt == '-o':
            arg_org_id = arg

    if arg_org_id == '':
        printhelp(argv)
        sys.exit(2)

    client = meraki.DashboardAPI(api_key=arg_apikey)

    networks = client.organizations.getOrganizationNetworks(organizationId=arg_org_id)

    NetworkAuthUsers = pd.read_csv("CreateNetworkAuthUsers.csv")

    for network in networks:

        for index, row in NetworkAuthUsers.iterrows():
            rowDict = row.to_dict()
            name = rowDict["name"]
            email = rowDict["email"]
            password = rowDict["password"]
            ssidnum = rowDict["ssidnum"]
            authorizations = [
                {
                    "expiresAt": "Never",
                    "ssidNumber": ssidnum
                },
            ]

            createNetworkAuthUserResponse = client.networks.createNetworkMerakiAuthUser(networkId=network["id"], email=email, name=name, password=password, authorizations=authorizations)


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