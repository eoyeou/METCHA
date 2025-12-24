from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reviews'
    
    def ready(self):
        """
        Django 앱이 시작될 때 실행되는 메서드
        임베딩 모델을 미리 로딩하여 검색 시 대기 시간을 제거
        """
        # 서버 시작 시 임베딩 모델 미리 로딩
        try:
            from .embedding_utils import get_embedding_model
            print("[시작] 임베딩 모델 사전 로딩 중...")
            get_embedding_model()
            print("[완료] 임베딩 모델 사전 로딩 완료")
        except Exception as e:
            # 임베딩 모델 로딩 실패 시에도 서버는 계속 실행
            print(f"[경고] 임베딩 모델 사전 로딩 실패: {e}")
            print("[경고] 첫 검색 시 모델이 로딩됩니다.")