import random
import os
import pandas as pd
import streamlit as st
from typing import Dict, Any, List

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

# 2. 딕셔너리를 Pandas DataFrame으로 변환 (행/열 이름 정렬)
teams_keys = list(MATCHUP_MATRIX.keys())
df_matchup = pd.DataFrame.from_dict(MATCHUP_MATRIX, orient='index', columns=teams_keys)

# 3. 🎨 셀 값에 따라 스타일(CSS)을 리턴하는 컬러 매퍼 함수 정의
def color_matchup_cells(val):
    # 기본 스타일
    base_style = "font-weight: bold; text-align: center;"
    
    if val == "우세":
        # 🟢 우세: 연한 초록 배경에 짙은 초록 글씨 (또는 핑크 돌핀스풍 연파랑)
        return f"{base_style} background-color: #e2f0d9; color: #385723;"
    elif val == "열세":
        # 🔴 열세: 연한 빨간(분홍) 배경에 짙은 빨간 글씨
        return f"{base_style} background-color: #fce4d6; color: #c65911;"
    elif val == "백중":
        # 🟡 백중: 연한 노란 배경에 회갈색 글씨
        return f"{base_style} background-color: #fff2cc; color: #7f6000;"
    elif val == "X":
        # 자기 자신과의 매치업: 회색 배경에 흰 글씨 처리
        return f"{base_style} background-color: #f2f2f2; color: #bfbfbf; font-style: italic;"
    
    return base_style

with st.expander("📊 KBO 전 구단 실시간 상성 매트릭스 보기 (클릭하여 열기)", expanded=False):
    st.write("세로축(행)이 **아군 팀**, 가로축(열)이 **상대 팀** 기준 상성표입니다핑! 😉")
    st.dataframe(styled_df, use_container_width=True)
    

# 4. Streamlit 화면에 스타일이 적용된 데이터프레임 렌더링
st.subheader("📊 KBO 전 구단 실시간 상성 매트릭스")
st.write("세로축(행)이 **아군 팀**, 가로축(열)이 **상대 팀** 기준 상성표입니다핑! 😉")

# Pandas Styler 적용 (.map은 pandas 최신 버전 기준이며, 구버전 환경이라면 .applymap 사용)
try:
    styled_df = df_matchup.style.map(color_matchup_cells)
except AttributeError:
    styled_df = df_matchup.style.applymap(color_matchup_cells)

# 화면에 가득 차게 띄우기
st.dataframe(styled_df, use_container_width=True)

MATRIX_COLUMNS = ["🔴레드", "🔵블루", "🟢그린", "🟡옐로우", "🟣퍼플", "🟠오렌지", "🟤브라운", "⚪화이트", "⚫블랙", "💖핑크"]

