import random
import os
import json
import base64
import pandas as pd
import streamlit as st
from typing import Dict, Any, List
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# =====================================================================
# [STATIC DATA LAYER] 1. KBO 글로벌 프로 스탯 인프라
# =====================================================================
TEAMS: Dict[str, Dict[str, int]] = {
    "🔴 레드 파이어스": {"homerun": 35, "hit": 55, "defense": 75, "stamina": 90, "steal_b": 30},
    "🔵 블루 웨이브스": {"homerun": 45, "hit": 60, "defense": 78, "stamina": 95, "steal_b": 10},
    "🟢 그린 몬스터즈": {"homerun": 65, "hit": 45, "defense": 65, "stamina": 85, "steal_b": 5},
    "🟡 옐로우 타이거즈": {"homerun": 50, "hit": 50, "defense": 70, "stamina": 90, "steal_b": 20},
    "🟣 퍼플 바이퍼스": {"homerun": 25, "hit": 52, "defense": 82, "stamina": 100, "steal_b": 25},
    "🟠 오렌지 자이언츠": {"homerun": 45, "hit": 48, "defense": 70, "stamina": 88, "steal_b": 10},
    "🟤 브라운 베어스": {"homerun": 38, "hit": 54, "defense": 78, "stamina": 92, "steal_b": 22},
    "⚪ 화이트 이글스": {"homerun": 30, "hit": 58, "defense": 75, "stamina": 85, "steal_b": 25},
    "⚫ 블랙 나이츠": {"homerun": 32, "hit": 48, "defense": 85, "stamina": 105, "steal_b": 15},
    "💖 핑크 돌핀스": {"homerun": 52, "hit": 55, "defense": 68, "stamina": 80, "steal_b": 28}
}

MATCHUP_MATRIX: Dict[str, List[str]] = {
    "🔴 레드 파이어스":  ["X", "우세", "우세", "백중", "열세", "열세", "우세", "백중", "열세", "백중"],
    "🔵 블루 웨이브스":  ["열세", "X", "우세", "우세", "열세", "백중", "열세", "우세", "우세", "백중"],
    "🟢 그린 몬스터즈":  ["열세", "열세", "X", "열세", "우세", "우세", "열세", "백중", "우세", "열세"],
    "🟡 옐로우 타이거즈": ["백중", "열세", "우세", "X", "열세", "우세", "우세", "열세", "우세", "열세"],
    "🟣 퍼플 바이퍼스":  ["우세", "우세", "열세", "우세", "X", "백중", "백중", "열세", "우세", "열세"],
    "🟠 오렌지 자이언츠": ["우세", "백중", "열세", "열세", "백중", "X", "우세", "우세", "백중", "우세"],
    "🟤 브라운 베어스":  ["열세", "우세", "우세", "열세", "백중", "열세", "X", "우세", "백중", "우세"],
    "⚪ 화이트 이글스":  ["백중", "열세", "백중", "우세", "우세", "열세", "열세", "X", "열세", "우세"],
    "⚫ 블랙 나이츠":  ["우세", "열세", "열세", "열세", "열세", "백중", "백중", "우세", "X", "우세"],
    "💖 핑크 돌핀스":  ["백중", "백중", "우세", "우세", "우세", "열세", "열세", "열세", "열세", "X"]
}

TEAM_ROSTERS = {
    "🔴 레드 파이어스": {
        "color": "영리함, 야비함, 눈야구, 기습 도루, 초전박살",
        "pitchers": {
            "선발(5)": ["강교대", "유인구", "신기루", "조지환", "서속임"],
            "중계/불펜(5)": ["꼼수열", "변칙현", "도지훈", "민속임", "기습진"],
            "셋업(2)": ["[Primary] 차눈치", "[Secondary] 임보크"],
            "마무리(1)": ["독사철"]
        },
        "batters": {
            "포수(1)": ["[C] 도볼배"],
            "내야(4)": ["[1B] 배볼넷", "[2B] 훔쳐라", "[3B] 위장번", "[SS] 기습주"],
            "외야(3)": ["[LF] 눈야구", "[CF] 쏜살이", "[RF] 발빠름"],
            "지명타자(1)": ["[DH] 출루왕"],
            "백업(4)": ["[C] 가짜미트", "[IF] 번트길", "[IF] 유도훈", "[OF] 잽싼이"]
        }
    },
    "🔵 블루 웨이브스": {
        "color": "침착함, 묵묵함, 만루 및 메가이닝 폭발력",
        "pitchers": {
            "선발(5)": ["해일성", "파도진", "심해묵", "우직한", "김수평"],
            "중계/불펜(5)": ["잔잔한", "여울목", "고래울", "수심깊", "안개철"],
            "셋업(2)": ["[Primary] 만조웅", "[Secondary] 해류혁"],
            "마무리(1)": ["쓰나미"]
        },
        "batters": {
            "포수(1)": ["[C] 대양건"],
            "내야(4)": ["[1B] 장타만", "[2B] 만루찬", "[3B] 만루싹", "[SS] 연결고"],
            "외야(3)": ["[LF] 빅이닝", "[CF] 바다샘", "[RF] 메가타"],
            "지명타자(1)": ["[DH] 파도타"],
            "백업(4)": ["[C] 잠수함", "[IF] 징검다", "[IF] 정단단", "[OF] 닻올려"]
        }
    },
    "🟢 그린 몬스터즈": {
        "color": "원시적인 괴력, 무자비함, 오직 풀스윙",
        "pitchers": {
            "선발(5)": ["강속구", "몽둥이", "괴력만", "돌멩이", "대포한"],
            "중계/불펜(5)": ["불기둥", "힘세찬", "강대함", "무쇠팔", "묵직해"],
            "셋업(2)": ["[Primary] 괴물성", "[Secondary] 돌풍우"],
            "마무리(1)": ["파괴왕"]
        },
        "batters": {
            "포수(1)": ["[C] 바위돌"],
            "내야(4)": ["[1B] 담장밖", "[2B] 분쇄기", "[3B] 장작패", "[SS] 돌도끼"],
            "외야(3)": ["[LF] 풀스윙", "[CF] 천붕타", "[RF] 대파괴"],
            "지명타자(1)": ["[DH] 오우거"],
            "백업(4)": ["[C] 통나무", "[IF] 대포알", "[IF] 무쇠벽", "[OF] 숲속길"]
        }
    },
    "🟡 옐로우 타이거즈": {
        "color": "야성미, 명문 자존심, 정면승부, 홈런과 도루의 하이브리드",
        "pitchers": {
            "선발(5)": ["호랑이", "용맹철", "정면승", "송곳니", "대륙호"],
            "중계/불펜(5)": ["자존심", "기선제", "호효성", "범눈빛", "매서운"],
            "셋업(2)": ["[Primary] 맹호웅", "[Secondary] 위풍당"],
            "마무리(1)": ["포효진"]
        },
        "batters": {
            "포수(1)": ["[C] 포효범"],
            "내야(4)": ["[1B] 맹호타", "[2B] 훔치기", "[3B] 호쾌한", "[SS] 질주호"],
            "외야(3)": ["[LF] 장타왕", "[CF] 맹수발", "[RF] 정면타"],
            "지명타자(1)": ["[DH] 명문가"],
            "백업(4)": ["[C] 호가호", "[IF] 기선제", "[IF] 호랑발", "[OF] 매의눈"]
        }
    },
    "🟣 퍼플 바이퍼스": {
        "color": "독기, 끈질긴 눈야구, 말려 죽이기, 볼넷 마스터",
        "pitchers": {
            "선발(5)": ["독사형", "보라빛", "치명독", "집요한", "뱀눈빛"],
            "중계/불펜(5)": ["서서히", "말려죽", "방전시", "서리독", "늪지대"],
            "셋업(2)": ["[Primary] 독기찬", "[Secondary] 끈질겨"],
            "마무리(1)": ["치사량"]
        },
        "batters": {
            "포수(1)": ["[C] 방망이"],
            "내야(4)": ["[1B] 밀어내", "[2B] 공볼래", "[3B] 서서히", "[SS] 끈질기"],
            "외야(3)": ["[LF] 눈야구", "[CF] 참아라", "[RF] 안휘둘"],
            "지명타자(1)": ["[DH] 볼넷왕"],
            "백업(4)": ["[C] 묵묵히", "[IF] 파울왕", "[IF] 차분한", "[OF] 느릿이"]
        }
    },
    "🟠 오렌지 자이언츠": {
        "color": "선 굵은 야구, 거대한 파괴력, 정면승부 강타",
        "pitchers": {
            "선발(5)": ["거인성", "대지진", "만성형", "묵직한", "웅장한"],
            "중계/불펜(5)": ["바위산", "거대웅", "선굵은", "대기만", "묵직구"],
            "셋업(2)": ["[Primary] 대지웅", "[Secondary] 통나무"],
            "마무리(1)": ["거인탑"]
        },
        "batters": {
            "포수(1)": ["[C] 큰바위"],
            "내야(4)": ["[1B] 쪼개버", "[2B] 파괴타", "[3B] 장작패", "[SS] 거대타"],
            "외야(3)": ["[LF] 묵직한", "[CF] 대지파", "[RF] 통나무"],
            "지명타자(1)": ["[DH] 대기만"],
            "백업(4)": ["[C] 도루포", "[IF] 묵직해", "[IF] 대지벽", "[OF] 둔하지만"]
        }
    },
    "🟤 브라운 베어스": {
        "color": "허허실실, 내유외강, 위기관리 타짜, 희생플라이/작전 야구",
        "pitchers": {
            "선발(5)": ["반달곰", "허허실", "베테랑", "위기탈", "지리산"],
            "중계/불펜(5)": ["꿀단지", "노련한", "잔뼈굵", "잠자는", "맹수본"],
            "셋업(2)": ["[Primary] 타짜신", "[Secondary] 허허실"],
            "마무리(1)": ["맹수눈"]
        },
        "batters": {
            "포수(1)": ["[C] 꿀곰이"],
            "내야(4)": ["[1B] 찬스강", "[2B] 희생타", "[3B] 밀어쳐", "[SS] 타짜노"],
            "외야(3)": ["[LF] 노련한", "[CF] 반달곰", "[RF] 뜬공짱"],
            "지명타자(1)": ["[DH] 끝내기"],
            "백업(4)": ["[C] 베테랑", "[IF] 득점짜", "[IF] 곰발바", "[OF] 순수한"]
        }
    },
    "⚪ 화이트 이글스": {
        "color": "고고함, 칼날 제구력, 신사적, 정교한 밀어치기",
        "pitchers": {
            "선발(5)": ["흰수리", "자로재", "칼날존", "하늘위", "고고한"],
            "중계/불펜(5)": ["칼날구", "정교한", "낚아채", "사냥꾼", "제구왕"],
            "셋업(2)": ["[Primary] 송골매", "[Secondary] 칼날제"],
            "마무리(1)": ["신사적인"]
        },
        "batters": {
            "포수(1)": ["[C] 정교한"],
            "내야(4)": ["[1B] 밀어쳐", "[2B] 정교타", "[3B] 안타샤", "[SS] 번개수"],
            "외야(3)": ["[LF] 낚아채", "[CF] 흰날개", "[RF] 칼날타"],
            "지명타자(1)": ["[DH] 안타왕"],
            "백업(4)": ["[C] 깔끔한", "[IF] 툭툭쳐", "[IF] 번개발", "[OF] 슈퍼캐"]
        }
    },
    "⚫ 블랙 나이츠": {
        "color": "결사 항전, 철벽 육탄 방어, 늪야구, 패배 없는 투지",
        "pitchers": {
            "선발(5)": ["흑기사", "결사항", "육탄방", "패배모", "칠흑건"],
            "중계/불펜(5)": ["방패막", "늪야구", "투지찬", "철벽성", "슬라이"],
            "셋업(2)": ["[Primary] 칠흑벽", "[Secondary] 육탄전"],
            "마무리(1)": ["수호신"]
        },
        "batters": {
            "포수(1)": ["[C] 방패철"],
            "내야(4)": ["[1B] 몸던져", "[2B] 슬라이", "[3B] 육탄방", "[SS] 늪야구"],
            "외야(3)": ["[LF] 결사대", "[CF] 다이빙", "[RF] 철벽갑"],
            "지명타자(1)": ["[DH] 투지왕"],
            "백업(4)": ["[C] 성벽건", "[IF] 1점짜", "[IF] 질식수", "[OF] 온몸던"]
        }
    },
    "💖 핑크 돌핀스": {
        "color": "유쾌함, 도파민 중독, 무지성 흥, 도깨비 팀, 분위기 메이커",
        "pitchers": {
            "선발(5)": ["핑크돌", "흥부자", "축제왕", "미친흥", "분홍바"],
            "중계/불펜(5)": ["신난다", "도깨비", "예측불", "춤추는", "신기한"],
            "셋업(2)": ["[Primary] 도파민", "[Secondary] 핑크빛"],
            "마무리(1)": ["축제끝"]
        },
        "batters": {
            "포수(1)": ["[C] 신난돌"],
            "내야(4)": ["[1B] 무지성", "[2B] 훔쳐라", "[3B] 풀스윙", "[SS] 핑크빛"],
            "외야(3)": ["[LF] 도파민", "[CF] 흥돌고", "[RF] 춤추자"],
            "지명타자(1)": ["[DH] 도깨비"],
            "백업(4)": ["[C] 귀요미", "[IF] 무지성", "[IF] 흥신흥", "[OF] 날아라"]
        }
    }
}
def render_roster_viewer():
    with st.sidebar.expander("📋 10개 구단 26인 로스터 열람"):
        selected_team = st.selectbox("팀을 선택하세요", list(TEAM_ROSTERS.keys()))
        team_info = TEAM_ROSTERS[selected_team]
        
        st.caption(f"**팀 컬러:** {team_info['color']}")
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### ⚾ 투수진 (13명)")
            for role, players in team_info["pitchers"].items():
                st.markdown(f"**{role}**")
                st.text(", ".join(players))
                
        with col2:
            st.markdown("### 🏏 타자진 (13명)")
            for role, players in team_info["batters"].items():
                st.markdown(f"**{role}**")
                st.text(", ".join(players))

teams_keys = list(MATCHUP_MATRIX.keys())
df_matchup = pd.DataFrame.from_dict(MATCHUP_MATRIX, orient='index', columns=teams_keys)

def color_matchup_cells(val):
    base_style = "font-weight: bold; text-align: center;"
    if val == "우세":
        return f"{base_style} background-color: #e2f0d9; color: #385723;"
    elif val == "열세":
        return f"{base_style} background-color: #fce4d6; color: #c65911;"
    elif val == "백중":
        return f"{base_style} background-color: #fff2cc; color: #7f6000;"
    elif val == "X":
        return f"{base_style} background-color: #f2f2f2; color: #bfbfbf; font-style: italic;"
    return base_style

try:
    styled_df = df_matchup.style.map(color_matchup_cells)
except AttributeError:
    styled_df = df_matchup.style.applymap(color_matchup_cells)

MATRIX_COLUMNS = ["🔴레드", "🔵블루", "🟢그린", "🟡옐로우", "🟣퍼플", "🟠오렌지", "🟤브라운", "⚪화이트", "⚫블랙", "💖핑크"]

PITCH_SPECS = {
    "직구": {"speed_min": 142, "speed_max": 155},
    "슬라이더": {"speed_min": 130, "speed_max": 142},
    "체인지업": {"speed_min": 125, "speed_max": 136},
    "커브": {"speed_min": 115, "speed_max": 126},
    "포크볼": {"speed_min": 125, "speed_max": 138},
    "싱커": {"speed_min": 133, "speed_max": 144}
}

# 💡 [신규 추가 1] 기본 선발 라인업 추출 헬퍼 함수
def get_default_lineup(team_name: str) -> List[str]:
    """팀 타자 명단 중 선발 9명을 추출하여 1~9번 자동 세팅하는 헬퍼"""
    b_dict = TEAM_ROSTERS[team_name]["batters"]
    primary = []
    for k in ["외야(3)", "내야(4)", "포수(1)", "지명타자(1)"]:
        if k in b_dict:
            primary.extend(b_dict[k])
    
    if len(primary) < 9 and "백업(4)" in b_dict:
        primary.extend(b_dict["백업(4)"])
    return primary[:9]

