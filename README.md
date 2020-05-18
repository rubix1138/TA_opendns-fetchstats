# TA_opendns-fetchstats
## A Splunk TA to pull stats from your OpenDNS account.
This Splunk Technology Add-on was built to pull statistics from OpenDNS.  Note that OpenDNS is the home and small business version of Cisco Umbrella.  The logic of this script was based on fetchstats: https://github.com/opendns/opendns-fetchstats.

Considering that OpenDNS is a free/inexpensive version of Umbrella, there isn't an API to pull down all the DNS data.  What this TA does is pull statistics that are collected day by day basis.  It recommended to schedule the input once per day right after midnight.  The script pulls data from the previous day.

This TA only supports Splunk 8.0+ since it uses python3.

## Using this Technology Add-on

* The add-on has to be installed on Search Heads
* If data is collected through Intermediate Heavy Forwarders, it has to be installed on Heavy Forwarders, otherwise on indexers
* Once installed, go to which ever Splunk server will be collecting the data, go to Manage Apps, find this app and click the *Set Up* link under actions.  Enter your username (typically an email address) and password.
* Once the TA is configured, you can enable the input provided.

## Compatibility

* Requires Splunk 8.0 or higher.
