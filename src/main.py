import uvicorn
import socket
import sqlite3

"""
TODO
- setup a page which displays the information about each of the models and gives an example translation. This should make it easier
for anyone to see whether they are currently online or not.
- allow anyone with appropriate login credentials to restart the web server. Would be great if this could be the done for the MT servers too.
- ensure that proper threading is in place to handle a lot of requests at once
- set up tests that will stress test the server and also just test different things to make sure it's working
- migrate over the remaining functions from the previous web server, such as those which concern pre- and post-processing
"""

db = sqlite3.connect("app/database.sqlite")
cursor = db.cursor()

MT_SERVER_IP = "0.0.0.0"
MT_SERVER_PORT = MT_SERVER_IP + ":8080"

def get_language_pair_port(src: str, tgt: str) -> str:
    get_port_query = f"SELECT port FROM models WHERE source='{src}' AND target='{tgt}'"
    print("Fetching port for ({src},{tgt})")
    try:
        port = cursor.execute(get_port_query).fetchone()[0]
    except Exception:
        print("Invalid language pair provided.")
    print(f"Port found in database as {port}.")
    return port

def connect_to_language_pair(src: str, tgt: str):
    lang_pair_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lang_pair_port = get_language_pair_port(src, tgt)
    try:
        connection_result = lang_pair_socket.connect_ex((MT_SERVER_IP, 8080))
        print(f"Connecting to port {lang_pair_port} on IP {MT_SERVER_IP}")

        if connection_result != 0: 
            raise socket.error()
        print("Connection to ({src},{tgt}) established.")
        lang_pair_socket.close()
    except socket.error:
        print(f"No response from pair ({src},{tgt})")
        lang_pair_socket.close()

if __name__ == "__main__":
    connect_to_language_pair("de","en")
    uvicorn.run("app.api:app", host="0.0.0.0", port=60000, reload=True)