# =====================================================================
# [NAVER INFRASTRUCTURE LAYER]
# =====================================================================
class HyperClovaX_AI:
    @staticmethod
    def get_recommendation(pitch_history: List[str], base3: bool, inning: int, is_attack: bool) -> str:
        if not is_attack:
            return "💡 상대 타자의 헛스윙 비율이 높습니다. '유인구 배정'으로 헛스윙을 유도하십시오."
        if base3 and inning >= 7:
            return "💡 득점 확률 88.4%! 3루 주자를 불러들이는 '기습 스퀴즈 번트'를 강력 추천합니다."
        if len(pitch_history) > 1 and "직구" in pitch_history[-1]:
            return "💡 직전 패턴 분석 결과 오프스피드 피칭이 예상됩니다. '웨이팅(눈야구)'으로 볼넷을 노리세요."
        return "💡 투수의 체력이 감소하는 타이밍입니다. '팀 배팅'으로 투구수를 늘리십시오."

# =====================================================================
# [DOMAIN LAYER] 
# =====================================================================
class PitcherDomain:
    def __init__(self, name: str, role: str, max_stamina: int) -> None:
        self.name = name
        self.role = role
        self.max_stamina = max_stamina
        self.stamina = max_stamina
        self.pitches_thrown = 0

    def consume(self, amt: int = 1) -> None:
        self.pitches_thrown += amt
        self.stamina = max(0, self.stamina - amt)

    def get_penalty(self) -> float:
        if self.role == "야수등판":
            return 0.25
        ratio = self.stamina / self.max_stamina
        if self.stamina <= 0: return 0.16
        elif ratio < 0.3: return 0.09
        elif ratio < 0.6: return 0.04
        return 0.0

