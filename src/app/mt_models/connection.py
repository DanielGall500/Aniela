from app.mt_models.information import model_info
from app.mt_models.requests import MTRequestHandler
import socket
import time

model_translation_test = {
    "en": "Climate change",
    "de": "Klimawandel",
    "it": "Cambiamento climatico",
    "fr": "Changement climatique",
    "pl": "Zmiana climatu",
    "ga": "Athrú aeráide"
}

class MTServerConnection:
    def __init__(self):
        self.MT_SERVER_IP = model_info.get_server_ip()
        self.MT_SERVER_PORT = model_info.get_server_port()
        self.model_connections = {}
        self.model_connections_output = {}
        self.request_handler = MTRequestHandler()

    def __str__(self) -> str:
        connection_view = "\n"
        for key in self.model_connections.keys():
            src, tgt = self._convert_key_to_pair(key)
            pair_status = self.get_connection_status(src,tgt)
            connection_view += key + ": " + str(pair_status) 
            connection_view += "\n"
        return connection_view

    def translate(self):
        pass

    async def connect_to_all(self):
        language_pairs = model_info.get_all_languages_pairs()
        for pair in language_pairs:
            src, tgt = pair 
            await self.connect_to(src,tgt)
        return self.all_as_dict()

    async def connect_to(self, src: str, tgt: str) -> bool:
        lang_pair_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            connection_result = lang_pair_socket.connect_ex((self.MT_SERVER_IP, self.MT_SERVER_PORT))
            if connection_result != 0: 
                raise socket.error()

            # Ensure an OK status is received when connecting to a particular model
            translation_test_input = model_translation_test[src]
            start_time = time.time()
            translation_test_response = await self.request_handler.translate(src, tgt, translation_test_input)
            translation_test_time = round(time.time() - start_time, 4)

            translation_test_output = translation_test_response["result"]
            is_model_available = translation_test_response["state"] == self.request_handler.STATUS_OK
        except socket.error:
            is_model_available = False

        # Update the new connection status and close the socket
        self.set_connection_status(src, tgt, is_model_available, translation_test_input, translation_test_output, translation_test_time)
        lang_pair_socket.close()
        return is_model_available

    def all_as_dict(self) -> dict:
        return self.model_connections

    def set_connection_status(self, src: str, tgt: str, is_connected: bool, test_input: str, test_output: str, test_time: float):
        key = self._convert_pair_to_key(src, tgt)
        output = ""
        if tgt in test_output:
            output = test_output[tgt]

        self.model_connections[key] = {
            "is_connected": is_connected,
            "input": test_input,
            "output": output,
            "time": test_time
        }

    def get_connection_status(self, src: str, tgt: str) -> dict:
        key = self._convert_pair_to_key(src, tgt)
        if key in self.model_connections:
            return self.model_connections[key] 
        return None

    def _convert_pair_to_key(self, src: str, tgt: str) -> str:
        return f"{src}-{tgt}"

    def _convert_key_to_pair(self, key: str) -> str:
        return key[0:2],key[3:5]

