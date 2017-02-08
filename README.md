# pingdom-tagbot
TAG checking for pingdom

## Environment variables
All environment variables are compuilsory.

- _PINGDOM_APIURL_  The pingdom api url
- _PINGDOM_USER_  Your pingdom username
- _PINGDOM_PASSWORD_  Your pingdom password
- _PINGDOM_ACCOUNT_EMAIL_  Your pingdom account email used for multi user access
- _PINGDOM_APIKEY_  Your pingdom api key for this application (register pingdom-tagbot as an app)

- _PINGDOM_TAG_TIER_  The prefix used to provide a service tier value as a tag. e.g. tier_  for tier_platinum
- _PINGDOM_TAG_SYSTEMCODE_  The prefix used to provide a sytemcode value as a tag. e.g. systemcode_  for systemcode_tagbot

- _CMDB_SYSURL_  The CMDB API url for retrieving syste, information.
- _CMDB_APIKEY_  The CMDB API key

THe output is a file named _pingdom_check.csv_ in the local directory
