⚾ 순수한 야구 시뮬레이터 PRO (Pure Baseball Simulator)
KBO풍 10대 구단 하이퍼 매니지먼트 & 9회말 클러치 야구 시뮬레이터

Streamlit 기반의 파이썬 전술 매니지먼트 웹 게임입니다. 144경기 페넌트레이스 장기 시즌, 계정 및 리셋 시스템, 그리고 다양한 미니게임을 제공합니다.

🌟 주요 기능 (Key Features)
1. 🏠 메인 계정 및 리셋 시스템 (Account & Gacha)
직접 정하는 ID/PW 계정 로그인: 간편한 계정 생성 및 로그인 연동

다이아 리셋: 취임 지원금 패키지(1,000 ~ 5,000 💎) 재뽑기 기능

세이브/로드 시스템: 암호화된 세이브 코드로 경기 및 다이아 완벽 복구

2. 🏆 페넌트레이스 144경기 모드 (Pennant Race)
KBO 스타일의 10개 구단 구현: 레드, 블루, 그린, 옐로우, 퍼플, 오렌지, 브라운, 화이트, 블랙, 핑크 돌핀스

감독 계약 & 중도 사퇴 위약금: 144경기 시즌 중 팀 변경 시 위약금 3,000 💎 차감

1~9번 타순 수동 커스텀: 라인업 중복 체크 및 구단별 기본 오더 저장 지원

타 구단 경기 자동 시뮬레이션: 매 경기 종료 후 나머지 8개 팀(4쌍)의 경기 결과 자동 연산

실시간 KBO 리그 순위표: 승, 패, 무, 승률, 승차(GB) 연산 및 실시간 스탠딩 열람

3. 🕹️ 미니게임 3종 (Mini Games)
🚀 챌린지 홈런 더비 (homerun_derby.py): 10구의 기회 동안 비거리별/장외 홈런 다이아 수급

⚡ 9회말 2아웃 만루 클러치 히터 (bottom_of_the_ninth.py): 극적인 역전 승부 타석 시뮬레이션

🎯 킹 오브 스트라이크아웃 (king_of_strikeout.py): 9분할 스트라이크존 코스 제구 탈삼진 챌린지

4. ⚾ 리얼 야구 엔진 (Core Engine)
투수 스태미나 & 불펜 교체 시나리오: 체력 저하에 따른 실투율 상승 및 야수 등판 예능 모드

돌발 이벤트: 벤치클리어링(벤클), 감독 퇴장 및 수석코치 AI 자동 전술 승계, 기습 번트, 피치클락 위반, 낫아웃 등 구현

실시간 치지직(Chzzk) 관중 채팅 연출 및 경기 중계 로그 렌더링

📁 프로젝트 파일 구조 (Project Architecture)
Plaintext
pro-baseball-game/
├── app.py / new_app.py     # 메인 실행 파일 (Streamlit UI & 모드 분기)
├── data.py                 # 구단 스탯, MATCHUP_MATRIX, 로스터 데이터
├── engine.py               # PureKboEngine 및 야구 연산 핵심 알고리즘
├── homerun_derby.py        # [미니게임 1] 홈런 더비 모듈
├── bottom_of_the_ninth.py  # [미니게임 2] 9회말 클러치 히터 모듈
├── king_of_strikeout.py    # [미니게임 3] 삼진왕 챌린지 모듈
├── assets/                 # 가이드, 스토리, 로스터 텍스트 데이터 (선택)
└── README.md               # 프로젝트 매뉴얼 문서

🛠️ 실행 방법 (Installation & Run)
1. 필수 라이브러리 설치
Bash
pip install streamlit pandas matplotlib
2. 로컬에서 실행하기
Bash
streamlit run app.py 

💎 비밀 상점 & 아이템 (P2W Store)
공격 턴: 타격 확률 극대화 버프, 적 투수 멘탈 교란 찌라시

수비 턴: 특수 링거 수액(투수 체력 회복), 관중 매수 야유 디버프

🎮 개발 스택 (Tech Stack)
Language: Python 3.10+

Framework: Streamlit

Data Processing: Pandas

Visualization: Matplotlib

Deployment: Streamlit Community Cloud
