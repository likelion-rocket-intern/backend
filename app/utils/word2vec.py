from gensim.models import KeyedVectors
import os
import sys
import threading

class WordVectorModelLoader:
    DATA_DIR = "datas/"

    _instance = None # 싱글톤 인스턴스를 저장할 변수
    _model = None    # Word2Vec 모델을 저장할 변수
    _lock = threading.Lock() # 멀티쓰레드 환경에서 안전하게 로드하기 위한 락

    def __new__(cls):
        # __new__ 메서드는 인스턴스가 생성되기 전에 호출됩니다.
        # 이를 통해 인스턴스가 하나만 생성되도록 제어할 수 있습니다.
        if cls._instance is None:
            with cls._lock: # 쓰레드 락을 사용하여 여러 쓰레드가 동시에 인스턴스를 만들지 못하게 함
                if cls._instance is None: # 이중 체크 (double-checked locking)
                    cls._instance = super(WordVectorModelLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # __init__은 인스턴스가 생성될 때마다 호출될 수 있으므로,
        # 모델 로딩 로직은 한 번만 실행되도록 보호해야 합니다.
        if WordVectorModelLoader._model is None:
            self.load_model()

    def load_model(self):
        # 모델 로딩 로직
        model_file_path = f'{WordVectorModelLoader.DATA_DIR}/cc.ko.300.vec' # 실제 모델 파일 경로로 변경하세요!
        
        # 모델 파일 경로 절대 경로 확인 (로그에 남기면 디버깅에 좋음)
        print(f"[ModelLoader] 모델 파일 경로: {os.path.abspath(model_file_path)}")

        try:
            print(f"[ModelLoader] '{model_file_path}' 모델을 로드 중입니다. (시간이 다소 소요될 수 있습니다)...")
            # largefile=True 제거, binary=False, encoding='utf-8' 유지
            WordVectorModelLoader._model = KeyedVectors.load_word2vec_format(
                                                model_file_path,
                                                binary=False,  # .vec 파일은 텍스트 형식
                                                no_header=False,  # 첫 줄에 헤더가 있음 (2000000 300)
                                                encoding='utf-8',
                                                unicode_errors='ignore'  # 인코딩 에러 무시
                                            )
            print("[ModelLoader] 모델 로드 성공!")
        except FileNotFoundError:
            print(f"[ModelLoader] 오류: 모델 파일이 '{model_file_path}' 경로에 없습니다.")
            WordVectorModelLoader._model = None
        except Exception as e:
            print(f"[ModelLoader] 모델 로드 중 예상치 못한 오류 발생: {e}")
            WordVectorModelLoader._model = None

    def get_model(self):
        # 로드된 모델 인스턴스를 반환
        if WordVectorModelLoader._model is None:
            # 이 경우는 보통 로드 실패했거나, 초기화가 제대로 안 됐을 때 발생
            print("[ModelLoader] 경고: 모델이 로드되지 않았습니다. get_model 전에 load_model이 호출되었는지 확인하세요.")
        return WordVectorModelLoader._model