# =====================================================================
# [CORE ENGINE] R H E B Tracking Engine
# =====================================================================
class PureKboEngine:
    # 💡 [신규 추가 2] my_lineup 매개변수 선언 추가 및 라인업 인스턴스 저장
    def __init__(self, my_team: str, enemy_team: str, my_lineup: List[str] = None) -> None:
        self.my_team = my_team
        self.enemy_team = enemy_team
        self.my_emoji = my_team[:2]
        self.enemy_emoji = enemy_team[:2]
        self.is_home_team = random.choice([True, False])

        # 💡 [신규 추가 3] 타순 등록 (전달된 값 없으면 자동 세팅)
        self.my_lineup = my_lineup if my_lineup else get_default_lineup(my_team)
        self.enemy_lineup = get_default_lineup(enemy_team)
        
        self.our_score = 0
        self.enemy_score = 0
        
        self.away_stats = {"R": 0, "H": 0, "E": 0, "B": 0}
        self.home_stats = {"R": 0, "H": 0, "E": 0, "B": 0}

        self.inning = 1
        self.phase = "초"
        
        self.my_batter_number = 1
        self.enemy_batter_number = 1
        self.our_total_pitches = 0
        self.enemy_total_pitches = 0
        
        self.strike = 0
        self.ball = 0
        self.out_count = 0
        self.base1 = self.base2 = self.base3 = False
        
        self.away_inning_scores = [""] * 12
        self.home_inning_scores = [""] * 12
        
        self.game_over = False
        self.game_result_msg = ""
        self.game_log = [f"🏟️ 경기 개시. 우리 팀은 {'후공(홈팀)' if self.is_home_team else '선공(원정팀)'}."]
        self.pitch_history = ["- 투구 기록 없음"]
        
        self.chzzk_chats = ["💬 **치지직 가이드**: 경기가 시작되었습니다. 전술 사인을 지켜보세요!"]
        self.hit_buff = 0.0 

        self.my_timeouts_left = 3 
        self.enemy_timeouts_left = 3 

        self.manager_ejected = False  # 감독 퇴장 여부 플래그
        self.update_is_attack()
        
        my_stats = TEAMS[my_team]
        enemy_stats = TEAMS[enemy_team]

        my_sp = TEAM_ROSTERS[my_team]["pitchers"]["선발(5)"]
        my_rp = TEAM_ROSTERS[my_team]["pitchers"]["중계/불펜(5)"]
        my_cl = TEAM_ROSTERS[my_team]["pitchers"]["마무리(1)"]

        chosen_sp_name = my_sp[starting_pitcher_idx] if 0 <= starting_pitcher_idx < len(my_sp) else my_sp[0]
        
        my_sp_pool = [
            PitcherDomain("1선발(에이스)", "선발", my_stats["stamina"]),
            PitcherDomain("2선발", "선발", int(my_stats["stamina"] * 0.95)),
            PitcherDomain("3선발", "선발", int(my_stats["stamina"] * 0.90)),
            PitcherDomain("4선발", "선발", int(my_stats["stamina"] * 0.85)),
            PitcherDomain("5선발", "선발", int(my_stats["stamina"] * 0.80)),
        ]
        self.my_pitchers = [
            random.choice(my_sp_pool),
            PitcherDomain("추격조 1번(롱릴리프)", "추격조", 45),
            PitcherDomain("추격조 2번(중간계투)", "추격조", 40),
            PitcherDomain("추격조 3번(좌완)", "추격조", 35),
            PitcherDomain("추격조 4번(추격)", "추격조", 35),
            PitcherDomain("필승조 1번(마당쇠)", "필승조", 35),
            PitcherDomain("셋업맨 1번 (필승조)", "필승조", 30),
            PitcherDomain("셋업맨 2번 (필승조)", "필승조", 30),
            PitcherDomain("클로저(마무리)", "마무리", 20)
        ]
        self.my_pitcher_idx = 0
        self.my_used_pitchers = {0}

        en_sp = TEAM_ROSTERS[enemy_team]["pitchers"]["선발(5)"]
        en_rp = TEAM_ROSTERS[enemy_team]["pitchers"]["중계/불펜(5)"]
        en_cl = TEAM_ROSTERS[enemy_team]["pitchers"]["마무리(1)"]

        enemy_sp_pool = [
            PitcherDomain("상대 에이스", "선발", enemy_stats["stamina"]),
            PitcherDomain("상대 2선발", "선발", int(enemy_stats["stamina"] * 0.95)),
            PitcherDomain("상대 3선발", "선발", int(enemy_stats["stamina"] * 0.90)),
            PitcherDomain("상대 4선발", "선발", int(enemy_stats["stamina"] * 0.85)),
            PitcherDomain("상대 5선발", "선발", int(enemy_stats["stamina"] * 0.80)),
        ]
        self.enemy_pitchers = [
            random.choice(enemy_sp_pool),
            PitcherDomain("상대 추격조 1번", "추격조", 45),
            PitcherDomain("상대 추격조 2번", "추격조", 40),
            PitcherDomain("상대 추격조 3번", "추격조", 35),
            PitcherDomain("상대 추격조 4번", "추격조", 35),
            PitcherDomain("상대 필승조 1번", "필승조", 35),
            PitcherDomain("상대 셋업맨 1번", "필승조", 30),
            PitcherDomain("상대 셋업맨 2번", "필승조", 30),
            PitcherDomain("상대 클로저", "마무리", 20)
        ]
        self.enemy_pitcher_idx = 0
        self.enemy_used_pitchers = {0}
        
        self.setup_half_inning()

    def update_is_attack(self) -> None:
        self.is_attack = (not self.is_home_team and self.phase == "초") or (self.is_home_team and self.phase == "말")

    def trigger_special_chat(self, custom_chats: List[str]) -> None:
        """특수 희귀/이벤트 발생 시 치지직 관중 채팅 주입 연출"""
        users = ["야구천재", "방구석펩", "침착한스트리머", "9회말2아웃", "KBO정신병자", "용규놀이터", "류뿡", "야잘알김동구"]
        for msg in custom_chats:
            self.chzzk_chats.append(f"💬 **{random.choice(users)}**: {msg}")
        if len(self.chzzk_chats) > 10:
            self.chzzk_chats = self.chzzk_chats[-10:]

    def eject_manager(self, reason: str) -> None:
        """감독 퇴장 트리거 및 수석코치 AI 전환"""
        if self.manager_ejected: return
        self.manager_ejected = True
        self.game_log.append(f"🟥 [감독 퇴장] 감독님이 {reason} 주심에게 격렬하게 항의하다 즉시 퇴장 명령을 받았습니다!")
        self.game_log.append("👔 [수석코치 대행] 이제부터 수석코치가 남은 경기를 자동 전술 지휘합니다.")
        
        eject_chats = [
            "아니 감독 쫓겨나니까 경기 더 잘 풀리는데??? ㅋㅋㅋㅋ",
            "명장 수석코치님 평생 감독해 주세요 ㅋㅋㅋ",
            "퇴장당하고 라커룸에서 족발 먹는 중 ㅋㅋㅋ",
            "수석코치 AI 등판 ㄷㄷㄷ 오히려 좋아 ㅋㅋㅋ"
        ]
        self.trigger_special_chat(eject_chats)

    def trigger_bench_clearing(self, reason: str, log_prefix: str = "") -> None:
        """벤치클리어링(벤클) 트리거 엔진"""
        self.game_log.append(log_prefix + f"🔥 [🚨 벤치클리어링 발동!] {reason} 양 팀 덕아웃과 불펜에서 선수들이 그라운드로 총출동합니다! 심한 언쟁과 몸싸움 발생!!! 😱")
        
        # 벤클 발생 시 20% 확률로 감독 같이 뛰어나왔다가 퇴장 처리!
        if random.random() < 0.20 and not self.manager_ejected:
            self.eject_manager("벤치클리어링 충돌 중 상대 감독 및 주심과의 물리적 마찰로")
        else:
            self.game_log.append("👨‍⚖️ [심판진 중재] 심판진이 긴급 수습에 나섭니다. 양 팀 벤치에 엄중 경고를 부여하고 경기를 재개합니다.")

        bc_chats = [
            "ㅋㅋㅋㅋㅋㅋㅋㅋ 벤클 떴다 🍿🍿🍿🍿🍿",
            "어어 밀지 마라 ㅋㅋㅋ 주먹 나가냐???",
            "아니 팝콘 가져와라 ㅋㅋㅋ 꿀잼 직관!!",
            "감독님 벤치에서 제일 먼저 뛰어나가는 거 보소 ㅋㅋㅋㅋ",
            "이게 KBO지 ㅋㅋㅋㅋ 낭만 야구 미쳤다"
        ]
        self.trigger_special_chat(bc_chats)

    def advance_all_runners(self, bases: int = 1) -> None:
        gained = 0
        for _ in range(bases):
            if self.base3: gained += 1; self.base3 = False
            if self.base2: self.base3 = True; self.base2 = False
            if self.base1: self.base2 = True; self.base1 = False
        if gained > 0:
            self.update_live_scoreboard(gained)

    def trigger_wild_pitch_or_passed_ball(self, log_prefix: str, pitch_zone: int) -> bool:
        if not (self.base1 or self.base2 or self.base3):
            return False
            
        wp_prob = 0.020 if pitch_zone == 0 else 0.008
        if random.random() < wp_prob:
            self.ball += 1
            self.game_log.append(log_prefix + f"💥 [원바운드 폭투!] 투수의 손가락이 빠지며 공이 바운드되어 튑니다! 주자 전원 진루! ({self.strike}S {self.ball}B)")
            self.advance_all_runners(1)
            if self.ball >= 4:
                self.process_walk(is_defense=not self.is_attack)
            return True
            
        if random.random() < 0.015:
            self.game_log.append(log_prefix + f"⚠️ [포수 포일!] 포수가 투구를 미트에서 놓치며 공이 뒤로 튑니다! 주자 한 베이스씩 진루! ({self.strike}S {self.ball}B)")
            self.advance_all_runners(1)
            return True
            
        return False

    def add_stat(self, stat: str, amt: int = 1):
        if self.phase == "초":
            if stat in ["H", "B"]: self.away_stats[stat] += amt
            elif stat == "E": self.home_stats[stat] += amt
        else:
            if stat in ["H", "B"]: self.home_stats[stat] += amt
            elif stat == "E": self.away_stats[stat] += amt

    def get_matchup_modifier(self, attack_team: str, defense_team: str) -> float:
        row = MATCHUP_MATRIX.get(attack_team)
        if not row: return 0.0
        try:
            def_idx = list(TEAMS.keys()).index(defense_team)
            status = row[def_idx]
            if status == "우세": return 0.005  
            if status == "열세": return -0.005
        except ValueError: pass
        return 0.0

    def manual_change_my_pitcher(self, selected_idx: int) -> bool:
        """감독이 직접 지정한 인덱스의 투수로 수동 교체"""
        if selected_idx != self.my_pitcher_idx and selected_idx not in self.my_used_pitchers:
            self.my_pitcher_idx = selected_idx
            self.my_used_pitchers.add(selected_idx)
            p = self.get_current_my_pytcher() if hasattr(self, 'get_current_my_pytcher') else self.get_current_my_pitcher()
            self.game_log.append(f"🔄 [감독 직접 교체] 벤치의 지시로 마운드 교체! [{p.role}] '{p.name}' 등판!")
            return True
        elif selected_idx == self.my_pitcher_idx:
            st.warning("현재 이미 던지고 있는 투수입니다!")
        else:
            st.warning("이미 경기에 등판했던 투수는 재등판할 수 없습니다!")
        return False
        
    def get_current_my_pitcher(self) -> PitcherDomain: return self.my_pitchers[self.my_pitcher_idx]
    def get_current_enemy_pitcher(self) -> PitcherDomain: return self.enemy_pitchers[self.enemy_pitcher_idx]

    def change_my_pitcher(self) -> bool:
        target_idx = self.evaluate_pitcher_scenario(is_defense=True)
        
        if target_idx == -99:
            p = self.get_current_my_pitcher()
            if p.role != "야수등판":
                p.name = "⚠️ 야수(패전처리)"
                p.role = "야수등판"
                p.max_stamina = 15
                p.stamina = 15
                self.game_log.append("🚨 [투수 교체] 대참사! 전술적으로 야수를 마운드에 올립니다.")
                return True
            return False
            
        if target_idx != self.my_pitcher_idx and target_idx not in self.my_used_pitchers:
            self.my_pitcher_idx = target_idx
            self.my_used_pitchers.add(target_idx)
            p = self.get_current_my_pitcher()
            self.game_log.append(f"🔄 [투수 교체] 시나리오 적용: {p.role} '{p.name}' 등판")
            return True
        else:
            for alt_idx in range(1, len(self.my_pitchers)):
                if alt_idx not in self.my_used_pitchers:
                    self.my_pitcher_idx = alt_idx
                    self.my_used_pitchers.add(alt_idx)
                    p = self.get_current_my_pitcher()
                    self.game_log.append(f"🔄 [투수 교체] 불펜 가동: {p.role} '{p.name}' 등판")
                    return True
        return False

    def change_enemy_pitcher(self) -> bool:
        target_en_idx = self.evaluate_pitcher_scenario(is_defense=False)
        
        if target_en_idx == -99:
            p = self.get_current_enemy_pitcher()
            if p.role != "야수등판":
                p.name = "⚠️ 야수(상대패전처리)"
                p.role = "야수등판"
                p.max_stamina = 15
                p.stamina = 15
                self.game_log.append("🚨 [상대 투수 교체] 대파 상황! 상대 감독이 포기하고 야수를 올립니다.")
                return True
            return False

        if target_en_idx != self.enemy_pitcher_idx and target_en_idx not in self.enemy_used_pitchers:
            self.enemy_pitcher_idx = target_en_idx
            self.enemy_used_pitchers.add(target_en_idx)
            p = self.get_current_enemy_pitcher()
            self.game_log.append(f"🔄 [상대 투수 교체] 시나리오 적용: 상대 불펜 가동: {p.role} '{p.name}' 등판")
            return True
        else:
            for alt_idx in range(1, len(self.enemy_pitchers)):
                if alt_idx not in self.enemy_used_pitchers:
                    self.enemy_pitcher_idx = alt_idx
                    self.enemy_used_pitchers.add(alt_idx)
                    p = self.get_current_enemy_pitcher()
                    self.game_log.append(f"🔄 [상대 투수 교체] 상대 불펜 가동: {p.role} '{p.name}' 등판")
                    return True
        return False

    def use_my_timeout(self) -> None:
        self.update_is_attack()
        left_timeouts = getattr(self, 'my_timeouts_left', 3)
        if left_timeouts <= 0:
            self.game_log.append("⚠️ 이미 남은 타임을 모두 사용했습니다! (경기당 최대 3회)")
            return
            
        self.my_timeouts_left = left_timeouts - 1 
        
        if self.is_attack:
            self.hit_buff = getattr(self, 'hit_buff', 0.0) + 0.05
            self.game_log.append(f"⏱️ [아군 타임] 감독님이 타임을 요청하고 타자를 불러 조언을 전달합니다. (타격 집중력 상승, 남은 타임: {self.my_timeouts_left}회)")
        else:
            p = self.get_current_my_pitcher()
            
            if isinstance(p, dict):
                cur_st = p.get("stamina", 20)
                max_st = p.get("max_stamina", 35)
                p["stamina"] = min(max_st, cur_st + 3)
            else:
                cur_st = getattr(p, "stamina", 20)
                max_st = getattr(p, "max_stamina", 35)
                p.stamina = min(max_st, cur_st + 3)
                
            self.game_log.append(f"⏱️ [아군 타임] 마운드 방문! 투수를 다독이고 흐름을 끊어갑니다. (투수 체력 +3 회복, 남은 타임: {self.my_timeouts_left}회)")
                
    def check_enemy_timeout(self, log_prefix: str) -> None:
        self.update_is_attack()
        enemy_left = getattr(self, 'enemy_timeouts_left', 3)
        if enemy_left <= 0:
            return
    
        enemy_timeout_triggered = False
    
        if self.is_attack and (self.base2 or self.base3) and self.out_count < 2:
            if random.random() < 0.20:
                enemy_timeout_triggered = True
                
        elif self.is_attack:
            p_enemy = self.get_current_enemy_pitcher()
            cur_st = p_enemy.get("stamina", 20) if isinstance(p_enemy, dict) else getattr(p_enemy, "stamina", 20)
            max_st = p_enemy.get("max_stamina", 35) if isinstance(p_enemy, dict) else getattr(p_enemy, "max_stamina", 35)
            
            if cur_st <= (max_st * 0.3):
                if random.random() < 0.25:
                    enemy_timeout_triggered = True
    
        if enemy_timeout_triggered:
            self.enemy_timeouts_left = enemy_left - 1
            p_enemy = self.get_current_enemy_pitcher()
            
            if isinstance(p_enemy, dict):
                p_enemy["stamina"] = min(p_enemy.get("max_stamina", 35), p_enemy.get("stamina", 0) + 2)
            else:
                p_enemy.stamina = min(getattr(p_enemy, "max_stamina", 35), getattr(p_enemy, "stamina", 0) + 2)
                
            self.game_log.append(
                log_prefix + f"⏱️ [적팀 타임] 상대 감독이 마운드로 이동해 투수와 포수를 불러 모읍니다! 흐름을 끊으려는 의도입니다. (상대 투수 체력 +2, 남은 타임: {self.enemy_timeouts_left}회)"
            )

    def play_intentional_walk(self) -> None:
        """고의사구(Intentional Walk) 지시 처리"""
        if self.game_over: return
        self.update_is_attack()
        
        # 공격 턴일 때는 고의사구 지시 불가
        if self.is_attack:
            st.warning("공격 턴에는 고의사구 작전을 지시할 수 없습니다.")
            return

        p_my = self.get_current_my_pitcher()
        p_my.consume(1) # 투구수 1구 추가
        self.our_total_pitches += 1

        self.strike = 0
        self.ball = 0
        
        gained = 0
        if self.base1 and self.base2 and self.base3:
            gained = 1
        elif self.base1 and self.base2:
            self.base3 = True
        elif self.base1:
            self.base2 = True
        else:
            self.base1 = True
            
        if gained > 0:
            self.update_live_scoreboard(gained)
            self.game_log.append(f"🛑 [고의사구 지시] 벤치에서 고의사구 사인을 냅니다. 만루 밀어내기 득점 허용! (+1점)")
        else:
            self.game_log.append(f"🛑 [고의사구 지시] 투수가 스트라이크존 바깥으로 공을 빼며 안전하게 타자를 1루로 걸러냅니다.")
            
        # 다음 타순으로 교체
        bat = self.enemy_batter_number
        self.enemy_batter_number = 1 if bat == 9 else bat + 1
        
        self.check_three_out_change()

    def check_weather_events(self) -> bool:
        # 5회 이전 무작위 폭우 (노게임)
        if self.inning < 5 and random.random() < 0.008:
            self.game_log.append("🚨 [🌧️ 폭우 기습] 갑작스러운 게릴라성 호우로 경기가 중단되었습니다!")
            self.game_log.append("❌ [노게임 선언] 5이닝 미만 진행으로 경기가 무효 처리됩니다.")
            self.game_over = True
            return True

        # 5회 이후 무작위 폭우 (강우 콜드)
        elif self.inning >= 5 and random.random() < 0.015:
            self.game_log.append("🚨 [☔ 억수 같은 폭우] 마운드와 타석이 물에 잠겨 경기가 지속 불가능합니다!")
            self.game_log.append("🏆 [강우 콜드게임] 정식 경기 요건을 충족하여 현 시점 스코어로 승패를 확정합니다.")
            self.end_kbo_game()
            return True

        return False
        

    def get_away_score(self) -> int: return self.away_stats["R"]
    def get_home_score(self) -> int: return self.home_stats["R"]

    def setup_half_inning(self) -> None:
        if self.game_over: return
        self.update_is_attack()

        idx = self.inning - 1
        if idx < 12:
            if self.away_inning_scores[idx] == "": self.away_inning_scores[idx] = 0
            if self.home_inning_scores[idx] == "": self.home_inning_scores[idx] = 0

        if self.inning >= 9 and self.phase == "말" and self.get_home_score() > self.get_away_score():
            self.game_log.append(f"👍 {self.inning}회초 종료. 홈팀 리드로 경기 종료 ('X' 승리).")
            if len(self.home_inning_scores) >= self.inning:
                self.home_inning_scores[self.inning - 1] = "X"
            self.end_kbo_game()
            return

        self.strike = 0; self.ball = 0; self.out_count = 0
        self.base1 = self.base2 = self.base3 = False
        self.hit_buff = 0.0

        if self.inning >= 6:
            current_is_our_defense = (self.phase == "초" and not self.is_home_team) or (self.phase == "말" and self.is_home_team)
            
            if current_is_our_defense:
                t_idx = self.evaluate_pitcher_scenario(is_defense=True)
                if t_idx != -99 and t_idx != self.my_pitcher_idx:
                    self.my_pitcher_idx = t_idx
                    self.my_used_pitchers.add(t_idx)
                    
                    p_obj = self.get_current_my_pitcher()
                    p_role = p_obj.get('role', 'RP') if isinstance(p_obj, dict) else getattr(p_obj, 'role', 'RP')
                    self.game_log.append(f"🔄 [이닝 교체] 벤치가 움직입니다. 새로운 이닝을 책임질 맞춤형 [{p_role}] 등판!")
            else:
                t_en_idx = self.evaluate_pitcher_scenario(is_defense=False)
                if t_en_idx != -99 and t_en_idx != self.enemy_pitcher_idx:
                    self.enemy_pitcher_idx = t_en_idx
                    self.enemy_used_pitchers.add(t_en_idx)
                    
                    p_obj = self.get_current_enemy_pitcher()
                    p_role = p_obj.get('role', 'RP') if isinstance(p_obj, dict) else getattr(p_obj, 'role', 'RP')
                    self.game_log.append(f"🔄 [상대 이닝 교체] 상대 팀이 이닝 시작과 동시에 투수를 바꿉니다. [{p_role}] 등판!")

    def check_defensive_replacement_event(self) -> None: 
        """8회~9회 리드 중 대수비 강화 투입"""
        current_is_our_defense = (self.phase == "초" and not self.is_home_team) or (self.phase == "말" and self.is_home_team)
        
        if current_is_our_defense and self.inning >= 8:
            score_diff = self.our_score - self.enemy_score
            if 1 <= score_diff <= 3 and random.random() < 0.30: # 1~3점 차 리드 시 30% 확률
                backup_list = TEAM_ROSTERS[self.my_team]["batters"].get("백업(4)", [])
                sub_def = next((p for p in backup_list if "대수비" in p or "미트" in p or "성벽" in p), backup_list[0] if backup_list else "대수비 요원")
                
                self.game_log.append(
                    f"🛡️ [대수비 교체] 벤치가 승리를 지키기 위해 철벽 수비 요원 '{sub_def}'(을)를 내야/포수 수비로 긴급 투입합니다! (실책 확률 대폭 감소)"
                )
                
                def_chats = [
                    f"지키는 야구 가자! {sub_def} 대수비 출격 🛡️",
                    "수비 안정감 든든하다 ㅋㅋㅋ 승리 굳히기 들어감",
                    "오늘 1점 차 승부 미쳤네 대수비 열일하자!"
                ]
                self.trigger_special_chat(def_chats)
                
    def update_live_scoreboard(self, run: int) -> None:
        idx = min(11, max(0, self.inning - 1))
        
        if self.phase == "초":
            base = 0 if self.away_inning_scores[idx] in ["", "X"] else int(self.away_inning_scores[idx])
            self.away_inning_scores[idx] = base + run
            self.away_stats["R"] += run
        else:
            base = 0 if self.home_inning_scores[idx] in ["", "X"] else int(self.home_inning_scores[idx])
            self.home_inning_scores[idx] = base + run
            self.home_stats["R"] += run
            
        if (self.is_home_team and self.phase == "말") or (not self.is_home_team and self.phase == "초"):
            self.our_score = self.home_stats["R"] if self.is_home_team else self.away_stats["R"]
        else:
            self.enemy_score = self.away_stats["R"] if self.is_home_team else self.home_stats["R"]

    def trigger_steal(self) -> None:
        if not (self.base1 or self.base2 or self.base3):
            st.warning("루상에 주자가 없습니다.")
            return

        # 💡 [벤클 트리거 2] 6점 차 이상 대승 시 도루 불문율 위반
        score_diff = self.our_score - self.enemy_score if self.is_attack else self.enemy_score - self.our_score
        if score_diff >= 6 and random.random() < 0.40:
            self.trigger_bench_clearing("6점 차 이상 큰 격차 상황에서 기습 도루를 감행하여 불문율을 위반했습니다!")

        p_en = self.get_current_enemy_pitcher()
        if p_en.stamina <= (p_en.max_stamina * 0.3) and not getattr(p_en, 'warned_stamina', False):
            p_en.warned_stamina = True
            self.game_log.append(f"🔥 [기회 도래] 상대 {p_en.name} 투수의 어깨가 무거워졌습니다! (남은 체력: {p_en.stamina}/{p_en.max_stamina})")
            self.game_log.append("💡 [타선 집중] 상대 투수의 실투 확률이 급증합니다. 적극적으로 타격해 빅이닝을 만드세요!")
        p_en.consume(1)
        self.enemy_total_pitches += 1

        my_stats = TEAMS[self.my_team]
        enemy_stats = TEAMS[self.enemy_team]
        success_rate = max(0.20, min(0.80, 0.62 + (my_stats["steal_b"] - enemy_stats["defense"] * 0.15) * 0.01))

        if self.base1 or self.base2:
            self.game_log.append("🏃‍♂️ 기습 도루 시도!")
            if random.random() < success_rate:
                if self.base2 and not self.base3: self.base3 = True; self.base2 = False
                elif self.base1 and not self.base2: self.base2 = True; self.base1 = False
                elif self.base1 and self.base2 and not self.base3: self.base3 = True; self.base2 = True; self.base1 = False
                self.game_log.append("✅ 도루 성공!")
            else:
                self.out_count += 1
                self.game_log.append("❌ 포수 송구 아웃!")
                if self.base1 and self.base2:
                    if random.choice([True, False]): self.base1 = False
                    else: self.base2 = False
                else: self.base1 = self.base2 = False
                self.check_three_out_change()
        elif self.base3:
            self.game_log.append("🚨 3루 주자 홈스틸 감행!!!")
            if random.random() < 0.15:
                self.update_live_scoreboard(1)
                self.base3 = False
                self.game_log.append("✅ 충격적인 홈스틸 성공!!! 포수 태그 피하며 득점합니다!")
            else:
                self.out_count += 1
                self.base3 = False
                self.game_log.append("❌ 홈스틸 저지 완료! 포수가 홈 플레이트 앞에서 주자를 완벽하게 블로킹하고 태그아웃 처리합니다!")
                self.check_three_out_change()

    def next_phase(self) -> None:
        if self.game_over: return

        current_away = self.get_away_score()
        current_home = self.get_home_score()

        if self.phase == "초" and self.inning >= 9: 
            if current_home > current_away:
                if len(self.home_inning_scores) >= self.inning:
                    self.home_inning_scores[self.inning - 1] = "X"
                self.end_kbo_game()
                return

        if self.phase == "말":
            if 9 <= self.inning < 11 and current_away != current_home:
                self.end_kbo_game()
                return
            if self.inning == 11:
                self.end_kbo_game()
                return

        if self.phase == "초":
            self.phase = "말"
        else:          
            self.phase = "초"
            self.inning += 1
            
        self.setup_half_inning()

    def end_kbo_game(self) -> None:
        self.game_over = True
        a, h = self.get_away_score(), self.get_home_score()
        
        if a == h: 
            self.game_result_msg = f"🤝 [무승부] 11회 {a}:{h} DRAW 종료."
        else: 
            if self.our_score > self.enemy_score:
                self.game_result_msg = f"🏆 [경기 종료] {self.our_score} 대 {self.enemy_score}(으)로 우리 팀 승리!"
            else:
                self.game_result_msg = f"😭 [경기 종료] {self.our_score} 대 {self.enemy_score}(으)로 우리 팀 패배."

    def process_error(self, log_prefix: str, bat: int) -> None:
        self.add_stat("E")
        self.game_log.append(log_prefix + f"🚨 수비 실책! 포구/송구 미스로 {bat}번 타자 출루.")
        if self.base1 and self.base2 and self.base3:
            self.update_live_scoreboard(1)
        elif self.base1 and self.base2: self.base3 = True
        elif self.base1: self.base2 = True
        else: self.base1 = True

    def evaluate_pitcher_scenario(self, score_diff: int = None, is_enemy: bool = False, is_defense: bool = True, **kwargs) -> int:
        if "is_defense" in kwargs:
            is_defense = kwargs["is_defense"]

        if score_diff is None:
            if is_defense:
                score_diff = self.our_score - self.enemy_score
            else:
                score_diff = self.enemy_score - self.our_score

        used_set = self.my_used_pitchers if is_defense else self.enemy_used_pitchers
        pitchers_list = self.my_pitchers if is_defene else self.enemy_pitchers 
        
        forbidden_indices = set()
        if self.inning < 8:
            forbidden_indices.add(8) #클로저 8회 이전 등판 금지 
        if self.inning < 7:
            forbidden_indices.add(6)
            forbidden_indices.add(7)#셋업맨 7회 이전 등판 금지 

        if abs(score_diff) >= 4:
            forbidden_indices.add(5)
            forbidden_indices.add(6)
            forbidden_indices.add(7)
            forbidden_indices.add(8)

        target = -1
        
        if 1 <= score_diff <= 3:
            if self.inning <= 6:
                target = 5
            elif self.inning == 7:
                target = 6 
            elif self.inning == 8:
                target = 7 
            else:
                target = 8 
                
        elif score_diff >= 4:
            if self.inning <= 6:
                target = 1
            elif self.inning <= 8:
                target = 2 
            else:
                target = 3
                
        elif score_diff == 0:
            if self.inning <= 6:
                target = 2 
            elif self.inning <= 7:
                target = 5 
            elif self.inning <= 8:
                target = 6 
            else:
                target = 8 
        else:
            abs_diff = abs(score_diff)
            if self.inning >= 7 and abs_diff >= 8:
                return -99
            elif abs_diff >= 4:
                target = 3 
            else:
                target = 1

        if target != -1 and target not in used_set and target not in forbidden_indices:
            return target

        search_candidates = [5, 6, 7, 8, 1, 2, 3, 4] if score_diff >= 0 else [1, 2, 3, 4, 5, 6, 7, 8]
        for idx in search_candidates:
            if idx not in used_set and idx not in forbidden_indices and idx < len(pitchers_list): 
                return idx

        for idx in range(1, len(pitchers_list)):
            if idx not in used_set:
                return idx
                
        return -99

    def check_pitch_clock_violation(self, log_prefix: str) -> bool:
        self.update_is_attack()
        current_p = self.get_current_enemy_pitcher() if self.is_attack else self.get_current_my_pitcher()
        violation_rate = 0.02 + (0.03 if current_p.stamina <= 5 else 0.0)
        if random.random() < violation_rate:
            if random.random() < 0.70:
                self.ball += 1
                self.game_log.append(log_prefix + f"⏱️ [피치클락 위반] 투수가 제한 시간을 초과했습니다! (자동 볼 1개 부여 -> {self.strike}S {self.ball}B)")
                if self.ball >= 4:
                    self.process_walk(is_defense=not self.is_attack)
                return True
            else:
                self.strike += 1
                self.game_log.append(log_prefix + f"⏱️ [피치클락 위반] 타자가 타석 복귀 시간을 지키지 않았습니다! (자동 스트라이크 1개 부여 -> {self.strike}S {self.ball}B)")
                if self.strike >= 3:
                    self.process_strikeout(is_defense=not self.is_attack, is_looking=True)
                return True

        return False 

    def play_defense_one_pitch(self, defense_choice: int) -> None:
        if self.game_over: return
        self.update_is_attack()
        p_my = self.get_current_my_pitcher()

        if (p_my.stamina <= 0 or self.inning >= 6) and p_my.role != "야수등판":
            target_idx = self.evaluate_pitcher_scenario(is_defense=True)
            
            if target_idx == -99:
                p_my.name = "⚠️ 야수(패전처리)"
                p_my.role = "야수등판"
                p_my.max_stamina = 15
                p_my.stamina = 15
                self.game_log.append("🚨 [예능 모드 활성화] 8점 차 이상 대참사 혹은 불펜 방전! 투수진을 아끼기 위해 야수가 마운드에 오릅니다!")
                p_my = self.get_current_my_pitcher()
            elif target_idx != self.my_pitcher_idx:
                self.my_pitcher_idx = target_idx
                self.my_used_pitchers.add(target_idx)
                p_my = self.get_current_my_pitcher()
                self.game_log.append(f"🔄 [명장 전술 작전] 시나리오 조건에 의거하여 투수를 교체합니다. [{p_my.role}] '{p_my.name}' 등판!")

        if p_my.role == "야수등판":
            speed = random.randint(110, 125)
            pitch_type = random.choice(["아리랑볼", "직구인척하는볼"])
            p_my.consume(1)
        else:
            if defense_choice == 3 and random.random() < 0.50:
                p_my.pitches_thrown += 1
            else:
                p_my.consume(1)
                
            pitch_type = random.choice(["직구", "슬라이더", "체인지업", "커브", "포크볼", "싱커"])
            speed = random.randint(PITCH_SPECS.get(pitch_type, {"speed_min":135, "speed_max":148})["speed_min"], PITCH_SPECS.get(pitch_type, {"speed_max":148})["speed_max"])
            
        self.our_total_pitches += 1
        
        enemy_stats = TEAMS[self.enemy_team]
        my_stats = TEAMS[self.my_team]
        penalty = p_my.get_penalty()
        matchup_mod = self.get_matchup_modifier(self.enemy_team, self.my_team)

        pitch_zone = random.randint(1, 9) if defense_choice != 2 else 0

        self.pitch_history.append(f"{pitch_type} ({speed}km/h) - 존: {pitch_zone if pitch_zone != 0 else '외곽'}")
        if len(self.pitch_history) > 3: self.pitch_history.pop(0)

        if defense_choice == 3:
            matchup_mod -= 0.05

        log_prefix = f"🥎 [{p_my.name} {speed}km/h {pitch_type}] -> "

        if self.trigger_wild_pitch_or_passed_ball(log_prefix, pitch_zone):
            return

        if pitch_zone == 0:
            roll_zone0 = random.random()
            
            if roll_zone0 < 0.25:
                self.process_pitch_hit_or_out(my_stats, enemy_stats, penalty, matchup_mod, log_prefix, False, True)
            
            elif roll_zone0 < 0.50:
                self.strike += 1
                self.game_log.append(log_prefix + f"헛스윙! 타자가 유인구에 완전히 속아 배트를 크게 돌립니다! 😱 ({self.strike}S {self.ball}B)")
                if self.strike >= 3:
                    self.process_strikeout(is_defense=True, is_looking=False)

            else:
                self.ball += 1
                self.game_log.append(log_prefix + f"볼! 타자가 침착하게 유인구를 골라냅니다. ({self.strike}S {self.ball}B)")
                if self.ball >= 4: 
                    self.process_walk(is_defense=True)
        else:
            swing_prob = 0.55 if defense_choice == 1 else 0.35
            
            if random.random() < swing_prob:
                if defense_choice == 1 and random.random() < 0.07:
                    self.strike = 0; self.ball = 0
                    self.enemy_batter_number = 1 if self.enemy_batter_number == 9 else self.enemy_batter_number + 1
                    self.out_count += 1
                    self.game_log.append(log_prefix + "⚾ [정면승부 적중] 타자가 힘껏 받아쳤으나 수비수 정면 땅볼! 가볍게 아웃 처리합니다.")
                    self.check_three_out_change()
                else:
                    self.process_pitch_hit_or_out(my_stats, enemy_stats, penalty, matchup_mod, log_prefix, True, True)
            else:
                self.strike += 1
                is_looking_strike = random.random() < 0.60
                
                # 💡 스트라이크 판정에 불복하여 확률적으로 감독 퇴장 트리거 (약 1.5% 확률)
                if random.random() < 0.015 and not self.manager_ejected:
                    self.eject_manager("볼/스트라이크 판정에 대해 더그아웃에서 거칠게 언쟁을 벌이다가")

                if self.strike >= 3:
                    self.process_strikeout(is_defense=True, is_looking=is_looking_strike)
                else:
                    if is_looking_strike:
                        self.game_log.append(log_prefix + f"👀 스트라이크! 루킹 스트라이크를 잡아냅니다. ({self.strike}S {self.ball}B)")
                    else:
                        self.game_log.append(log_prefix + f"💨 헛스윙! 타자의 방망이가 허공을 찌릅니다. ({self.strike}S {self.ball}B)")

    def play_turn(self, user_choice: int) -> None:
        if self.game_over: 
            return
        self.update_is_attack()
        log_prefix = f"[{self.inning}회 {'초' if self.phase == '초' else '말'}] "
        p_en = self.get_current_enemy_pitcher()
        
        if (p_en.stamina <= 0 or self.inning >= 6) and p_en.role != "야수등판":
            target_en_idx = self.evaluate_pitcher_scenario(is_defense=False)
            
            if target_en_idx == -99:
                p_en.name = "⚠️ 야수(상대패전처리)"
                p_en.role = "야수등판"
                p_en.max_stamina = 15
                p_en.stamina = 15
                self.game_log.append("🚨 [상대팀 예능 모드] 폭망 상태 혹은 불펜 고갈! 상대 감독이 포기하고 야수를 마운드에 올립니다!")
                p_en = self.get_current_enemy_pitcher()
            elif target_en_idx != self.enemy_pitcher_idx:
                self.enemy_pitcher_idx = target_en_idx
                self.enemy_used_pitchers.add(target_en_idx)
                p_en = self.get_current_enemy_pitcher()
                self.game_log.append(f"🔄 [상대 벤치 움직임] 시나리오 조건에 의거하여 투수를 교체합니다. [{p_en.role}] '{p_en.name}' 등판!")

        if p_en.role == "야수등판":
            speed = random.randint(110, 125)
            pitch_type = random.choice(["아리랑볼", "직구인척하는볼"])
            p_en.consume(1)
        else:
            pitch_type = random.choice(["직구", "슬라이더", "체인지업", "커브", "포크볼", "싱커"])
            speed = random.randint(PITCH_SPECS.get(pitch_type, {"speed_min":135, "speed_max":148})["speed_min"], PITCH_SPECS.get(pitch_type, {"speed_max":148})["speed_max"])

        runners_count = (1 if self.base1 else 0) + (1 if self.base2 else 0) + (1 if self.base3 else 0)

        strike_probability = 0.70
        mental_penalty = 0.0

        if (self.base3 or (self.base2 and self.base3)) and self.out_count < 2 and random.random() < 0.08:
            self.game_log.append(log_prefix + "🛑 [상대 벤치 작전] 득점권 위기를 맞은 상대 벤치가 고의사구 사인을 냅니다. 타자를 1루로 거릅니다.")
            self.process_walk(is_defense=False)
            return

        if self.base2 or self.base3:
            if runners_count >= 2:
                strike_probability += 0.05
                mental_penalty = -0.05
                p_en.stamina = max(0, p_en.stamina - 1)
            else:
                strike_probability += 0.02
                mental_penalty = -0.02

        if p_en.stamina < (p_en.max_stamina * 0.4):
            strike_probability -= 0.03
            mental_penalty += 0.01

        added_pitches = 1
        p_en.consume(added_pitches)
        self.enemy_total_pitches += added_pitches
        
        pitch_zone = random.randint(1, 9) if random.random() < max(0.50, strike_probability) else 0
        self.guess_zone = random.randint(1, 9)

        self.pitch_history.append(f"{pitch_type} ({speed}km/h) - 존: {pitch_zone if pitch_zone != 0 else '외곽'}")
        if len(self.pitch_history) > 3: self.pitch_history.pop(0)

        my_stats = TEAMS[self.my_team]
        enemy_stats = TEAMS[self.enemy_team]
        penalty = p_en.get_penalty()
        matchup_mod = self.get_matchup_modifier(self.my_team, self.enemy_team)
        is_zone_matched = (pitch_zone == self.guess_zone) and (pitch_zone != 0)
        
        log_prefix = f"🔮 [상대 {speed}km/h {pitch_type}] -> "
        b_ctx = f"[{self.my_batter_number}번 타자] "

        if self.trigger_wild_pitch_or_passed_ball(log_prefix, pitch_zone):
            return

        pinch_hit_buff = 0.0
        if self.inning >= 6:
            score_diff = self.our_score - self.enemy_score
            if score_diff <= 2 and self.my_batter_number in [7, 8, 9]:
                if random.random() < 0.35:
                    pinch_hit_buff = 0.07
                    b_ctx = f"[{self.my_batter_number}번 대타 요원] "
                    self.game_log.append(log_prefix + f"🔄 [대타 작전 발동] ⚡ 감독님의 신의 한 수! 승부처 득점을 위해 {self.my_batter_number}번 타자 자리에 '해결사 대타'를 대기석에서 긴급 투입합니다!")
                   
        total_buff = matchup_mod + self.hit_buff + 0.02 + mental_penalty + pinch_hit_buff

        hbp_probability = 0.005
        if p_en.stamina < (p_en.max_stamina * 0.4):
            hbp_probability += 0.01
        if runners_count >= 2:
            hbp_probability -= 0.003

        if pitch_zone == 0 and random.random() < hbp_probability:
            if random.random() < 0.15: # 💡 [벤클 트리거 1] 헤드샷 및 강한 사구 시 벤클 발동
                self.trigger_bench_clearing("상대 투수의 위험천만한 실투가 타자의 위협 부위(머리)를 직격했습니다!", log_prefix)
            else:
                self.game_log.append(log_prefix + b_ctx + "💥 악! 투수가 던진 실투가 타자의 몸을 강타합니다! 몸에 맞는 공으로 출루!")
            self.process_walk(is_defense=False)
            return
        
        if user_choice == 1:
            res = random.choices(["HR", "HIT", "OUT", "FOUL", "MISS"], weights=[180, 320, 200, 200, 100] if is_zone_matched else [40, 260, 350, 200, 150])[0] if pitch_zone != 0 else random.choices(["HIT", "OUT", "FOUL", "MISS"], weights=[70, 380, 150, 400])[0]
            self.process_swing_result(res, log_prefix, b_ctx, my_stats, enemy_stats, penalty, is_zone_matched, total_buff, pitch_zone)
        
        elif user_choice == 2:
            res = random.choices(["HIT", "OUT", "FOUL", "MISS"], weights=[520, 180, 200, 100] if is_zone_matched else [320, 330, 200, 150])[0] if pitch_zone != 0 else random.choices(["HIT", "OUT", "FOUL", "MISS"], weights=[80, 350, 200, 370])[0]
            self.process_swing_result(res, log_prefix, b_ctx, my_stats, enemy_stats, penalty, is_zone_matched, total_buff, pitch_zone)
       
        elif user_choice == 3: # 웨이팅
            if pitch_zone == 0 or random.random() < 0.25:
                self.ball += 1
                self.game_log.append(log_prefix + b_ctx + f"👀 예리한 선구안! 공을 골라냅니다. ({self.strike}S {self.ball}B)")
                if self.ball >= 4: 
                    self.process_walk(is_defense=False)
                    return
            else:
                self.strike += 1
                if self.strike >= 3: 
                    self.process_strikeout(is_defense=False, is_looking=True)
                    return
                else:
                    self.game_log.append(log_prefix + b_ctx + f"👀 스트라이크 지켜봄. ({self.strike}S {self.ball}B)")
                
        elif user_choice == 4: # 스퀴즈 번트
            if not self.base3:
                st.warning("3루에 주자가 없어 스퀴즈 번트가 불가능합니다.")
                return

            # 💡 [벤클 트리거 2] 6점 차 이상 대승 시 스퀴즈 번트 불문율 위반
            score_diff = self.our_score - self.enemy_score
            if score_diff >= 6 and random.random() < 0.35:
                self.trigger_bench_clearing("6점 차 이상 대승 중 기습 스퀴즈 번트를 시도하여 상대 마운드를 자극했습니다!")

            bunt_success_rate = max(0.30, min(0.75, 0.55 - (enemy_stats["defense"] - my_stats["hit"]) * 0.002))
            self.strike = 0; self.ball = 0
            bat = self.my_batter_number
            self.my_batter_number = 1 if bat == 9 else bat + 1
            if random.random() < bunt_success_rate:
                self.update_live_scoreboard(1)
                self.base3 = False
                if self.base2: self.base3 = True; self.base2 = False
                if self.base1: self.base2 = True; self.base1 = False
                self.out_count += 1
                self.game_log.append(log_prefix + b_ctx + "📉 기습 스퀴즈 번트 성공!!! 3루 주자가 홈을 밟았습니다! 타자는 1루에서 아웃. (+1점)")
                self.check_three_out_change()
            else:
                self.out_count += 1
                self.game_log.append(log_prefix + b_ctx + "❌ 스퀴즈 실패! 번트 타구가 포수 정면 플라이로 잡혔습니다. 주자 이동 불가.")
                self.check_three_out_change()
        
        elif user_choice == 5:
            if not (self.base1 or self.base2 or self.base3):
                st.warning("루상에 진루한 주자가 없어 런앤히트 작전이 불가능합니다.")
                return
                
            if pitch_zone != 0:
                res = random.choices(["HIT", "OUT", "FOUL"], weights=[600, 300, 100])[0]
                self.process_swing_result(res, log_prefix, b_ctx, my_stats, enemy_stats, penalty, is_zone_matched, total_buff, pitch_zone)
            else:
                if random.random() < 0.65:
                    self.out_count += min(3, self.out_count + 2)
                    self.strike = 0; self.ball = 0
                    bat = self.my_batter_number
                    self.my_batter_number = 1 if bat == 9 else bat + 1
                    self.base1 = self.base2 = self.base3 = False
                    self.game_log.append(log_prefix + f"😱 작전 대실패!! 볼 존 유인구에 타자가 헛스윙 삼진을 당한 사이, 스타트를 끊은 주자까지 포수 송구에 걸려 더블아웃(2아웃) 처리됩니다!")
                    self.check_three_out_change()
                    return
                else:
                    if self.strike < 2: self.strike += 1
                    self.game_log.append(log_prefix + b_ctx + "⚠️ 작전 미스! 빠지는 공을 타자가 간신히 걷어내며 파울을 만들었습니다.")
                    
        if self.inning >= 9 and self.phase == "말":
            home_score = self.get_home_score()
            away_score = self.get_away_score()
            if home_score > away_score:
                msg = "🎉 [끝내기 역전!] 홈팀이 극적인 역전 타구로 경기 마침표를 찍습니다!"
                self.game_log.append(msg)
                self.end_kbo_game()
                return

    def process_swing_result(self, res, log_prefix, b_ctx, my_stats, enemy_stats, penalty, is_zone_matched, total_buff, pitch_zone) -> None:
        match_msg = "🎯 [노림수 적중] " if is_zone_matched else ""

        is_power_hitter = my_stats.get("homerun", 30) >= 40
        is_contact_pest = (my_stats.get("hit", 65) >= 70 and not is_power_hitter) or (self.my_batter_number in [2, 9])

        if res == "HR":
            self.add_stat("H")
            pts = (1 if self.base1 else 0) + (1 if self.base2 else 0) + (1 if self.base3 else 0) + 1
            self.base1 = self.base2 = self.base3 = False
            self.update_live_scoreboard(pts)
                
            # 💡 [신규 추가] 확률적 장외 홈런 멘트 분기 (약 1% 확률)
            if random.random() < 0.01:
                hr_msg = f"🚀💥 [장외 대형 홈런!!] {b_ctx} 타구가 야구장 장외로 까마득하게 넘어갑니다! 엄청난 비거리! (+{pts}점)"
            else:
                hr_msg = f"🔥 {b_ctx} 홈런!! (+{pts}점)"

            self.game_log.append(log_prefix + match_msg + hr_msg)

            #실제 점수차 계산 
            current_score_diff = self.our_score - self.enemy_score 

            #대승할 때만 트리거 
            if current_score_diff >= 6 and random.random() < 0.25:
                self.trigger_bench_clearing("큰 점수 차에서 타자가 화려한 빠던과 과도한 승리 세리머니를 선보여 상대 벤치를 자극했습니다!")

            return

        elif res == "HIT" and total_buff < 0 and random.random() < 0.20:
            res = "OUT" 
            
        elif res == "OUT" and total_buff > 0:
            p_en = self.get_current_enemy_pitcher()
            pitcher_stamina_factor = 0.5 if p_en.stamina > (p_en.max_stamina * 0.7) else 1.0 
                
            if random.random() < (total_buff * 0.05 * pitcher_stamina_factor): 
                res = "HIT"

            else:
                if self.out_count == 0 and self.base1 and self.base2 and random.random() < 0.002:
                    self.strike = 0; self.ball = 0
                    self.out_count = 3
                    self.base1 = self.base2 = self.base3 = False
                    self.game_log.append(log_prefix + b_ctx + "😱 [대참사! 삼중살(트리플 플레이)!] 날카로운 직선타가 내야수 글러브로 흡수된 뒤, 2루, 1루 주자까지 모조리 태그아웃! 순식간에 쓰리아웃 체인지!!")
                    self.check_three_out_change()
                    return

                self.strike = 0; self.ball = 0
                bat = self.my_batter_number
                self.my_batter_number = 1 if bat == 9 else bat + 1

                if self.out_count < 2 and self.base1 and random.random() < 0.25:
                    self.out_count += 2
                    self.base1 = False
                    self.game_log.append("💥 [병살타!] 버프 투구였으나 뼈아픈 병살타로 이어집니다!")
                else:
                    self.out_count += 1
                    out_roll = random.random()
                    is_pest = locals().get('is_contact_pest', False)
                    if is_pest:
                        self.game_log.append(log_prefix + "⚾ 빗맞은 내야 땅볼 아웃.")
                    elif out_roll < 0.40:
                        self.game_log.append(log_prefix + "⚾ 유격수 방면 정면 땅볼 아웃.")
                    elif out_roll < 0.75:
                        self.game_log.append(log_prefix + "⚾ 큼지막한 외야 뜬공(플라이) 아웃.")
                    else:
                        self.game_log.append(log_prefix + "⚾ 3루수 정면으로 빨려 들어가는 날카로운 라인드라이브 아웃!")
                self.check_three_out_change()
                return 
                  
        if res == "MISS":
            if pitch_zone == 0 and random.random() < 0.50:
                self.ball += 1
                self.game_log.append(log_prefix + b_ctx + f"🔍 참아냈습니다! 빠지는 유인구를 침착하게 골라냅니다. ({self.strike}S {self.ball}B)")
                if self.ball >= 4:
                    self.process_walk(is_defense=False)
                return
                
            self.strike += 1
            self.game_log.append(log_prefix + b_ctx + f"헛스윙! ({self.strike}S {self.ball}B)")
            if self.strike >= 3: 
                self.process_strikeout(is_defense=False, is_looking=False)
                return 
                
        elif res == "FOUL":
            foul_decision = True
            #2스트라이크 이후 컨택 능력 높을수록 파울 커트 확률 상승
            if self.strike == 2:
                foul_cut_bonus = 0.20 + (my_stats.get("hit", 50) * 0.003)

                #용규형 타자 보정
                if is_contact_pest:
                    foul_cut_bonus += 0.15

                #파울 커트
                if random.random() < foul_cut_bonus:
                    foul_decision = True

            if is_power_hitter and self.strike == 2 and random.random() < 0.30:
                res = "MISS"
                foul_decision = False 
                
            if foul_decision:
                if self.strike < 2: 
                    self.strike += 1
                    self.game_log.append(log_prefix + b_ctx + f"파울. ({self.strike}S {self.ball}B)")
                else:
                    if is_contact_pest or random.random() < 0.40:
                        cut_logs = [
                            f"⚡ [용규놀이 발동!] 2스트라이크 이후 끈질기게 공을 커트해내며 투수의 투구수를 늘립니다! ({self.strike}S {self.ball}B)",
                            f"🛡️ [지독한 커트] 꽉 찬 공을 어떻게든 방망이에 맞혀 파울을 만듭니다! 끈질긴 볼배합 싸움! ({self.strike}S {self.ball}B)",
                            f"⚾ 파울볼! 벼랑 끝에서 배트를 커트해내며 2스트라이크 볼카운트를 계속 유지합니다! ({self.strike}S {self.ball}B)"
                        ]
                        self.game_log.append(log_prefix + b_ctx + random.choice(cut_logs))
                    else:
                        self.game_log.append(log_prefix + b_ctx + f"파울볼! 2스트라이크 이후 파울로 기존 볼 카운트가 정교하게 유지됩니다. ({self.strike}S {self.ball}B)")
                return
                
            else:
                self.process_strikeout(is_defense=False, is_looking=False)
                return 
            
        else:
            bat = self.my_batter_number
            self.strike = 0; self.ball = 0
            self.my_batter_number = 1 if bat == 9 else bat + 1

            if res == "HIT" and is_power_hitter and random.random() < 0.20:
                res = "HR"
            
            # 💡 [레어] 인사이드 더 파크 홈런 (그라운드 홈런)
            if res == "HIT" and random.random() < 0.005:
                self.add_stat("H")
                pts = (1 if self.base1 else 0) + (1 if self.base2 else 0) + (1 if self.base3 else 0) + 1
                self.base1 = self.base2 = self.base3 = False
                self.update_live_scoreboard(pts)
                self.game_log.append(log_prefix + match_msg + f"🏃‍♂️💨 [인사이드 더 파크 홈런!!] {b_ctx} 외야수가 펜스에 크게 부딪히며 공을 더듬는 사이! 타자 주자가 미친 전력 질주로 홈까지 훔쳐냅니다!!! (+{pts}점)")
                return

            if res == "HR":
                self.add_stat("H")
                pts = (1 if self.base1 else 0) + (1 if self.base2 else 0) + (1 if self.base3 else 0) + 1
                self.base1 = self.base2 = self.base3 = False
                self.update_live_scoreboard(pts)
                
                # 💡 [벤클 트리거 3] 6점 차 이상 대승 중 과도한 배트 플립 및 홈런 세리머니
                score_diff = self.our_score - self.enemy_score if self.is_attack else self.enemy_score - self.our_score
                if score_diff >= 6 and random.random() < 0.25:
                    self.trigger_bench_clearing("큰 점수 차에서 타자가 화려한 빠던과 과도한 승리 세리머니를 선보여 상대 벤치를 자극했습니다!")

                self.game_log.append(log_prefix + match_msg + f"🔥 {b_ctx} 홈런!! (+{pts}점)")

            elif res == "HIT":             
                self.add_stat("H")
                gained = 0
                hit_roll = random.random()
                batter_speed_factor = 0.05 + (my_stats["hit"] * 0.0005)
                if is_contact_pest:
                    batter_speed_factor += 0.05
                
                if hit_roll < 0.03 + (batter_speed_factor * 0.2): 
                    if self.base3: gained += 1
                    if self.base2: gained += 1
                    if self.base1: gained += 1
                    self.base3 = True; self.base2 = False; self.base1 = False
                    self.game_log.append(log_prefix + match_msg + f"🔥 {b_ctx} 우중간을 완전히 가르는 3루타!!! (+{gained}점)")
                elif hit_roll < 0.18 + batter_speed_factor: 
                    if self.base3: gained += 1
                    if self.base2: gained += 1
                    if self.base1: self.base3 = True; self.base1 = False
                    else: self.base3 = False
                    self.base2 = True; self.base1 = False
                    self.game_log.append(log_prefix + match_msg + f"🌟 좌익수 키를 넘기는 2루타!! (+{gained}점)")
                else: 
                    if self.base3: gained += 1
                    if self.base2: gained += 1
                    self.base3 = self.base1; self.base2 = False; self.base1 = True
                    self.game_log.append(log_prefix + match_msg + f"⚾ 깨끗한 우전 안타! 주자 한 칸씩 진루합니다. (+{gained}점)")
                
                if gained > 0: 
                    self.update_live_scoreboard(gained)
                    
            elif res == "OUT":
                error_rate = max(0.025, 0.075 - (enemy_stats["defense"] * 0.0005))

                if random.random() < error_rate:
                    self.strike = 0
                    self.ball = 0
                    
                    if hasattr(self, 'add_stat_error'):
                        self.add_stat_error(is_defense=False)
                    else:
                        self.enemy_team_errors = getattr(self, 'enemy_team_errors', 0) + 1
                    
                    bat = self.my_batter_number
                    self.my_batter_number = 1 if bat == 9 else bat + 1
                    
                    gained = 0
                    if self.base3: gained += 1; self.base3 = False
                    if self.base2: self.base3 = True; self.base2 = False
                    if self.base1: self.base2 = True
                    self.base1 = True
                
                    if gained > 0: self.update_live_scoreboard(gained)
                
                    enemy_err_log = random.choice([
                        "🔥 [상대 실책 대박] 평범한 땅볼 타구! 그런데 상대 내야수가 송구 실책을 저지르며 타자가 안전하게 1루를 밟습니다! 🤩",
                        "🔥 [상대 알까기] 완전히 잡힌 플라이 타구였으나, 상대 외야수가 낙구 지점을 놓치며 글러브에서 공을 떨어뜨립니다! 행운의 출루!",
                        "🔥 [상대 야수 선택 에러] 상대 유격수가 볼을 더듬는 사이 주자와 타자 모두 세이프! 수비 집중력이 무너집니다!"
                    ])
                    self.game_log.append(log_prefix + b_ctx + match_msg + enemy_err_log + (f" (+{gained}점)" if gained > 0 else ""))
                    return

                # 💡 [레어] 삼중살 (트리플 플레이)
                if self.out_count == 0 and self.base1 and self.base2 and random.random() < 0.002:
                    self.strike = 0; self.ball = 0
                    self.out_count = 3
                    self.base1 = self.base2 = self.base3 = False
                    self.game_log.append(log_prefix + b_ctx + "😱 [대참사! 삼중살(트리플 플레이)!] 병살 타구가 나오며 2루, 1루 주자 및 타자 주자까지 모조리 잡힙니다! 순식간에 쓰리아웃 체인지!!")
                    self.check_three_out_change()
                    return

                self.strike = 0
                self.ball = 0 

                bat = self.my_batter_number
                self.my_batter_number = 1 if bat == 9 else bat + 1

                if self.out_count < 2 and self.base1 and random.random() < 0.25:
                    self.out_count += 2
                    self.base1 = False
                    
                    # 💡 [벤클 트리거 4/5] 거친 플레이 및 트래시 토크 
                    if random.random() < 0.03:
                        self.trigger_bench_clearing("2루 태그 과정에서 주자와 내야수가 과도하게 부딪히며 신경전이 벌어졌습니다!")
                    else:
                        self.game_log.append(log_prefix + "💥 2루수-1루수 이어지는 뼈아픈 병살타 아웃!")
                elif self.out_count < 2 and self.base3 and random.random() < 0.45:
                    self.out_count += 1
                    self.base3 = False
                    self.update_live_scoreboard(1)
                    
                    # 💡 [벤클 트리거 5] 홈 슬라이딩 충돌 거친 플레이
                    if random.random() < 0.04:
                        self.trigger_bench_clearing("홈 쇄도 중 주자와 포수의 격렬한 충돌이 터졌습니다!")
                    else:
                        self.game_log.append(log_prefix + "🕊️ 깊숙한 외야 플라이! 3루 주자 홈인, 희생플라이 타점!") 
                         
                else:
                    self.out_count += 1
                    out_roll = random.random()
                
                    is_pest = locals().get('is_contact_pest', False)
                
                    if is_pest:
                        self.game_log.append(log_prefix + "⚾ 빗맞은 내야 땅볼 아웃.")
                    elif out_roll < 0.40:
                        self.game_log.append(log_prefix + "⚾ 유격수 방면 정면 땅볼 아웃.")
                    elif out_roll < 0.75:
                        self.game_log.append(log_prefix + "⚾ 큼지막한 외야 뜬공(플라이) 아웃.")
                    else:
                        self.game_log.append(log_prefix + "⚾ 3루수 정면으로 빨려 들어가는 날카로운 라인드라이브 아웃!")

                self.check_three_out_change()

    def process_pitch_hit_or_out(self, my_stats, enemy_stats, penalty, matchup_mod, log_prefix, is_strike_context: bool, is_defense: bool) -> None:
        self.update_is_attack()
        bat = self.enemy_batter_number
        p_my = self.get_current_my_pitcher()
        if p_my.stamina <= (p_my.max_stamina * 0.3) and not getattr(p_my, 'warned_stamina', False):
            p_my.warned_stamina = True
            self.game_log.append(f"⚠️ [벤치 비상] 마운드의 {p_my.name} 투수가 현저히 지쳤습니다! (남은 체력: {p_my.stamina}/{p_my.max_stamina})")
            self.game_log.append("💡 [감독 지시] 구위와 제구력이 크게 떨어져 실점 확률이 높아집니다. 불펜 교체를 고려하십시오!")

        if self.out_count < 2 and self.base3:
            if random.random() < 0.25:
                self.game_log.append(log_prefix + "⚡ [적팀 작전 발동] 상대 감독이 기습적인 스퀴즈 번트 지시를 내립니다!")
                
                score_diff = self.enemy_score - self.our_score
                if score_diff >= 6 and random.random() < 0.35:
                    self.trigger_bench_clearing("상대 팀이 6점 차 이상 대승 중에 스퀴즈 번트를 대어 불문율을 위반했습니다!")

                if pitch_zone != 0 if 'pitch_zone' in locals() else True:
                    if random.random() < 0.70:
                        self.out_count += 1
                        self.enemy_score += 1
                        self.base3 = False
                        self.update_live_scoreboard(0)
                        self.game_log.append(log_prefix + "💥 [스퀴즈 성공!] 타자가 침착하게 번트를 대어 3루 주자를 홈으로 불러들입니다! (타자 아웃, +1점)")
                        self.check_three_out_change()
                        return
                    else:
                        self.out_count += 1
                        self.game_log.append(log_prefix + "⚠️ [스퀴즈 실패] 번트 타구가 뜬공이 되며 포수에게 바로 잡힙니다!")
                        self.check_three_out_change()
                        return

                else: 
                    self.out_count += 1
                    self.base3 = False
                    self.game_log.append(log_prefix + "😱 [작전 파탄!] 투구가 빠지는 공! 3루 주자가 스타트를 끊었으나 포수 태그아웃 처리됩니다!")
                    self.check_three_out_change()
                    return
                    
        if (self.base1 or self.base2) and not self.base3 and self.out_count < 3:
            steal_attempt_prob = 0.08
            if self.inning >= 6 and (self.our_score - self.enemy_score) <= 2:
                steal_attempt_prob += 0.05
                
            if random.random() < steal_attempt_prob:
                score_diff = self.enemy_score - self.our_score
                if score_diff >= 6 and random.random() < 0.40:
                    self.trigger_bench_clearing("상대 팀이 6점 차 이상으로 이기고 있는 상황에서 도루를 감행했습니다!")

                if self.base3 and random.random() < 0.01:
                    self.game_log.append(log_prefix + "🔥 [🚨 비상사태!! 홈스틸 시도] 투수가 와인드업에 들어간 순간, 3루 주자가 홈으로 무모하게 몸을 던졌습니다!!! 전 관중 기립!!!")
                    
                    home_cs_rate = 0.75 + (my_stats["defense"] - 65) * 0.002
                    if p_my.stamina < (p_my.max_stamina * 0.3):
                        home_cs_rate -= 0.10
                    home_cs_rate = max(0.40, min(0.95, home_cs_rate))
                    
                    if random.random() < home_cs_rate:
                        self.out_count += 1
                        self.base3 = False
                        self.game_log.append(log_prefix + "⚡ [도루 저지 성공] 투수의 재빠른 홈 송구!! 포수가 홈 플레이트를 슬라이딩하던 주자를 완벽하게 블로킹하며 태그 아웃시켰습니다! 아웃! 😤")
                        self.check_three_out_change()
                        return
                    else:
                        self.base3 = False
                        self.update_live_scoreboard(1)
                        self.game_log.append(log_prefix + "😱 [상대 홈스틸 성공] 세상에 이런 일이!! 투수의 허점을 완벽하게 찌르고 3루 주자가 홈을 훔쳐냈습니다! 상대 팀의 미친 승부수 적중! (+1점)")
                        
                elif (self.base1 or self.base2) and not self.base3:
                    self.game_log.append(log_prefix + "🏃‍♂️ [상대 기습 도루] 앗! 투수가 와인드업에 들어간 순간, 루상의 주자가 다음 베이스로 스타트를 끊었습니다!!")
                    
                    cs_rate = 0.30 + (my_stats["defense"] - 65) * 0.003
                    if p_my.stamina < (p_my.max_stamina * 0.3):
                        cs_rate -= 0.08
                    cs_rate = max(0.10, min(0.70, cs_rate))
                    
                    is_3rd_steal = self.base2
                    
                    if random.random() < cs_rate:
                        self.out_count += 1
                        if is_3rd_steal:
                            self.base2 = False
                            self.game_log.append(log_prefix + "⚡ [도루 저지 성공] 포수가 총알 같은 3루 송구로 슬라이딩하던 주자를 저격했습니다! 아웃! 😤")
                        else:
                            self.base1 = False
                            self.game_log.append(log_prefix + "⚡ [도루 저지 성공] 우리 포수의 앉아쏴 레이저 송구!! 2루에서 주자를 지워버립니다! 아웃! ⚾")
                        self.check_three_out_change()
                        return
                    else:
                        if is_3rd_steal:
                            self.base3 = True; self.base2 = False
                            self.game_log.append(log_prefix + "💨 [도루 허용] 상대 2루 주자가 기가 막힌 타이밍에 3루를 훔쳐냈습니다. 3루 위기!")
                        else:
                            self.base2 = True; self.base1 = False
                            self.game_log.append(log_prefix + "💨 [도루 허용] 투수의 모션을 완전히 빼앗겼습니다! 상대 주자 2루 안착.")

        hbp_probability = 0.01
        if p_my.stamina < (p_my.max_stamina * 0.4):
            hbp_probability += 0.02
            
        if not is_strike_context and random.random() < hbp_probability:
            if random.random() < 0.15: # 💡 [벤클 트리거 1] 수비 중 사구 벤클
                self.trigger_bench_clearing("우리 투수의 빠른 공이 상대 타자 위협 부위를 강타했습니다!", log_prefix)
            else: 
                self.game_log.append(log_prefix + "💥 아웃사이드 실투! 투수가 던진 빠른 공이 상대 타자의 몸에 맞았습니다. 사구 허용.")
            self.process_walk(is_defense=True)
            return

        enemy_hit_base = enemy_stats["hit"] * 0.0020
        enemy_hr_base = enemy_stats["homerun"] * 0.0010

        hit_prob = 0.20 + (enemy_hit_base - my_stats["defense"] * 0.0010) + penalty + matchup_mod
        hr_prob = 0.015 + enemy_hr_base + (matchup_mod * 0.01)

        if p_my.stamina < (p_my.max_stamina * 0.5):
            hit_prob += 0.03
            hr_prob += 0.01

        if self.base2 or self.base3:
            hit_prob += 0.04
            hr_prob += 0.02
        
        if not is_strike_context: 
            hit_prob *= 0.48
            hr_prob *= 0.12

        hit_prob = max(0.08, min(0.42, hit_prob))
        hr_prob = max(0.005, min(0.10, hr_prob))
        
        roll = random.random()
        
        if roll < hr_prob:
            self.add_stat("H")
            self.enemy_batter_number = 1 if bat == 9 else bat + 1
            self.strike = 0; self.ball = 0
            pts = (1 if self.base1 else 0) + (1 if self.base2 else 0) + (1 if self.base3 else 0) + 1
            self.base1 = self.base2 = self.base3 = False
            self.update_live_scoreboard(pts)

            if random.random() < 0.01:
                self.game_log.append(log_prefix + f"🚀💥 [장외 홈런 피안타!] 관중석을 완전히 넘어가는 무자비한 장외 홈런 허용! (+{pts}점)")
            else:     
                self.game_log.append(log_prefix + f"💥 실투 실점! {pts}점 홈런 허용.")
            
        elif roll < (hit_prob + hr_prob):
            self.enemy_batter_number = 1 if bat == 9 else bat + 1
            self.strike = 0; self.ball = 0
            self.add_stat("H")
            gained = 0

            hit_roll = random.random()
            if hit_roll < 0.25 and (self.base1 or self.base2 or self.base3):
                if self.base3: gained += 1
                if self.base2: gained += 1
                if self.base1: self.base3 = True; self.base1 = False
                else: self.base3 = False
                self.base2 = True
                self.game_log.append(log_prefix + f"🌟 [상대 집중 타선] 좌익수 키를 무자비하게 넘기는 좌중간 대형 2루타 피안타! (+{gained}점)")
            else:
                if self.base3: gained += 1
                if self.base2: gained += 1
                self.base3 = self.base1; self.base2 = False; self.base1 = True
                self.game_log.append(log_prefix + f"🌟 피안타! 정교하게 밀어친 안타로 주자 주판알 튕기듯 진루합니다. (+{gained}점)")
                
            if gained > 0: self.update_live_scoreboard(gained)
            
        else:
            is_two_strikes = (self.strike == 2)
            foul_cut_prob = 0.38 if is_two_strikes else 0.22
            
            if roll > (hit_prob + hr_prob) and random.random() < foul_cut_prob:
                if self.strike < 2: 
                    self.strike += 1
                    self.game_log.append(log_prefix + f"파울! 타자가 날카롭게 커트해 냅니다. ({self.strike}S {self.ball}B)")
                else:
                    self.game_log.append(log_prefix + f"파울! 2스트라이크 이후 파울로 카운트는 계속 유지됩니다. 끈질깁니다! ({self.strike}S {self.ball}B)")
                return

            error_prob = 0.04 + (100 - my_stats["defense"]) * 0.001
            if p_my.stamina < (p_my.max_stamina * 0.3):
                error_prob += 0.03

            if random.random() < error_prob:
                if self.is_attack:
                    bat = self.my_batter_number
                    self.my_batter_number = 1 if bat == 9 else bat + 1
                else: 
                    bat = self.enemy_batter_number
                    self.enemy_batter_number = 1 if bat == 9 else bat + 1
                    
                self.strike = 0
                self.ball = 0
                self.add_stat("E")
                
                gained = 0
                if self.base3: gained += 1; self.base3 = False
                if self.base2: self.base3 = True; self.base2 = False
                if self.base1: self.base2 = True
                self.base1 = True
                
                if gained > 0: self.update_live_scoreboard(gained)
                
                err_log = random.choice([
                    "⚠️ [치명적 실책] 평범한 내야 땅볼! 그러나 1루수의 포구 실책이 나오며 타자가 살아나갑니다! 😱",
                    "⚠️ [송구 실책] 유격수가 타구를 잘 잡았으나 1루에 악송구를 범했습니다! 공이 뒤로 빠집니다! 😭",
                    "⚠️ [알까기 실책] 외야 플라이성 타구! 어처구니없게도 좌익수가 공을 글러브에서 떨어뜨립니다!"
                ])
                self.game_log.append(log_prefix + err_log + (f" (+{gained}점)" if gained > 0 else ""))
                return
                
            self.strike = 0
            self.ball = 0

            if self.is_attack:
                bat = self.my_batter_number
                self.my_batter_number = 1 if bat == 9 else bat + 1
            else:
                bat = self.enemy_batter_number
                self.enemy_batter_number = 1 if bat == 9 else bat + 1
                
            if self.base1 and self.out_count < 2 and random.random() < 0.25:
                self.out_count += 2
                self.base1 = False
                self.game_log.append(log_prefix + "😱 우리 수비진의 환상적인 병살타 유도 성공!")
            else:
                self.out_count += 1
                out_style = random.random()
                if out_style < 0.40:
                    self.game_log.append(log_prefix + "⚾ 내야 땅볼 유도! 1루에서 아웃 처리합니다.")
                elif out_style < 0.75:
                    self.game_log.append(log_prefix + "⚾ 큰 타구였으나 외야수가 침착하게 플라이 아웃으로 잡아냅니다.")
                else:
                    self.game_log.append(log_prefix + "⚾ 투수 앞 빗맞은 땅볼! 가볍게 아웃.")
            self.check_three_out_change()
            return 

        if self.inning >= 9 and self.phase == "말" and not self.is_home_team and self.get_home_score() > self.get_away_score():
            self.game_log.append("❌ 이닝 끝내기 패배.")
            self.end_kbo_game()

    def check_pinch_runner_event(self, base_type: str, log_prefix: str) -> None: 
        """7회 이후 박빙 상황 시 확률적 대주자 투입"""
        if self.inning >= 7 and abs(self.our_score - self.enemy_score) <= 2:
            if random.random() < 0.25: # 25% 확률로 대주자 투입
                # 백업 명단에서 대주자 요원 추출
                backup_list = TEAM_ROSTERS[self.my_team]["batters"].get("백업(4)", [])
                pr_player = next((p for p in backup_list if "대주자" in p or "잽싼" in p or "발" in p), backup_list[-1] if backup_list else "대주자 요원")
                
                # 대주자 버프 부여 (도루 버프 가산)
                self.hit_buff += 0.03 # 주루 플레이로 인한 마운드 압박
                self.game_log.append(
                    log_prefix + f"🏃‍♂️💨 [대주자 투입] ⚡ 승부처! 벤치에서 발 빠른 대주자 '{pr_player}'(을)를 {base_type}에 대주자로 전격 투입합니다! (도루/진루 보너스 가산)"
                )
                
                pr_chats = [
                    f"와 {pr_player} 대주자 나왔다 ㅋㅋㅋ 뛸 생각만 하고 있네",
                    "대주자 발 미쳤음 ㅋㅋㅋ 무조건 도루 가자!",
                    "투수 견제구 계속 던지겠네 ㅋㅋㅋ 쫄렸다"
                ]
                self.trigger_special_chat(pr_chats)

    def process_walk(self, is_defense: bool) -> None:
        self.add_stat("B", 1)
        
        if is_defense:
            self.enemy_bb = getattr(self, 'enemy_bb', 0) + 1
        else:
            self.our_bb = getattr(self, 'our_bb', 0) + 1 
            
        self.strike = 0
        self.ball = 0
        
        gained = 0
        if self.base1 and self.base2 and self.base3:
            gained = 1
        elif self.base1 and self.base2:
            self.base3 = True
        elif self.base1:
            self.base2 = True
        else:
            self.base1 = True
            
        if gained > 0:
            self.update_live_scoreboard(gained)
            self.game_log.append("🚶‍♂️ 볼넷 밀어내기 득점! 주자 전원 진루합니다. (+1점)")
        else:
            self.game_log.append("🚶‍♂️ 볼넷 출루! 주자가 한 베이스씩 밀려 나갑니다.")
            
        if not is_defense:
            bat = self.my_batter_number
            self.my_batter_number = 1 if bat == 9 else bat + 1
        else:
            bat = self.enemy_batter_number
            self.enemy_batter_number = 1 if bat == 9 else bat + 1
            
        self.check_three_out_change()

    def process_strikeout(self, is_defense: bool, is_looking: bool = False) -> None:
        # 💡 [레어] 스트라이크아웃 낫아웃
        if not is_looking and (not self.base1 or self.out_count == 2) and random.random() < 0.03:
            if random.random() < 0.70:
                self.strike = 0; self.ball = 0
                self.base1 = True
                self.game_log.append("⚡ [낫아웃 폭투 출루!] 포수가 3스트라이크 공을 뒤로 흘렸습니다! 타자 주자가 1루로 전력 질주하여 살아나갑니다!")
                return
            else:
                self.game_log.append("⚡ [낫아웃 송구 아웃] 포수가 빠뜨린 공을 재빠르게 주워 1루에 송구하며 가까스로 삼진 아웃 처리합니다.")

        self.strike = 0
        self.ball = 0
        self.out_count += 1
        
        if is_defense:
            if is_looking:
                self.game_log.append(f"👀 [루킹 삼진아웃!] 투수가 꽂아 넣은 꽉 찬 스트라이크를 타자가 바라만 보며 루킹 삼진으로 물러납니다!")
            else:
                self.game_log.append(f"⚡ 탈삼진 성공! 타자의 배트가 허공을 가릅니다.")
            bat = self.enemy_batter_number
            self.enemy_batter_number = 1 if bat == 9 else bat + 1
        else:
            if is_looking:
                self.game_log.append(f"👀 [루킹 삼진아웃!] 타자가 꼼짝없이 꽂히는 스트라이크를 바라만 보며 루킹 삼진 아웃!")
            else:
                self.game_log.append(f"⚡ 헛스윙 삼진 아웃.")
            bat = self.my_batter_number
            self.my_batter_number = 1 if bat == 9 else bat + 1
            
        self.check_three_out_change()

    def check_three_out_change(self) -> None:
        if self.out_count >= 3:
            self.game_log.append("📢 쓰리아웃 체인지!")
            
            if self.inning >= 9 and self.phase == "초" and self.get_home_score() > self.get_away_score():
                if len(self.home_inning_scores) >= self.inning:
                    self.home_inning_scores[self.inning - 1] = "X"
                self.end_kbo_game()
                return
            
            self.next_phase()


