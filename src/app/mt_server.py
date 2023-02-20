import socket
import sqlite3

db = sqlite3.connect("app/database.sqlite")
cursor = db.cursor()

MT_SERVER_IP = "0.0.0.0"
MT_SERVER_PORT = 8080

class MTServerConnection:
    def __init__(self, server_ip: str, server_port: str):
        self.MT_SERVER_IP = server_ip
        self.MT_SERVER_PORT = server_port
        self.model_connections = {}
        self.model_info = MTModelInformation()

        self.connect_to_all()

    def __str__(self) -> str:
        connection_view = "\n"
        for key in self.model_connections.keys():
            src, tgt = self._convert_key_to_pair(key)
            pair_status = self.get_connection_status(src,tgt)
            connection_view += key + ": " + str(pair_status) 
            connection_view += "\n"
        return connection_view

    def connect_to_all(self):
        language_pairs = self.model_info.get_all_languages_pairs()
        for pair in language_pairs:
            src, tgt = pair 
            self.connect_to(src,tgt)
        return self.all_as_dict()

    def connect_to(self, src: str, tgt: str) -> bool:
        lang_pair_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # this should be included in connection
        #lang_pair_port = get_language_pair_port(src, tgt)
        try:
            connection_result = lang_pair_socket.connect_ex((self.MT_SERVER_IP, self.MT_SERVER_PORT))
            if connection_result != 0: 
                raise socket.error()

            connection_status = True
        except socket.error:
            connection_status = False

        # update the new connection status and close the socket
        self.set_connection_status(src, tgt, connection_status)
        lang_pair_socket.close()
        return connection_status

    def all_as_dict(self) -> dict:
        return self.model_connections

    def set_connection_status(self, src: str, tgt: str, is_connected: bool):
        key = self._convert_pair_to_key(src, tgt)
        self.model_connections[key] = is_connected

    def get_connection_status(self, src: str, tgt: str) -> bool:
        key = self._convert_pair_to_key(src, tgt)
        if key in self.model_connections:
            return self.model_connections[key] 
        return False

    def _convert_pair_to_key(self, src: str, tgt: str) -> str:
        return f"{src}-{tgt}"

    def _convert_key_to_pair(self, key: str) -> str:
        return key[0:2],key[3:5]

class MTModelInformation:
    def get_language_pair_port(self, src: str, tgt: str) -> str:
        get_port_query = f"SELECT port FROM models WHERE source='{src}' AND target='{tgt}'"
        try:
            port = cursor.execute(get_port_query).fetchone()[0]
        except Exception:
            return "N/A"
        return port

    def get_all_languages_pairs(self):
        get_pairs_query = f"SELECT source,target FROM models"
        pairs = cursor.execute(get_pairs_query).fetchall()
        return pairs

model_connections = MTServerConnection(MT_SERVER_IP, MT_SERVER_PORT)
model_info = MTModelInformation()
