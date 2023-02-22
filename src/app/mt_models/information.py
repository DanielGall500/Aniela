import sqlite3
import numpy
from dotenv import dotenv_values

db = sqlite3.connect("app/database.sqlite")
cursor = db.cursor()

# -- JWT Configuration Variables --
app_config = dotenv_values('app/.env')

class MTModelInformation:
    MT_SERVER_IP = str(app_config["MT_SERVER_IP"])
    MT_SERVER_PORT = int(app_config["MT_SERVER_PORT"])
    MT_SERVER_URL = f"http://{MT_SERVER_IP}:{MT_SERVER_PORT}/translator/translate"

    def get_language_pair_port(self, src: str, tgt: str) -> int:
        get_port_query = f"SELECT port FROM models WHERE source='{src}' AND target='{tgt}'"
        try:
            port = cursor.execute(get_port_query).fetchone()[0]
        except Exception:
            return -1 
        return int(port)

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

    def get_server_url(self) -> str:
        return self.MT_SERVER_URL

    def get_server_port(self) -> int:
        return self.MT_SERVER_PORT

    def get_server_ip(self) -> str:
        return self.MT_SERVER_IP

model_info = MTModelInformation()