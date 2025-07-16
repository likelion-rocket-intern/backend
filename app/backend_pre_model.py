import logging
from app.utils.word2vec import WordVectorModelLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_model() -> None:
    logger.info("Starting model initialization")
    try:
        model = WordVectorModelLoader().get_model()
        if model is None:
            logger.warning("Model initialization failed, but continuing...")
        else:
            logger.info("Model successfully loaded")
    except Exception as e:
        logger.error(f"Unexpected error during model initialization: {e}")
        raise e

def init_json_keywords_list() -> None:
    logger.info("Starting json keywords list initialization")
    try:
        json_keywords_list = WordVectorModelLoader().get_json_keywords_list()
        if json_keywords_list is None:
            logger.warning("Json keywords list initialization failed, but continuing...")
        else:
            logger.info("Json keywords list successfully loaded")
    except Exception as e:
        logger.error(f"Unexpected error during json keywords list initialization: {e}")
        raise e

if __name__ == "__main__":
    init_model()
    init_json_keywords_list()