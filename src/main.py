from app.mt_server import model_connections, model_info
import uvicorn

"""
TODO
- setup a page which displays the information about each of the models and gives an example translation. This should make it easier
for anyone to see whether they are currently online or not.
- allow anyone with appropriate login credentials to restart the web server. Would be great if this could be the done for the MT servers too.
- ensure that proper threading is in place to handle a lot of requests at once
- set up tests that will stress test the server and also just test different things to make sure it's working. These tests should be usable 
for the page which displays stats about the server
- migrate over the remaining functions from the previous web server, such as those which concern pre- and post-processing
- eventually, it would be great to create a report with a direct comparison between the two implementations and add this to the Github
as well as your Upwork profile.
"""


if __name__ == "__main__":
    # start up the web server with established connections
    uvicorn.run("app.api:app", host="0.0.0.0", port=60000, reload=True)