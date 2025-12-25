"""
.env 파일 확인 스크립트
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
env_file = BASE_DIR / '.env'

print("=" * 60)
print(".env 파일 확인")
print("=" * 60)

if not env_file.exists():
    print("\n[ERROR] .env 파일이 없습니다!")
    print(f"경로: {env_file}")
    print("\n.env 파일을 생성하고 다음 형식으로 추가하세요:")
    print("TMDB_API_KEY=your_api_key_here")
else:
    print(f"\n.env 파일 존재: {env_file}")
    print(f"파일 크기: {env_file.stat().st_size} bytes")
    
    # .env 파일 읽기 (TMDB 관련만)
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    tmdb_found = False
    print("\n.env 파일 내용 (TMDB 관련):")
    for i, line in enumerate(lines, 1):
        if 'TMDB' in line.upper() or 'API' in line.upper():
            tmdb_found = True
            # 민감한 정보는 일부만 표시
            if '=' in line:
                key, value = line.split('=', 1)
                value = value.strip()
                if len(value) > 10:
                    display_value = value[:10] + '...' + value[-5:]
                else:
                    display_value = '***'
                print(f"  라인 {i}: {key.strip()}={display_value}")
                print(f"    전체 길이: {len(value)} 문자")
                
                # 공백이나 따옴표 확인
                if value.startswith('"') or value.startswith("'"):
                    print(f"    [경고] 따옴표가 포함되어 있습니다!")
                if value.startswith(' ') or value.endswith(' '):
                    print(f"    [경고] 앞뒤 공백이 있습니다!")
    
    if not tmdb_found:
        print("  [경고] TMDB_API_KEY를 찾을 수 없습니다!")
        print("\n.env 파일에 다음을 추가하세요:")
        print("TMDB_API_KEY=your_api_key_here")

print("\n" + "=" * 60)

