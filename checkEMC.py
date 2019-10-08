#!/usr/bin/python

import subprocess, re
import time
import sys, getopt

def main():

    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:u:p:", ["host=","user=","pwd="])
    except getopt.GetoptError:
        print "Parametes should be given to run the macro:"
        print "Enter -h or --host to define the host,"
        print "Enter -u or --user to define the user,"
        print "Enter -p or --pwd to define the password!"
        sys.exit()
    for o,a in opts:
        if o in ("-h","--host"):
            host = str(a)
        if o in ("-u","--user"):
            user = str(a)
        if o in ("-p","--pwd"):
            pwd = str(a)
    
    delay = 1.0
    timeout = int(5.0/delay)
    
    ans = subprocess.Popen(["/opt/Navisphere/bin/naviseccli", \
        "-h", host, \
        "-User", user, \
        "-Password", pwd, \
        "-scope", "0", \
        "storagepool", "-list", "-capacities"], \
        stdout=subprocess.PIPE, \
    )
    
    while ans.poll() is None and timeout > 0:
        time.sleep(delay)
        timeout -= delay
    
    if ans.poll() is None and timeout == 0:
        Msg_Nagios = "Request has timed out!"
        subprocess.call(["echo", Msg_Nagios])
        sys.exit(2)
    else:
        Msg_Nagios = ""
    
        for line in ans.stdout:
        
            namePool = re.search(r"Pool Name:.*", line)
            if namePool:
                Msg_Nagios = Msg_Nagios+namePool.group()+", "
        
            usagePool = re.search(r"Percent Full:.*", line)
            if usagePool:
                Msg_Nagios = Msg_Nagios+usagePool.group()+" ~ "
        
        if re.search("9[0-9].[0-9][0-9][0-9]", Msg_Nagios) or re.search("100.000", Msg_Nagios):
            subprocess.call(["echo", Msg_Nagios])
            sys.exit(2)
        elif re.search("8[0-9].[0-9][0-9][0-9]", Msg_Nagios):
            subprocess.call(["echo", Msg_Nagios])
            sys.exit(1)
        elif re.search("[0-7][0-9].[0-9][0-9][0-9]", Msg_Nagios):
            subprocess.call(["echo", Msg_Nagios])
            sys.exit(0)
        else:
            subprocess.call(["echo", "Please check the system at EMC Unisphere Web Application. Unknown Message in STDOUT:", str(ans.stdout)])
            sys.exit(3)

if __name__ == "__main__":
    main()
