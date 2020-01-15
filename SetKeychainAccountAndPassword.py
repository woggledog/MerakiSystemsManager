import keyring, getpass

requiredKeychainName = input("Please type the name of the keychain object you want to store your Meraki API key... ")
requiredKeychainAccount = input("please enter the name of the account you wish to use")

keyring.set_password(requiredKeychainName, requiredKeychainAccount, getpass.getpass())