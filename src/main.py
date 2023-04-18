import uvicorn
from dotenv import dotenv_values

# URL to which the tests should be sending requests
# This is the URL of the web server and not the MT servers
config_app = dotenv_values('app/.env')
WEB_SERVER_IP: str = config_app["WEB_SERVER_IP"]
WEB_SERVER_PORT: int = int(config_app["WEB_SERVER_PORT"])

def main():
    # start up the web server with established connections
    uvicorn.run("app.api:app", host=WEB_SERVER_IP, port=WEB_SERVER_PORT, reload=True)

if __name__ == "__main__":
    main()
