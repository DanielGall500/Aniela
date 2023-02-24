import uvicorn
from dotenv import dotenv_values

"""
TODO
- add UI to the status page
- set up stress tests for the web API 
- allow anyone with appropriate login credentials to restart the web server. Would be great if this could be the done for the MT servers too.
- ensure that proper threading is in place to handle a lot of requests at once
- eventually, it would be great to create a report with a direct comparison between the two implementations and add this to the Github
as well as your Upwork profile.
"""

# URL to which the tests should be sending requests
# This is the URL of the web server and not the MT servers
config_app = dotenv_values('app/.env')
WEB_SERVER_IP: str = config_app["WEB_SERVER_IP"]
WEB_SERVER_PORT: str = config_app["WEB_SERVER_PORT"]

def main():
    # start up the web server with established connections
    uvicorn.run("app.api:app", host=WEB_SERVER_IP, port=WEB_SERVER_PORT, reload=True)

if __name__ == "__main__":
    main()
