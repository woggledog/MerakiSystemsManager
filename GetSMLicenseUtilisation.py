# This script, for a given API key, gets every Organisation for that key
# For each org, get the SM licenses, and networks
# for each network, gets the enrolled devices
# and reports back the Orgs, SM Licenses, and Enrolled Devices
# Mandatory arguments:
# -k <API KEY>      : Your Meraki Dashboard API Key
# Pre requisites:
# Meraki library : pip install meraki : https://developer.cisco.com/meraki/api/#/python/getting-started

import meraki
import logging, sys, getopt, keyring, getpass

loggingEnabled = False


def main(argv):
    arg_apikey = keyring.get_password('MerakiAPI', 'personal')
    APIKeyExists = True

    if len(arg_apikey) == 0:
        writeToLog('No API key found in keychain, use passed command line arg instead...', loggingEnabled)
        APIKeyExists = False

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

    # Create Meraki Client Object and initialise
    client = meraki.DashboardAPI(api_key=arg_apikey)

    # Get Orgs for API Key
    orgs = client.organizations.getOrganizations()
    writeToLog(orgs, loggingEnabled)
    # For each Org, get networks
    for org in orgs:
        organization_id = (org['id'])
        organization_name = (org['name'])
        sm_licenses = 0
        sm_devices = 0

        licenseResults = client.organizations.getOrganizationLicenseState(organizationId=organization_id)

        writeToLog({"Licenses for org", organization_id, organization_name}, loggingEnabled)
        writeToLog(licenseResults, loggingEnabled)

        for thislicense, value in licenseResults['licensedDeviceCounts'].items():
            if thislicense == "SM":
                writeToLog({"Number of SM Licenses = ", thislicense, value}, loggingEnabled)
                sm_licenses = value

        # get networks
        ourNetworks = getNetworks(client, organization_id)

        for network in ourNetworks:
            networkName = (network['name'])
            networkID = (network['id'])
            ourDevices = getDevices(client, networkID)
            if ourDevices == "fail":
                writeToLog({organization_id, networkID, networkName, "No SM Network"}, loggingEnabled)
            else:
                ourDevicesList = ourDevices["devices"]
                deviceCounter = 0
                for ourDevice in ourDevicesList:
                    if "id" in ourDevice:
                        deviceCounter = deviceCounter + 1
                writeToLog({organization_id, organization_name, networkID, networkName, deviceCounter}, loggingEnabled)
                sm_devices = sm_devices + deviceCounter

        collective_list[organization_id] = {'OrgName': organization_name, 'smLicenses': sm_licenses,
                                            'enrolledDevices': sm_devices}
    print(collective_list)


def printhelp():
    # prints help information

    print('This is a script to Get the SM licenses and enrolled devices across multiple organisations.')
    print('')
    print('Mandatory arguments:')
    print(' -k <api key>         : Your Meraki Dashboard API key')


def getDevices(passedClient, passedNetworkID):
    try:
        result = passedClient.sm.getNetworkSmDevices(networkId=passedNetworkID)
    except meraki.APIError as e:
        writeToLog(e, loggingEnabled)
        writeToLog("No SM in this network", loggingEnabled)
        result = 'fail'
    return result


def getNetworks(passedClient, passedOrgID):
    networksResult = passedClient.networks.getOrganizationNetworks(organizationId=passedOrgID)
    return networksResult


def writeToLog(MessageToLog, toLog):
    if toLog:
        logging.warning(MessageToLog)


if __name__ == '__main__':
    main(sys.argv[1:])
