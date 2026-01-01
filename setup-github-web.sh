#!/bin/bash

# 웹 환경에서 GitHub 사용을 위한 빠른 설정 스크립트
# Quick setup script for GitHub usage in web environment

echo "=================================="
echo "GitHub 웹 환경 설정 스크립트"
echo "GitHub Web Environment Setup"
echo "=================================="
echo ""

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# GitHub 사용자 이름 입력
echo -e "${YELLOW}GitHub 사용자 이름을 입력하세요:${NC}"
read -p "GitHub Username: " GITHUB_USER

if [ -z "$GITHUB_USER" ]; then
    echo -e "${RED}오류: 사용자 이름이 필요합니다.${NC}"
    exit 1
fi

# Personal Access Token 입력
echo ""
echo -e "${YELLOW}GitHub Personal Access Token을 입력하세요:${NC}"
echo -e "${YELLOW}(토큰 생성: https://github.com/settings/tokens/new)${NC}"
read -sp "Token (입력 내용은 숨겨집니다): " GITHUB_TOKEN
echo ""

if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}오류: Personal Access Token이 필요합니다.${NC}"
    exit 1
fi

# Git 설정
echo ""
echo -e "${GREEN}[1/4] Git 전역 설정 중...${NC}"

# 사용자 정보 설정
if ! git config --global user.name > /dev/null 2>&1; then
    echo -e "${YELLOW}Git 사용자 이름 설정${NC}"
    git config --global user.name "$GITHUB_USER"
fi

if ! git config --global user.email > /dev/null 2>&1; then
    echo -e "${YELLOW}Git 이메일 설정${NC}"
    read -p "Git Email: " GIT_EMAIL
    git config --global user.email "$GIT_EMAIL"
fi

# Credential helper 설정
echo -e "${GREEN}[2/4] Git credential helper 설정 중...${NC}"
git config --global credential.helper store

# 환경 변수 설정 파일 생성
echo -e "${GREEN}[3/4] 환경 변수 파일 생성 중...${NC}"

cat > .env.github << EOF
# GitHub 인증 정보
# 주의: 이 파일을 절대 커밋하지 마세요!
export GITHUB_USER="$GITHUB_USER"
export GITHUB_TOKEN="$GITHUB_TOKEN"

# GitHub API URL
export GITHUB_API="https://api.github.com"
export GITHUB_URL="https://github.com"

# Git 원격 저장소 URL 헬퍼 함수
github_url() {
    local repo=\$1
    echo "https://\${GITHUB_USER}:\${GITHUB_TOKEN}@github.com/\${GITHUB_USER}/\${repo}.git"
}
EOF

# .gitignore 업데이트
if [ ! -f .gitignore ]; then
    touch .gitignore
fi

if ! grep -q ".env.github" .gitignore; then
    echo ".env.github" >> .gitignore
    echo "*.env" >> .gitignore
    echo ".env.*" >> .gitignore
fi

echo -e "${GREEN}[4/4] GitHub 연결 테스트 중...${NC}"

# API 테스트
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: token $GITHUB_TOKEN" \
    https://api.github.com/user)

if [ "$HTTP_CODE" == "200" ]; then
    echo -e "${GREEN}✓ GitHub 인증 성공!${NC}"

    # 사용자 정보 가져오기
    USER_INFO=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user)
    USER_LOGIN=$(echo $USER_INFO | grep -o '"login":"[^"]*' | cut -d'"' -f4)
    USER_NAME=$(echo $USER_INFO | grep -o '"name":"[^"]*' | cut -d'"' -f4)

    echo ""
    echo "=================================="
    echo -e "${GREEN}설정 완료!${NC}"
    echo "=================================="
    echo "사용자: $USER_NAME (@$USER_LOGIN)"
    echo ""
    echo "다음 단계:"
    echo "1. 환경 변수 로드:"
    echo "   source .env.github"
    echo ""
    echo "2. Git 명령 사용 예제:"
    echo "   git clone https://\${GITHUB_USER}:\${GITHUB_TOKEN}@github.com/\${GITHUB_USER}/repository.git"
    echo ""
    echo "3. GitHub CLI 사용:"
    echo "   gh auth login --with-token <<< \$GITHUB_TOKEN"
    echo ""
else
    echo -e "${RED}✗ GitHub 인증 실패 (HTTP $HTTP_CODE)${NC}"
    echo "토큰을 확인하고 다시 시도하세요."
    exit 1
fi

echo ""
echo -e "${YELLOW}⚠️  보안 주의사항:${NC}"
echo "- .env.github 파일을 절대 공유하거나 커밋하지 마세요"
echo "- 토큰이 노출되면 즉시 GitHub에서 삭제하세요"
echo "- 정기적으로 토큰을 갱신하세요"
echo ""
