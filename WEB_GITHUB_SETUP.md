# 웹 환경에서 GitHub 사용 설정 가이드

이 가이드는 웹 환경(브라우저 기반 Claude)에서 GitHub를 사용할 수 있도록 설정하는 방법을 안내합니다.

## 목차
1. [GitHub Personal Access Token 생성](#1-github-personal-access-token-생성)
2. [웹 Claude에서 Git 인증 설정](#2-웹-claude에서-git-인증-설정)
3. [GitHub MCP 서버 설정 (선택사항)](#3-github-mcp-서버-설정-선택사항)
4. [사용 예제](#4-사용-예제)

---

## 1. GitHub Personal Access Token 생성

### 단계별 가이드

1. **GitHub에 로그인**
   - https://github.com 접속 및 로그인

2. **Settings로 이동**
   - 우측 상단 프로필 아이콘 클릭 → Settings

3. **Developer settings 접속**
   - 좌측 메뉴 하단의 "Developer settings" 클릭

4. **Personal access tokens 생성**
   - "Personal access tokens" → "Tokens (classic)" 클릭
   - "Generate new token" → "Generate new token (classic)" 선택

5. **Token 권한 설정**
   - Note: `Claude Web Integration` (토큰 이름)
   - Expiration: 원하는 만료 기간 선택
   - 필요한 권한 선택:
     - ✅ `repo` - 전체 저장소 접근
     - ✅ `workflow` - GitHub Actions 관리
     - ✅ `write:packages` - 패키지 업로드
     - ✅ `delete:packages` - 패키지 삭제
     - ✅ `admin:org` - 조직 관리 (필요시)
     - ✅ `admin:public_key` - SSH 키 관리
     - ✅ `admin:repo_hook` - 웹훅 관리
     - ✅ `user` - 사용자 정보 읽기

6. **토큰 생성 및 복사**
   - "Generate token" 클릭
   - ⚠️ **중요**: 생성된 토큰을 즉시 안전한 곳에 복사/저장
   - 토큰은 한 번만 표시되므로 반드시 저장!

---

## 2. 웹 Claude에서 Git 인증 설정

### 방법 1: HTTPS URL에 토큰 포함

```bash
# 기본 형식
git clone https://<USERNAME>:<TOKEN>@github.com/<USERNAME>/<REPOSITORY>.git

# 예제
git clone https://Glasowk75:ghp_xxxxxxxxxxxx@github.com/Glasowk75/my-project.git
```

### 방법 2: Git Credential Helper 사용

```bash
# Git 자격 증명 저장 설정
git config --global credential.helper store

# 저장소 clone 또는 pull 시 한 번만 입력
# Username: your-github-username
# Password: your-personal-access-token
```

### 방법 3: 환경 변수 설정

```bash
# GitHub 토큰을 환경 변수로 설정
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
export GITHUB_USER=Glasowk75

# Git 명령 시 사용
git clone https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/repository.git
```

---

## 3. GitHub MCP 서버 설정 (선택사항)

웹 Claude에서 GitHub MCP 서버를 사용하면 더 강력한 GitHub 통합이 가능합니다.

### 설정 방법

1. **MCP 설정 파일 생성** (로컬 환경)

   `~/.config/claude-code/mcp_servers.json`:
   ```json
   {
     "mcpServers": {
       "github": {
         "command": "npx",
         "args": [
           "-y",
           "@modelcontextprotocol/server-github"
         ],
         "env": {
           "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_your_token_here"
         }
       }
     }
   }
   ```

2. **Claude Code 재시작**
   - MCP 서버 설정이 자동으로 로드됩니다

### MCP 서버로 가능한 작업

- 📝 이슈 생성, 조회, 업데이트
- 🔀 Pull Request 생성, 리뷰, 머지
- 🌿 브랜치 관리
- 📊 저장소 통계 조회
- 🔍 코드 검색
- ⭐ 저장소 star/unstar

---

## 4. 사용 예제

### 기본 Git 작업

```bash
# 저장소 clone
git clone https://Glasowk75:${GITHUB_TOKEN}@github.com/Glasowk75/Glasowk75.git

# 변경사항 확인
git status

# 파일 추가
git add .

# 커밋
git commit -m "Add web GitHub integration guide"

# 푸시
git push origin main
```

### 웹 Claude에서 브랜치 작업

```bash
# 새 브랜치 생성
git checkout -b feature/new-feature

# 변경사항 푸시
git push -u origin feature/new-feature

# Pull Request 생성 (gh CLI 사용)
gh pr create --title "New Feature" --body "Description"
```

### GitHub API 사용 (curl)

```bash
# 저장소 정보 조회
curl -H "Authorization: token ${GITHUB_TOKEN}" \
  https://api.github.com/repos/Glasowk75/Glasowk75

# 이슈 생성
curl -X POST \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"title":"New Issue","body":"Issue description"}' \
  https://api.github.com/repos/Glasowk75/Glasowk75/issues
```

---

## 보안 주의사항

⚠️ **중요한 보안 수칙**

1. **토큰 노출 방지**
   - Personal Access Token을 코드에 직접 작성하지 마세요
   - `.env` 파일 사용 시 `.gitignore`에 추가
   - 환경 변수나 시크릿 관리 도구 사용

2. **최소 권한 원칙**
   - 필요한 권한만 부여
   - 토큰별로 용도를 구분

3. **토큰 만료 관리**
   - 정기적으로 토큰 갱신
   - 사용하지 않는 토큰은 삭제

4. **토큰 유출 시 대응**
   - 즉시 GitHub에서 해당 토큰 삭제
   - 새 토큰 생성 및 적용

---

## 트러블슈팅

### 인증 실패 (401 Unauthorized)
```bash
# 토큰 권한 확인
# GitHub Settings > Developer settings > Personal access tokens

# Git 자격 증명 초기화
git config --global --unset credential.helper
```

### 푸시 실패 (403 Forbidden)
```bash
# 원격 저장소 URL 확인
git remote -v

# URL 업데이트 (토큰 포함)
git remote set-url origin https://<USER>:<TOKEN>@github.com/<USER>/<REPO>.git
```

### Rate Limit 초과
```bash
# API 사용량 확인
curl -H "Authorization: token ${GITHUB_TOKEN}" \
  https://api.github.com/rate_limit
```

---

## 추가 리소스

- [GitHub Docs - Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub REST API](https://docs.github.com/en/rest)
- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [MCP GitHub Server](https://github.com/modelcontextprotocol/server-github)

---

## 문의 및 지원

문제가 발생하거나 추가 도움이 필요하면:
- GitHub Issues: https://github.com/Glasowk75/Glasowk75/issues
- Claude Code 지원: https://github.com/anthropics/claude-code/issues
