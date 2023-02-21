from app.mt_models.information import MTModelInformation
from sacremoses import MosesTokenizer, MosesDetokenizer, MosesPunctNormalizer
from app.mt_models.information import MTModelInformation
from threading import Thread
import socket
import nltk
import requests

MT_SERVER_IP = "0.0.0.0"
MT_SERVER_PORT = 8080
MT_SERVER_URL = f"http://{MT_SERVER_IP}:{MT_SERVER_PORT}/translator/translate"

STATUS_OK = "ok"
STATUS_ERROR = "error"
mpn = MosesPunctNormalizer()
moses_tokenizers = {}
moses_detokenizers = {}

model_translation_test = {
    "en": "Climate change",
    "de": "Klimawandel",
    "it": "Cambiamento climatico",
    "fr": "Changement climatique",
    "pl": "Zmiana climatu",
    "ga": "Athrú aeráide"
}

model_info = MTModelInformation()

class MTRequestHandler:
    def __init__(self):
        pass

    async def translate(self, src: str, tgt: str, text: str):

        out = {}
        out['result'] = {}
        out['state'] = "OK"

        # get all target languages as a list
        target_langs = []
        if tgt == 'all':
            target_langs = model_info.get_all_target_languages(src)
        else:
            target_langs = [tgt]

        print(target_langs)

        # allocate the appropriate model for each src-tgt pair
        model_ids = [model_info.get_language_pair_port(src,t) for t in target_langs]
        print(model_ids)

        # iterate through each language model that we need
        for i,model_id in enumerate(model_ids):
            print("Running for target " + target_langs[i])
            print(f"Model id: {model_id}")
            sentences = self.preprocess(text, src)
            print(sentences)

            model_id = 2001
            sentences = [{'src': s, 'id': model_id} for s in sentences]
            print(sentences)

            # send the translation request to the MT server
            response = requests.post(url=MT_SERVER_URL, json=sentences)
            print(sentences)
            print(response)

            # TODO: error handling
            list_tgt_lines = []
            list_from_server = response.json()[0]
            if response.status_code == 200:
                # only output result under the status of OK
                for result_dict in list_from_server:
                    list_tgt_lines.append(result_dict['tgt'])
                trans_text = self.postprocess(list_tgt_lines, tgt)
                out['result'][tgt] = trans_text
            else:
                out['result'][tgt] = "An error occurred."

        log_msg1 = f'src_lang:{src}|tgt_lang:{tgt}|src:{text}'
        log_msg2 = f'pre_processed:{sentences}'
        log_msg3 = f'state:{out["state"]}'
        print('----------------')
        print(log_msg1)
        print(log_msg2)
        print('\n')
        print(log_msg3)
        return out

    def preprocess(self, src_text: str, src_lang: str):
        mt = moses_tokenizers.get(src_lang, None)
        if not mt:
            mt = MosesTokenizer(lang=src_lang)
            moses_tokenizers[src_lang] = mt
        sentence_list = []
        # first split lines by \n , so to keep the format of the original
        lines = src_text.splitlines()  # first split with \n
        for line in lines:
            # to split the long sentence into small sentence
            sents = nltk.sent_tokenize(line)  # this gives us a list of sentences
            for sent in sents:
                # normalize and tokenize the sentences using sacremoses
                sent_normalized = mpn.normalize(sent)
                sent_tokenized = mt.tokenize(sent_normalized, return_str=True)
                sentence_list.append(sent_tokenized)
            # TODO: consider the \n in the input text. So to keep the original format
            # sentence_list.append('\n')  # use \n to keep original input format
        return sentence_list

    def postprocess(self, tgt_sents: str, tgt_lang: str):
        mt = moses_detokenizers.get(tgt_lang, None)
        if not mt:
            mt = MosesDetokenizer(lang=tgt_lang)
            moses_detokenizers[tgt_lang] = mt
        tgt_text = " ".join(tgt_sents)
        tgt_text = mt.detokenize(tgt_text.split())
        return tgt_text

    def get_available_languages(self):
        return model_info.get_all_languages()

class MTServerConnection:
    def __init__(self, server_ip: str, server_port: str):
        self.MT_SERVER_IP = server_ip
        self.MT_SERVER_PORT = server_port
        self.model_connections = {}

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
        language_pairs = model_info.get_all_languages_pairs()
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


model_connections = MTServerConnection(MT_SERVER_IP, MT_SERVER_PORT)
model_info = MTModelInformation()
