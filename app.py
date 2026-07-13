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

PITCH_SPECS = {
    "직구": {"speed_min": 142, "speed_max": 155},
    "슬라이더": {"speed_min": 130, "speed_max": 142},
    "체인지업": {"speed_min": 125, "speed_max": 136},
    "커브": {"speed_min": 115, "speed_max": 126}
}

# =====================================================================
# [NAVER / NC / RIOT INFRASTRUCTURE LAYER]
# =====================================================================
class HyperClovaX_AI:
    """[네이버] 빅데이터 기반 초거대 AI 작전 추천 알고리즘"""
    @staticmethod
    def get_recommendation(pitch_history: List[str], base3: bool, inning: int, is_attack: bool) -> str:
        if not is_attack:
            return "💡 [HyperClovaX] 상대 타자의 헛스윙 비율이 높습니다. '유인구 배정'으로 헛스윙을 유도하십시오."
        
        if base3 and inning >= 7:
            return "💡 [HyperClovaX] 득점 확률 88.4%! 3루 주자를 불러들이는 '기습 스퀴즈 번트'를 강력 추천합니다."
        
        if len(pitch_history) > 1 and "직구" in pitch_history[-1]:
            return "💡 [HyperClovaX] 직전 패턴 분석 결과 오프스피드 피칭이 예상됩니다. '웨이팅(눈야구)'으로 볼넷을 노리세요."
        return "💡 [HyperClovaX] 투수의 체력이 감소하는 타이밍입니다. '팀 배팅'으로 투구수를 늘리십시오."

class ChzzkStreaming:
    """[네이버] 치지직 플랫폼 채팅 생태계 시뮬레이터"""
    CHAT_POOL = ["아니 감독 돌았냐 ㅋㅋㅋ", "대기업 급 연산력 ㄷㄷ", "지금 스퀴즈 각인데??", "투수 좀 바꿔라 제발!!", 
                 "이게 KBO지 ㅋㅋㅋㅋ", "방구석 과몰입 꿀잼", "네이버 폼 미쳤다", "NC식 과금 개에반데 ㅋㅋㅋ", "혈압 올라 죽겠네"]
    @staticmethod
    def generate_chat() -> str:
        users = ["야구천재", "방구석펩", "침착한스트리머", "로켓단", "다이아수저"]
        return f"💬 **{random.choice(users)}**: {random.choice(ChzzkStreaming.CHAT_POOL)}"

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
        if self.stamina <= 0: return 0.20
        elif self.stamina < (self.max_stamina * 0.3): return 0.08
        return 0.0