PITCH_SPECS = {
    "직구": {"speed_min": 142, "speed_max": 155},
    "슬라이더": {"speed_min": 130, "speed_max": 142},
    "체인지업": {"speed_min": 125, "speed_max": 136},
    "커브": {"speed_min": 115, "speed_max": 126},
    "포크볼": {"speed_min": 125, "speed_max": 138},
    "싱커": {"speed_min": 133, "speed_max": 144}
}

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
    def __init__(self, my_team: str, enemy_team: str) -> None:
        self.my_team = my_team
        self.enemy_team = enemy_team
        self.my_emoji = my_team[:2]
        self.enemy_emoji = enemy_team[:2]
        self.is_home_team = random.choice([True, False])
        
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
        
        # 💬 [안정성 패치] 오류 방지를 위해 도메인 내부에 안전하게 초기 리스트 생성
        self.chzzk_chats = ["💬 **치지직 가이드**: 경기가 시작되었습니다. 전술 사인을 지켜보세요!"]
        
        self.hit_buff = 0.0 
        
        my_stats = TEAMS[my_team]
        enemy_stats = TEAMS[enemy_team]
        
        self.my_pitchers = [
            PitcherDomain("제1선발", "선발", my_stats["stamina"]),
            PitcherDomain("롱릴리프", "추격조", 40),
            PitcherDomain("셋업맨", "필승조", 30),
            PitcherDomain("클로저", "마무리", 20)
        ]
        self.my_pitcher_idx = 0
        self.enemy_pitchers = [
            PitcherDomain("상대 에이스", "선발", enemy_stats["stamina"]),
            PitcherDomain("상대 불펜", "추격조", 40),
            PitcherDomain("상대 셋업맨", "필승조", 30),
            PitcherDomain("상대 클로저", "마무리", 20)
        ]
        self.enemy_pitcher_idx = 0
        self.setup_half_inning()

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

    def get_current_my_pitcher(self) -> PitcherDomain: return self.my_pitchers[self.my_pitcher_idx]
    def get_current_enemy_pitcher(self) -> PitcherDomain: return self.enemy_pitchers[self.enemy_pitcher_idx]

    def change_my_pitcher(self) -> bool:
        if self.my_pitcher_idx < len(self.my_pitchers) - 1:
            self.my_pitcher_idx += 1
            p = self.get_current_my_pitcher()
            self.game_log.append(f"🔄 [투수 교체] {p.role} '{p.name}' 등판")
            return True
        return False

    def change_enemy_pitcher(self) -> bool:
        if self.enemy_pitcher_idx < len(self.enemy_pitchers) - 1:
            self.enemy_pitcher_idx += 1
            p = self.get_current_enemy_pitcher()
            self.game_log.append(f"🔄 [상대 투수 교체] 상대 불펜 가동: {p.role} '{p.name}' 등판")
            return True
        return False

    def get_away_score(self) -> int: return self.away_stats["R"]
    def get_home_score(self) -> int: return self.home_stats["R"]

    def setup_half_inning(self) -> None:
        if self.game_over: return
        idx = self.inning - 1
        if idx < 12:
            if self.away_inning_scores[idx] == "": self.away_inning_scores[idx] = 0
            if self.home_inning_scores[idx] == "": self.home_inning_scores[idx] = 0

        if self.inning == 9 and self.phase == "말" and self.get_home_score() > self.get_away_score():
            self.game_log.append("👍 9회초 종료. 홈팀 리드로 경기 종료.")
            self.home_inning_scores[8] = "X"
            self.end_kbo_game()
            return

        if self.inning > 9 and self.phase == "초":
            if self.get_away_score() != self.get_home_score(): self.end_kbo_game(); return
            elif self.inning > 12: self.inning = 12; self.phase = "말"; self.end_kbo_game(); return

        self.strike = 0; self.ball = 0; self.out_count = 0
        self.base1 = self.base2 = self.base3 = False
        self.hit_buff = 0.0

    def update_live_scoreboard(self, run: int) -> None:
        idx = self.inning - 1
        if idx >= 12: return
        if self.phase == "초":
            base = 0 if self.away_inning_scores[idx] in ["", "X"] else int(self.away_inning_scores[idx])
            self.away_inning_scores[idx] = base + run
            self.away_stats["R"] += run
        else:
            base = 0 if self.home_inning_scores[idx] in ["", "X"] else int(self.home_inning_scores[idx])
            self.home_inning_scores[idx] = base + run
            self.home_stats["R"] += run
            
        if (self.is_home_team and self.phase == "말") or (not self.is_home_team and self.phase == "초"):
            self.our_score += run
        else:
            self.enemy_score += run

    def trigger_steal(self) -> None:
        if not (self.base1 or self.base2 or self.base3):
            st.warning("루상에 주자가 없습니다.")
            return
        p_en = self.get_current_enemy_pitcher()
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
            # 3루 주자 단독 홈스틸 시도 시: 홈스틸은 극악의 확률(15%)로만 성공하며 실패 시 아웃(저지)
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

        if self.phase == "말":
            if self.inning >= 9 and current_away != current_home:
                self.end_kbo_game()
                return
            if self.inning == 12:
                self.end_kbo_game()
                return
            
        if self.phase == "초" and self.inning == 9: 
            if current_home > current_away:
                self.home_inning_scores[8] = "X"
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
        if a == h: self.game_result_msg = f"🤝 [무승부] 12회 {a}:{h} DRAW 종료."
        else: self.game_result_msg = f"🏆 [경기 종료] {self.our_score} 대 {self.enemy_score}(으)로 우리 팀 {'승리!' if self.our_score > self.enemy_score else '패배.'}"

    def process_error(self, log_prefix: str, bat: int) -> None:
        self.add_stat("E")
        self.game_log.append(log_prefix + f"🚨 수비 실책! 포구/송구 미스로 {bat}번 타자 출루.")
        if self.base1 and self.base2 and self.base3:
            self.update_live_scoreboard(1)
        elif self.base1 and self.base2: self.base3 = True
        elif self.base1: self.base2 = True
        else: self.base1 = True

    def play_defense_one_pitch(self, defense_choice: int) -> None:
        if self.game_over: return
        p_my = self.get_current_my_pitcher()

        need_change = False
        
        if p_my.stamina <= (p_my.max_stamina * 0.20):
            need_change = True

        if self.inning >= 7 and p_my.role in ["선발", "추격조"]:
            # 1~2점 차 팽팽한 리드/접전 상황이면 바로 필승조(셋업맨/마무리) 준비
            score_diff = abs(self.get_away_score() - self.get_home_score())
            if score_diff <= 2:
                need_change = True

        if need_change:
            # 아직 불펜에 투수가 남아있다면 다음 투수로 정상 교체
            if self.my_pitcher_idx < len(self.my_pitchers) - 1:
                if self.inning >= 8 and self.my_pitcher_idx < 2:
                    self.my_pitcher_idx = 2  # 셋업맨 단계 점프
                self.change_my_pitcher()
                p_my = self.get_current_my_pitcher()
            # 🚨 [막장 고증] 마지막 마무리 투수인데 체력이 0 이하로 방전되었다면? 야수 등판 발동!
            elif p_my.role == "마무리" and p_my.stamina <= 0 and p_my.name != "⚠️ 야수(패전처리)":
                p_my.name = "⚠️ 야수(패전처리)"
                p_my.role = "야수등판"
                p_my.max_stamina = 15
                p_my.stamina = 15  # 야수의 똥볼 체력 부여
                self.game_log.append("🚨 [비상사태] 불펜 투수가 전원 방전되었습니다! 감독님이 어쩔 수 없이 야수를 마운드에 올립니다!! 야수 등판!!! 😱")

        # 야수가 던지면 110~125km/h 수준의 아리랑 똥볼 고정
        if p_my.role == "야수등판":
            speed = random.randint(110, 125)
            pitch_type = random.choice(["아리랑볼", "직구인척하는볼"])
            p_my.consume(1)
        else:
            p_my.consume(1)
            # (기존 구속/구종 결정 변수가 아래에 선언되어 있다면 이 구역에서 speed와 pitch_type을 오버라이딩 하도록 연동)
            
        self.our_total_pitches += 1
        
        enemy_stats = TEAMS[self.enemy_team]
        my_stats = TEAMS[self.my_team]
        penalty = p_my.get_penalty()
        matchup_mod = self.get_matchup_modifier(self.enemy_team, self.my_team)

        pitch_type = random.choice(["직구", "슬라이더", "체인지업", "커브", "포크볼", "싱커"])
        speed = random.randint(PITCH_SPECS.get(pitch_type, {"speed_min":135, "speed_max":148})["speed_min"], PITCH_SPECS.get(pitch_type, {"speed_max":148})["speed_max"])
        pitch_zone = random.randint(1, 9) if defense_choice != 2 else 0

        self.pitch_history.append(f"{pitch_type} ({speed}km/h) - 존: {pitch_zone if pitch_zone != 0 else '외곽'}")
        if len(self.pitch_history) > 3: self.pitch_history.pop(0)

        log_prefix = f"🥎 [{p_my.name} {speed}km/h {pitch_type}] -> "

        if pitch_zone == 0:
            if random.random() < (0.12 if defense_choice == 2 else 0.22):
                self.process_pitch_hit_or_out(my_stats, enemy_stats, penalty, matchup_mod, log_prefix, False, True)
            else:
                self.ball += 1
                self.game_log.append(log_prefix + f"볼! ({self.strike}S {self.ball}B)")
                if self.ball >= 4: self.process_walk(is_defense=True)
        else:
            if random.random() < (0.35 if defense_choice == 1 else 0.42):
                self.process_pitch_hit_or_out(my_stats, enemy_stats, penalty, matchup_mod, log_prefix, True, True)
            else:
                self.strike += 1
                self.game_log.append(log_prefix + f"스트라이크! ({self.strike}S {self.ball}B)")
                if self.strike >= 3: self.process_strikeout(is_defense=True)

    def play_turn(self, user_choice: int) -> None:
        if self.game_over: return
        p_en = self.get_current_enemy_pitcher()
        if p_en.stamina <= 0 and p_en.role != "마무리":
            self.change_enemy_pitcher()
            p_en = self.get_current_enemy_pitcher()

        pitch_type = random.choice(["직구", "슬라이더", "체인지업", "커브", "포크볼", "싱커"])
        speed = random.randint(PITCH_SPECS.get(pitch_type, {"speed_min":135, "speed_max":148})["speed_min"], PITCH_SPECS.get(pitch_type, {"speed_max":148})["speed_max"])
        
        runners_count = (1 if self.base1 else 0) + (1 if self.base2 else 0) + (1 if self.base3 else 0)

        strike_probability = 0.70
        mental_penalty = 0.0

        if self.base2 or self.base3:
            if runners_count >= 2:
                # 득점권 만루/참사 위기: 멘탈이 심하게 요동쳐 볼을 마구 던지거나(볼넷 급증) 한가운데 실투 폭등
                strike_probability -= 0.12
                mental_penalty = 0.05
                p_en.stamina = max(0, p_en.stamina - 1)  # 스트레스로 체력 1 추가 소모
            else:
                # 득점권 주자 1명: 긴장감 상승
                strike_probability -= 0.06
                mental_penalty = 0.02

        if p_en.stamina < (p_en.max_stamina * 0.4):
            strike_probability -= 0.10  # 제구 난조로 볼넷 허용 증가
            mental_penalty += 0.04

        added_pitches = 1
        if random.random() > 0.15:
            added_pitches = random.choices([2, 3, 4], weights=[500, 400, 100])[0]

        # 실제 투수 체력 소모 및 전광판 투구수 반영
        p_en.consume(added_pitches)
        self.enemy_total_pitches += added_pitches
        
        pitch_zone = random.randint(1, 9) if random.random() < max(0.40, strike_probability) else 0
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
        
        total_buff = matchup_mod + self.hit_buff + 0.085 + mental_penalty 

        hbp_probability = 0.01
        if p_en.stamina < (p_en.max_stamina * 0.4):
            hbp_probability += 0.02  # 체력 저하 시 +2%
        if runners_count >= 2:
            hbp_probability += 0.02  # 위기 상황 시 제구 난조로 +2%

        if pitch_zone == 0 and random.random () < hbp_probability:
            # 사구 중 10%의 확률로 헤드샷 발생!
            if random.random() < 0.10:
                self.game_log.append(f"🚨 [헤드샷 퇴장] 콰쾅! 상대 투수의 {speed}km/h 속구가 우리 타자의 뚝배기(헬멧)를 직격했습니다!!! 😱")
                self.game_log.append(f"👨‍⚖️ 주심 주먹을 치켜들며 즉시 퇴장 명령! 상대 투수가 마운드에서 쫓겨납니다!")
                self.process_walk(is_defense=False)
                # 상대 투수 강제 교체 연산
                if self.enemy_pitcher_idx < len(self.enemy_pitchers) - 1:
                    self.enemy_pitcher_idx += 1
                    next_p = self.get_current_enemy_pitcher()
                    self.game_log.append(f"🔄 급하게 상대 불펜에서 {next_p.name}(이)가 마운드를 구원하러 올라옵니다.")
                else:
                    # 상대 팀도 투수가 없으면 야수 등판 야근 행차
                    p_en.name = "⚠️ 야수(상대패전처리)"
                    p_en.role = "야수등판"
                    p_en.max_stamina = 15
                    p_en.stamina = 15
                    self.game_log.append("🚨 [상대팀 비상] 상대 불펜 전원 방전! 상대 팀도 어쩔 수 없이 야수를 마운드에 올립니다!!")
            else:
                self.game_log.append(log_prefix + b_ctx + "💥 악! 투수가 던진 실투가 타자의 몸을 강타합니다! 몸에 맞는 공으로 출루!")
                self.process_walk(is_defense=False)
            return  # 타석 종료 후 즉시 리턴
                
                
            

        # 데드볼 주사위 굴리기 (지정된 확률 충족 시 즉시 사구 출루 처리)
        if pitch_zone == 0 and random.random() < hbp_probability:
            self.game_log.append(log_prefix + b_ctx + "💥 악! 투수가 던진 실투가 타자의 몸을 정면으로 강타합니다! 몸에 맞는 공(사구)으로 출루!")
            self.process_walk(is_defense=False)
            return  # 타석 종료 후 즉시 리턴하여 후속 타격 연산 방지

        

        if user_choice == 1: # 💥 강공 (풀스윙) - 노림수가 비껴가도 시원한 장타가 뚫고 나갈 확률 상향
            res = random.choices(["HR", "HIT", "OUT", "FOUL", "MISS"], weights=[220, 380, 120, 180, 100] if is_zone_matched else [60, 320, 270, 200, 150])[0] if pitch_zone != 0 else random.choices(["HIT", "OUT", "FOUL", "MISS"], weights=[100, 350, 150, 400])[0]
            self.process_swing_result(res, log_prefix, b_ctx, my_stats, enemy_stats, penalty, is_zone_matched, total_buff)
        elif user_choice == 2: # 🌟 팀 배팅 (밀어치기) - 범타 아웃 확률을 줄이고 스프레이 히팅(단타) 유도
            res = random.choices(["HIT", "OUT", "FOUL", "MISS"], weights=[620, 80, 200, 100] if is_zone_matched else [400, 250, 200, 150])[0] if pitch_zone != 0 else random.choices(["HIT", "OUT", "FOUL", "MISS"], weights=[120, 310, 200, 370])[0]
            self.process_swing_result(res, log_prefix, b_ctx, my_stats, enemy_stats, penalty, is_zone_matched, total_buff)
        elif user_choice == 3: 
            if pitch_zone != 0:
                self.strike += 1
                self.game_log.append(log_prefix + b_ctx + f"스트라이크 지켜봄. ({self.strike}S {self.ball}B)")
                if self.strike >= 3: self.process_strikeout(is_defense=False)
            else:
                self.ball += 1
                self.game_log.append(log_prefix + b_ctx + f"볼 골라냄. ({self.strike}S {self.ball}B)")
                if self.ball >= 4: self.process_walk(is_defense=False)
     #----------    
        
        elif user_choice == 4: # 📉 기습 스퀴즈 번트 (3루 주자 강제 홈인 작전)
            if not self.base3:
                st.warning("3루에 주자가 없어 스퀴즈 번트가 불가능합니다.")
                return
            
            # 번트 컨택 성공률 연산 (수비 팀의 defense 스탯에 영향)
            bunt_success_rate = max(0.40, min(0.85, 0.65 - (enemy_stats["defense"] - my_stats["hit"]) * 0.002))
            
            self.strike = 0; self.ball = 0
            bat = self.my_batter_number
            self.my_batter_number = 1 if bat == 9 else bat + 1
            
            if random.random() < bunt_success_rate:
                # 작전 성공: 3루 주자 홈인, 타자는 희생아웃 처리
                self.update_live_scoreboard(1)
                self.base3 = False
                
                # 루상 주자 한 칸씩 진루 처리
                if self.base2: self.base3 = True; self.base2 = False
                if self.base1: self.base2 = True; self.base1 = False
                
                self.out_count += 1
                self.game_log.append(log_prefix + b_ctx + "📉 기습 스퀴즈 번트 성공!!! 3루 주자가 홈을 밟았습니다! 타자는 1루에서 아웃. (+1점)")
                self.check_three_out_change()
            else:
                # 작전 실패: 번트 플라이 미스 포구 또는 삼중살 위기 유도 아웃
                self.out_count += 1
                self.game_log.append(log_prefix + b_ctx + "❌ 스퀴즈 실패! 번트 타구가 포수 정면 플라이로 잡혔습니다. 주자 이동 불가.")
                self.check_three_out_change()

        elif user_choice == 5: # 🔥 런앤히트 (주자 강제 기동 및 타자 무조건 타격 작전)
            if not (self.base1 or self.base2 or self.base3):
                st.warning("루상에 진루한 주자가 없어 런앤히트 작전이 불가능합니다.")
                return
            
            # 런앤히트 특성: 볼배합과 상관없이 주자는 무조건 뛰고 타자는 스트라이크/볼 모두 타격 유도
            if pitch_zone != 0:
                # 스트라이크 존인 경우: 주자가 미리 기동했으므로 안타 시 추가 진루(R/H 대폭 유리) 및 병살 방지
                # 컨택 가중치 부여하여 연산
                res = random.choices(["HIT", "OUT", "FOUL"], weights=[600, 300, 100])[0]
                self.process_swing_result(res, log_prefix, b_ctx, my_stats, enemy_stats, penalty, is_zone_matched, total_buff)
            else:
                # 볼 존인 경우: 타자가 나쁜 공에 강제로 배트를 대야 하므로 삼진(헛스윙) 확률 폭등 및 도루자(더블아웃) 유도
                if random.random() < 0.65:
                    self.out_count += 2  # 타자 삼진 + 주자 도루자 연동 (더블 아웃)
                    self.strike = 0; self.ball = 0
                    bat = self.my_batter_number
                    self.my_batter_number = 1 if bat == 9 else bat + 1
                    
                    self.base1 = self.base2 = self.base3 = False
                    self.game_log.append(log_prefix + f"😱 작전 대실패!! 볼 존 유인구에 타자가 헛스윙 삼진을 당한 사이, 스타트를 끊은 주자까지 포수 송구에 걸려 더블아웃(2아웃) 처리됩니다!")
                    self.check_three_out_change()
                else:
                    # 가까스로 커트하여 파울 처리
                    if self.strike < 2: self.strike += 1
                    self.game_log.append(log_prefix + b_ctx + "⚠️ 작전 미스! 빠지는 공을 타자가 간신히 걷어내며 파울을 만들었습니다.")

        if self.inning >= 9 and self.phase == "말" and self.is_home_team and self.get_home_score() > self.get_away_score():
            self.game_log.append(f"🎉 🎉 끝내기 역전!")
            self.end_kbo_game()

    def process_swing_result(self, res, log_prefix, b_ctx, my_stats, enemy_stats, penalty, is_zone_matched, total_buff) -> None:
        match_msg = "🎯 [노림수 적중] " if is_zone_matched else ""

        # 🧠 [타자별 동적 플레이 스타일 엔진 빌드]
        # 타자의 고유 스탯 분석 (홈런 스탯 40 기준 거포형 판정, 히트 스탯 70 이상 또는 특정 타순 용규형 판정)
        is_power_hitter = my_stats.get("homerun", 30) >= 40
        is_contact_pest = (my_stats.get("hit", 65) >= 70 and not is_power_hitter) or (self.my_batter_number in [2, 9])
        
        #상성 열세 
        if res in ["HR", "HIT"] and total_buff < 0 and random.random() < 0.07: 
            res = "OUT"
        #상성 우세 
        elif res == "OUT" and total_buff > 0:
            p_en = self.get_current_enemy_pitcher()
            pitcher_stamina_factor = 0.5 if p_en.stamina > (p_en.max_stamina * 0.7) else 1.0 
            if random.random() < (total_buff * 0.45 * pitcher_stamina_factor): 
                res = "HIT"
        
        if res == "MISS":
            self.strike += 1
            self.game_log.append(log_prefix + b_ctx + f"헛스윙! ({self.strike}S {self.ball}B)")
            if self.strike >= 3: self.process_strikeout(is_defense=False)
                
        elif res == "FOUL":
            foul_decision = True
            # 거포형 타자는 삼진 아니면 홈런이므로 파울 커트를 덜 하고 헛스윙/삼진으로 전환될 확률이 높음
            if is_power_hitter and self.strike == 2 and random.random() < 0.45:
                res = "MISS"
                foul_decision = False
            
            # 용규형 타자는 2스트라이크 이후에 극악의 생명력으로 파울을 더 끈질기게 깎아냄
            elif is_contact_pest and self.strike == 2:
                # 85%의 아주 높은 확률로 파울 커트 유지 (용규놀이 본색 발동)
                pass 
                
            if foul_decision:
                if self.strike < 2: 
                    self.strike += 1
                
                # 로그 메시지도 타자의 성향에 따라 다르게 출력하여 개성을 강조!
                if is_contact_pest:
                    self.game_log.append(log_prefix + b_ctx + f"⚡ 용규놀이 발동! 커트하고 또 커트하며 투수를 지치게 만듭니다! ({self.strike}S {self.ball}B)")
                elif is_power_hitter:
                    self.game_log.append(log_prefix + b_ctx + f"💥 거구의 스윙! 먹힌 타구가 라인 밖 파울이 됩니다. ({self.strike}S {self.ball}B)")
                else:
                    self.game_log.append(log_prefix + b_ctx + f"파울. ({self.strike}S {self.ball}B)")
                return
            else:
                # 파울 실패하고 삼진 처리 분기점 재집입
                self.strike = 3
                self.game_log.append(log_prefix + b_ctx + f"헛스윙! 힘껏 돌렸으나 삼진 아웃! ({self.strike}S {self.ball}B)")
                self.process_strikeout(is_defense=False)
            
        else:
            bat = self.my_batter_number
            self.strike = 0; self.ball = 0
            self.my_batter_number = 1 if bat == 9 else bat + 1

            # 거포형 타자가 인플레이 타구를 쳤을 때 홈런 확률에 시원하게 버프 가산
            if res == "HIT" and is_power_hitter and random.random() < 0.20:
                res = "HR"
            
            if res == "HR":
                self.add_stat("H")
                pts = (1 if self.base1 else 0) + (1 if self.base2 else 0) + (1 if self.base3 else 0) + 1
                self.base1 = self.base2 = self.base3 = False
                self.update_live_scoreboard(pts)
                self.game_log.append(log_prefix + match_msg + f"🔥 {b_ctx} 홈런!! (+{pts}점)")
            elif res == "HIT":             
                self.add_stat("H")
                gained = 0
                hit_roll = random.random()
                batter_speed_factor = 0.05 + (my_stats["hit"] * 0.0005)
                if is_contact_pest:
                    batter_speed_factor += 0.05
                
                if hit_roll < 0.03 + (batter_speed_factor * 0.2): # 🏃‍♂️ 3루타 (초대형 삼루타)
                    if self.base3: gained += 1
                    if self.base2: gained += 1
                    if self.base1: gained += 1
                    self.base3 = True; self.base2 = False; self.base1 = False
                    self.game_log.append(log_prefix + match_msg + f"🔥 {b_ctx} 우중간을 완전히 가르는 3루타!!! (+{gained}점)")
                elif hit_roll < 0.18 + batter_speed_factor: # 🏃‍♂️ 2루타 (좌우선상 2루타)
                    if self.base3: gained += 1
                    if self.base2: gained += 1
                    if self.base1: self.base3 = True; self.base1 = False
                    else: self.base3 = False
                    self.base2 = True; self.base1 = False
                    self.game_log.append(log_prefix + match_msg + f"🌟 좌익수 키를 넘기는 2루타!! (+{gained}점)")
                else: # 🚶‍♂️ 1루타 (단타)
                    if self.base3: gained += 1
                    if self.base2: gained += 1
                    self.base3 = self.base1; self.base2 = False; self.base1 = True
                    self.game_log.append(log_prefix + match_msg + f"⚾ 깨끗한 우전 안타! 주자 한 칸씩 진루합니다. (+{gained}점)")
                
                if gained > 0: 
                    self.update_live_scoreboard(gained)
                    
            elif res == "OUT":
                error_rate = max(0.01, 0.05 - (enemy_stats["defense"] * 0.0005))
                if random.random() < error_rate:
                    self.process_error(log_prefix, bat)
                else:
                    out_roll = random.random()
                    
                    if self.base1 and self.out_count < 2 and random.random() < 0.25:
                        self.out_count += 2; self.base1 = False
                        self.game_log.append(log_prefix + "😱 2루수-1루수 이어지는 병살타 아웃.")
                        
                    elif self.base3 and self.out_count < 2 and random.random() < 0.45:
                        self.out_count += 1; self.base3 = False
                        self.update_live_scoreboard(1)
                        self.game_log.append(log_prefix + "🕊️ 깊숙한 외야 플라이! 희생플라이 타점.")
                    else:
                        self.out_count += 1
                        if is_contact_pest:
                            self.game_log.append(log_prefix + "⚾ 빗맞은 내야 땅볼 아웃.")
                        elif out_roll < 0.40:
                            self.game_log.append(log_prefix + "⚾ 유격수 방면 정면 땅볼 아웃.")
                        elif out_roll < 0.75:
                            self.game_log.append(log_prefix + "⚾ 큼지막한 외야 뜬공(플라이) 아웃.")
                        else:
                            self.game_log.append(log_prefix + "⚾ 3루수 정면으로 빨려 들어가는 날카로운 라인드라이브 아웃!")
                self.check_three_out_change()

    def process_pitch_hit_or_out(self, my_stats, enemy_stats, penalty, matchup_mod, log_prefix, is_strike_context: bool, is_defense: bool) -> None:
        p_my = self.get_current_my_pitcher()

        # ⚾ 우리 투수의 체력 및 제구 상태에 따른 사구(HBP) 확률 계산
        hbp_probability = 0.01
        if p_my.stamina < (p_my.max_stamina * 0.4):
            hbp_probability += 0.02
            
        if not is_strike_context and random.random() < hbp_probability:
            # 사구 중 10%의 확률로 헤드샷 발생!
            if random.random() < 0.10:
                self.game_log.append(f"🚨 [헤드샷 퇴장] 퍽! 우리 투수의 실투가 상대 타자의 머리를 강타했습니다!!! 😱")
                self.game_log.append(f"👨‍⚖️ [경고] KBO 헤드샷 즉시 퇴장 룰 적용! {p_my.name} 투수가 강제 퇴장당합니다!")
                self.process_walk(is_defense=True)
                # 아군 투수 자동 교체 연산
                if self.my_pitcher_idx < len(self.my_pitchers) - 1:
                    # 다음 투수로 즉시 교체 처리
                    self.my_pitcher_idx += 1
                    next_p = self.get_current_my_pitcher()
                    self.game_log.append(f"🔄 벤치가 발칵 뒤집혔습니다! 급하게 불펜에서 {next_p.name}(이)가 구원 등판합니다!")
                else:
                    # 우리 팀 불펜이 전멸했다면 야수 등판 강제 활성화!
                    p_my.name = "⚠️ 야수(패전처리)"
                    p_my.role = "야수등판"
                    p_my.max_stamina = 15
                    p_my.stamina = 15
                    self.game_log.append("🚨 [비상사태] 남은 불펜 투수가 없습니다!!! 어쩔 수 없이 야수를 급하게 마운드에 올립니다!!")
            else: 
                self.game_log.append(log_prefix + "💥 아웃사이드 실투! 투수가 던진 빠른 공이 상대 타자의 몸에 맞았습니다. 사구 허용.")
                self.process_walk(is_defense=True)
            return  # 즉시 리턴하여 후속 플레이 방지
                

        
        hit_prob = 0.23 + (enemy_stats["hit"] - my_stats["defense"]) * 0.0015 + penalty + matchup_mod
        hr_prob = 0.02 + (enemy_stats["homerun"] * 0.0006) + (matchup_mod * 0.01)
        
        if not is_strike_context: 
            hit_prob *= 0.4
            hr_prob *= 0.10
        
        roll = random.random()
        bat = self.enemy_batter_number
        self.enemy_batter_number = 1 if bat == 9 else bat + 1
        self.strike = 0; self.ball = 0

        if roll < hr_prob:
            self.add_stat("H")
            pts = (1 if self.base1 else 0) + (1 if self.base2 else 0) + (1 if self.base3 else 0) + 1
            self.base1 = self.base2 = self.base3 = False
            self.update_live_scoreboard(pts)
            self.game_log.append(log_prefix + f"💥 실투 실점! {pts}점 홈런 허용.")
            
        elif roll < (hit_prob + hr_prob):
            self.add_stat("H")
            gained = 0
            if self.base3: gained += 1
            if self.base2: gained += 1
            self.base3 = self.base1; self.base2 = False; self.base1 = True
            if gained > 0: self.update_live_scoreboard(gained)
            self.game_log.append(log_prefix + f"🌟 피안타! (+{gained}점)")
        else:
            # ⚾ [수비 시에도 다양한 아웃과 파울 커트 이식]
            # 1. 상대 타자가 파울을 친 경우: 타석을 유지하고 투구수만 올린 채 다음 피칭 대기
            if roll > (hit_prob + hr_prob) and random.random() < 0.25:
                if self.strike < 2: self.strike += 1
                self.game_log.append(log_prefix + f"파울! 타자가 날카롭게 커트해 냅니다. ({self.strike}S {self.ball}B)")
                return
                
            # 2. 인플레이 아웃 시 다양한 아웃 루트 분기
            self.strike = 0; self.ball = 0
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

        if self.inning >= 9 and self.phase == "말" and not self.is_home_team and self.get_home_score() > self.get_away_score():
            self.game_log.append("❌ 이닝 끝내기 패배.")
            self.end_kbo_game()

    def process_walk(self, is_defense: bool) -> None:
        # ⚾ [KBO 야구 기록 규정 준수]
        # 볼넷은 안타(H) 개수를 늘리지 않고, 전광판의 볼넷(B) 개수만 1 증가시킵니다.
        if is_defense:
            if hasattr(self, 'our_bb'):
                self.our_bb += 1  # 아군 수비 시 상대 팀의 볼넷(B) 누적
            elif hasattr(self, 'our_walk'):
                self.our_walk += 1
            else:
                self.our_bb = 1
        else:
            if hasattr(self, 'enemy_bb'):
                self.enemy_bb += 1  # 아군 공격 시 우리 팀의 볼넷(B) 누적
            elif hasattr(self, 'enemy_walk'):
                self.enemy_walk += 1
            else:
                self.enemy_bb = 1
            
        self.strike = 0
        self.ball = 0
        
        # 주자 밀어내기 및 진루 연산 (안타 카운트인 self.add_stat("H")는 철저히 배제)
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
            
        # 타석 종료 후 타순 변경
        if not is_defense:
            bat = self.my_batter_number
            self.my_batter_number = 1 if bat == 9 else bat + 1
        else:
            bat = self.enemy_batter_number
            self.enemy_batter_number = 1 if bat == 9 else bat + 1
            
        self.check_three_out_change()

    def process_strikeout(self, is_defense: bool) -> None:
        self.strike = 0; self.ball = 0
        if is_defense:
            self.game_log.append(f"⚡ 탈삼진 성공!")
            bat = self.enemy_batter_number
            self.enemy_batter_number = 1 if bat == 9 else bat + 1
        else:
            self.game_log.append(f"⚡ 헛스윙 삼진 아웃.")
            bat = self.my_batter_number
            self.my_batter_number = 1 if bat == 9 else bat + 1
        self.out_count += 1
        self.check_three_out_change()

    def check_three_out_change(self) -> None:
        if self.out_count >= 3:
            
            self.game_log.append("📢 쓰리아웃 체인지!")
            if self.inning >= 9 and self.phase == "초" and self.get_away_score() < self.get_home_score():
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

    with st.sidebar:
        st.header("💎 비밀 상점 (P2W)")
        st.write(f"보유 다이아: {st.session_state.nc_diamonds} 💎")
        if st.button("💳 N Pay로 5000 다이아 충전 (11만원)"): st.session_state.nc_diamonds += 5000; st.rerun()
        
        if st.session_state.full_kbo_engine and not st.session_state.full_kbo_engine.game_over:
            game = st.session_state.full_kbo_engine
            current_is_our_turn = (not game.is_home_team and game.phase == "초") or (game.is_home_team and game.phase == "말")
            if current_is_our_turn:
                if st.button("🔥 타격 확률 극대화 버프 (100💎)"):
                    if st.session_state.nc_diamonds >= 100:
                        st.session_state.nc_diamonds -= 100
                        game.hit_buff += 0.05
                        st.success("이번 이닝 타격 버프 +5% 적용 완료!")
                    else: st.error("다이아가 부족합니다.")
            else:
                if st.button("💉 투수 체력 10 회복 (200💎)"):
                    if st.session_state.nc_diamonds >= 200:
                        st.session_state.nc_diamonds -= 200
                        p = game.get_current_my_pitcher()
                        p.stamina += 10
                        st.success("투수 체력 회복 완료!")
                    else: st.error("다이아가 부족합니다.")
        
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
        st.header("💡 [Guide] 전술 매뉴얼")
        if st.button("가이드 열람"):
            if os.path.exists("assets/game_tips.txt"):
                with open("assets/game_tips.txt", "r", encoding="utf-8") as f:
                    st.text_area("공식 가이드", value=f.read(), height=200, disabled=True)
            else: st.error("⚠️ assets/game_tips.txt 파일 누락.")

        st.divider()
        st.header("📊 상성 매트릭스")
        if st.button("상성 표 열람"):
            df_matrix = pd.DataFrame.from_dict(MATCHUP_MATRIX, orient='index', columns=MATRIX_COLUMNS)
            st.dataframe(df_matrix, use_container_width=True)

    if st.session_state.full_kbo_engine is None:
        my_team = st.selectbox("우리 팀 선택:", list(TEAMS.keys()))
        if st.button("글로벌 서버 경기 개시", type="primary"):
            st.session_state.full_kbo_engine = PureKboEngine(my_team, random.choice([t for t in TEAMS.keys() if t != my_team]))
            st.rerun()
    else:
        game: PureKboEngine = st.session_state.full_kbo_engine
        p_my = game.get_current_my_pitcher()
        p_en = game.get_current_enemy_pitcher()

        c1, c2, c3 = st.columns([2, 1, 2])
        with c1:
            st.metric(label=f"우리 팀 {game.my_emoji}", value=f"{game.our_score} 점")
            st.caption(f"🔋 {p_my.name} | 체력: [{p_my.stamina}/{p_my.max_stamina}] | {game.our_total_pitches}구")
            if not game.game_over and p_my.role != "마무리" and st.button("🔄 불펜 교체"): game.change_my_pitcher(); st.rerun()
        with c2:
            if game.game_over:
                st.markdown("<h3 style='text-align: center; color: #9E9E9E;'>경기 종료</h3>", unsafe_allow_html=True)
            else:
                st.markdown(f"<h3 style='text-align: center; color: #E63946;'>{game.inning}회{game.phase}</h3>", unsafe_allow_html=True)
                current_is_our_turn = (not game.is_home_team and game.phase == "초") or (game.is_home_team and game.phase == "말")
                st.markdown(f"<p style='text-align: center; font-size:12px;'>{'[공격 턴]' if current_is_our_turn else '[수비 턴]'}</p>", unsafe_allow_html=True)
        with c3:
            st.metric(label=f"상대 팀 {game.enemy_emoji}", value=f"{game.enemy_score} 점")
            st.caption(f"🥎 {p_en.name} | 체력: [{p_en.stamina}/{p_en.max_stamina}] | {game.enemy_total_pitches}구")

        away_name = game.enemy_team if game.is_home_team else game.my_team
        home_name = game.my_team if game.is_home_team else game.enemy_team

        display_away = []
        display_home = []

        # 경기 종료 시 실제 기록이 표기되어야 하는 정식 한계 이닝 계산
        final_inning = game.inning
        if game.game_over and game.phase == "초" and game.home_inning_scores[game.inning - 1] == "":
            # 초 공격 도중 끝났고 말 공격 기록이 없다면 이전 이닝까지만 표기 범위 한정
            final_inning = max(1, game.inning - 1)

        for i in range(12):
            if game.game_over:
                # 9회말 없이 조기 종료 시 9회말 자리에 X를 명시적으로 표기
                if i == 8 and game.home_inning_scores[i] == "X":
                    display_away.append(game.away_inning_scores[i])
                    display_home.append("X")
                # 종료된 시점 이후의 모든 유령 이닝 슬롯은 공백 처리하여 전광판 마감
                elif i >= game.inning:
                    display_away.append("")
                    display_home.append("")
                else:
                    display_away.append(game.away_inning_scores[i])
                    display_home.append(game.home_inning_scores[i])
            else:
                # 진행 중인 게임일 경우 기존 로직 유지
                display_away.append("" if i >= game.inning else game.away_inning_scores[i])
                display_home.append("" if i >= game.inning else game.home_inning_scores[i])
        
        sb = {
            "BOARD": [f"🚌 {away_name}", f"🏟️ {home_name}"],
            "1": [display_away[0], display_home[0]], "2": [display_away[1], display_home[1]], "3": [display_away[2], display_home[2]],
            "4": [display_away[3], display_home[3]], "5": [display_away[4], display_home[4]], "6": [display_away[5], display_home[5]],
            "7": [display_away[6], display_home[6]], "8": [display_away[7], display_home[7]], "9": [display_away[8], display_home[8]],
            "10": [display_away[9], display_home[9]], "11": [display_away[10], display_home[10]], "12": [display_away[11], display_home[11]],
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
                    st.markdown(f"* **아웃:** {'🔴' * game.out_count}{'⚪' * (3-game.out_count)}")
                    st.markdown(f"* **S:** {'🔥' * game.strike}{'⚪' * (3-game.strike)} | **B:** {'🟢' * game.ball}{'⚪' * (4-game.ball)}")
                with cz2:
                    st.code(f"   [{'🏃' if game.base2 else '◯'}] 2루\n[{'🏃' if game.base3 else '◯'}] 3루   [{'🏃' if game.base1 else '◯'}] 1루", language="text")

                st.info(HyperClovaX_AI.get_recommendation(game.pitch_history, game.base3, game.inning, current_is_our_turn))

                if current_is_our_turn:
                    st.caption(f"🔍 구질 히스토리: {', '.join(game.pitch_history)}")
                    st.markdown("### 📢 공격 작전")
                    b1, b2, b3 = st.columns(3)
                    with b1:
                        if st.button("💥 강공 (풀스윙)"): game.play_turn(1); st.rerun()
                        if st.button("🏃‍♂️ 스퀴즈 번트"): game.play_turn(4); st.rerun()
                    with b2:
                        if st.button("🌟 밀어치기"): game.play_turn(2); st.rerun()
                        if st.button("🔥 런앤히트"): game.play_turn(5); st.rerun()
                    with b3:
                        if st.button("👀 웨이팅"): game.play_turn(3); st.rerun()
                        if st.button("🏃 도루"): game.trigger_steal(); st.rerun()
                else:
                    st.markdown("### 🛡️ 수비 볼배합")
                    d1, d2, d3 = st.columns(3)
                    with d1:
                        if st.button("⚾ 정면 승부"): game.play_defense_one_pitch(1); st.rerun()
                    with d2:
                        if st.button("🥎 유인구"): game.play_defense_one_pitch(2); st.rerun()
                    with d3:
                        if st.button("🔮 제구 위주"): game.play_defense_one_pitch(3); st.rerun()

                st.divider()
                st.markdown("### 📜 게임 로그")
                for log in reversed(game.game_log[-5:]): st.write(log)

            with col_chat:
                st.markdown("#### 📺 실시간 채팅")
                
                # 💬 [핵심 버그 수정] 게임 플레이(클릭) 중일 때만 안전하게 코멘트를 누적 생성
                if not game.game_over:
                    users = ["야구천재", "방구석펩", "침착한스트리머", "로켓단", "다이아수저", "삼진에진심인편", "치지직조율사", "치킨치킨",
                        "물개아님돌고래임", "돔구장건설요청", "내주머니속100원", "야잘알김동구",
                        "도루묵", "클로저스파크", "9회말2아웃", "대타전문가", "KBO정신병자", "용규놀이터", 
                            "찜질방수건도둑", "월급루팡", "카미야최고야", "메카미야"]
                    chat_pool = [
                        # 전술 훈수 및 극대노
                        "아니 감독 돌았냐 ㅋㅋㅋ 진짜 뇌 빼고 경기하네", 
                        "지금 스퀴즈 각인데?? 왜 안 번트??", 
                        "투수 제발 좀 바꿔라!! 어깨 갈린다 ㅠㅠ", 
                        "감독 혹사 수준 보소 ㅋㅋㅋ 노동청 신고함",
                        "대타 누구 올릴 거냐?? 벤치 멤버 믿을 놈이 없다",
                        "이 타이밍에 도루 안 하면 언제 하냐고!!! 🏃‍♂️💨",
                        
                        # 게임 시스템 & 밸런스 드립
                        "대기업 급 핑돌이 물리 연산력 ㄷㄷ", 
                        "이게 진짜 KBO 클래식이지 ㅋㅋㅋㅋ 고증 보소", 
                        "방구석 과몰입 꿀잼이네 ㅋㅋㅋ 중계 맛집", 
                        "오늘 밸런스 패치 황밸이네 ㅋㅋ 쫄깃하다",
                        "NC식 현질 유도 없어서 갓겜 인정합니다", 
                        "데드볼 던질 때 흠칫했다 ㅋㅋㅋ 리얼리티 굿",
                        "야수 마운드 기어 올라오는 거 실화냐?? 막장 야구 ㅋㅋㅋ",
                        "일본의 카미야가 생각난다"
                        
                        # 극단적 과몰입 & 억까/억빠
                        "혈압 올라 죽겠네 ㅋㅋㅋ 혈압약 시켰다",
                        "네이버 톡방 폼 미쳤다 ㅋㅋㅋ",
                        "오늘 주심 스트존 왜 저럼?? 눈을 장식으로 달았나",
                        "아웃 아웃 아웃!! 맨날 플라이 아웃만 치냐!! 수비 보소",
                        "볼넷 밀어내기로 점수 내는 거 개꿀잼이네 ㅋㅋㅋ",
                        "2스트라이크 이후에 파울 커트 미쳤다 ㅋㅋㅋ 끈질기네",
                        "용규놀이 지독하다 지독해 ㅋㅋㅋ 투수 눈물 흘리는 중 😭",
                        "이게 야구냐?? 예능이지 ㅋㅋㅋㅋ",
                        "킹갓 제네럴 에이스 마운드 등장 ㄷㄷㄷ 지렸다",
                        "야수 등판하면 배팅볼 꿀맛인데 ㅋㅋㅋ 홈런 가자!!!",
                        "오늘 경기 9회말 끝내기 각이다 가슴이 웅장해진다"
                    ]
                    new_chat = f"💬 **{random.choice(users)}**: {random.choice(chat_pool)}"
                    game.chzzk_chats.append(new_chat)
                    
                    if len(game.chzzk_chats) > 10:
                        game.chzzk_chats.pop(0)

                # 고정된 스크롤 박스 내부에 누적 코멘트 최신순 표출
                chat_box = st.container(height=350)
                with chat_box:
                    for chat in reversed(game.chzzk_chats):
                        st.markdown(f"<div style='font-size: 14px; margin-bottom: 5px;'>{chat}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
