"""
ChromaDB를 사용한 리뷰 임베딩 검색 유틸리티
"""
import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import numpy as np

# ChromaDB 클라이언트 초기화
CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'chroma_db')
COLLECTION_NAME = 'review_embeddings'

_client = None
_collection = None


def get_chroma_client():
    """ChromaDB 클라이언트 싱글톤"""
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=CHROMA_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
    return _client


def get_collection():
    """ChromaDB 컬렉션 싱글톤"""
    global _collection
    if _collection is None:
        client = get_chroma_client()
        try:
            _collection = client.get_collection(COLLECTION_NAME)
        except:
            raise Exception(f"컬렉션 '{COLLECTION_NAME}'을 찾을 수 없습니다. 먼저 create_chroma_db.py를 실행하세요.")
    return _collection


def search_similar_reviews(
    query_embedding: List[float],
    n_results: int = 10,
    movie_id: Optional[int] = None,
    user_id: Optional[int] = None,
    meta_class: Optional[str] = None
) -> List[Dict]:
    """
    유사한 리뷰 검색
    
    Args:
        query_embedding: 검색할 임베딩 벡터
        n_results: 반환할 결과 수
        movie_id: 특정 영화 ID로 필터링 (선택)
        user_id: 특정 사용자 ID로 필터링 (선택)
        meta_class: 메타 클래스로 필터링 (선택)
    
    Returns:
        검색 결과 리스트 (각 항목은 review_id, distance, metadata 포함)
    """
    collection = get_collection()
    
    # 필터 조건 구성
    where = {}
    if movie_id is not None:
        where['movie_id'] = str(movie_id)
    if user_id is not None:
        where['user_id'] = str(user_id)
    if meta_class is not None:
        where['meta_class'] = meta_class
    
    # 검색 실행
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where if where else None
    )
    
    # 결과 포맷팅
    formatted_results = []
    if results['ids'] and len(results['ids'][0]) > 0:
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'review_id': int(results['ids'][0][i]),
                'distance': results['distances'][0][i] if 'distances' in results else None,
                'metadata': results['metadatas'][0][i] if 'metadatas' in results else {},
                'document': results['documents'][0][i] if 'documents' in results else None
            })
    
    return formatted_results


def get_review_by_id(review_id: int) -> Optional[Dict]:
    """
    리뷰 ID로 임베딩 정보 가져오기
    
    Args:
        review_id: 리뷰 ID
    
    Returns:
        리뷰 임베딩 정보 또는 None
    """
    collection = get_collection()
    
    try:
        results = collection.get(ids=[str(review_id)])
        if results['ids'] and len(results['ids']) > 0:
            return {
                'review_id': int(results['ids'][0]),
                'metadata': results['metadatas'][0] if 'metadatas' in results else {},
                'document': results['documents'][0] if 'documents' in results else None
            }
    except:
        pass
    
    return None


def get_collection_stats() -> Dict:
    """컬렉션 통계 정보 반환"""
    collection = get_collection()
    count = collection.count()
    return {
        'total_reviews': count,
        'collection_name': COLLECTION_NAME,
        'db_path': CHROMA_DB_PATH
    }