# =====================================================================
# [FRONTEND] 통합 렌더러
# =====================================================================
def main() -> None:
    st.set_page_config(layout="wide")
    st.markdown("<style>.stButton>button { width: 100%; font-size: 14px !important; font-weight: bold; }</style>", unsafe_allow_html=True)
    
    st.title("⚾ 순수한 야구 시뮬레이터")

    if "full_kbo_engine" not in st.session_state: st.session_state.full_kbo_engine = None
    if "nc_diamonds" not in st.session_state: st.session_state.nc_diamonds = 1000
    if "my_team" not in st.session_state: st.session_state.my_team = "💖 핑크 돌핀스"

    with st.sidebar:
        st.header("💎 비밀 상점 (P2W)")
        st.write(f"보유 다이아: {st.session_state.nc_diamonds} 💎")
        
        if st.button("💳 N Pay로 5000 다이아 충전 (11만원)"):
            st.session_state.nc_diamonds += 5000
            st.toast("💸 지갑 전사 발동! 5000 다이아가 즉시 충전되었습니다핑!", icon="💎")
            st.rerun()
            
        st.markdown("---")
        
        if st.session_state.full_kbo_engine and not st.session_state.full_kbo_engine.game_over:
            game = st.session_state.full_kbo_engine
            current_is_our_turn = (not game.is_home_team and game.phase == "초") or (game.is_home_team and game.phase == "말")
            
            if current_is_our_turn:
                st.markdown("#### 🌸 [공격 턴 전용 아이템]")
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("🔥 **타격 확률 극대화**  \n`안타 확률 +2.0%` (100💎)")
                with col2:
                    if st.button("구매", key="buy_buff_hit"):
                        if st.session_state.nc_diamonds >= 100:
                            st.session_state.nc_diamonds -= 100
                            game.hit_buff += 0.085
                            st.toast("🔥 타자들에게 각성제를 주입했습니다! 안타 확률 가산!", icon="💪")
                            st.rerun()
                        else:
                            st.error("다이아 부족!")

                col1_d, col2_d = st.columns([3, 1])
                with col1_d:
                    st.markdown("🤫 **멘탈 교란 찌라시**  \n`적 투수 체력 -20` (150💎)")
                with col2_d:
                    if st.button("구매", key="buy_debuff_scandal"):
                        if st.session_state.nc_diamonds >= 150:
                            st.session_state.nc_diamonds -= 150
                            p_en = game.get_current_enemy_pitcher()
                            p_en.stamina = max(5, p_en.stamina - 20)
                            st.toast("🚨 적 투수 라커룸에 찌라시를 투척했습니다! 제구력 흔들림!", icon="🤫")
                            st.rerun()
                        else:
                            st.error("다이아 부족!")

            else:
                st.markdown("#### 🔋 [수비 턴 전용 아이템]")
                
                col3, col4 = st.columns([3, 1])
                with col3:
                    st.markdown("💉 **특수 링거 수액**  \n`현재 투수 체력 +25` (150💎)")
                with col4:
                    if st.button("구매", key="buy_buff_stamina_1"):
                        if st.session_state.nc_diamonds >= 150:
                            st.session_state.nc_diamonds -= 150
                            p = game.get_current_my_pitcher()
                            p.stamina = min(p.max_stamina, p.stamina + 25)
                            st.toast("🔋 마운드로 특수 링거 공수 완료! 투수 기력 충전!", icon="💪")
                            st.rerun()
                        else:
                            st.error("다이아 부족!")

                col3_d, col4_d = st.columns([3, 1])
                with col3_d:
                    st.markdown("🔊 **관중 매수 야유**  \n`적 안타 확률 -2%` (120💎)")
                with col4_d:
                    if st.button("구매", key="buy_debuff_crowd"):
                        if st.session_state.nc_diamonds >= 120:
                            st.session_state.nc_diamonds -= 120
                            game.hit_buff -= 0.05
                            st.toast("📢 전원 확성기 기동! 상대 팀의 집중력이 흐트러집니다!", icon="👿")
                            st.rerun()
                        else:
                            st.error("다이아 부족!")

        st.markdown("---")
        
        st.markdown("### 💾 세이브 / 로드")
        
        with st.expander("🔑 세이브 코드 발급"):
            if st.session_state.full_kbo_engine is None:
                st.caption("경기가 시작된 후에 중간 저장이 가능합니다. ")
            else:
                st.write("현재 경기 상황과 투수 체력까지 모두 저장됩니다. 코드를 복사해 보관하세요.")
                game = st.session_state.full_kbo_engine

                my_pitchers_data = [
                    {"name": p.name, "role": p.role, "max_stamina": p.max_stamina, "stamina": p.stamina, "pitches_thrown": p.pitches_thrown}
                    for p in game.my_pitchers
                ]
                enemy_pitchers_data = [
                    {"name": p.name, "role": p.role, "max_stamina": p.max_stamina, "stamina": p.stamina, "pitches_thrown": p.pitches_thrown}
                    for p in game.enemy_pitchers
                ]
                save_data = {
                    "diamonds": st.session_state.nc_diamonds,
                    "my_team": st.session_state.my_team,
                    "enemy_team": game.enemy_team,
                    "is_home_team": game.is_home_team,
                    "our_score": game.our_score,
                    "enemy_score": game.enemy_score,
                    "away_stats": game.away_stats,
                    "home_stats": game.home_stats,
                    "inning": game.inning,
                    "phase": game.phase,
                    "my_batter_number": game.my_batter_number,
                    "enemy_batter_number": game.enemy_batter_number,
                    "our_total_pitches": game.our_total_pitches,
                    "enemy_total_pitches": game.enemy_total_pitches,
                    "strike": game.strike,
                    "ball": game.ball,
                    "out_count": game.out_count,
                    "base1": game.base1,
                    "base2": game.base2,
                    "base3": game.base3,
                    "away_inning_scores": game.away_inning_scores,
                    "home_inning_scores": game.home_inning_scores,
                    "game_log": game.game_log,
                    "pitch_history": game.pitch_history,
                    "chzzk_chats": game.chzzk_chats,
                    "hit_buff": game.hit_buff,
                    "manager_ejected": game.manager_ejected,
                    "my_pitcher_idx": game.my_pitcher_idx,
                    "my_used_pitchers": list(game.my_used_pitchers),
                    "my_pitchers": my_pitchers_data,
                    "enemy_pitcher_idx": game.enemy_pitcher_idx,
                    "enemy_used_pitchers": list(game.enemy_used_pitchers),
                    "enemy_pitchers": enemy_pitchers_data
                }
                json_str = json.dumps(save_data, ensure_ascii=False)
                encoded_code = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
                st.code(encoded_code, language="text")
                st.caption("위 코드를 더블클릭해 복사하세요!")

        with st.expander("🔓 코드 불러오기"):
            input_code = st.text_input("코드 입력", key="save_code_input", placeholder="세이브 코드를 붙여넣으세요")
            if st.button("📂 데이터 로드 실행"):
                if input_code.strip():
                    try:
                        decoded_bytes = base64.b64decode(input_code.encode('utf-8'))
                        decoded_str = decoded_bytes.decode('utf-8')
                        data = json.loads(decoded_str)
                        
                        st.session_state.nc_diamonds = data.get("diamonds", 1000)
                        st.session_state.my_team = data.get("my_team", "💖 핑크 돌핀스")

                        loaded_game = PureKboEngine(data["my_team"], data["enemy_team"])

                        loaded_game.is_home_team = data["is_home_team"]
                        loaded_game.our_score = data["our_score"]
                        loaded_game.enemy_score = data["enemy_score"]
                        loaded_game.away_stats = data["away_stats"]
                        loaded_game.home_stats = data["home_stats"]
                        loaded_game.inning = data["inning"]
                        loaded_game.phase = data["phase"]
                        loaded_game.my_batter_number = data["my_batter_number"]
                        loaded_game.enemy_batter_number = data["enemy_batter_number"]
                        loaded_game.our_total_pitches = data["our_total_pitches"]
                        loaded_game.enemy_total_pitches = data["enemy_total_pitches"]
                        loaded_game.strike = data["strike"]
                        loaded_game.ball = data["ball"]
                        loaded_game.out_count = data["out_count"]
                        loaded_game.base1 = data["base1"]
                        loaded_game.base2 = data["base2"]
                        loaded_game.base3 = data["base3"]
                        loaded_game.away_inning_scores = data["away_inning_scores"]
                        loaded_game.home_inning_scores = data["home_inning_scores"]
                        loaded_game.game_log = data["game_log"]
                        loaded_game.pitch_history = data["pitch_history"]
                        loaded_game.chzzk_chats = data["chzzk_chats"]
                        loaded_game.hit_buff = data["hit_buff"]
                        loaded_game.manager_ejected = data.get("manager_ejected", False)

                        loaded_game.my_pitcher_idx = data["my_pitcher_idx"]
                        loaded_game.my_used_pitchers = set(data["my_used_pitchers"])
                        loaded_game.my_pitchers = []
                        for p_dict in data["my_pitchers"]:
                            p_obj = PitcherDomain(p_dict["name"], p_dict["role"], p_dict["max_stamina"])
                            p_obj.stamina = p_dict["stamina"]
                            p_obj.pitches_thrown = p_dict["pitches_thrown"]
                            loaded_game.my_pitchers.append(p_obj)
                            
                        loaded_game.enemy_pitcher_idx = data["enemy_pitcher_idx"]
                        loaded_game.enemy_used_pitchers = set(data["enemy_used_pitchers"])
                        loaded_game.enemy_pitchers = []
                        for p_dict in data["enemy_pitchers"]:
                            p_obj = PitcherDomain(p_dict["name"], p_dict["role"], p_dict["max_stamina"])
                            p_obj.stamina = p_dict["stamina"]
                            p_obj.pitches_thrown = p_dict["pitches_thrown"]
                            loaded_game.enemy_pitchers.append(p_obj)
                        
                        st.session_state.full_kbo_engine = loaded_game
                        
                        st.toast("🎉 데이터 복구 성공! 로드가 완료되었습니다핑!", icon="💾")
                        st.rerun()
                    except Exception:
                        st.error("❌ 유효하지 않은 암호 코드입니다.")
                else:
                    st.warning("코드를 입력해 주세요!")

        st.markdown("---")
        st.markdown("### 📊 상성 매트릭스 전체 열람")
        if st.button("상성 표 열람"):
            df_matrix = pd.DataFrame.from_dict(MATCHUP_MATRIX, orient='index', columns=MATRIX_COLUMNS)
            st.dataframe(df_matrix, width="stretch")

        st.divider()
        st.header("📖 구단 유니버스")
        team_lore = st.selectbox("세계관 열람:", list(TEAMS.keys()))
        if st.button("스토리 보기"):
            if os.path.exists("assets/team_stories.txt"):
                with open("assets/team_stories.txt", "r", encoding="utf-8") as f:
                    st.text_area(f"{team_lore} 설정", value=f.read(), height=200, disabled=True)
            else:
                st.error("⚠️ assets/team_stories.txt 파일 누락.")

        st.divider()
        st.header("💡 전술 매뉴얼")
        if st.button("가이드 열람"):
            if os.path.exists("assets/game_tips.txt"):
                with open("assets/game_tips.txt", "r", encoding="utf-8") as f:
                    st.text_area("공식 가이드", value=f.read(), height=200, disabled=True)
            else: st.error("⚠️ assets/game_tips.txt 파일 누락.")

        st.divider()
        st.header("👤 선수 로스터")
        if st.button("이번 시즌 선수단"):
            if os.path.exists("assets/team-roster.txt"):
                with open("assets/team-roster.txt", "r", encoding="utf-8") as f:
                    st.text_area("팀별 로스터", value=f.read(), height=200, disabled=True)
            else:
                st.error("⚠️ assets/team-roster.txt 파일 누락.")

        st.divider()
        st.header("팀별 디폴트 타순")
        if st.button("기본 선발 라인업과 선발투수"):
            if os.path.exists("assets/default-lineup.txt"):
                with open("assets/default-lineup.txt", "r", encoding="utf-8") as f:
                    st.text_area("팀별 주전", value=f.read(), height=200, disabled=True)
            else:
                st.error("⚠️ assets/default-lineup.txt 파일 누락.")

    # -----------------------------------------------------------------
    # 1. 경기 개시 전 팀 선택 및 라인업 커스텀 설정 영역
    # -----------------------------------------------------------------
    if st.session_state.full_kbo_engine is None:
        st.session_state.my_team = st.selectbox("우리 팀 선택:", list(TEAMS.keys()), index=list(TEAMS.keys()).index(st.session_state.my_team))

        sp_list = TEAM_ROSTERS[st.session_state.my_team]["pitchers"]["선발(5)"]
        selected_sp_idx = st.selectbox("⚾ **오늘의 선발 투수 지명**",
            options=list(range(len(sp_list))),
            format_func=lambda x: f"{x+1}선발: {sp_list[x]} (체력: {TEAMS[st.session_state.my_team]['stamina']})",
            key=f"select_sp_{st.session_state.my_team}"
        )
        
        st.markdown(f"#### 📊 {st.session_state.my_team}의 구단별 상성표 요약")
        if st.session_state.my_team in df_matchup.index:
            my_status = df_matchup.loc[[st.session_state.my_team]]
            try:
                styled_status = my_status.style.map(color_matchup_cells)
            except AttributeError:
                styled_status = my_status.style.applymap(color_matchup_cells)
                
            st.dataframe(styled_status, width="stretch")

        # 💡 [신규 추가 4] 오늘의 선발 라인업 (1~9번 타순 수동 커스텀 UI)
        saved_key = f"saved_lineup_{st.session_state.my_team}"
        default_lineup = get_default_lineup(st.session_state.my_team)
        initial_lineup = st.session_state.get(saved_key, default_lineup) 
        
        with st.expander("⚙️ 오늘의 선발 라인업 (1~9번 타순 수동 커스텀)", expanded=True):
            st.caption("💡 각 드롭다운에서 원하는 타자 및 타순을 조합할 수 있습니다.")
            
            all_batters = []
            for p_list in TEAM_ROSTERS[st.session_state.my_team]["batters"].values():
                all_batters.extend(p_list)
                
            custom_lineup = []
            col_l1, col_l2 = st.columns(2)
            
            for idx in range(9):
                target_col = col_l1 if idx < 5 else col_l2
                with target_col:
                    default_player = default_lineup[idx] if idx < len(default_lineup) else all_batters[idx % len(all_batters)]
                    d_idx = all_batters.index(default_player) if default_player in all_batters else 0
                    
                    sel = st.selectbox(
                        f"**{idx+1}번 타자**",
                        options=all_batters,
                        index=d_idx,
                        key=f"start_lineup_select_{idx}"
                    )
                    custom_lineup.append(sel)

            st.markdown("---")
            #라인업 저장/불러오기
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                if st.button("💾 현재 타순을 이 팀의 기본 오더로 저장", key="btn_save_lineup"):
                    st.session_state[saved_key] = custom_lineup
                    st.toast(f"✅ {st.session_state.my_team}의 선발 타순이 저장되었습니다!", icon="💾")
            with b_col2:
                if st.button("🔄 기본 추천 타순으로 초기화", key="btn_reset_lineup"):
                    if saved_key in st.session_state:
                        del st.session_state[saved_key]
                    st.toast("🔄 추천 타순으로 초기화되었습니다.", icon="🧹")
                    st.rerun()
        
        has_duplicates = len(set(custom_lineup)) != len(custom_lineup)
        if has_duplicates:
            # 중복된 선수명 추출
            seen = set()
            duplicates = set(p for p in custom_lineup if p in seen or seen.add(p))
            dup_names = ", ".join(duplicates)
            st.warning(f"⚠️ **라인업 중복 경고**: [{dup_names}] 선수가 중복 선택되었습니다! 서로 다른 9명의 타자로 라인업을 완성해 주세요.")
        else:
            st.info(f"⚾ **선발 투수**: {sp_list[selected_sp_idx]} | "
                f"📋 **선발 타순**: {' ➔ '.join([f'{i+1}.{p.split()[-1]}' for i, p in enumerate(custom_lineup)])}")
        # 🛑 중복이 있으면 버튼 비활성화 (disabled=has_duplicates)
        if st.button("⚾️ PLAY BALL!", type="primary", disabled=has_duplicates):
            enemy_team = random.choice([t for t in TEAMS.keys() if t != st.session_state.my_team])
            st.session_state.full_kbo_engine = PureKboEngine(
                my_team=st.session_state.my_team, 
                enemy_team=enemy_team, 
                my_lineup=custom_lineup
            )
            st.rerun()
                    
        st.info(f"📋 **확정 선발 라인업**: {' ➔ '.join([f'{i+1}.{p.split()[-1]}' for i, p in enumerate(custom_lineup)])}")
      
        if st.button("⚾️ PLAY BALL!", type="primary"):
            enemy_team = random.choice([t for t in TEAMS.keys() if t != st.session_state.my_team])
            st.session_state.full_kbo_engine = PureKboEngine(
                my_team=st.session_state.my_team, 
                enemy_team=enemy_team, 
                my_lineup=custom_lineup
            )
            st.rerun()

    # -----------------------------------------------------------------
    # 2. 경기 진행 중 메인 화면
    # -----------------------------------------------------------------
    else:
        game: PureKboEngine = st.session_state.full_kbo_engine
        st.session_state.my_team = game.my_team
        p_my = game.get_current_my_pitcher()
        p_en = game.get_current_enemy_pitcher()

        # 💡 [신규 추가 5] 화면 상단 오늘의 양 팀 선발 라인업 및 실시간 타순 열람 UI
        with st.expander("📋 오늘의 양 팀 선발 라인업 및 실시간 타순 열람", expanded=False):
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                st.markdown(f"#### 🏠 {game.my_team} 선발 라인업")
                st.write(f"⚾ **선발 투수**: {p_my.name}")
                st.markdown("---")
                for i, batter in enumerate(game.my_lineup):
                    is_current = (game.is_attack and game.my_batter_number == (i+1))
                    marker = " 👈 [현재 타석]" if is_current else ""
                    st.write(f"**{i+1}번 타자**: {batter}{marker}")
            with col_u2:
                st.markdown(f"#### 🚌 {game.enemy_team} 선발 라인업")
                st.write(f"⚾ **선발 투수**: {p_en.name}")
                st.markdown("---")
                for i, batter in enumerate(game.enemy_lineup):
                    is_current = (not game.is_attack and game.enemy_batter_number == (i+1))
                    marker = " 👈 [현재 타석]" if is_current else ""
                    st.write(f"**{i+1}번 타자**: {batter}{marker}")

        st.markdown(f"##### 📊 실시간 상성 파트너: {game.my_team} vs {game.enemy_team}")
        if game.my_team in df_matchup.index:
            my_status = df_matchup.loc[[game.my_team]]
            try:
                styled_status = my_status.style.map(color_matchup_cells)
            except AttributeError:
                styled_status = my_status.style.applymap(color_matchup_cells)
                
            st.dataframe(styled_status, width="stretch")

        c1, c2, c3 = st.columns([2, 1, 2])
        with c1:
            st.metric(label=f"우리 팀 {game.my_emoji}", value=f"{game.our_score} 점")
            st.caption(f"🔋 {p_my.name} | 체력: [{p_my.stamina}/{p_my.max_stamina}] | 총 {game.our_total_pitches}구")
            if not game.game_over and p_my.role != "마무리":
                with st.expander("🔄 투수 수동 교체 (드롭다운)"):
                    # 아직 등판하지 않은 투수들(또는 전체 투수 중 선택 가능하게 매핑)
                    available_pitchers = {
                        f"{i}: {p.name} ({p.role}) - 체력 {p.stamina}/{p.max_stamina}": i 
                        for i, p in enumerate(game.my_pitchers) 
                        if i not in game.my_used_pitchers and i != game.my_pitcher_idx
                    }
                    if available_pitchers:
                        chosen_label = st.selectbox("올릴 투수를 선택하세요", list(available_pitchers.keys()), key="manual_pitcher_select")
                        if st.button("마운드 지명 교체", key="btn_confirm_manual_pitcher"):
                            target_idx = available_pitchers[chosen_label]
                            game.my_pitcher_idx = target_idx
                            game.my_used_pitchers.add(target_idx)
                            new_p = game.get_current_my_pitcher()
                            game.game_log.append(f"🔄 [감독 직접 교체] 벤치의 지시로 마운드 교체! [{new_p.role}] '{new_p.name}' 등판!")
                            st.rerun()

                    else:
                        st.caption("🚨 더 이상 교체 가능한 대기 투수가 없습니다!")
        with c2:
            if game.game_over:
                st.markdown("<h3 style='text-align: center; color: #9E9E9E;'>경기 종료</h3>", unsafe_allow_html=True)
            else:
                st.markdown(f"<h3 style='text-align: center; color: #E63946;'>{game.inning}회{game.phase}</h3>", unsafe_allow_html=True)
                current_is_our_turn = (not game.is_home_team and game.phase == "초") or (game.is_home_team and game.phase == "말")
                st.markdown(f"<p style='text-align: center; font-size:12px;'>{'[공격 턴]' if current_is_our_turn else '[수비 턴]'}</p>", unsafe_allow_html=True)
        with c3:
            st.metric(label=f"상대 팀 {game.enemy_emoji}", value=f"{game.enemy_score} 점")
            st.caption(f"🥎 {p_en.name} | 체력: [{p_en.stamina}/{p_en.max_stamina}] | 총 {game.enemy_total_pitches}구")

        away_name = game.enemy_team if game.is_home_team else game.my_team
        home_name = game.my_team if game.is_home_team else game.enemy_team

        display_away = []
        display_home = []

        final_inning = game.inning
        if game.game_over and game.phase == "초" and game.home_inning_scores[game.inning - 1] == "":
            final_inning = max(1, game.inning - 1)

        for i in range(12):
            if game.game_over:
                if i == 8 and game.home_inning_scores[i] == "X":
                    display_away.append(game.away_inning_scores[i])
                    display_home.append("X")
                elif i >= game.inning:
                    display_away.append("")
                    display_home.append("")
                else:
                    display_away.append(game.away_inning_scores[i])
                    display_home.append(game.home_inning_scores[i])
            else:
                display_away.append("" if i >= game.inning else game.away_inning_scores[i])
                display_home.append("" if i >= game.inning else game.home_inning_scores[i])
        
        sb = {
            "BOARD": [f"🚌 {away_name}", f"🏟️ {home_name}"],
            "1": [display_away[0], display_home[0]], "2": [display_away[1], display_home[1]], "3": [display_away[2], display_home[2]],
            "4": [display_away[3], display_home[3]], "5": [display_away[4], display_home[4]], "6": [display_away[5], display_home[5]],
            "7": [display_away[6], display_home[6]], "8": [display_away[7], display_home[7]], "9": [display_away[8], display_home[8]],
            "10": [display_away[9], display_home[9]], "11": [display_away[10], display_home[10]],
            "R": [game.away_stats["R"], game.home_stats["R"]],
            "H": [game.away_stats["H"], game.home_stats["H"]],
            "E": [game.away_stats["E"], game.home_stats["E"]],
            "B": [game.away_stats["B"], game.home_stats["B"]]
        }
        st.table(pd.DataFrame(sb).set_index("BOARD"))

        if game.game_over:
            st.success(game.game_result_msg)
            if st.button("새 경기 시작", type="primary"): st.session_state.full_kbo_engine = None; st.rerun()
        else:
            col_main, col_chat = st.columns([3, 1])
            
            with col_main:
                cz1, cz2 = st.columns(2)
                with cz1:
                    st.markdown(f"#### **🚨 COUNT BOARD**")
                    st.markdown(f"**OUT :** {'🔴' * game.out_count}{'⚪' * (3-game.out_count)}")
                    st.markdown(f"**STRIKE :** {'🟡' * game.strike}{'⚪' * (3-game.strike)}")
                    st.markdown(f"**BALL :** {'🟢' * game.ball}{'⚪' * (4-game.ball)}")
                with cz2:
                    fig, ax = plt.subplots(figsize=(3, 3), facecolor='#1e1e1e')
                    ax.set_facecolor('#1e1e1e')
                    ax.set_xlim(-1.5, 1.5)
                    ax.set_ylim(-0.5, 2.8)
                    ax.axis('off')

                    inning_text = f"TOP {game.inning}" if game.phase == "초" else f"BOT {game.inning}"
                    ax.text(0, 2.7, inning_text, color='#ff922b', fontsize=12, ha='center', va='center', 
                            weight='bold', bbox=dict(facecolor='#2b2b2b', edgecolor='#ff922b', boxstyle='round,pad=0.4', lw=1.5))

                    base_coords = {
                        "home": (0, 0),
                        "base1": (1, 1),
                        "base2": (0, 2),
                        "base3": (-1, 1)
                    }

                    base_states = {
                        "base1": game.base1,
                        "base2": game.base2,
                        "base3": game.base3
                    }

                    for b_name, (x, y) in base_coords.items():
                        if b_name == "home":
                            rect = patches.Rectangle((x-0.1, y-0.1), 0.2, 0.2, angle=45, edgecolor='#aaaaaa', facecolor='#ffffff', lw=1.5)
                            ax.add_patch(rect)
                            continue

                        is_runner = base_states[b_name]
                        bg_color = '#ff6b6b' if is_runner else '#3d3d3d'
                        edge_color = '#ffcbd1' if is_runner else '#777777'
                        line_width = 2.0 if is_runner else 1.0

                        rect = patches.Rectangle((x-0.18, y-0.18), 0.36, 0.36, angle=45, rotation_point='center',
                                                 edgecolor=edge_color, facecolor=bg_color, lw=line_width)
                        ax.add_patch(rect)
                        
                        label_map = {"base1": "1B", "base2": "2B", "base3": "3B"}
                        text_color = '#ffffff' if is_runner else '#aaaaaa'
                        ax.text(x, y, label_map[b_name], color=text_color, fontsize=9, ha='center', va='center', weight='bold')

                    line_style = dict(color='#555555', linestyle='--', linewidth=1, zorder=0)
                    ax.plot([0, 1, 0, -1, 0], [0, 1, 2, 1, 0], **line_style)

                    current_is_our_turn = (not game.is_home_team and game.phase == "초") or (game.is_home_team and game.phase == "말")
                    if current_is_our_turn:
                        active_batter = f"OUR BATTER: {game.my_batter_number}"
                    else:
                        active_batter = f"ENEMY BATTER: {game.enemy_batter_number}"

                    ax.text(0, -0.4, active_batter, color='#51cf66', fontsize=11, ha='center', va='center', 
                            weight='bold', bbox=dict(facecolor='#2b2b2b', edgecolor='#51cf66', boxstyle='round,pad=0.3', lw=1))

                    st.pyplot(fig, width="stretch")
                    plt.close(fig)
                st.info(HyperClovaX_AI.get_recommendation(game.pitch_history, game.base3, game.inning, current_is_our_turn))

                # 💡 감독 퇴장 여부 체크하여 수석코치 AI 자동 지휘로 분기
                if game.manager_ejected:
                    st.error("🟥 감독 퇴장 상태입니다! 수석코치 AI가 전술을 위임받아 진행합니다.")
                    if st.button("🤖 [수석코치 AI] 다음 구 진행", type="primary", key="btn_coach_ai", width="stretch"):
                        # ⏱️ [수석코치 AI 타임 판단 로직]
                        my_p = game.get_current_my_pitcher()
                        has_timeout = game.my_timeouts_left > 0
                        
                        # 조건 1) 수비 턴인데 투수 체력이 30% 이하로 떨어져 비상일 때
                        # 조건 2) 공격 턴인데 득점권(2루/3루) 찬스에서 20% 확률로 흐름 끊기
                        should_use_timeout = False
                        if has_timeout:
                            if not current_is_our_turn and my_p.stamina <= (my_p.max_stamina * 0.3):
                                should_use_timeout = True
                            elif current_is_our_turn and (game.base2 or game.base3) and random.random() < 0.20:
                                should_use_timeout = True
                
                        if should_use_timeout:
                            game.use_my_timeout() # ⏱️ 수석코치 AI의 전술 타임 발동!
                        else:
                            # ⚾ 기존 피칭/타격 작전 수행
                            if current_is_our_turn:
                                valid_choices = [1, 2, 3]
                                has_runner = game.base1 or game.base2 or game.base3
                                if has_runner: valid_choices.append(5) # 런앤히트
                                if game.base3: valid_choices.append(4)  # 스퀴즈 번트
                                
                                ai_choice = random.choice(valid_choices)
                                if has_runner and random.random() < 0.10:
                                    game.trigger_steal()
                                else:
                                    game.play_turn(ai_choice)
                            else:
                                choice = random.choice([1, 2, 3, 4])
                                if choice == 4:
                                    game.play_intentional_walk()
                                else:
                                    game.play_defense_one_pitch(choice)
                                    
                        st.rerun()

                elif current_is_our_turn:
                    st.caption(f"🔍 구질 히스토리: {', '.join(game.pitch_history)}")
                    st.markdown("### 📢 공격 작전")
                    b1, b2, b3, b4 = st.columns(4)
                    
                    with b1:
                        if st.button("💥 강공 (풀스윙)", key="btn_swing_1"):
                            game.play_turn(1)    
                            st.rerun()
                        if st.button("🏃‍♂️ 스퀴즈 번트", key="btn_bunt_4"):
                            game.play_turn(4)
                            st.rerun()
                    with b2:
                        if st.button("🌟 밀어치기", key="btn_push_2"):
                            game.play_turn(2)
                            st.rerun()
                        if st.button("🔥 런앤히트", key="btn_runhit_5"):
                            game.play_turn(5)
                            st.rerun()
                    with b3:
                        if st.button("👀 웨이팅", key="btn_wait_3"): 
                            game.play_turn(3)
                            st.rerun()
                        if st.button("🏃 도루", key="btn_steal"): 
                            game.trigger_steal()
                            st.rerun()

                    with b4:
                        if st.button(f"⏱️ 타임 (잔여 {game.my_timeouts_left}회)", width="stretch"):
                            game.use_my_timeout()
                            st.rerun()
                            
                else:
                    st.markdown("### 🛡️ 수비 볼배합")
                    d1, d2, d3, d4, d5 = st.columns(5)
                    with d1:
                        if st.button("⚾ 정면 승부"): game.play_defense_one_pitch(1); st.rerun()
                    with d2:
                        if st.button("🥎 유인구"): game.play_defense_one_pitch(2); st.rerun()
                    with d3:
                        if st.button("🔮 제구 위주"): game.play_defense_one_pitch(3); st.rerun()
                    with d4:
                        if st.button("🛑 고의사구"): game.play_intentional_walk(); st.rerun()
                    with d5: 
                        if st.button(f"⏱️ 타임 (잔여 {game.my_timeouts_left}회)", width="stretch"):
                            game.use_my_timeout()
                            st.rerun()

                st.divider()
                st.markdown("### 📜 게임 로그")
                for log in reversed(game.game_log[-5:]): st.write(log)

            with col_chat:
                st.markdown("#### 📺 실시간 채팅")
                
                if not game.game_over:
                    users = ["야구천재", "방구석펩", "침착한스트리머", "로켓단", "다이아수저", "삼진에진심인편", "치지직조율사", "치킨치킨",
                        "물개아님돌고래임", "돔구장건설요청", "내주머니속100원", "야잘알김동구",
                        "도루묵", "클로저스파크", "9회말2아웃", "대타전문가", "KBO정신병자", "용규놀이터", 
                            "찜질방수건도둑", "월급루팡", "카미야최고야", "메카미야", "츄츄트레인", "자라나라머리머리", "류뿡"]
                    chat_pool = [
                        "아니 감독 돌았냐 ㅋㅋㅋ 진짜 뇌 빼고 경기하네", 
                        "지금 스퀴즈 각인데?? 왜 안 번트??", 
                        "투수 제발 좀 바꿔라!! 어깨 갈린다 ㅠㅠ", 
                        "감독 혹사 수준 보소 ㅋㅋㅋ 노동청 신고함",
                        "대타 누구 올릴 거냐?? 벤치 멤버 믿을 놈이 없다",
                        "이 타이밍에 도루 안 하면 언제 하냐고!!! 🏃‍♂️💨",
                        "대기업 급 핑돌이 물리 연산력 ㄷㄷ", 
                        "이게 진짜 KBO 클래식이지 ㅋㅋㅋㅋ 고증 보소", 
                        "방구석 과몰입 꿀잼이네 ㅋㅋㅋ 중계 맛집", 
                        "오늘 밸런스 패치 황밸이네 ㅋㅋ 쫄깃하다",
                        "NC식 현질 유도 없어서 갓겜 인정합니다", 
                        "데드볼 던질 때 흠칫했다 ㅋㅋㅋ 리얼리티 굿",
                        "야수 마운드 기어 올라오는 거 실화냐?? 막장 야구 ㅋㅋㅋ",
                        "일본의 카미야가 생각난다",
                        "혈압 올라 죽겠네 ㅋㅋㅋ 혈압약 시켰다",
                        "네이버 톡방 폼 미쳤다 ㅋㅋㅋ",
                        "오늘 주침 스트존 왜 저럼?? 눈을 장식으로 달았나",
                        "아웃 아웃 아웃!! 맨날 플라이 아웃만 치냐!! 수비 보소",
                        "볼넷 밀어내기로 점수 내는 거 개꿀잼이네 ㅋㅋㅋ",
                        "2스트라이크 이후에 파울 커트 미쳤다 ㅋㅋㅋ 끈질기네",
                        "용규놀이 지독하다 지독해 ㅋㅋㅋ 투수 눈물 흘리는 중 😭",
                        "이게 야구냐?? 예능이지 ㅋㅋㅋㅋ",
                        "킹갓 제네럴 에이스 마운드 등장 ㄷㄷㄷ 지렸다",
                        "야수 등판하면 배팅볼 꿀맛인데 ㅋㅋㅋ 홈런 가자!!!",
                        "오늘 경기 9회말 끝내기 각이다 가슴이 웅장해진다",
                        "야구는 뒷전이냐",
                        "왜 이렇게 못 치냐", 
                        "답답해서 내가 친다"
                    ]
                    new_chat = f"💬 **{random.choice(users)}**: {random.choice(chat_pool)}"
                    game.chzzk_chats.append(new_chat)
                    
                    if len(game.chzzk_chats) > 10:
                        game.chzzk_chats.pop(0)

                chat_box = st.container(height=350)
                with chat_box:
                    for chat in reversed(game.chzzk_chats):
                        st.markdown(f"<div style='font-size: 14px; margin-bottom: 5px;'>{chat}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
