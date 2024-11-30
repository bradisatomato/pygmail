# pygmail
gmail client in python

# installation
1. `sudo apt install python3-tk`
2. `pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client`
3. put your credentials.json beside your executable

# getting credentials
1. open [google cloud console](https://console.cloud.google.com/)
2. create a new project
3. enable gmail api
4. hit create credentials
5. enable the scope `gmail.send`