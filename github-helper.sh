#!/bin/bash

# GitHub Helper Script for Web Claude Code
# 웹 Claude Code에서 GitHub를 쉽게 사용하기 위한 헬퍼 스크립트

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 도움말 함수
show_help() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}GitHub Helper - 웹 Claude Code용${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "사용법: ./github-helper.sh [명령어]"
    echo ""
    echo "명령어:"
    echo "  setup       - GitHub 인증 설정"
    echo "  test        - GitHub 연결 테스트"
    echo "  clone       - 저장소 clone"
    echo "  push        - 현재 브랜치 push"
    echo "  repos       - 내 저장소 목록"
    echo "  issues      - 저장소 이슈 목록"
    echo "  create-repo - 새 저장소 생성"
    echo "  help        - 이 도움말 표시"
    echo ""
    echo "예제:"
    echo "  ./github-helper.sh setup"
    echo "  ./github-helper.sh clone username/repo"
    echo "  ./github-helper.sh push"
    echo ""
}

# Setup 함수
setup_github() {
    echo -e "${BLUE}━━━ GitHub 인증 설정 ━━━${NC}"
    echo ""

    # 사용자 이름 입력
    read -p "GitHub 사용자 이름: " GITHUB_USER

    # 토큰 입력
    echo ""
    echo -e "${YELLOW}GitHub Personal Access Token 입력${NC}"
    echo -e "${YELLOW}생성: https://github.com/settings/tokens/new${NC}"
    read -sp "Token: " GITHUB_TOKEN
    echo ""

    # .env 파일 생성
    cat > .env.github << EOF
export GITHUB_USER="${GITHUB_USER}"
export GITHUB_TOKEN="${GITHUB_TOKEN}"
EOF

    # .gitignore 업데이트
    if [ ! -f .gitignore ]; then
        echo ".env.github" > .gitignore
    else
        if ! grep -q ".env.github" .gitignore; then
            echo ".env.github" >> .gitignore
        fi
    fi

    # 환경 변수 로드
    source .env.github

    echo ""
    echo -e "${GREEN}✓ 설정 완료!${NC}"
    echo ""
    echo "환경 변수를 로드하려면:"
    echo -e "${YELLOW}  source .env.github${NC}"
}

# Test 함수
test_github() {
    if [ -f .env.github ]; then
        source .env.github
    fi

    if [ -z "$GITHUB_TOKEN" ]; then
        echo -e "${RED}✗ GitHub 토큰이 설정되지 않았습니다.${NC}"
        echo "먼저 './github-helper.sh setup'을 실행하세요."
        exit 1
    fi

    echo -e "${BLUE}━━━ GitHub 연결 테스트 ━━━${NC}"
    echo ""

    RESPONSE=$(curl -s -H "Authorization: token ${GITHUB_TOKEN}" https://api.github.com/user)

    if echo "$RESPONSE" | grep -q "login"; then
        LOGIN=$(echo "$RESPONSE" | grep -o '"login":"[^"]*' | cut -d'"' -f4)
        NAME=$(echo "$RESPONSE" | grep -o '"name":"[^"]*' | cut -d'"' -f4)

        echo -e "${GREEN}✓ GitHub 인증 성공!${NC}"
        echo ""
        echo "사용자: $NAME (@$LOGIN)"
    else
        echo -e "${RED}✗ GitHub 인증 실패${NC}"
        echo "토큰을 확인하세요."
    fi
}

# Clone 함수
clone_repo() {
    if [ -f .env.github ]; then
        source .env.github
    fi

    if [ -z "$1" ]; then
        read -p "저장소 (예: username/repo): " REPO
    else
        REPO=$1
    fi

    echo -e "${BLUE}━━━ 저장소 Clone ━━━${NC}"
    echo ""

    git clone "https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${REPO}.git"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Clone 성공!${NC}"
    else
        echo -e "${RED}✗ Clone 실패${NC}"
    fi
}

# Push 함수
push_branch() {
    if [ -f .env.github ]; then
        source .env.github
    fi

    echo -e "${BLUE}━━━ 브랜치 Push ━━━${NC}"
    echo ""

    BRANCH=$(git branch --show-current)
    echo "현재 브랜치: $BRANCH"

    git push -u origin "$BRANCH"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Push 성공!${NC}"
    else
        echo -e "${RED}✗ Push 실패${NC}"
        echo ""
        echo "원격 저장소 URL을 확인하세요:"
        git remote -v
    fi
}

# 저장소 목록
list_repos() {
    if [ -f .env.github ]; then
        source .env.github
    fi

    echo -e "${BLUE}━━━ 내 저장소 목록 ━━━${NC}"
    echo ""

    curl -s -H "Authorization: token ${GITHUB_TOKEN}" \
        "https://api.github.com/user/repos?per_page=20&sort=updated" | \
        grep -o '"full_name":"[^"]*' | cut -d'"' -f4 | nl
}

# 이슈 목록
list_issues() {
    if [ -f .env.github ]; then
        source .env.github
    fi

    if [ -z "$1" ]; then
        # 현재 저장소에서 origin URL 파싱
        REPO_URL=$(git remote get-url origin 2>/dev/null)
        if [ -z "$REPO_URL" ]; then
            read -p "저장소 (예: username/repo): " REPO
        else
            REPO=$(echo "$REPO_URL" | sed -n 's#.*/\([^/]*/[^/]*\)\.git#\1#p')
        fi
    else
        REPO=$1
    fi

    echo -e "${BLUE}━━━ 이슈 목록: $REPO ━━━${NC}"
    echo ""

    curl -s -H "Authorization: token ${GITHUB_TOKEN}" \
        "https://api.github.com/repos/${REPO}/issues" | \
        grep -E '"title"|"number"' | paste - - | \
        sed 's/"number": \([0-9]*\),.*"title": "\(.*\)"/  #\1: \2/'
}

# 저장소 생성
create_repo() {
    if [ -f .env.github ]; then
        source .env.github
    fi

    echo -e "${BLUE}━━━ 새 저장소 생성 ━━━${NC}"
    echo ""

    read -p "저장소 이름: " REPO_NAME
    read -p "설명: " REPO_DESC
    read -p "비공개 (y/n)? " PRIVATE

    if [ "$PRIVATE" = "y" ]; then
        PRIVATE_JSON="true"
    else
        PRIVATE_JSON="false"
    fi

    RESPONSE=$(curl -s -X POST \
        -H "Authorization: token ${GITHUB_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"${REPO_NAME}\",\"description\":\"${REPO_DESC}\",\"private\":${PRIVATE_JSON}}" \
        https://api.github.com/user/repos)

    if echo "$RESPONSE" | grep -q "full_name"; then
        FULL_NAME=$(echo "$RESPONSE" | grep -o '"full_name":"[^"]*' | cut -d'"' -f4)
        echo ""
        echo -e "${GREEN}✓ 저장소 생성 성공!${NC}"
        echo "URL: https://github.com/${FULL_NAME}"
    else
        echo -e "${RED}✗ 저장소 생성 실패${NC}"
        echo "$RESPONSE"
    fi
}

# 메인 로직
case "$1" in
    setup)
        setup_github
        ;;
    test)
        test_github
        ;;
    clone)
        clone_repo "$2"
        ;;
    push)
        push_branch
        ;;
    repos)
        list_repos
        ;;
    issues)
        list_issues "$2"
        ;;
    create-repo)
        create_repo
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        echo -e "${RED}알 수 없는 명령어: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
