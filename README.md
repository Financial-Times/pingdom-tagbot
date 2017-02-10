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

- _CMDB_SYSURL_  The CMDB API url for retrieving system, information. e.g. https://cmdb.xx.com/v2/items/system
- _CMDB_APIKEY_  The CMDB API key

## Execution
Ensure you have defined the environmental variables

python pingdom-tagbot.py

The output is a file named _pingdom_check.csv_ in the local directory

It contains a list of all the pingdom checks with their name and target url as well as all the tags

two special columns are output "system?" and "tier?"

If there is a tag named systemcode_xxxxxx then xxxxxx will be extracted and output as the systemcode.
If there is a tag named tier_xxxxxx then xxxxxx will be extracted and output as the servicerTier.

if a systemcode tag is not supplied then the systemcode? cell will be set to "@ MISSING @".
if the systemcode is in the cmdb then the systemcode? cell will be set to "Yes"; it not in the cmdb it will be set to "@ NOT IN CMDB @".

if a tier tag is not suplied then the tier? cell will be set to "@ MISSING @".
if the systemcode is in the cmdb and the tier matches then the tier? cell will be set to "Matching CMDB"; it not matching the cmdb it will be set to "@ MISMATCH CMDB @".