# =====================================================================
# [CORE ENGINE]
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
        self.game_log = [f"🏟️ Riot Direct 초저지연망 연결 성공. 우리 팀은 {'후공(홈팀)' if self.is_home_team else '선공(원정팀)'}."]
        self.pitch_history = ["- 투구 기록 없음"]
        self.chzzk_chats = [ChzzkStreaming.generate_chat()]
        
        # [NCSoft] BM System 버프 상태
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

    def get_away_score(self) -> int: return self.enemy_score if self.is_home_team else self.our_score
    def get_home_score(self) -> int: return self.our_score if self.is_home_team else self.enemy_score

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
            prev_a = sum([int(x) for x in self.away_inning_scores[:self.inning-1] if str(x).isdigit()])
            prev_h = sum([int(x) for x in self.home_inning_scores[:self.inning-1] if str(x).isdigit()])
            if prev_a != prev_h: self.end_kbo_game(); return
            elif self.inning > 12: self.inning = 12; self.phase = "말"; self.end_kbo_game(); return

        self.strike = 0; self.ball = 0; self.out_count = 0
        self.base1 = self.base2 = self.base3 = False
        self.hit_buff = 0.0 # 이닝 교대 시 과금 버프 초기화

    def update_live_scoreboard(self, run: int) -> None:
        idx = self.inning - 1
        if idx >= 12: return
        if self.phase == "초":
            base = 0 if self.away_inning_scores[idx] in ["", "X"] else int(self.away_inning_scores[idx])
            self.away_inning_scores[idx] = base + run
        else:
            base = 0 if self.home_inning_scores[idx] in ["", "X"] else int(self.home_inning_scores[idx])
            self.home_inning_scores[idx] = base + run

    def trigger_steal(self) -> None:
        if not (self.base1 or self.base2 or self.base3):
            st.warning("루상에 주자가 없습니다.")
            return
        p_en = self.get_current_enemy_pitcher()
        p_en.consume(1)
        self.enemy_total_pitches += 1
        self.chzzk_chats.append(ChzzkStreaming.generate_chat())

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

    def next_phase(self) -> None:
        if self.game_over: return
        if self.inning == 12 and self.phase == "말": self.end_kbo_game(); return
        if self.phase == "초": self.phase = "말"
        else: self.phase = "초"; self.inning += 1
        self.setup_half_inning()

    def end_kbo_game(self) -> None:
        self.game_over = True
        a, h = self.get_away_score(), self.get_home_score()
        if a == h: self.game_result_msg = f"🤝 [무승부] 12회 {a}:{h} DRAW 종료."
        else: self.game_result_msg = f"🏆 [경기 종료] {self.our_score} 대 {self.enemy_score}로 우리 팀 {'승리!' if self.our_score > self.enemy_score else '패배.'}"

    def play_defense_one_pitch(self, defense_choice: int) -> None:
        if self.game_over: return
        p_my = self.get_current_my_pitcher()
        if p_my.stamina <= 0 and p_my.role != "마무리":
            self.change_my_pitcher()
            p_my = self.get_current_my_pitcher()

        p_my.consume(1)
        self.our_total_pitches += 1
        self.chzzk_chats.append(ChzzkStreaming.generate_chat())
        
        enemy_stats = TEAMS[self.enemy_team]
        my_stats = TEAMS[self.my_team]
        penalty = p_my.get_penalty()
        matchup_mod = self.get_matchup_modifier(self.enemy_team, self.my_team)

        pitch_type = random.choice(["직구", "슬라이더", "체인지업", "커브"])
        speed = random.randint(PITCH_SPECS[pitch_type]["speed_min"], PITCH_SPECS[pitch_type]["speed_max"])
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
        pitch_zone = random.randint(1, 9) if random.random() < 0.72 else 0
        self.guess_zone = random.randint(1, 9)
        p_en.consume(1)
        self.enemy_total_pitches += 1
        self.chzzk_chats.append(ChzzkStreaming.generate_chat())

        self.pitch_history.append(f"{pitch_type} ({speed}km/h) - 존: {pitch_zone if pitch_zone != 0 else '외곽'}")
        if len(self.pitch_history) > 3: self.pitch_history.pop(0)

        my_stats = TEAMS[self.my_team]
        enemy_stats = TEAMS[self.enemy_team]
        penalty = p_en.get_penalty()
        matchup_mod = self.get_matchup_modifier(self.my_team, self.enemy_team)
        is_zone_matched = (pitch_zone == self.guess_zone) and (pitch_zone != 0)
        
        log_prefix = f"🔮 [상대 {speed}km/h {pitch_type}] -> "
        b_ctx = f"[{self.my_batter_number}번 타자] "

        # [NCSoft] 가챠 버프 시스템 적용 (hit_buff)
        total_buff = matchup_mod + self.hit_buff 

        if user_choice == 1: 
            res = random.choices(["HR", "HIT", "OUT", "FOUL", "MISS"], weights=[120, 280, 260, 200, 140] if is_zone_matched else [25, 180, 420, 220, 155])[0] if pitch_zone != 0 else random.choices(["HIT", "OUT", "FOUL", "MISS"], weights=[20, 480, 200, 300])[0]
            self.process_swing_result(res, log_prefix, b_ctx, my_stats, enemy_stats, penalty, is_zone_matched, total_buff)
        elif user_choice == 2: 
            res = random.choices(["HIT", "OUT", "FOUL", "MISS"], weights=[480, 200, 200, 120] if is_zone_matched else [260, 390, 200, 150])[0] if pitch_zone != 0 else random.choices(["HIT", "OUT", "FOUL", "MISS"], weights=[30, 450, 220, 300])[0]
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
            if not self.base3: return
            if random.random() < 0.60:
                self.strike = 0; self.ball = 0
                self.my_batter_number = 1 if self.my_batter_number == 9 else self.my_batter_number + 1
                self.our_score += 1
                self.update_live_scoreboard(1)
                self.base3 = False
                if self.base2: self.base3 = True; self.base2 = False
                if self.base1: self.base2 = True; self.base1 = False
                self.out_count += 1
                self.game_log.append(log_prefix + b_ctx + "📉 스퀴즈 번트 성공! (+1점)")
                self.check_three_out_change()
            else:
                self.strike += 1
                self.game_log.append(log_prefix + b_ctx + f"번트 파울. ({self.strike}S {self.ball}B)")
                if self.strike >= 3: self.process_strikeout(is_defense=False)
        elif user_choice == 5: 
            if not (self.base1 or self.base2): return
            if pitch_zone != 0:
                res = random.choices(["HIT", "OUT", "FOUL"], weights=[400, 450, 150])[0]
                self.process_swing_result(res, log_prefix, b_ctx, my_stats, enemy_stats, penalty, is_zone_matched, total_buff)
            else:
                self.out_count += 2
                self.strike = 0; self.ball = 0
                self.my_batter_number = 1 if self.my_batter_number == 9 else self.my_batter_number + 1
                self.base1 = self.base2 = self.base3 = False
                self.game_log.append(log_prefix + f"😱 작전 실패! 더블아웃!")
                self.check_three_out_change()

        if self.inning >= 9 and self.phase == "말" and self.is_home_team and self.our_score > self.enemy_score:
            self.game_log.append(f"🎉 🎉 끝내기 역전!")
            self.end_kbo_game()

    def process_swing_result(self, res, log_prefix, b_ctx, my_stats, enemy_stats, penalty, is_zone_matched, total_buff) -> None:
        match_msg = "🎯 [노림수 적중] " if is_zone_matched else ""
        if res in ["HR", "HIT"] and total_buff < 0 and random.random() < 0.15: res = "OUT"
        
        if res == "MISS":
            self.strike += 1
            self.game_log.append(log_prefix + b_ctx + f"헛스윙! ({self.strike}S {self.ball}B)")
            if self.strike >= 3: self.process_strikeout(is_defense=False)
        elif res == "FOUL":
            if self.strike < 2: self.strike += 1
            self.game_log.append(log_prefix + b_ctx + f"파울. ({self.strike}S {self.ball}B)")
        else:
            self.strike = 0; self.ball = 0
            self.my_batter_number = 1 if self.my_batter_number == 9 else self.my_batter_number + 1
            if res == "HR":
                pts = (1 if self.base1 else 0) + (1 if self.base2 else 0) + (1 if self.base3 else 0) + 1
                self.our_score += pts
                self.base1 = self.base2 = self.base3 = False
                self.update_live_scoreboard(pts)
                self.game_log.append(log_prefix + match_msg + f"🔥 {b_ctx} 홈런!! (+{pts}점)")
            elif res == "HIT":
                gained = 0
                if self.base3: gained += 1
                if self.base2: gained += 1
                self.our_score += gained
                self.base3 = self.base1; self.base2 = False; self.base1 = True
                if gained > 0: self.update_live_scoreboard(gained)
                self.game_log.append(log_prefix + match_msg + f"🌟 안타! (+{gained}점)")
            elif res == "OUT":
                if self.base1 and self.out_count < 2 and random.random() < 0.25:
                    self.out_count += 2; self.base1 = False
                    self.game_log.append(log_prefix + "😱 병살타 아웃.")
                elif self.base3 and self.out_count < 2 and random.random() < 0.45:
                    self.out_count += 1; self.base3 = False; self.our_score += 1
                    self.update_live_scoreboard(1)
                    self.game_log.append(log_prefix + "🕊️ 희생플라이 타점.")
                else:
                    self.out_count += 1
                    self.game_log.append(log_prefix + "⚾ 플라이 아웃.")
                self.check_three_out_change()

    def process_pitch_hit_or_out(self, my_stats, enemy_stats, penalty, matchup_mod, log_prefix, is_strike_context: bool, is_defense: bool) -> None:
        hit_prob = 0.25 + (enemy_stats["hit"] - my_stats["defense"]) * 0.0015 + penalty + matchup_mod
        hr_prob = 0.03 + (enemy_stats["homerun"] * 0.0008) + (matchup_mod * 0.01)
        if not is_strike_context: hit_prob *= 0.5; hr_prob *= 0.25
        
        roll = random.random()
        bat = self.enemy_batter_number
        self.enemy_batter_number = 1 if bat == 9 else bat + 1
        self.strike = 0; self.ball = 0

        if roll < hr_prob:
            pts = (1 if self.base1 else 0) + (1 if self.base2 else 0) + (1 if self.base3 else 0) + 1
            self.enemy_score += pts
            self.base1 = self.base2 = self.base3 = False
            self.update_live_scoreboard(pts)
            self.game_log.append(log_prefix + f"💥 실투 실점! {pts}점 홈런 허용.")
        elif roll < (hit_prob + hr_prob):
            gained = 0
            if self.base3: gained += 1
            if self.base2: gained += 1
            self.enemy_score += gained
            self.base3 = self.base1; self.base2 = False; self.base1 = True
            if gained > 0: self.update_live_scoreboard(gained)
            self.game_log.append(log_prefix + f"🌟 피안타! (+{gained}점)")
        else:
            if self.base1 and self.out_count < 2 and random.random() < 0.25:
                self.out_count += 2; self.base1 = False
                self.game_log.append(log_prefix + "😱 병살타 유도 성공!")
            else:
                self.out_count += 1
                self.game_log.append(log_prefix + f"⚾ 범타 캐치.")
            self.check_three_out_change()

        if self.inning >= 9 and self.phase == "말" and not self.is_home_team and self.enemy_score > self.our_score:
            self.game_log.append("❌ 이닝 끝내기 패배.")
            self.end_kbo_game()

    def process_walk(self, is_defense: bool) -> None:
        self.strike = 0; self.ball = 0
        if is_defense:
            bat = self.enemy_batter_number
            self.enemy_batter_number = 1 if bat == 9 else bat + 1
            self.game_log.append(f"🚶‍♂️ 볼넷 출루 허용.")
        else:
            bat = self.my_batter_number
            self.my_batter_number = 1 if bat == 9 else bat + 1
            self.game_log.append(f"🚶‍♂️ 볼넷 출루 성공.")
        
        if self.base1 and self.base2 and self.base3:
            if is_defense: self.enemy_score += 1
            else: self.our_score += 1
            self.update_live_scoreboard(1)
        elif self.base1 and self.base2: self.base3 = True
        elif self.base1: self.base2 = True
        else: self.base1 = True

    def process_strikeout(self, is_defense: bool) -> None:
        self.strike = 0; self.ball = 0
        if is_defense:
            bat = self.enemy_batter_number
            self.enemy_batter_number = 1 if bat == 9 else bat + 1
            self.game_log.append(f"⚡ 탈삼진 성공!")
        else:
            bat = self.my_batter_number
            self.my_batter_number = 1 if bat == 9 else bat + 1
            self.game_log.append(f"⚡ 헛스윙 삼진 아웃.")
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
    
    # [Naver Infra / Riot Network / NC MMO] 최상단 대시보드
    cc1, cc2, cc3 = st.columns(3)
    cc1.success("🟢 Naver Cloud: 99.99% Uptime")
    cc2.info(f"⚡ Riot Direct Ping: {random.randint(1, 4)}ms")
    cc3.warning(f"🌐 NC Seamless World CCU: {random.randint(15400, 18900):,}명 접속중")
    
    st.title("⚾ 초거대 엔터프라이즈 KBO 시뮬레이터")

    if "full_kbo_engine" not in st.session_state: st.session_state.full_kbo_engine = None
    if "nc_diamonds" not in st.session_state: st.session_state.nc_diamonds = 1000

    # 사이드바: NC식 매운맛 BM 상점 & Riot 유니버스
    with st.sidebar:
        st.header("💎 [NC] 비밀 상점 (P2W)")
        st.write(f"보유 다이아: {st.session_state.nc_diamonds} 💎")
        if st.button("💳 N Pay 충전 (11만원)"): st.session_state.nc_diamonds += 5000; st.rerun()
        
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
        st.header("📖 [Riot] 구단 유니버스")
        team_lore = st.selectbox("세계관 열람:", list(TEAMS.keys()))
        if st.button("스토리 보기"):
            st.info(f"{team_lore}는 수백 년 전 룬테라 대륙에서 기원한 정통파 전투 야구 구단으로...")

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
            st.caption(f"🔋 {p_my.name} | 체력: {p_my.stamina} | {game.our_total_pitches}구")
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
            st.caption(f"🥎 {p_en.name} | 체력: {p_en.stamina} | {game.enemy_total_pitches}구")

        # 스코어보드
        away_name = game.enemy_team if game.is_home_team else game.my_team
        home_name = game.my_team if game.is_home_team else game.enemy_team
        
        display_away = [("" if game.game_over and i >= game.inning else game.away_inning_scores[i]) for i in range(12)]
        display_home = [("" if game.game_over and i >= game.inning else game.home_inning_scores[i]) for i in range(12)]

        sb = {
            "BOARD": [f"🚌 {away_name}", f"🏟️ {home_name}"],
            "1": [display_away[0], display_home[0]], "2": [display_away[1], display_home[1]], "3": [display_away[2], display_home[2]],
            "4": [display_away[3], display_home[3]], "5": [display_away[4], display_home[4]], "6": [display_away[5], display_home[5]],
            "7": [display_away[6], display_home[6]], "8": [display_away[7], display_home[7]], "9": [display_away[8], display_home[8]],
            "10": [display_away[9], display_home[9]], "11": [display_away[10], display_home[10]], "12": [display_away[11], display_home[11]],
            "R": [game.get_away_score(), game.get_home_score()]
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

                # [Naver] 하이퍼클로바X AI 코치
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
                # [Naver] 치지직 채팅 생태계 연동
                st.markdown("#### 📺 치지직 실시간 채팅")
                st.container(height=300)
                for chat in reversed(game.chzzk_chats[-7:]):
                    st.caption(chat)

if __name__ == "__main__":
    main()
