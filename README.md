- 👋 Hi, I'm @Glasowk75
- 👀 I'm interested in coding
- 🌱 I'm currently learning ...
- 💞️ I'm looking to collaborate on ...
- 📫 How to reach me ...
- 😄 Pronouns: ...
- ⚡ Fun fact: ...

## 🚀 웹 Claude Code에서 GitHub 사용하기

이 저장소는 웹 환경(브라우저 기반 Claude Code)에서 GitHub를 쉽게 사용할 수 있도록 도와주는 가이드와 도구를 제공합니다.

### 📖 빠른 시작

1. **5분 안에 시작하기**: [WEB_QUICKSTART.md](./WEB_QUICKSTART.md) 👈 여기서 시작!
2. **상세 가이드**: [WEB_GITHUB_SETUP.md](./WEB_GITHUB_SETUP.md)
3. **헬퍼 스크립트**: `./github-helper.sh`

### 🛠️ 제공하는 도구

#### 1. GitHub Helper Script
```bash
./github-helper.sh help    # 도움말
./github-helper.sh setup   # 빠른 설정
./github-helper.sh test    # 연결 테스트
./github-helper.sh clone   # 저장소 clone
./github-helper.sh push    # 브랜치 push
```

#### 2. 자동 설정 스크립트
```bash
bash setup-github-web.sh   # 대화형 설정
```

### 📚 문서

- **[WEB_QUICKSTART.md](./WEB_QUICKSTART.md)** - 5분 안에 시작하기 (권장)
- **[WEB_GITHUB_SETUP.md](./WEB_GITHUB_SETUP.md)** - 완전한 설정 가이드

### ✨ 주요 기능

- ✅ GitHub Personal Access Token 설정 가이드
- ✅ 웹 환경에서 Git 인증 설정
- ✅ GitHub API 사용 예제
- ✅ 자동화 스크립트 제공
- ✅ 트러블슈팅 가이드

### 🎯 사용 예제

```bash
# 1. 환경 변수 설정
export GITHUB_USER="your-username"
export GITHUB_TOKEN="ghp_your_token"

# 2. 저장소 clone
git clone https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/user/repo.git

# 3. Push
git push origin main
```

---

<!---
Glasowk75/Glasowk75 is a ✨ special ✨ repository because its `README.md` (this file) appears on your GitHub profile.
You can click the Preview link to take a look at your changes.
--->
