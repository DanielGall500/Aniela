from sacremoses import MosesTokenizer, MosesPunctNormalizer, MosesDetokenizer
from app.mt_models.information import model_info
from threading import Thread
from loguru import logger
import nltk
import requests

nltk.download("punkt")

class MTRequestHandler:
    # Create sacremoses
    mpn = MosesPunctNormalizer()
    moses_tokenizers = {}
    moses_detokenizers = {}

    # Messages for the various return states
    STATUS_OK = "SUCCESS"
    STATUS_ERROR = "ERROR"
        
    def translate(self, src: str, tgt: str, text: str, timeout: float = None):
        # Assume an error until proven successful!
        out = {'state': self.STATUS_ERROR, 'result': {}}

        # We can choose to translate the input text into all possible target languages.
        # Otherwise, we translate only to the target language specified.
        target_langs = []
        if tgt == 'all':
            target_langs = model_info.get_all_target_languages(src)
        else:
            target_langs = [tgt]

        # Allocate the appropriate model for each src-tgt pair
        model_server_endpoints = [model_info.get_language_pair_endpoint(src,t) for t in target_langs]
        model_ids = [model_info.get_language_pair_ID(src,t) for t in target_langs]
        num_models = len(model_ids)

        # Iterate through each language model that we need
        for i in range(num_models):
            model_server_endpoint = model_server_endpoints[i]
            model_id = model_ids[i]

            # Convert the input text to a form more suitable for
            # the language model. This is known as tokenization.
            # This also breaks the text into individual sentences
            tokenize_input = self._tokenize(text, src)

            # Associate each input sentence with the appropriate MT model 
            tokenized_sentences = [{'src': sentence, 'id': model_id} for sentence in tokenize_input]

            response = self._send_request_to_MT_server(model_server_endpoint, tokenized_sentences, timeout)

            if self._is_valid_server_response(response):
                # Put together all the returned sentences into one string
                target_output = self._combine_response_sentences(response)

                # Detokenize this returned output to make it more reader-friendly
                detokenized_target_output = self._detokenize(target_output, tgt)

                # Save the resulting translation to the response
                out['result'][target_langs[i]] = detokenized_target_output
                out['state'] = self.STATUS_OK

        return out

    def get_available_languages(self):
        return model_info.get_all_languages()

    def _tokenize(self, src_text: str, src_lang: str):
        # retrieve the tokenizer for a specific language
        mt = self.moses_tokenizers.get(src_lang, None)

        if not mt:
            mt = MosesTokenizer(lang=src_lang)
            self.moses_tokenizers[src_lang] = mt

        sentence_list = []
        # first split lines by \n , so to keep the format of the original
        lines = src_text.splitlines()  # first split with \n
        for line in lines:
            # to split the long sentence into small sentence
            sents = nltk.sent_tokenize(line)  # this gives us a list of sentences
            for sent in sents:
                # normalize and tokenize the sentences using sacremoses
                sent_normalized = self.mpn.normalize(sent)
                sent_tokenized = mt.tokenize(sent_normalized, return_str=True)
                sentence_list.append(sent_tokenized)
        return sentence_list

    def _detokenize(self, tgt_sents: str, tgt_lang: str):
        mt = self.moses_detokenizers.get(tgt_lang, None)
        if not mt:
            mt = MosesDetokenizer(lang=tgt_lang)
            self.moses_detokenizers[tgt_lang] = mt
        tgt_text = mt.detokenize(tgt_sents.split())
        return tgt_text

    def _send_request_to_MT_server(self, endpoint: str, sentences: list[str], timeout: float = None):
        return requests.post(url=endpoint, json=sentences, timeout=timeout)

    def _is_valid_server_response(self, response: requests.Response):
        return response.status_code == 200

    def _combine_response_sentences(self, target_sentences) -> str:
        # TODO: error handling
        target_output = " ".join(target_sentence["tgt"] for target_sentence in target_sentences)
        return target_output

    def _log_info(self, src: str, tgt: str, text: str):
        logger.info("-- New Translation --")
        logger.info(f"source: {src}, target: {tgt}")
        logger.info(f"Input: {text}")
        logger.info(f"Output: {text}")
        logger.info("----")