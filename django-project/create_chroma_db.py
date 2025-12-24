"""
Parquet 파일에서 리뷰 임베딩을 읽어서 ChromaDB 벡터 데이터베이스 생성
"""
import os
import sys
import django
import pandas as pd
import chromadb
from chromadb.config import Settings

# Django 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pjt.settings')
django.setup()

from reviews.models import Review

def create_chroma_db(parquet_file='review_embeddings_final.parquet', 
                     db_path='./chroma_db',
                     collection_name='review_embeddings'):
    """
    Parquet 파일에서 임베딩 데이터를 읽어 ChromaDB에 저장
    
    Args:
        parquet_file: parquet 파일 경로
        db_path: ChromaDB 저장 경로
        collection_name: ChromaDB 컬렉션 이름
    """
    print(f"📖 Parquet 파일 읽기: {parquet_file}")
    
    # Parquet 파일 읽기
    try:
        df = pd.read_parquet(parquet_file)
        print(f"✅ 데이터 로드 완료: {df.shape[0]}개 행, {df.shape[1]}개 열")
        print(f"📊 컬럼: {df.columns.tolist()}")
        print(f"\n첫 5개 행 미리보기:")
        print(df.head())
    except Exception as e:
        print(f"❌ Parquet 파일 읽기 실패: {e}")
        return
    
    # ChromaDB 클라이언트 생성 (로컬 저장소)
    print(f"\n🗄️  ChromaDB 초기화: {db_path}")
    client = chromadb.PersistentClient(path=db_path, settings=Settings(anonymized_telemetry=False))
    
    # 기존 컬렉션이 있으면 삭제
    try:
        client.delete_collection(collection_name)
        print(f"🗑️  기존 컬렉션 '{collection_name}' 삭제됨")
    except:
        pass
    
    # 새 컬렉션 생성 (코사인 거리 사용)
    # ChromaDB는 기본적으로 L2 거리를 사용하지만, 코사인 유사도가 더 적합
    # 코사인 거리 = 1 - 코사인 유사도 (0~2 범위)
    collection = client.create_collection(
        name=collection_name,
        metadata={"description": "Movie review embeddings", "hnsw:space": "cosine"}
    )
    print(f"✅ 컬렉션 '{collection_name}' 생성 완료")
    
    # 데이터 준비 및 추가
    print(f"\n📝 데이터를 ChromaDB에 추가 중...")
    
    # 임베딩 벡터와 메타데이터 추출
    embeddings = []
    ids = []
    metadatas = []
    documents = []
    
    for idx, row in df.iterrows():
        # 리뷰 ID
        review_id = str(int(row['id']))
        
        # 임베딩 벡터 추출 (numpy array를 리스트로 변환)
        import numpy as np
        embedding = row['embedding_vector']
        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()
        elif isinstance(embedding, list):
            embedding = embedding
        else:
            print(f"⚠️  임베딩 형식 확인 필요 (행 {idx}): {type(embedding)}")
            continue
        
        # 문서 내용 (처리된 리뷰 텍스트)
        document = str(row['processed_text']) if 'processed_text' in df.columns else f"Review {review_id}"
        
        # 메타데이터 준비
        metadata = {
            'review_id': review_id,
            'movie_id': str(int(row['movie_id'])) if 'movie_id' in df.columns else None,
            'user_id': str(int(row['user_id'])) if 'user_id' in df.columns else None,
        }
        
        # 추가 메타데이터
        if 'meta_class' in df.columns:
            meta_class_val = row['meta_class']
            if pd.notna(meta_class_val) and meta_class_val is not None:
                metadata['meta_class'] = str(meta_class_val)
        
        if 'keywords' in df.columns:
            keywords = row['keywords']
            if keywords is not None:
                try:
                    if isinstance(keywords, np.ndarray):
                        if len(keywords) > 0:
                            metadata['keywords'] = ', '.join([str(k) for k in keywords.tolist()])
                    elif isinstance(keywords, list):
                        if len(keywords) > 0:
                            metadata['keywords'] = ', '.join([str(k) for k in keywords])
                    else:
                        metadata['keywords'] = str(keywords)
                except:
                    pass  # keywords 처리 실패 시 무시
        
        # None 값 제거
        metadata = {k: v for k, v in metadata.items() if v is not None}
        
        embeddings.append(embedding)
        ids.append(review_id)
        metadatas.append(metadata)
        documents.append(document)
        
        # 진행 상황 출력 (100개마다)
        if (idx + 1) % 100 == 0:
            print(f"  처리 중: {idx + 1}/{len(df)}")
    
    # ChromaDB에 일괄 추가
    print(f"\n💾 ChromaDB에 {len(embeddings)}개 임베딩 추가 중...")
    collection.add(
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas,
        documents=documents
    )
    
    print(f"✅ 완료! {len(embeddings)}개 리뷰 임베딩이 ChromaDB에 저장되었습니다.")
    print(f"📁 저장 위치: {os.path.abspath(db_path)}")
    
    # 테스트 쿼리
    print(f"\n🔍 테스트 쿼리 실행...")
    results = collection.query(
        query_embeddings=[embeddings[0]],
        n_results=3
    )
    print(f"✅ 쿼리 성공! {len(results['ids'][0])}개 결과 반환")
    
    return collection

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Parquet 파일에서 ChromaDB 벡터 DB 생성')
    parser.add_argument('--parquet', type=str, default='review_embeddings_final.parquet',
                        help='Parquet 파일 경로')
    parser.add_argument('--db-path', type=str, default='./chroma_db',
                        help='ChromaDB 저장 경로')
    parser.add_argument('--collection', type=str, default='review_embeddings',
                        help='ChromaDB 컬렉션 이름')
    
    args = parser.parse_args()
    
    create_chroma_db(
        parquet_file=args.parquet,
        db_path=args.db_path,
        collection_name=args.collection
    )

