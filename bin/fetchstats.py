import requests
import re
import sys
import time
import datetime
import splunk.entity as entity

# access the credentials in /servicesNS/nobody/<YourApp>/storage/passwords
def getCredentials(sessionKey):
   myapp = 'TA_opendns-fetchstats'
   try:
      # list all credentials
      entities = entity.getEntities(['admin', 'passwords'], namespace=myapp,
                                    owner='nobody', sessionKey=sessionKey)
   except Exception as e:
      raise Exception("Could not get %s credentials from splunk. Error: %s"
                      % (myapp, str(e)))

   # return first set of credentials
   for i, c in entities.items():
               return c['username'], c['clear_password']

   raise Exception("No credentials have been found")

def main():
        csvURL="https://dashboard.opendns.com"
        loginURL="https://login.opendns.com/?source=dashboard"
        
        sys.stderr.write("TA-opendns starting up\n")                  
        # read session key sent from splunkd
        sessionKey = sys.stdin.readline().strip()

        if len(sessionKey) == 0:
           sys.stderr.write("Did not receive a session key from splunkd. " +
                            "Please enable passAuth in inputs.conf for this " +
                            "script\n")
           exit(2)

        # now get twitter credentials - might exit if no creds are available
        user, passwd = getCredentials(sessionKey)
        
        # current not supporting multiple accounts.  change the next line if you need to get a specific network
        networkid="all"
        
        # Always pull yesterday's information
        dateFrom=datetime.date.today() - datetime.timedelta(days = 1)
        timestamp=time.time() - 86400
        
        # create a session object to store cookies
        s = requests.Session()
        # get the form token for the session
        response1 = s.get(loginURL)
        searchObj1 = re.search(r'formtoken\"\svalue=\"(.*?)\"', response1.content.decode('utf-8'))
        if searchObj1:
            formToken = searchObj1.group(1)
        else:
            sys.exit("No token found!!\n")

        # now we can logon
        data = {
          'formtoken': formToken,
          'username': user,
          'password': passwd,
          'sign_in_submit': 'foo'
        }
        response2 = s.post(loginURL, data=data)
        #print(response2.content.decode('utf-8'))
        if(re.search(r'Login failed', response2.content.decode('utf-8'))):
            sys.exit("Password Failure\n")
        else:
            sys.stderr.write("Logon Success\n")

        # now we will iterate and get all the data
        go=True
        page=1
        csvOut=""
        while(go):
            sys.stderr.write(f"Requesting Page {page}\n")
            r = s.get(f"{csvURL}/stats/{networkid}/topdomains/{dateFrom}/page{page}.csv")
            csv = r.content.decode('utf-8')
            if( page == 1 ):
                if not csv:
                    sys.exit(f"You can not access {network_id}\n")
                if(re.search(r'DOCTYPE', csv)):
                    sys.exit("Error retrieving data.  Date range may be outside of available data.\n")
                csvOut = csv.split("\n",1)[1]
            else:
                if(re.search(r'DOCTYPE', csv)):
                    go=False
                else:
                    csvOut = csvOut + csv.split("\n",1)[1]
            page += 1
            csv = None
            r = None

        sys.stderr.write("Data retreival complete\n")
        # send events to Splunk with timestamp
        for line in csvOut.splitlines():
            print(str(timestamp) + "," +line)
        sys.stderr.write("Execution complete\n")

if __name__ == "__main__":
    main()
