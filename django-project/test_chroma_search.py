"""
ChromaDB 검색 기능 테스트
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pjt.settings')
django.setup()

from reviews.chroma_utils import (
    search_similar_reviews,
    get_review_by_id,
    get_collection_stats,
    get_collection
)

def test_search():
    """검색 기능 테스트"""
    print("=" * 60)
    print("ChromaDB 검색 기능 테스트")
    print("=" * 60)
    
    # 컬렉션 통계
    stats = get_collection_stats()
    print(f"\n📊 컬렉션 통계:")
    print(f"  총 리뷰 수: {stats['total_reviews']}")
    print(f"  컬렉션 이름: {stats['collection_name']}")
    print(f"  DB 경로: {stats['db_path']}")
    
    # 첫 번째 리뷰 가져오기
    collection = get_collection()
    sample_results = collection.get(limit=1)
    if sample_results['ids']:
        sample_id = int(sample_results['ids'][0])
        sample_embedding = None
        
        # 임베딩 벡터 가져오기 (ChromaDB는 기본적으로 임베딩을 반환하지 않으므로 직접 가져와야 함)
        # 대신 첫 번째 리뷰의 임베딩을 사용
        print(f"\n🔍 리뷰 ID {sample_id}로 유사 리뷰 검색 테스트...")
        
        # 검색을 위해 실제 임베딩 벡터 사용
        # 첫 번째 리뷰의 임베딩을 가져와서 검색에 사용
        import pandas as pd
        import numpy as np
        df = pd.read_parquet('review_embeddings_final.parquet')
        sample_embedding = df[df['id'] == sample_id]['embedding_vector'].iloc[0]
        if isinstance(sample_embedding, np.ndarray):
            sample_embedding = sample_embedding.tolist()
        print(f"  임베딩 차원: {len(sample_embedding)}")
        
        results = search_similar_reviews(
            query_embedding=sample_embedding,
            n_results=5
        )
        
        print(f"\n✅ 검색 결과 ({len(results)}개):")
        for i, result in enumerate(results, 1):
            print(f"\n  {i}. 리뷰 ID: {result['review_id']}")
            print(f"     거리: {result['distance']:.4f}" if result['distance'] else "     거리: N/A")
            print(f"     영화 ID: {result['metadata'].get('movie_id', 'N/A')}")
            print(f"     사용자 ID: {result['metadata'].get('user_id', 'N/A')}")
            print(f"     메타 클래스: {result['metadata'].get('meta_class', 'N/A')}")
            if result['document']:
                doc_preview = result['document'][:100] + "..." if len(result['document']) > 100 else result['document']
                print(f"     내용: {doc_preview}")
    
    # 특정 리뷰 조회
    print(f"\n📖 리뷰 ID 104 조회 테스트...")
    review = get_review_by_id(104)
    if review:
        print(f"  ✅ 리뷰 찾음:")
        print(f"     영화 ID: {review['metadata'].get('movie_id', 'N/A')}")
        print(f"     사용자 ID: {review['metadata'].get('user_id', 'N/A')}")
        print(f"     메타 클래스: {review['metadata'].get('meta_class', 'N/A')}")
    else:
        print(f"  ❌ 리뷰를 찾을 수 없습니다.")
    
    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)

if __name__ == '__main__':
    test_search()

