import uvicorn

"""
TODO
- add UI to the status page
- allow anyone with appropriate login credentials to restart the web server. Would be great if this could be the done for the MT servers too.
- ensure that proper threading is in place to handle a lot of requests at once
- set up tests that will stress test the server and also just test different things to make sure it's working. These tests should be usable 
for the page which displays stats about the server
- eventually, it would be great to create a report with a direct comparison between the two implementations and add this to the Github
as well as your Upwork profile.
"""

def main():
    # start up the web server with established connections
    uvicorn.run("app.api:app", host="0.0.0.0", port=60000, reload=True)

if __name__ == "__main__":
    main()
