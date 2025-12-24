"""
실패한 영화 목록 확인 스크립트
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pjt.settings')
django.setup()

from movies.models import Movie

failed = Movie.objects.filter(heaviness__isnull=True, satisfaction__isnull=True)

print(f"\nFailed movies (Total: {failed.count()}):")
print("=" * 80)

for m in failed:
    try:
        desc = m.description[:50] if m.description and len(m.description) > 0 else "No description"
        print(f"ID: {m.id:3d} | {m.title} ({m.release_year})")
        print(f"      Original Title: {m.original_title or 'N/A'}")
        print(f"      Description: {desc}...")
        print(f"      Director: {m.director}")
        print(f"      Has Description: {bool(m.description and len(m.description) > 50)}")
        print("-" * 80)
    except UnicodeEncodeError:
        print(f"ID: {m.id:3d} | Movie ID {m.id} ({m.release_year})")
        print(f"      Has Description: {bool(m.description and len(m.description) > 50)}")
        print("-" * 80)

