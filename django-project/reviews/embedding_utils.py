"""
검색어 임베딩 생성 유틸리티
"""
import os
from typing import List
import numpy as np

# 임베딩 모델 싱글톤
_embedding_model = None
_tokenizer = None


def get_embedding_model():
    """임베딩 모델 로드 (싱글톤)"""
    global _embedding_model, _tokenizer
    
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            
            # 환경 변수로 모델 선택 가능 (기본값: 원본 parquet 파일 생성 모델)
            model_name = os.getenv('EMBEDDING_MODEL', 'BAAI/bge-m3')
            
            # 원본 모델: BAAI/bge-m3
            # - 크기: ~2.2GB, 차원: 1024, 다국어 지원, 한국어 성능 우수
            # - parquet 파일 생성 시 사용한 모델과 동일
            # - normalize_embeddings=True로 정규화됨
            
            # 가벼운 대안 모델들:
            # 1. sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
            #    - 크기: ~420MB, 차원: 384, 다국어 지원, 빠름 (패딩 필요)
            # 2. all-MiniLM-L6-v2
            #    - 크기: ~80MB, 차원: 384, 영어 전용, 매우 빠름 (패딩 필요)
            
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            print(f"[INFO] 임베딩 모델 로딩 중: {model_name}")
            print(f"[INFO] 디바이스: {device}")
            print(f"[INFO] 더 가벼운 모델을 원하면 환경 변수 EMBEDDING_MODEL 설정")
            _embedding_model = SentenceTransformer(model_name, device=device)
            model_dim = _embedding_model.get_sentence_embedding_dimension()
            print(f"[INFO] 임베딩 모델 로딩 완료 (차원: {model_dim})")
            
            if model_dim != 1024:
                print(f"[경고] 모델 차원이 1024가 아닙니다. ChromaDB와 호환성 문제가 있을 수 있습니다.")
        except ImportError:
            raise ImportError("sentence-transformers가 설치되지 않았습니다. pip install sentence-transformers")
        except Exception as e:
            print(f"[ERROR] 임베딩 모델 로딩 실패: {e}")
            raise
    
    return _embedding_model


def embed_text(text: str) -> List[float]:
    """
    텍스트를 임베딩 벡터로 변환
    
    Args:
        text: 임베딩할 텍스트
    
    Returns:
        1024차원 임베딩 벡터 (리스트)
    """
    model = get_embedding_model()
    
    # 텍스트 임베딩 생성 (원본 모델과 동일한 설정)
    # normalize_embeddings=True: 코사인 유사도 계산을 위해 자동 정규화
    embedding = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    
    # 모델 차원 확인
    model_dim = model.get_sentence_embedding_dimension()
    
    if model_dim == 1024:
        # 원본 모델과 동일한 차원
        return embedding.tolist()
    elif model_dim < 1024:
        # 패딩으로 1024차원으로 확장 (다른 모델 사용 시)
        # 주의: 패딩은 유사도 계산에 영향을 줄 수 있음
        padding = np.zeros(1024 - model_dim)
        embedding = np.concatenate([embedding, padding])
        # 패딩 후 다시 정규화
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        return embedding.tolist()
    else:
        # 차원 축소: 처음 1024개만 사용
        embedding = embedding[:1024]
        # 정규화
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        return embedding.tolist()


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    여러 텍스트를 일괄 임베딩
    
    Args:
        texts: 임베딩할 텍스트 리스트
    
    Returns:
        임베딩 벡터 리스트
    """
    model = get_embedding_model()
    # 원본 모델과 동일한 설정
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True, batch_size=32)
    
    model_dim = model.get_sentence_embedding_dimension()
    
    if model_dim == 1024:
        # 원본 모델과 동일한 차원
        return embeddings.tolist()
    elif model_dim < 1024:
        # 패딩으로 1024차원으로 확장 (다른 모델 사용 시)
        padding = np.zeros((len(texts), 1024 - model_dim))
        embeddings = np.concatenate([embeddings, padding], axis=1)
        # 패딩 후 다시 정규화
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = np.where(norms > 0, embeddings / norms, embeddings)
        return embeddings.tolist()
    else:
        # 차원 축소
        embeddings = embeddings[:, :1024]
        # 정규화
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = np.where(norms > 0, embeddings / norms, embeddings)
        return embeddings.tolist()

