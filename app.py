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

# 데이터프레임 빌드 및 매퍼 스타일 정의
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

# Pandas Styler 안전 정의
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
        
        self.chzzk_chats = ["💬 **치지직 가이드**: 경기가 시작되었습니다. 전술 사인을 지켜보세요!"]
        self.hit_buff = 0.0 
        
        my_stats = TEAMS[my_team]
        enemy_stats = TEAMS[enemy_team]
        
        # 아군 5선발 로테이션 및 불펜 구축
        my_sp_pool = [
            PitcherDomain("1선발(에이스)", "선발", my_stats["stamina"]),
            PitcherDomain("2선발", "선발", int(my_stats["stamina"] * 0.95)),
            PitcherDomain("3선발", "선발", int(my_stats["stamina"] * 0.90)),
            PitcherDomain("4선발", "선발", int(my_stats["stamina"] * 0.85)),
            PitcherDomain("5선발", "선발", int(my_stats["stamina"] * 0.80)),
        ]
        self.my_pitchers = [
            random.choice(my_sp_pool), # 🎲 5인 중 랜덤 결정
            PitcherDomain("추격조 1번(롱릴리프)", "추격조", 45), # 1: 추격조 1 (롱릴리프)
            PitcherDomain("추격조 2번(중간계투)", "추격조", 40), # 2: 추격조 2 (순수 패전처리)
            PitcherDomain("추격조 3번(좌완)", "추격조", 35), # 3: 추격조 3 (원포인트/중간계투)
            PitcherDomain("추격조 4번(추격)", "추격조", 35),
            PitcherDomain("필승조 1번(마당쇠)", "필승조", 35), # 4: 셋업맨 앞을 책임질 필승조
            PitcherDomain("셋업맨", "필승조", 30),          # 5: 셋업맨 (인덱스 3 -> 5로 이동)
            PitcherDomain("클로저(마무리)", "마무리", 20)     # 6: 마무리 (인덱스 4 -> 6으로 이동)
        ]
        self.my_pitcher_idx = 0
        self.my_used_pitchers = {0} # 이미 등판한 투수 인덱스 기록 (중복 부활 방지)

        # 적군 5선발 로테이션 및 불펜 구축
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
            PitcherDomain("상대 셋업맨", "필승조", 30),
            PitcherDomain("상대 클로저", "마무리", 20)
        ]
        self.enemy_pitcher_idx = 0
        self.enemy_used_pitchers = {0}
        
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
        target_idx = self.evaluate_pitcher_scenario(is_defense=True)
        
        if target_idx == -99:
            p = self.get_current_my_pitcher()
            if p.role != "야수등판":
                p.name = "⚠️ 야수(패전처리)"
                p.role = "야수등판"
                p.max_stamina = 15
                p.stamina = 15
                self.game_log.append("🚨 [투수 교체] 8점 차 이상 대참사! 전술적으로 야수를 마운드에 올립니다.")
                return True
            return False
            
        if target_idx != self.my_pitcher_idx:
            self.my_pitcher_idx = target_idx
            self.my_used_pitchers.add(target_idx)
            p = self.get_current_my_pitcher()
            self.game_log.append(f"🔄 [투수 교체] 시나리오 적용: {p.role} '{p.name}' 등판")
            return True
        else:
            # 만약 시나리오상 다음 투수가 현재 투수와 같다면 차선책으로 강제 한 칸 이동
            if self.my_pitcher_idx < len(self.my_pitchers) - 1:
                self.my_pitcher_idx += 1
                self.my_used_pitchers.add(self.my_pitcher_idx)
                p = self.get_current_my_pitcher()
                self.game_log.append(f"🔄 [투수 교체] 수동 조절: {p.role} '{p.name}' 등판")
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

        if target_en_idx != self.enemy_pitcher_idx:
            self.enemy_pitcher_idx = target_en_idx
            self.enemy_used_pitchers.add(target_en_idx)
            p = self.get_current_enemy_pitcher()
            self.game_log.append(f"🔄 [상대 투수 교체] 시나리오 적용: 상대 불펜 가동: {p.role} '{p.name}' 등판")
            return True
        else:
            if self.enemy_pitcher_idx < len(self.enemy_pitchers) - 1:
                self.enemy_pitcher_idx += 1
                self.enemy_used_pitchers.add(self.enemy_pitcher_idx)
                p = self.get_current_enemy_pitcher()
                self.game_log.append(f"🔄 [상대 투수 교체] 수동 조절: {p.role} '{p.name}' 등판")
                return True
        return False
        

    def get_away_score(self) -> int: return self.away_stats["R"]
    def get_home_score(self) -> int: return self.home_stats["R"]

    def setup_half_inning(self) -> None:
        is_def = getattr(self, 'is_defense', True)
        try: 
            p_def = self.get_current_my_pitcher() if self.is_defense else self.get_current_enemy_pitcher()

            if p_def.stamina <= 0:
                next_idx = self.evaluate_pitcher_scenario(is_defense=self.is_def)
                if self.is_def:
                    self.my_pitcher_idx = next_idx
                    self.my_used_pitchers.add(next_idx)
                    p_new = self.get_current_my_pitcher()
                    if p_new.stamina <= 0: p_new.stamina = 20
                else:
                    self.enemy_pitcher_idx = next_idx
                    self.enemy_used_pitchers.add(next_idx)
                    p_new = self.get_current_enemy_pitcher()
                    if new_p.stamina <= 0: new_p.stamina = 20
                    self.game_log.append(f"🔄 [상대 벤치] 지친 투수가 내려가고 {p_new.name}(이)가 마운드를 받칩니다.")
        except Exception:
            pass 
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
        
        if self.inning >= 6:
            current_is_our_defense = (self.phase == "초" and not self.is_home_team) or (self.phase == "말" and self.is_home_team)
            if current_is_our_defense:
                t_idx = self.evaluate_pitcher_scenario(is_defense=True)
                if t_idx != -99 and t_idx != self.my_pitcher_idx:
                    self.my_pitcher_idx = t_idx
                    self.my_used_pitchers.add(t_idx)
                    self.game_log.append(f"🔄 [이닝 교체 공수전환] 벤치가 움직입니다. 새로운 이닝을 책임질 리드 맞춤형 [{self.get_current_my_pitcher().role}] 등판!")
            else:
                t_en_idx = self.evaluate_pitcher_scenario(is_defense=False)
                if t_en_idx != -99 and t_en_idx != self.enemy_pitcher_idx:
                    self.enemy_pitcher_idx = t_en_idx
                    self.enemy_used_pitchers.add(t_en_idx)
                    self.game_log.append(f"🔄 [이닝 교체 공수전환] 상대 팀이 이닝 시작과 동시에 투수를 바꿉니다. [{self.get_current_enemy_pitcher().role}] 등판!")

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
        if p_en.stamina <= (p_en.max_stamina * 0.3) and not getattr(p_en, 'warned_stamina', False):
            p_en.warned_stamina = True  # 중복 출력 방지
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

    def evaluate_pitcher_scenario(self, score_diff: int = None, is_enemy: bool = False, is_defense: bool = True, **kwargs) -> int:
        """현재 이닝, 점수차를 계산하여 시나리오 트리에 맞는 투수 인덱스를 반환합니다."""
        if "is_defense" in kwargs:
            is_enemy = not kwargs["is_defense"]

        if score_diff is None:
            if is_defense:
                score_diff = self.our_score - self.enemy_score
                is_enemy = False
            else:
                score_diff = self.enemy_score - self.our_score
                is_enemy = True

        used_set = self.enemy_used_pitchers if is_enemy else self.my_used_pitchers

        forbidden_indices = set()
        if self.inning < 8:
            forbidden_indices.add(7)
        if self.inning < 7:
            forbidden_indices.add(6) 

        if not (1 <= score_diff <= 3):
            forbidden_indices.add(6)
            forbidden_indices.add(7)
            
        #연장전 (10회 이상)
        if self.inning >= 10:
            candidate_list = [7, 6, 5, 4, 3, 2, 1] if (1 <= score_diff <= 3) else [5, 4, 3, 2, 1]
            for idx in candidate_list:
                if idx not in used_set and idx not in forbidden_indices:
                    return idx
                        
        # 정규 이닝 (9회 이하) 
        if 1 <= score_diff <= 3:  # 근소하게 이기고 있는 경우 (세이브/홀드)
            if self.inning <= 7:
                target = 5 #필승조 1번
            elif self.inning == 8:
                target = 6 #셋업맨
            else:  # 9회
                target = 7 #클로저
        elif score_diff => 4:  # 큰 차이로 이기는 경우
            if self.inning <= 6:
                target = 1
            elif self.inning <= 8:
                target = 2 if 2 not in used_set else 3
            else:
                target = 4 if 4 not in used_Set else 5
        elif score_diff == 0:
            if self.inning <= 6:
                target = 2
            elif self.inning <= 8:
                target = 4
            else:
                targer = 5

        else:  # 지고 있는 경우 (score_diff < 0)
            abs_diff = abs(score_diff)
            if self.inning >= 7 and abs_diff >= 8:
                return -99  # 야수 패전처리
            elif abs_diff >= 4:
                target = 3 if 3 not in used_set else 4
            else:
                target = 1 if 1 not in used_set else 2

        # 선택된 타겟이 이미 사용되었거나 금지된 투수라면 대체 투수 순차 탐색
        if target not in used_set and target not in forbidden_indices:
            return target

        # 순서 및 사용 여부 검증 후 사용 가능한 가장 낮은 인덱스(추격조 우선) 순차 등판
        for idx in [1, 2, 3, 4, 5, 6, 7]:
            if idx not in used_set and idx not in forbidden_indices:
                return idx

        # 7회 이전 비상 상황 시 4, 3번 중 사용 가능한 투수 반환
        for idx in [1, 2, 3, 4, 5]:
            if idx not in used_set:
                return idx

        return 1

        # 🔒 [무한 루프 방지 락] 만약 선택된 불펜 투수가 이미 이전에 등판해서 체력을 다 썼다면?
        # 차선책으로 다음 순번의 살아있는 불펜 투수를 찾거나, 다 뻗었다면 야수를 올립니다.
        if next_idx != current_idx and next_idx in used_set:
            # 대안 탐색
            fallback_found = False
            for alt_idx in range(1, 7):
                if alt_idx not in used_set:
                    next_idx = alt_idx
                    fallback_found = True
                    break
            if not fallback_found:
                return -99 # 불펜 전멸 시 야수 등판 신호

        return next_idx

    def play_defense_one_pitch(self, defense_choice: int) -> None:
        if self.game_over: return
        p_my = self.get_current_my_pitcher()

        # 🔋 [완전체 시나리오 엔진] 아군 현재 투수 체력 고갈 혹은 이닝 조건에 따른 교체 연산
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
                self.my_used_pitchers.add(target_idx) # 등판 기록 잠금
                p_my = self.get_current_my_pitcher()
                self.game_log.append(f"🔄 [명장 전술 작전] 시나리오 조건에 의거하여 투수를 교체합니다. [{p_my.role}] '{p_my.name}' 등판!")

        
        #1클릭 1구
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

        #볼배합 피칭존
        pitch_zone = random.randint(1, 9) if defense_choice != 2 else 0

        self.pitch_history.append(f"{pitch_type} ({speed}km/h) - 존: {pitch_zone if pitch_zone != 0 else '외곽'}")
        if len(self.pitch_history) > 3: self.pitch_history.pop(0)

        if defense_choice == 3:
            matchup_mod -= 0.05

        log_prefix = f"🥎 [{p_my.name} {speed}km/h {pitch_type}] -> "

        if pitch_zone == 0:
            roll_zone0 = random.random()
            
            if roll_zone0 < 0.25: #유인구 타격 유도
                self.process_pitch_hit_or_out(my_stats, enemy_stats, penalty, matchup_mod, log_prefix, False, True)
            
            elif roll_zone0 < 0.50: #유인구 헛스윙 유도
                self.strike += 1
                self.game_log.append(log_prefix + f"헛스윙! 타자가 유인구에 완전히 속아 배트를 크게 돌립니다! 😱 ({self.strike}S {self.ball}B)")
                if self.strike >= 3:
                    self.process_strikeout(is_defense=True)

            else: #유인구 지켜보고 골라냄 
                self.ball += 1
                self.game_log.append(log_prefix + f"볼! 타자가 침착하게 유인구를 골라냅니다. ({self.strike}S {self.ball}B)")
                if self.ball >= 4: 
                    self.process_walk(is_defense=True)
        else:
            # ⚾ [정면 승부 선택 시 버프 1] 타자가 적극적으로 받아치게 유도 (타격 룰 증가)
            swing_prob = 0.55 if defense_choice == 1 else 0.35
            
            if random.random() < swing_prob:
                # ⚾ [정면 승부 선택 시 버프 2] 정면승부 룰 적용을 판단하기 위해 임시 변수 플래그 세우기
                # (정면승부 시 맞춰 잡는 쾌감을 위해 안타성 타구를 7% 확률로 범타/아웃 처리 우회)
                if defense_choice == 1 and random.random() < 0.07:
                    # 강제로 범타 아웃 유도하는 분기 생성
                    self.strike = 0; self.ball = 0
                    self.enemy_batter_number = 1 if self.enemy_batter_number == 9 else self.enemy_batter_number + 1
                    self.out_count += 1
                    self.game_log.append(log_prefix + "⚾ [정면승부 적중] 타자가 힘껏 받아쳤으나 수비수 정면 땅볼! 가볍게 아웃 처리합니다.")
                    self.check_three_out_change()
                else:
                    self.process_pitch_hit_or_out(my_stats, enemy_stats, penalty, matchup_mod, log_prefix, True, True)
            else:
                self.strike += 1
                self.game_log.append(log_prefix + f"스트라이크! 루킹 스트라이크를 잡아냅니다. ({self.strike}S {self.ball}B)")
                if self.strike >= 3: 
                    self.process_strikeout(is_defense=True)
        

    def play_turn(self, user_choice: int) -> None:
        if self.game_over: return
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
                self.enemy_used_pitchers.add(target_en_idx) # 등판 기록 잠금
                p_en = self.get_current_enemy_pitcher()
                self.game_log.append(f"🔄 [상대 벤치 움직임] 시나리오 조건에 의거하여 투수를 교체합니다. [{p_en.role}] '{p_en.name}' 등판!")

        pitch_type = random.choice(["직구", "슬라이더", "체인지업", "커브", "포크볼", "싱커"])
        speed = random.randint(PITCH_SPECS.get(pitch_type, {"speed_min":135, "speed_max":148})["speed_min"], PITCH_SPECS.get(pitch_type, {"speed_max":148})["speed_max"])
        
        runners_count = (1 if self.base1 else 0) + (1 if self.base2 else 0) + (1 if self.base3 else 0)

        strike_probability = 0.75
        mental_penalty = 0.0

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

        #승부처 하위 타선 대타 
        pinch_hit_buff = 0.0
        if self.inning >= 6:
            score_diff = self.our_score - self.enemy_score
            # 6회 이후 비기고 있거나, 2점 차 이내 박빙이거나, 지고 있을 때 하위 타선(7, 8, 9번) 등장 시
            if score_diff <= 2 and self.my_batter_number in [7, 8, 9]:
                # 35%의 전술적 확률로 대타 요원 대기석에서 박차고 등판!
                if random.random() < 0.35:
                    pinch_hit_buff = 0.07  # 타격 기본 베이스 확률 +7.0% 가산
                    b_ctx = f"[{self.my_batter_number}번 대타 요원] "  # 로그 식별자 변경
                    self.game_log.append(log_prefix + f"🔄 [대타 작전 발동] ⚡ 감독님의 신의 한 수! 승부처 득점을 위해 {self.my_batter_number}번 타자 자리에 '해결사 대타'를 대기석에서 긴급 투입합니다!")
                   
        total_buff = matchup_mod + self.hit_buff + 0.02 + mental_penalty + pinch_hit_buff

        hbp_probability = 0.005
        if p_en.stamina < (p_en.max_stamina * 0.4):
            hbp_probability += 0.01
        if runners_count >= 2:
            hbp_probability -= 0.003

        if pitch_zone == 0 and random.random() < hbp_probability:
            if random.random() < 0.10:
                self.game_log.append(f"🚨 [헤드샷 퇴장] 콰쾅! 상대 투수의 {speed}km/h 속구가 우리 타자의 뚝배기(헬멧)를 직격했습니다!!! 😱")
                self.game_log.append(f"👨‍⚖️ 주심 주먹을 치켜들며 즉시 퇴장 명령! 상대 투수가 마운드에서 쫓겨납니다!")
                self.process_walk(is_defense=False)
                if self.enemy_pitcher_idx < len(self.enemy_pitchers) - 1:
                    self.enemy_pitcher_idx += 1
                    next_p = self.get_current_enemy_pitcher()
                    self.game_log.append(f"🔄 급하게 상대 불펜에서 {next_p.name}(이)가 마운드를 구원하러 올라옵니다.")
                else:
                    p_en.name = "⚠️ 야수(상대패전처리)"
                    p_en.role = "야수등판"
                    p_en.max_stamina = 15
                    p_en.stamina = 15
                    self.game_log.append("🚨 [상대팀 비상] 상대 불펜 전원 방전! 상대 팀도 어쩔 수 없이 야수를 마운드에 올립니다!!")
            else:
                self.game_log.append(log_prefix + b_ctx + "💥 악! 투수가 던진 실투가 타자의 몸을 강타합니다! 몸에 맞는 공으로 출루!")
                self.process_walk(is_defense=False)
            return

        if pitch_zone == 0 and random.random() < hbp_probability:
            self.game_log.append(log_prefix + b_ctx + "💥 악! 투수가 던진 실투가 타자의 몸을 정면으로 강타합니다! 몸에 맞는 공(사구)으로 출루!")
            self.process_walk(is_defense=False)
            return

        if user_choice == 1:
            res = random.choices(["HR", "HIT", "OUT", "FOUL", "MISS"], weights=[180, 320, 200, 200, 100] if is_zone_matched else [40, 260, 350, 200, 150])[0] if pitch_zone != 0 else random.choices(["HIT", "OUT", "FOUL", "MISS"], weights=[70, 380, 150, 400])[0]
            self.process_swing_result(res, log_prefix, b_ctx, my_stats, enemy_stats, penalty, is_zone_matched, total_buff)
        elif user_choice == 2:
            res = random.choices(["HIT", "OUT", "FOUL", "MISS"], weights=[520, 180, 200, 100] if is_zone_matched else [320, 330, 200, 150])[0] if pitch_zone != 0 else random.choices(["HIT", "OUT", "FOUL", "MISS"], weights=[80, 350, 200, 370])[0]
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
        elif user_choice == 4:
            if not self.base3:
                st.warning("3루에 주자가 없어 스퀴즈 번트가 불가능합니다.")
                return
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
                self.process_swing_result(res, log_prefix, b_ctx, my_stats, enemy_stats, penalty, is_zone_matched, total_buff)
            else:
                if random.random() < 0.65:
                    self.out_count += 2
                    self.strike = 0; self.ball = 0
                    bat = self.my_batter_number
                    self.my_batter_number = 1 if bat == 9 else bat + 1
                    self.base1 = self.base2 = self.base3 = False
                    self.game_log.append(log_prefix + f"😱 작전 대실패!! 볼 존 유인구에 타자가 헛스윙 삼진을 당한 사이, 스타트를 끊은 주자까지 포수 송구에 걸려 더블아웃(2아웃) 처리됩니다!")
                    self.check_three_out_change()
                else:
                    if self.strike < 2: self.strike += 1
                    self.game_log.append(log_prefix + b_ctx + "⚠️ 작전 미스! 빠지는 공을 타자가 간신히 걷어내며 파울을 만들었습니다.")

        if self.inning >= 9 and self.phase == "말" and self.is_home_team and self.get_home_score() > self.get_away_score():
            self.game_log.append(f"🎉 🎉 끝내기 역전!")
            self.end_kbo_game()

    def process_swing_result(self, res, log_prefix, b_ctx, my_stats, enemy_stats, penalty, is_zone_matched, total_buff) -> None:
        match_msg = "🎯 [노림수 적중] " if is_zone_matched else ""

        is_power_hitter = my_stats.get("homerun", 30) >= 40
        is_contact_pest = (my_stats.get("hit", 65) >= 70 and not is_power_hitter) or (self.my_batter_number in [2, 9])

        base_hit_prob = 0.20 + (my_stats["hit"] * 0.0020 - enemy_stats["defense"] * 0.0010)
        base_hr_prob = 0.010 + (my_stats["homerun"] * 0.0008)
        
        if res == "HR":
            if total_buff > 0 and random.random() < 0.35:
                res = "HR"
            elif total_buff > 0:
                res = "HIT"
            else:
                res = "OUT" 

        elif res == "HIT" and total_buff < 0 and random.random() < 0.20:
            res = "OUT" 
            
        elif res == "OUT" and total_buff > 0:
            p_en = self.get_current_enemy_pitcher()
            pitcher_stamina_factor = 0.5 if p_en.stamina > (p_en.max_stamina * 0.7) else 1.0 
            
            if random.random() < (total_buff * 0.05 * pitcher_stamina_factor): 
                res = "HIT"
        
        if res == "MISS":
            self.strike += 1
            self.game_log.append(log_prefix + b_ctx + f"헛스윙! ({self.strike}S {self.ball}B)")
            if self.strike >= 3: self.process_strikeout(is_defense=False)
                
        elif res == "FOUL":
            foul_decision = True
            
            if is_power_hitter and self.strike == 2 and random.random() < 0.45:
                res = "MISS"
                foul_decision = False
                
            elif is_contact_pest and self.strike == 2:
                pass 
                
            if foul_decision:
                if self.strike < 2: 
                    self.strike += 1
                    self.game_log.append(log_prefix + b_ctx + f"파울. ({self.strike}S {self.ball}B)")
                else:
                    if is_contact_pest:
                        self.game_log.append(log_prefix + b_ctx + f"⚡ 용규놀이 발동! 2스트라이크 이후 끈질기게 커트하며 기존 카운트를 유지합니다! ({self.strike}S {self.ball}B)")
                    else:
                        self.game_log.append(log_prefix + b_ctx + f"파울볼! 2스트라이크 이후 파울로 기존 볼 카운트가 정교하게 유지됩니다. ({self.strike}S {self.ball}B)")
                return
                
            else:
                self.strike = 3
                self.game_log.append(log_prefix + b_ctx + f"헛스윙! 힘껏 돌렸으나 삼진 아웃! ({self.strike}S {self.ball}B)")
                self.process_strikeout(is_defense=False)
                return 
            
        else:
            bat = self.my_batter_number
            self.strike = 0; self.ball = 0
            self.my_batter_number = 1 if bat == 9 else bat + 1

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
                #상대팀 수비 실책 
                error_rate = max(0.01, 0.05 - (enemy_stats["defense"] * 0.0005))
                
                if random.random() < error_rate:
                    self.strike = 0
                    self.ball = 0
                    #아웃 없이 다음 타자로 
                    bat = self.my_batter_number #실책 구역용 
                    self.my_batter_number = 1 if bat == 9 else bat + 1
                    
                    #주자 진루 처리
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
                    return # 💥 아웃 카운트를 올리지 않고 기분 좋게 턴 종료!
                         
                else:
                    out_roll = random.random()

                    self.strike = 0
                    self.ball = 0
                    bat = self.my_batter_number
                    self.my_batter_number = 1 if bat == 9 else bat + 1 
                    
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
        bat = self.enemy_batter_number #함수 시작과 동시에 bat 등록  
        p_my = self.get_current_my_pitcher()
        if p_my.stamina <= (p_my.max_stamina * 0.3) and not getattr(p_my, 'warned_stamina', False):
            p_my.warned_stamina = True  # 중복 출력 방지
            self.game_log.append(f"⚠️ [벤치 비상] 마운드의 {p_my.name} 투수가 현저히 지쳤습니다! (남은 체력: {p_my.stamina}/{p_my.max_stamina})")
            self.game_log.append("💡 [감독 지시] 구위와 제구력이 크게 떨어져 실점 확률이 높아집니다. 불펜 교체를 고려하십시오!")

        #상대 팀 도루와 아군의 도루 저지
        # 3루가 비어있고, 1루나 2루에 주자가 있을 때 도루 시도 조건 성립 (단, 3아웃 상황 제외)
        if (self.base1 or self.base2) and not self.base3 and self.out_count < 3:
            # 경기 후반 박빙이거나 지고 있을 때 상대가 더 공격적으로 도루 시도 (기본 8% 확률)
            steal_attempt_prob = 0.08
            if self.inning >= 6 and (self.our_score - self.enemy_score) <= 2:
                steal_attempt_prob += 0.05
                
            if random.random() < steal_attempt_prob:
                # 🚨 [확률 분기] 3루에 주자가 있고 1%의 극악의 확률이 뚫렸을 때 '기습 홈스틸' 발동!
                if self.base3 and random.random() < 0.01:
                    self.game_log.append(log_prefix + "🔥 [🚨 비상사태!! 홈스틸 시도] 투수가 와인드업에 들어간 순간, 3루 주자가 홈으로 무모하게 몸을 던졌습니다!!! 전 관중 기립!!!")
                    
                    # 홈스틸 저지율 (포수와 투수의 완벽한 호흡 필요, 기본적으로 세이프 확률이 극히 낮음)
                    home_cs_rate = 0.75 + (my_stats["defense"] - 65) * 0.002
                    if p_my.stamina < (p_my.max_stamina * 0.3):
                        home_cs_rate -= 0.10
                    home_cs_rate = max(0.40, min(0.95, home_cs_rate))
                    
                    if random.random() < home_cs_rate:
                        # 🛑 홈에서 태그 아웃!
                        self.out_count += 1
                        self.base3 = False
                        self.game_log.append(log_prefix + "⚡ [도루 저지 성공] 투수의 재빠른 홈 송구!! 포수가 홈 플레이트를 슬라이딩하던 주자를 완벽하게 블로킹하며 태그 아웃시켰습니다! 아웃! 😤")
                        self.check_three_out_change()
                        return
                    else:
                        # 💨 홈스틸 대성공!
                        self.base3 = False
                        self.update_live_scoreboard(1)
                        self.game_log.append(log_prefix + "😱 [상대 홈스틸 성공] 세상에 이런 일이!! 투수의 허점을 완벽하게 찌르고 3루 주자가 홈을 훔쳐냈습니다! 상대 팀의 미친 승부수 적중! (+1점)")
                        # 홈스틸 성공 후 주자만 사라진 채로 원래 예정된 투구 계속 진행
                        
                # 🏃‍♂️ 일반 도루 (1루 혹은 2루 주자 진루 연산)
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


        #몸에 맞는공과 헤드샷        
        hbp_probability = 0.01
        if p_my.stamina < (p_my.max_stamina * 0.4):
            hbp_probability += 0.02
            
        if not is_strike_context and random.random() < hbp_probability:
            if random.random() < 0.10:
                self.game_log.append(f"🚨 [헤드샷 퇴장] 퍽! 우리 투수의 실투가 상대 타자의 머리를 강타했습니다!!! 😱")
                self.game_log.append(f"👨‍⚖️ [경고] KBO 헤드샷 즉시 퇴장 룰 적용! {p_my.name} 투수가 강제 퇴장당합니다!")
                self.process_walk(is_defense=True)
                if self.my_pitcher_idx < len(self.my_pitchers) - 1:
                    self.my_pitcher_idx += 1
                    next_p = self.get_current_my_pitcher()
                    self.game_log.append(f"🔄 벤치가 발칵 뒤집혔습니다! 급하게 불펜에서 {next_p.name}(이)가 구원 등판합니다!")
                else:
                    p_my.name = "⚠️ 야수(패전처리)"
                    p_my.role = "야수등판"
                    p_my.max_stamina = 15
                    p_my.stamina = 15
                    self.game_log.append("🚨 [비상사태] 남은 불펜 투수가 없습니다!!! 어쩔 수 없이 야수를 급하게 마운드에 올립니다!!")
            else: 
                self.game_log.append(log_prefix + "💥 아웃사이드 실투! 투수가 던진 빠른 공이 상대 타자의 몸에 맞았습니다. 사구 허용.")
                self.process_walk(is_defense=True)
            return

        #상대팀 공격 확률 상향 
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
        
        #분기 발생
        if roll < hr_prob:
            self.add_stat("H")
            self.enemy_batter_number = 1 if bat == 9 else bat + 1
            self.strike = 0; self.ball = 0  # 인플레이 타격 종료 시에만 초기화!
            self.add_stat("H")
            pts = (1 if self.base1 else 0) + (1 if self.base2 else 0) + (1 if self.base3 else 0) + 1
            self.base1 = self.base2 = self.base3 = False
            self.update_live_scoreboard(pts)
            self.game_log.append(log_prefix + f"💥 실투 실점! {pts}점 홈런 허용.")
            
        elif roll < (hit_prob + hr_prob):
            self.enemy_batter_number = 1 if bat == 9 else bat + 1
            self.strike = 0; self.ball = 0  # 인플레이 안타 종료 시에만 초기화!
            self.add_stat("H")
            gained = 0

            # 안타 시 주자 진루 다이내믹 확장 (2루타 확률 가산)
            hit_roll = random.random()
            if hit_roll < 0.25 and (self.base1 or self.base2 or self.base3):
                # 상대 팀의 우중간 가르는 연속 2루타 기믹
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
            if roll > (hit_prob + hr_prob) and random.random() < 0.25:
                if self.strike < 2: 
                    self.strike += 1
                    self.game_log.append(log_prefix + f"파울! 타자가 날카롭게 커트해 냅니다. ({self.strike}S {self.ball}B)")
                else:
                    self.game_log.append(log_prefix + f"파울! 2스트라이크 이후 파울로 카운트는 계속 유지됩니다. 끈질깁니다! ({self.strike}S {self.ball}B)")
                return

            #실책 추가 
            error_prob = 0.04 + (100 - my_stats["defense"]) * 0.001
            if p_my.stamina < (p_my.max_stamina * 0.3):
                error_prob += 0.03

            if random.random() < error_prob:
                # 타석 카운트 초기화 및 다음 타자로 체인지 (실책으로 출루했으므로 타석 종료)
                self.enemy_batter_number = 1 if bat == 9 else bat + 1
                self.strike = 0
                self.ball = 0
                self.add_stat("E") # 팀 실책 스탯 가산
                
                # 실책으로 인한 주자 진루 연산 (안타와 유사하게 한 루씩 밀어내기/이동)
                gained = 0
                if self.base3: gained += 1; self.base3 = False
                if self.base2: self.base3 = True; self.base2 = False
                if self.base1: self.base2 = True
                self.base1 = True # 타자는 실책으로 1루 출루
                
                if gained > 0: self.update_live_scoreboard(gained)
                
                err_log = random.choice([
                    "⚠️ [치명적 실책] 평범한 내야 땅볼! 그러나 1루수의 포구 실책이 나오며 타자가 살아나갑니다! 😱",
                    "⚠️ [송구 실책] 유격수가 타구를 잘 잡았으나 1루에 악송구를 범했습니다! 공이 뒤로 빠집니다! 😭",
                    "⚠️ [알까기 실책] 외야 플라이성 타구! 어처구니없게도 좌익수가 공을 글러브에서 떨어뜨립니다!"
                ])
                self.game_log.append(log_prefix + err_log + (f" (+{gained}점)" if gained > 0 else ""))
                return # 아웃카운트 증가 없이 함수 강제 종료!
                
            #실책을 피했을 때 아웃카운트 가산 
            self.enemy_batter_number = 1 if bat == 9 else bat + 1 
            self.strike = 0
            self.ball = 0
            
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
        self.add_stat("B", 1)
        if is_defense:
            if hasattr(self, 'our_bb'):
                self.our_bb += 1
            elif hasattr(self, 'our_walk'):
                self.our_walk += 1
            else:
                self.our_bb = 1
        else:
            if hasattr(self, 'enemy_bb'):
                self.enemy_bb += 1
            elif hasattr(self, 'enemy_walk'):
                self.enemy_walk += 1
            else:
                self.enemy_bb = 1
            
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

    # 세션 상태 변수 안정화 빌드업
    if "full_kbo_engine" not in st.session_state: st.session_state.full_kbo_engine = None
    if "nc_diamonds" not in st.session_state: st.session_state.nc_diamonds = 1000
    if "my_team" not in st.session_state: st.session_state.my_team = "💖 핑크 돌핀스"

    # =====================================================================
    # ⚡ [1번 수정 구역] SIDEBAR: 상점 목록 다양화, 상성 표 격리, 쯔꾸르 세이브 시스템
    # =====================================================================
    with st.sidebar:
        st.header("💎 비밀 상점 (P2W)")
        st.write(f"보유 다이아: {st.session_state.nc_diamonds} 💎")
        
        # 💳 1. N Pay 5000 다이아 충전
        if st.button("💳 N Pay로 5000 다이아 충전 (11만원)"):
            st.session_state.nc_diamonds += 5000
            st.toast("💸 지갑 전사 발동! 5000 다이아가 즉시 충전되었습니다핑!", icon="💎")
            st.rerun()
            
        st.markdown("---")
        
        # 🛒 2. 상황별 동적 아이템 상점 (공수 교대 시 상점 목록 즉각 최적화)
        if st.session_state.full_kbo_engine and not st.session_state.full_kbo_engine.game_over:
            game = st.session_state.full_kbo_engine
            current_is_our_turn = (not game.is_home_team and game.phase == "초") or (game.is_home_team and game.phase == "말")
            
            # ⚔️ [공격 턴 상점]
            if current_is_our_turn:
                st.markdown("#### 🌸 [공격 턴 전용 아이템]")
                
                # 아이템 1. 타격 확률 극대화 버프
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

                # 아이템 2. 멘탈 교란 찌라시 (적 투수 디버프)
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

            # 🛡️ [수비 턴 상점]
            else:
                st.markdown("#### 🔋 [수비 턴 전용 아이템]")
                
                # 아이템 1. 특수 링거 수액
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

                # 아이템 2. 관중 매수 야유 (적 타자 디버프)
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
        
        # 📂 3. 쯔꾸르식 세이브 / 로드
        st.markdown("### 💾 세이브 / 로드")
        
        # 세이브 발급
        with st.expander("🔑 세이브 코드 발급"):
            if st.session_state.full_kbo_engine is None:
                st.caption("경기가 시작된 후에 중간 저장이 가능합니다. ")
            else:
                st.write("현재 경기 상황과 투수 체력까지 모두 저장됩니다. 코드를 복사해 보관하세요.")
                game = st.session_state.full_kbo_engine

                # 아군 불펜진 실시간 상태 추출
                my_pitchers_data = [
                    {"name": p.name, "role": p.role, "max_stamina": p.max_stamina, "stamina": p.stamina, "pitches_thrown": p.pitches_thrown}
                    for p in game.my_pitchers
                ]
                # 적군 불펜진 실시간 상태 추출
                enemy_pitchers_data = [
                    {"name": p.name, "role": p.role, "max_stamina": p.max_stamina, "stamina": p.stamina, "pitches_thrown": p.pitches_thrown}
                    for p in game.enemy_pitchers
                ]
                #세이브할 데이터 
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
                    "my_pitcher_idx": game.my_pitcher_idx,
                    "my_used_pitchers": list(game.my_used_pitchers), # JSON 변환을 위해 list로 직렬화
                    "my_pitchers": my_pitchers_data,
                    "enemy_pitcher_idx": game.enemy_pitcher_idx,
                    "enemy_used_pitchers": list(game.enemy_used_pitchers),
                    "enemy_pitchers": enemy_pitchers_data
                }
                json_str = json.dumps(save_data, ensure_ascii=False)
                encoded_code = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
                st.code(encoded_code, language="text")
                st.caption("위 코드를 더블클릭해 복사하세요!")

            # 로드 실행
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

                        # 3. 실시간 경기 스코어 및 변수 덮어쓰기 복구
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

                        # 4. 🔥 [핵심] 투수진 객체화 복구 및 락(Lock) 상태 복원
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
                        
                        # 5. 세션 엔진 최종 교체 완료
                        st.session_state.full_kbo_engine = loaded_game
                        
                        st.toast("🎉 데이터 복구 성공! 로드가 완료되었습니다핑!", icon="💾")
                        st.rerun()
                    except Exception:
                        st.error("❌ 유효하지 않은 암호 코드입니다.")
                else:
                    st.warning("코드를 입력해 주세요!")

        # 📊 4. [기존 메인 화면에 있던 거대한 상성 표를 사이드바 하단으로 안전하게 격리]
        st.markdown("---")
        st.markdown("### 📊 상성 매트릭스 전체 열람")
        if st.button("상성 표 열람"):
            df_matrix = pd.DataFrame.from_dict(MATCHUP_MATRIX, orient='index', columns=MATRIX_COLUMNS)
            st.dataframe(df_matrix, use_container_width=True)

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

    # =====================================================================
    # ⚡ [2번 수정 구역] MAIN: 메인 화면에는 선택한 '우리 팀'의 깔끔한 1줄 상성 요약만 출력
    # =====================================================================
    if st.session_state.full_kbo_engine is None:
        # 게임 시작 전 팀 선택창
        st.session_state.my_team = st.selectbox("우리 팀 선택:", list(TEAMS.keys()), index=list(TEAMS.keys()).index(st.session_state.my_team))
        
        # 1줄 맞춤 상성 요약 노출
        st.markdown(f"#### 📊 {st.session_state.my_team}의 구단별 상성표 요약")
        if st.session_state.my_team in df_matchup.index:
            my_status = df_matchup.loc[[st.session_state.my_team]]
            try:
                styled_status = my_status.style.map(color_matchup_cells)
            except AttributeError:
                styled_status = my_status.style.applymap(color_matchup_cells)
                
            st.dataframe(styled_status, use_container_width=True)
      
        if st.button("글로벌 서버 경기 개시", type="primary"):
            st.session_state.full_kbo_engine = PureKboEngine(st.session_state.my_team, random.choice([t for t in TEAMS.keys() if t != st.session_state.my_team]))
            st.rerun()
            
    else:
        # 게임 시작 후 구동창
        game: PureKboEngine = st.session_state.full_kbo_engine
        st.session_state.my_team = game.my_team # 싱크 동기화
        p_my = game.get_current_my_pitcher()
        p_en = game.get_current_enemy_pitcher()

        # 1줄 맞춤 상성 요약 노출 (인게임 중에도 메인 상단에서 즉각 확인 가능)
        st.markdown(f"##### 📊 실시간 상성 파트너: {game.my_team} vs {game.enemy_team}")
        if game.my_team in df_matchup.index:
            my_status = df_matchup.loc[[game.my_team]]
            try:
                styled_status = my_status.style.map(color_matchup_cells)
            except AttributeError:
                styled_status = my_status.style.applymap(color_matchup_cells)
                
            st.dataframe(styled_status, use_container_width=True)


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
                    st.markdown(f"#### **🚨 COUNT BOARD**")
                    st.markdown(f"**OUT :** {'🔴' * game.out_count}{'⚪' * (3-game.out_count)}")
                    st.markdown(f"**STRIKE :** {'🟡' * game.strike}{'⚪' * (3-game.strike)}")
                    st.markdown(f"**BALL :** {'🟢' * game.ball}{'⚪' * (4-game.ball)}")
                with cz2:
                    # 🎨 다이아몬드 베이스 시각화 도화지 설정
                    fig, ax = plt.subplots(figsize=(3, 3), facecolor='#1e1e1e') # 다크 모드 배경 테마
                    ax.set_facecolor('#1e1e1e')
                    ax.set_xlim(-1.5, 1.5)
                    ax.set_ylim(-0.5, 2.8)
                    ax.axis('off') # 불필요한 축 레이블 제거

                    # 각 루의 중심 좌표 (홈, 1루, 2루, 3루)
                    base_coords = {
                        "home": (0, 0),
                        "base1": (1, 1),
                        "base2": (0, 2),
                        "base3": (-1, 1)
                    }

                    # 주자 진루 상태 체크 연동
                    base_states = {
                        "base1": game.base1,
                        "base2": game.base2,
                        "base3": game.base3
                    }

                    # 1루, 2루, 3루 다이아몬드 패치 그리기
                    for b_name, (x, y) in base_coords.items():
                        if b_name == "home":
                            # 홈 플레이트는 오각형 기믹이지만 간결하게 작은 사각형으로 마킹
                            rect = patches.Rectangle((x-0.1, y-0.1), 0.2, 0.2, angle=45, edgecolor='#aaaaaa', facecolor='#ffffff', lw=1.5)
                            ax.add_patch(rect)
                            continue

                        # 주자 유무에 따른 동적 컬러 바인딩 (주자 있음: 주황 불빛 🔥, 주자 없음: 빈 베이스 ⚪)
                        is_runner = base_states[b_name]
                        bg_color = '#ff6b6b' if is_runner else '#3d3d3d'
                        edge_color = '#ffcbd1' if is_runner else '#777777'
                        line_width = 2.0 if is_runner else 1.0

                        rect = patches.Rectangle((x-0.18, y-0.18), 0.36, 0.36, angle=45, rotation_point='center',
                                                 edgecolor=edge_color, facecolor=bg_color, lw=line_width)
                        ax.add_patch(rect)
                        
                        # 루상 넘버링 텍스트 레이블 가독성 부여
                        label_map = {"base1": "1B", "base2": "2B", "base3": "3B"}
                        text_color = '#ffffff' if is_runner else '#aaaaaa'
                        ax.text(x, y, label_map[b_name], color=text_color, fontsize=9, ha='center', va='center', weight='bold')

                    # 베이스 간 연결선 그리기 (야구장 흙길 라인 고증)
                    line_style = dict(color='#555555', linestyle='--', linewidth=1, zorder=0)
                    ax.plot([0, 1, 0, -1, 0], [0, 1, 2, 1, 0], **line_style)

                    # 🎯 [신규 기능] 현재 공수 상태에 따른 타석의 타자 번호 판별
                    current_is_our_turn = (not game.is_home_team and game.phase == "초") or (game.is_home_team and game.phase == "말")
                    if current_is_our_turn:
                        active_batter = f"👉 OUR BATTER: {game.my_batter_number}"
                    else:
                        active_batter = f"🔥 ENEMY BATTER {game.enemy_batter_number}"

                    # 전광판 최하단 홈 플레이트 아래(y=-0.4)에 타자 정보 텍스트 박스 출력
                    ax.text(0, -0.4, active_batter, color='#51cf66', fontsize=11, ha='center', va='center', 
                            weight='bold', bbox=dict(facecolor='#2b2b2b', edgecolor='#51cf66', boxstyle='round,pad=0.3', lw=1))

                    # Streamlit 화면에 차트 주입
                    st.pyplot(fig, use_container_width=False)
                    plt.close(fig) # 메모리 누수 방지용 클로즈 인터셉트
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
                
                if not game.game_over:
                    users = ["야구천재", "방구석펩", "침착한스트리머", "로켓단", "다이아수저", "삼진에진심인편", "치지직조율사", "치킨치킨",
                        "물개아님돌고래임", "돔구장건설요청", "내주머니속100원", "야잘알김동구",
                        "도루묵", "클로저스파크", "9회말2아웃", "대타전문가", "KBO정신병자", "용규놀이터", 
                            "찜질방수건도둑", "월급루팡", "카미야최고야", "메카미야"]
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

                chat_box = st.container(height=350)
                with chat_box:
                    for chat in reversed(game.chzzk_chats):
                        st.markdown(f"<div style='font-size: 14px; margin-bottom: 5px;'>{chat}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
