import sqlite3
import numpy
from dotenv import dotenv_values
import pandas as pd

db = sqlite3.connect("app/database.sqlite")
cursor = db.cursor()

# -- JWT Configuration Variables --
app_config = dotenv_values('app/.env')

def get_server_IP_from_config(server: str) -> str:
    server_ip = str(app_config[f"{server}_IP"])
    return str(server_ip)

def get_server_port_from_config(server: str) -> int:
    server_ip = app_config[f"{server}_PORT"]
    return int(server_ip)

# -- Translation Model Information --
# The information provided by this class should be loaded into a python dictionary,
# assuming that it will not change once the models are up and running.
# Calling it for each translation would be an unnecessarily costly.

class MTModelInformation:
    # Language models can exist on different IPs and ports
    # This function will return which IP-port combination a
    # specific source and target language pair exists on
    def get_language_pair_server_IP_and_port(self, src: str, tgt: str):
        get_server_name = f"SELECT server FROM models WHERE source='{src}' AND target='{tgt}'"
        try:
            server_name = cursor.execute(get_server_name).fetchone()[0]
            server_ip = get_server_IP_from_config(server_name)
            server_port = get_server_port_from_config(server_name)
        except Exception:
            return None, None 

        print("----")
        print("IP & Port found for " + src + "," + tgt)
        print(server_ip)
        print(server_port)
        print("----")

        return str(server_ip), int(server_port)

    # Each language model has an ID associated with it on its corresponding MT server port
    def get_language_pair_ID(self, src: str, tgt: str) -> int:
        # change this in SQL to become ID and not port
        get_port_query = f"SELECT port FROM models WHERE source='{src}' AND target='{tgt}'"
        try:
            port = cursor.execute(get_port_query).fetchone()[0]
        except Exception:
            return None 
        return int(port)

    # The URL that will correspond to a specific source and target language
    def get_language_pair_endpoint(self, src: str, tgt:str) -> str:
        ip, port = self.get_language_pair_server_IP_and_port(src, tgt)
        if ip and port:
            return f"http://{ip}:{port}/translator/translate"
        else:
            return "Invalid Source / Target Language"

    def get_all_languages_pairs(self) -> list[list]:
        get_pairs_query = f"SELECT source,target FROM models"
        pairs = cursor.execute(get_pairs_query).fetchall()
        return pairs

    def get_all_languages(self) -> list:
        all_language_pairs = self.get_all_languages_pairs()
        all_languages = list(set(list(numpy.concatenate(all_language_pairs).flat)))
        return all_languages

    def get_all_target_languages(self, src: str) -> list:
        all_languages = self.get_all_languages()
        source_lang_removed = [x for x in all_languages if x != src]
        return source_lang_removed

model_info = MTModelInformation()