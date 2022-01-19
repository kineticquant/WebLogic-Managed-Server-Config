# WebLogic-Managed-Server-Build
Python scripts to create, modify, and delete WebLogic managed servers automatically.

## How to use
These scripts all need to be initialized by WLST. wlst.sh typically sits in the common/bin directory of the WebLogic install folders.
EX: Oracle_Home/oracle_common/common/bin/wlst.sh

Use would be ~/Oracle_Home/oracle_common/common/bin/wlst.sh FULL_PATH_TO_PY/script.py

Change the full path to your full path for the script and the script name to match here.

The scripts can either be hard-coded to have the credentials in them or they will prompt for connection info at launch.



## Troubleshooting connection method
If the method below is not prompting for credentials, simply replace the whole thing with the comment out "connect()" line and see if WLST initiates the credential prompt.<br><br>
console = System.console()
uname = raw_input("Weblogic username (weblogic): ")
if uname == "":
    uname = "weblogic"
pw = "".join(java.lang.System.console().readPassword("%s", ["Password for %s: " % uname]))
url = raw_input("Enter AdminServer url (t3://localhost:7001): ")
if url == "":
    url = "t3://localhost:7001"
connect(uname, pw, url)
