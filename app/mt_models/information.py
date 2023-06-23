import sqlite3
import numpy
from dotenv import dotenv_values
from loguru import logger

"""
----MTModelInformation Class--------------------------------------
This class reads, stores, and provides information on the MT model
setup that you have specified in the SQLite database, using either
SQL injections or the provided model setup feature in the API's
interactive dashboard.
This configuration is loaded into a Python dictionary upon startup,
and refreshed each time the table is updated in the dashboard.
------------------------------------------------------------------
"""

# -- JWT Configuration Variables --
app_config = dotenv_values('app/.env')

# Match a server name (e.g EUCOM_A) to its IP adddress,
# which must be specified in your environment variables.
def get_server_IP_from_config(server: str) -> str:
    try:
        server_ip = str(app_config[f"{server}_IP"])
    except Exception as e:
        logger.error(f"Server {server} not found.")
        raise Exception(e)
    return str(server_ip)

# Similarly, match a server name (e.g EUCOM_A) to its port,
# which also must be specified in your environment variables.
def get_server_port_from_config(server: str) -> int:
    try:
        server_port = app_config[f"{server}_PORT"]
    except Exception as e:
        logger.error(f"Server {server} not found.")
        raise Exception(e)
    return int(server_port)

class MTModelInformation:
    CONFIG = {}
    
    # Upon API startup, load our model setup
    # from the SQLite datbase.
    def __init__(self):
        self.refresh()

    # Refreshes the model setup - should be called
    # whenever there is an update to the database.
    def refresh(self):
        db = sqlite3.connect("app/database.sqlite") 
        cursor = db.cursor()

        get_server_data = f"SELECT source, target, server, gpu, id FROM models"
        self.CONFIG = {}
        try:
            server_data = cursor.execute(get_server_data).fetchall()
        except Exception as e:
            logger.error("Connection to database not successful. Did you provide the correct DB path?")
            raise Exception("Invalid SQL Database for Server Data.")

        for src, tgt, server, gpu, id in server_data:
            # ensure that the mult-dimensional dictionary is 
            # set up with both source and target as keys
            if not src in self.CONFIG:
                self.CONFIG[src] = {}
                self.CONFIG[src][tgt] = {}
            elif not tgt in self.CONFIG[src]:
                self.CONFIG[src][tgt] = {}

            self.CONFIG[src][tgt]['server'] = server
            self.CONFIG[src][tgt]['gpu'] = gpu
            self.CONFIG[src][tgt]['id'] = id
        db.close()

    # For a given source and target language, retrieve the URL
    # which corresponds to this language model.
    def get_language_pair_endpoint(self, src: str, tgt:str) -> str:
        ip, port = self.get_language_pair_server_IP_and_port(src, tgt)
        if ip and port:
            return f"http://{ip}:{port}/translator/translate"
        else:
            logger.error("IP Found: {}", ip)
            logger.error("Port Found: {}", port)
            logger.error("Source Language: {}", src)
            logger.error("Target Language: {}", tgt)
            raise Exception(f"Invalid Source / Target Language: {src}-{tgt}")

    # For a given source and target language, retrieve the IP and port
    # combination corresponding to where this model is being hosted.
    def get_language_pair_server_IP_and_port(self, src: str, tgt: str):
        try:
            server_name = self.get_server(src, tgt)
            server_ip = get_server_IP_from_config(server_name)
            server_port = get_server_port_from_config(server_name)
        except Exception:
            return None, None 

        return str(server_ip), int(server_port)

    # Check if the model setup actually contains
    # a given source-target language pair.
    def _contains_language_pair(self, src: str, tgt: str):
        if src in self.CONFIG:
            if tgt in self.CONFIG[src]:
                return True
        return False

    # Retrieve the name of the server in which a particular
    # source-target language pair is stored.
    def get_server(self, src: str, tgt: str) -> str | None:
        if self._contains_language_pair(src, tgt):
            server_name = self.CONFIG[src][tgt]['server']
            return str(server_name)
        return None

    # Each language model has an ID associated with it on its corresponding MT server port
    def get_language_pair_ID(self, src: str, tgt: str) -> int | None:
        if self._contains_language_pair(src, tgt):
            model_ID = self.CONFIG[src][tgt]['id']
            return int(model_ID)
        return None

    # All language pairs, represented as a list.
    # Note both combinations of the same two languages are included.
    def get_all_language_pairs(self) -> list[list]:
        pairs = []
        for src in self.CONFIG.keys():
            for tgt in self.CONFIG[src].keys():
                p = (src,tgt)
                pairs.append(p)
        return pairs

    # A list of all unique languages included
    # in the model setup.
    def get_all_languages(self) -> list:
        all_language_pairs = self.get_all_language_pairs()
        all_languages = list(set(list(numpy.concatenate(all_language_pairs).flat)))
        return all_languages

    # A list of all target languages included
    # in the model setup.
    def get_all_target_languages(self, src: str) -> list:
        all_languages = self.get_all_languages()
        source_lang_removed = [x for x in all_languages if x != src]
        return source_lang_removed

    # Retrieve the current and most
    # up-to-date model setup.
    def get_config(self) -> dict:
        return self.CONFIG

# imported and used in other classes
model_info = MTModelInformation()
