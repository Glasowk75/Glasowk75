# 웹 Claude Code에서 GitHub 바로 사용하기

## 🚀 5분 안에 시작하기

### 1단계: GitHub Personal Access Token 받기 (1분)

1. 새 탭에서 열기: https://github.com/settings/tokens/new
2. 설정:
   - **Note**: `Claude-Web` (이름)
   - **Expiration**: 90 days (권장)
   - **권한 선택**:
     - ✅ `repo` (전체)
     - ✅ `workflow`
     - ✅ `write:packages`
3. 맨 아래 **"Generate token"** 클릭
4. ⚠️ **토큰 복사** (ghp_로 시작, 한 번만 보임!)

---

### 2단계: 웹 Claude Code에서 사용하기 (2분)

#### 방법 A: 환경 변수 설정 (권장)

```bash
# Claude Code에서 실행:
export GITHUB_USER="당신의GitHub아이디"
export GITHUB_TOKEN="ghp_복사한토큰"

# 테스트
echo "User: $GITHUB_USER"
echo "Token: ${GITHUB_TOKEN:0:10}..." # 앞 10자만 표시
```

#### 방법 B: Git 자격 증명 저장

```bash
# Git에 자격 증명 저장 설정
git config --global credential.helper store

# 사용자 정보 설정
git config --global user.name "당신의이름"
git config --global user.email "your@email.com"
```

---

### 3단계: 바로 사용해보기 (2분)

#### 예제 1: 저장소 Clone

```bash
# 환경 변수 사용
git clone https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/repository.git

# 또는 직접 입력
git clone https://Glasowk75:ghp_your_token@github.com/Glasowk75/repository.git
```

#### 예제 2: 현재 저장소 GitHub에 푸시

```bash
# 원격 저장소 추가 (환경 변수 사용)
git remote add github https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/Glasowk75.git

# 또는 기존 origin 변경
git remote set-url origin https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/Glasowk75.git

# 푸시
git push -u github main
```

#### 예제 3: GitHub API 사용

```bash
# 내 저장소 목록 보기
curl -H "Authorization: token ${GITHUB_TOKEN}" \
  https://api.github.com/user/repos | grep -o '"full_name":"[^"]*' | cut -d'"' -f4

# 새 저장소 생성
curl -X POST \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name":"test-repo","description":"Web Claude Code에서 생성","private":false}' \
  https://api.github.com/user/repos
```

---

## 🎯 실전 사용 패턴

### 패턴 1: 매번 환경 변수 설정

매 세션 시작 시:

```bash
export GITHUB_USER="your-username"
export GITHUB_TOKEN="ghp_your_token"
```

### 패턴 2: .env 파일 사용 (더 편리)

1. 파일 생성:

```bash
cat > .env.github << 'EOF'
export GITHUB_USER="Glasowk75"
export GITHUB_TOKEN="ghp_your_token_here"
EOF

# .gitignore에 추가
echo ".env.github" >> .gitignore
```

2. 사용할 때마다:

```bash
source .env.github
```

### 패턴 3: Git URL에 직접 포함 (가장 간단)

```bash
# Clone
git clone https://username:token@github.com/username/repo.git

# Remote 추가
git remote add origin https://username:token@github.com/username/repo.git

# Push
git push origin main
```

---

## 💡 웹 Claude Code에서 자주 쓰는 명령어

### 저장소 작업

```bash
# 저장소 clone
git clone https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/user/repo.git

# 브랜치 생성 및 푸시
git checkout -b feature/new-feature
git push -u origin feature/new-feature

# 변경사항 커밋 및 푸시
git add .
git commit -m "Update from web Claude Code"
git push
```

### GitHub API로 이슈/PR 관리

```bash
# 이슈 목록
curl -H "Authorization: token ${GITHUB_TOKEN}" \
  https://api.github.com/repos/${GITHUB_USER}/Glasowk75/issues

# 이슈 생성
curl -X POST \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -d '{"title":"제목","body":"내용"}' \
  https://api.github.com/repos/${GITHUB_USER}/Glasowk75/issues

# PR 목록
curl -H "Authorization: token ${GITHUB_TOKEN}" \
  https://api.github.com/repos/${GITHUB_USER}/Glasowk75/pulls
```

---

## 🔧 트러블슈팅

### 문제: 인증 실패

```bash
# 토큰 테스트
curl -H "Authorization: token ${GITHUB_TOKEN}" https://api.github.com/user

# 200 OK가 나와야 정상
```

### 문제: Push 실패 (403)

```bash
# 원격 저장소 URL 확인
git remote -v

# URL 다시 설정
git remote set-url origin https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/repo.git
```

### 문제: 토큰을 잊어버림

- GitHub → Settings → Developer settings → Personal access tokens
- 기존 토큰 삭제하고 새로 생성

---

## ⚡ 빠른 체크리스트

- [ ] GitHub Token 생성 (https://github.com/settings/tokens/new)
- [ ] Token 복사 (ghp_로 시작)
- [ ] 환경 변수 설정 (`export GITHUB_USER=...`)
- [ ] 테스트 (`curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user`)
- [ ] Git 명령어 사용 또는 GitHub API 호출

---

## 🎓 다음 단계

1. **상세 가이드**: `WEB_GITHUB_SETUP.md` 참조
2. **자동 설정**: `bash setup-github-web.sh` 실행
3. **GitHub CLI**: `gh` 설치하면 더 편리 (선택사항)

---

**준비 완료! 이제 웹 Claude Code에서 GitHub를 자유롭게 사용하세요! 🎉**
