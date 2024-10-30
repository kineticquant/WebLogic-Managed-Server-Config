# WebLogic-Managed-Server-Build
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](#)

Python scripts to create, modify, and delete WebLogic managed servers automatically.

## How to use
These scripts all need to be initialized by WLST. wlst.sh typically sits in the common/bin directory of the WebLogic install folders.
EX: Oracle_Home/oracle_common/common/bin/wlst.sh

Use would be ~/Oracle_Home/oracle_common/common/bin/wlst.sh FULL_PATH_TO_PY/script.py

Change the full path to your full path for the script and the script name to match here.

The scripts can either be hard-coded to have the credentials in them or they will prompt for connection info at launch.


## Create script configuration
The creation script for managed servers has variables for a massive amount of configuration. Most deployments do not need that much configuration so it can be stripped down and modified to only include minor details.

For the creation script, you need to:
1) Ensure you replace the values with what you need to match your environment.
2) Change the roleName. roleName is defined as the actual role that will be placed in the security realm.
3) This script enables SSL by default - you will need to return and attach the keystore in the SSL configuration settings.
4) You will need to define a user that belongs to the role that can connect across multiple builds if you use the adapter configuration settings. This is not necessary if you strip this script down to just building managed servers using the properties file.


## Troubleshooting connection method
If the method below is not prompting for credentials, simply replace the whole thing with the commented out "connect()" line and see if WLST initiates the credential prompt.<br>
```
console = System.console()
uname = raw_input("Weblogic username (weblogic): ")
if uname == "":
    uname = "weblogic"
pw = "".join(java.lang.System.console().readPassword("%s", ["Password for %s: " % uname]))
url = raw_input("Enter AdminServer url (t3://localhost:7001): ")
if url == "":
    url = "t3://localhost:7001"
connect(uname, pw, url)
```
