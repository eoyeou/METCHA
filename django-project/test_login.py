"""
로그인 테스트 스크립트
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pjt.settings')
django.setup()

from accounts.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

# 첫 번째 사용자 확인
user = User.objects.first()
if user:
    print(f"사용자: {user.username}")
    print(f"이메일: {user.email}")
    print(f"활성화: {user.is_active}")
    print(f"ID: {user.id}")
    
    # 비밀번호 설정 (없으면)
    user.set_password('test1234')
    user.save()
    print("비밀번호를 'test1234'로 설정했습니다.")
    
    # 인증 테스트
    result = authenticate(username=user.username, password='test1234')
    if result:
        print("인증 성공!")
        # 토큰 확인
        token, created = Token.objects.get_or_create(user=user)
        print(f"토큰: {token.key}")
    else:
        print("인증 실패!")
else:
    print("사용자가 없습니다.")

