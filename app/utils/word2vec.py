from gensim.models import KeyedVectors
import json
import os
import sys
import threading
import numpy as np
import logging

logger = logging.getLogger(__name__)

class WordVectorModelLoader:
    DATA_DIR = "datas/"

    _instance = None
    _model = None
    _json_keywords_list = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(WordVectorModelLoader, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

    def load_model(self):
        with self._lock:
            if self._model is not None:
                logger.info("[ModelLoader] Model already loaded, skipping...")
                return

            model_file_path = f'{WordVectorModelLoader.DATA_DIR}/cc.ko.300.vec'
            logger.info(f"[ModelLoader] Loading model from: {os.path.abspath(model_file_path)}")

            try:
                logger.info("[ModelLoader] Loading Word2Vec model (this may take a while)...")
                self._model = KeyedVectors.load_word2vec_format(
                    model_file_path,
                    binary=False,
                    no_header=False,
                    encoding='utf-8',
                    unicode_errors='ignore',
                    limit=None,
                    datatype=np.float32
                )

                if '' in self._model.key_to_index:
                    del self._model.key_to_index['']
                    logger.info("[ModelLoader] Removed empty string vector")

                logger.info("[ModelLoader] Model loaded successfully!")
            except FileNotFoundError:
                logger.error(f"[ModelLoader] Error: Model file not found at '{model_file_path}'")
                self._model = None
                raise
            except Exception as e:
                logger.error(f"[ModelLoader] Unexpected error while loading model: {e}")
                self._model = None
                raise

    def load_json_keywords_list(self):
        with self._lock:
            if self._json_keywords_list is not None:
                logger.info("[ModelLoader] Keywords already loaded, skipping...")
                return

            json_file_path = f'{WordVectorModelLoader.DATA_DIR}/keywords.json'
            try:
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    self._json_keywords_list = json.load(f)
                logger.info("[ModelLoader] Keywords loaded successfully!")
            except Exception as e:
                logger.error(f"[ModelLoader] Error loading keywords: {e}")
                self._json_keywords_list = None
                raise

    def get_model(self):
        return self._model

    def get_json_keywords_list(self):
        return self._json_keywords_list