from app.mt_models.information import model_info
from app.mt_models.requests import MTRequestHandler
from loguru import logger
import socket
import time

model_translation_test = {
    "en": "Its major markets include Spain, Greece, Poland and Turkey.",
    "de": "Zu den Hauptmärkten gehören Spanien, Griechenland, Polen und die Türkei.",
    "it": "I suoi principali mercati includono Spagna, Grecia, Polonia e Turchia.",
    "fr": "Ses principaux marchés sont l'Espagne, la Grèce, la Pologne et la Turquie.",
    "pl": "Główne rynki zbytu to Hiszpania, Grecja, Polska i Turcja.",
    "ga": "Áirítear ar a margaí móra an Spáinn, an Ghréig, an Pholainn agus an Tuirc."
}

class MTServerConnection:
    def __init__(self):
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

    def connect_to_all(self):
        language_pairs = model_info.get_all_languages_pairs()
        for pair in language_pairs:
            src, tgt = pair 
            # formerly await
            self.connect_to(src,tgt)
        return self.all_as_dict()

    def connect_to(self, src: str, tgt: str) -> bool:
        lang_pair_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        translation_test_input = ""
        translation_test_output = ""
        translation_test_time = -1
        
        try:
            server_ip, server_port = model_info.get_language_pair_server_IP_and_port(src,tgt)
            connection_result = lang_pair_socket.connect_ex((server_ip, server_port))

            logger.info("Attempting to establish connection to {}-{}", src, tgt)

            if connection_result != 0: 
                logger.error("Connection to server was unsuccessful.")
                raise socket.error()
            else:
                logger.success("Connection to {}:{} established.", server_ip, server_port)

            # Ensure an OK status is received when connecting to a particular model
            translation_test_input = model_translation_test[src]
            start_time = time.time()

            translation_test_response = self.request_handler.translate(src, tgt, translation_test_input)
            translation_test_time = round(time.time() - start_time, 4)

            translation_test_output = translation_test_response["result"]
            is_model_available = translation_test_response["state"] == self.request_handler.STATUS_OK

            if is_model_available:
                logger.success("Connection to model {}-{} established.", src, tgt)
            else:
                logger.error("Connection to model {}-{} unsuccessful.", src, tgt)

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

