import random
import os
import pandas as pd
import streamlit as st
from typing import Dict, Any, List

# =====================================================================
# [KBO OFFICIAL DATA LAYER] 1. KBO 10대 구단 프로 밸런스 스탯
# =====================================================================
TEAMS: Dict[str, Dict[str, int]] = {
    "🔴 레드 파이어스": {"homerun": 25, "hit": 45, "defense": 80, "stamina": 90, "steal_b": 30},
    "🔵 블루 웨이브스": {"homerun": 35, "hit": 50, "defense": 85, "stamina": 95, "steal_b": 10},
    "🟢 그린 몬스터즈": {"homerun": 55, "hit": 30, "defense": 70, "stamina": 85, "steal_b": 5},
    "🟡 옐로우 타이거즈": {"homerun": 40, "hit": 40, "defense": 75, "stamina": 90, "steal_b": 20},
    "🟣 퍼플 바이퍼스": {"homerun": 15, "hit": 42, "defense": 90, "stamina": 100, "steal_b": 25},
    "🟠 오렌지 자이언츠": {"homerun": 35, "hit": 38, "defense": 75, "stamina": 88, "steal_b": 10},
    "🟤 브라운 베어스": {"homerun": 28, "hit": 44, "defense": 85, "stamina": 92, "steal_b": 22},
    "⚪ 화이트 이글스": {"homerun": 20, "hit": 48, "defense": 80, "stamina": 85, "steal_b": 25},
    "⚫ 블랙 나이츠": {"homerun": 22, "hit": 38, "defense": 95, "stamina": 105, "steal_b": 15},
    "💖 핑크 돌핀스": {"homerun": 42, "hit": 45, "defense": 72, "stamina": 80, "steal_b": 28}
}

# 📊 구단 상성 매트릭스
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

MATRIX_COLUMNS = ["🔴레드", "🔵블루", "🟢그린", "🟡옐로우", "🟣퍼플", "🟠오렌지", "🟤브라운", "⚪화이트", "⚫블랙", "💖핑크"]

PITCH_SPECS = {
    "직구": {"speed_min": 142, "speed_max": 155, "desc": "포수 미트에 정면으로 내리꽂히는 속구"},
    "슬라이더": {"speed_min": 130, "speed_max": 142, "desc": "홈플레이트 근처에서 타자 바깥쪽으로 날카롭게 휘어 나가는 궤적"},
    "체인지업": {"speed_min": 125, "speed_max": 136, "desc": "직구와 같은 폼에서 나오다가 가라앉는 타이밍 오프 구종"},
    "커브": {"speed_min": 115, "speed_max": 126, "desc": "큰 포물선을 그리며 낙차가 크게 떨어지는 폭포수 궤적"}
}

# =====================================================================
# [DOMAIN MODEL] 2. 투수 객체 캡슐화 모듈
# =====================================================================
class Pitcher:
    def __init__(self, name: str, role: str, max_stamina: int) -> None:
        self.name: str = name
        self.role: str = role
        self.max_stamina: int = max_stamina
        self.stamina: int = max_stamina
        self.pitches_thrown: int = 0

    def record_pitch(self, count: int = 1) -> None:
        self.pitches_thrown += count
        self.stamina = max(0, self.stamina - count)

    def get_fatigue_penalty(self) -> float:
        if self.stamina <= 0: return 0.35  
        elif self.stamina < (self.max_stamina * 0.3): return 0.15  
        return 0.0

# =====================================================================
# [CORE ENGINE] 3. KBO 공식 룰북 기반 경기 시뮬레이션 엔진
# =====================================================================
class PureKboEngine:
    def __init__(self, my_team: str, enemy_team: str) -> None:
        self.my_team: str = my_team
        self.enemy_team: str = enemy_team
        self.my_emoji: str = my_team[:2]
        self.enemy_emoji: str = enemy_team[:2]
        
        self.is_home_team: bool = random.choice([True, False])
        
        self.our_score: int = 0
        self.enemy_score: int = 0
        self.inning: int = 1
        self.phase: str = "초"  
        
        self.my_batter_number: int = 1
        self.enemy_batter_number: int = 1
        
        self.our_total_pitches: int = 0
        self.enemy_total_pitches: int = 0
        
        self.out_count: int = 0
        self.strike: int = 0
        self.ball: int = 0
        self.base1: bool = False
        self.base2: bool = False
        self.base3: bool = False
        
        self.away_inning_scores: List[Any] = [""] * 12
        self.home_inning_scores: List[Any] = [""] * 12
        
        self.game_over: bool = False
        self.game_result_msg: str = ""
        self.game_log: List[str] = [
            f"🏟️ 경기 준비 완료. 동전 던지기 결과: 우리 팀은 {'후공(홈팀)' if self.is_home_team else '선공(원정팀)'}입니다."
        ]
        
        my_stats = TEAMS[my_team]
        enemy_stats = TEAMS[enemy_team]
        
        self.my_pitchers: List[Pitcher] = [
            Pitcher("제1선발", "선발", my_stats["stamina"]),
            Pitcher("롱릴리프", "추격조", 40),
            Pitcher("셋업맨", "필승조", 30),
            Pitcher("클로저", "마무리", 20)
        ]
        self.my_pitcher_idx: int = 0
        
        self.enemy_pitchers: List[Pitcher] = [
            Pitcher("상대 에이스", "선발", enemy_stats["stamina"]),
            Pitcher("상대 불펜", "추격조", 40),
            Pitcher("상대 셋업맨", "필승조", 30),
            Pitcher("상대 클로저", "마무리", 20)
        ]
        self.enemy_pitcher_idx: int = 0

        self.pitch_type: str = "직구"
        self.pitch_zone: int = 5
        self.guess_zone: int = 5
        self.pitch_speed: int = 145
        self.pitch_desc: str = ""
        
        self.setup_half_inning()

    def get_matchup_modifier(self, attack_team: str, defense_team: str) -> float:
        row = MATCHUP_MATRIX.get(attack_team)
        if not row: return 0.0
        keys = list(TEAMS.keys())
        try:
            def_idx = keys.index(defense_team)
            status = row[def_idx]
            if status == "우세": return 0.05   
            if status == "열세": return -0.05  
        except ValueError:
            pass
        return 0.0

    def get_current_my_pitcher(self) -> Pitcher:
        return self.my_pitchers[self.my_pitcher_idx]

    def get_current_enemy_pitcher(self) -> Pitcher:
        return self.enemy_pitchers[self.enemy_pitcher_idx]

    def change_my_pitcher(self) -> bool:
        if self.my_pitcher_idx < len(self.my_pitchers) - 1:
            self.my_pitcher_idx += 1
            p = self.get_current_my_pitcher()
            self.game_log.append(f"🔄 [투수 교체] 감독 지시: {p.role} '{p.name}' 등판")
            return True
        return False

    def change_enemy_pitcher(self) -> bool:
        if self.enemy_pitcher_idx < len(self.enemy_pitchers) - 1:
            self.enemy_pitcher_idx += 1
            p = self.get_current_enemy_pitcher()
            self.game_log.append(f"🔄 [상대 투수 교체] 상대 불펜 가동: {p.role} '{p.name}' 등판")
            return True
        return False

    def get_away_score(self) -> int:
        return self.enemy_score if self.is_home_team else self.our_score

    def get_home_score(self) -> int:
        return self.our_score if self.is_home_team else self.enemy_score

    def setup_half_inning(self) -> None:
        if self.game_over: return

        idx = self.inning - 1
        if idx < 12:
            if self.away_inning_scores[idx] == "": self.away_inning_scores[idx] = 0
            if self.home_inning_scores[idx] == "": self.home_inning_scores[idx] = 0

        away_score = self.get_away_score()
        home_score = self.get_home_score()

        if self.inning == 9 and self.phase == "말":
            if home_score > away_score:
                self.game_log.append("👍 [KBO 공식 규정] 9회초 종료 시점 홈팀 리드로 9회말 없이 경기를 조기 종료합니다.")
                self.home_inning_scores[8] = "X"
                self.end_kbo_game()
                return

        if self.inning > 9 and self.phase == "초":
            prev_away = sum([int(x) for x in self.away_inning_scores[:self.inning-1] if isinstance(x, int) or str(x).isdigit()])
            prev_home = sum([int(x) for x in self.home_inning_scores[:self.inning-1] if isinstance(x, int) or str(x).isdigit()])
            if prev_away != prev_home:
                self.end_kbo_game()
                return
            elif self.inning > 12:
                # 12회초 연장 제한 조건 정밀 연동 시 이닝 오버플로우 강제 차단
                self.inning = 12
                self.phase = "말"
                self.end_kbo_game()
                return

        self.strike = 0; self.ball = 0; self.out_count = 0
        self.base1 = self.base2 = self.base3 = False

    def update_live_scoreboard(self, run: int) -> None:
        idx = self.inning - 1
        if idx >= 12: return
        if self.phase == "초":
            current = self.away_inning_scores[idx]
            base = 0 if current == "" or current == "X" else int(current)
            self.away_inning_scores[idx] = base + run
        else:
            current = self.home_inning_scores[idx]
            base = 0 if current == "" or current == "X" else int(current)
            self.home_inning_scores[idx] = base + run

    def trigger_steal(self) -> None:
        if not (self.base1 or self.base2 or self.base3):
            st.warning("루상에 주자가 없습니다.")
            return

        enemy_pitcher = self.get_current_enemy_pitcher()
        enemy_pitcher.record_pitch(1)
        self.enemy_total_pitches += 1

        my_stats = TEAMS[self.my_team]
        enemy_stats = TEAMS[self.enemy_team]
        success_rate = 0.60 + (my_stats["steal_b"] - enemy_stats["defense"] * 0.15) * 0.01
        success_rate = max(0.15, min(0.85, success_rate))

        if self.base1 or self.base2:
            self.game_log.append("🏃‍♂️ [도루 시도] 주자가 다음 베이스로 스타트를 끊었습니다!")
            if random.random() < success_rate:
                if self.base2 and not self.base3:
                    self.base3 = True; self.base2 = False
                    self.game_log.append("✅ 3루 도루 성공!")
                elif self.base1 and not self.base2:
                    self.base2 = True; self.base1 = False
                    self.game_log.append("✅ 2루 도루 성공!")
                elif self.base1 and self.base2 and not self.base3:
                    self.base3 = True; self.base2 = True; self.base1 = False
                    self.game_log.append("✅ 더블 스틸 성공!")
            else:
                self.out_count += 1
                self.game_log.append("❌ 포수 송구에 걸려 주자 태그 아웃!")
                if self.base1 and self.base2:
                    if random.choice([True, False]): self.base1 = False
                    else: self.base2 = False
                elif self.base1: self.base1 = False
                elif self.base2: self.base2 = False
                self.check_three_out_change()

    def next_phase(self) -> None:
        if self.game_over: return
        
        # 12회말 종료 시점 스토퍼 가동 (13회초 유령 출력 차단 커널)
        if self.inning == 12 and self.phase == "말":
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
        away_score = self.get_away_score()
        home_score = self.get_home_score()

        if away_score == home_score:
            self.game_result_msg = f"🤝 [무승부] 연장 12회 종료 시점 {away_score}:{home_score} 최종 무승부(DRAW)로 경기가 종료되었습니다."
        else:
            we_won = (not self.is_home_team and self.our_score > self.enemy_score) or (self.is_home_team and self.our_score > self.enemy_score)
            if we_won: self.game_result_msg = f"🏆 [경기 종료] 최종 스코어 {self.our_score} 대 {self.enemy_score}로 우리 팀이 승리했습니다!"
            else: self.game_result_msg = f"😭 [경기 종료] 최종 스코어 {self.our_score} 대 {self.enemy_score}로 패배했습니다."

    def play_defense_one_pitch(self) -> None:
        if self.game_over: return

        pitcher = self.get_current_my_pitcher()
        if pitcher.stamina <= 0 and p_role != "마무리":
            self.change_my_pitcher()
            pitcher = self.get_current_my_pitcher()

        pitcher.record_pitch(1)
        self.our_total_pitches += 1
        
        enemy_stats = TEAMS[self.enemy_team]
        my_stats = TEAMS[self.my_team]
        penalty = pitcher.get_fatigue_penalty()
        matchup_mod = self.get_matchup_modifier(self.enemy_team, self.my_team)

        self.pitch_type = random.choice(["직구", "슬라이더", "체인지업", "커브"])
        spec = PITCH_SPECS[self.pitch_type]
        self.pitch_speed = random.randint(spec["speed_min"], spec["speed_max"])
        self.pitch_desc = spec["desc"]
        self.pitch_zone = random.randint(1, 9) if random.random() < 0.70 else 0
        
        batter_num = self.enemy_batter_number
        log_prefix = f"🥎 [{pitcher.name} {self.pitch_speed}km/h {self.pitch_type} 투구] -> "

        if self.pitch_zone == 0:  
            if random.random() < 0.25:  
                self.process_pitch_hit_or_out(my_stats, enemy_stats, penalty, matchup_mod, log_prefix, is_strike_context=False)
            else:
                self.ball += 1
                self.game_log.append(log_prefix + f"볼! 존 바깥쪽으로 빠집니다. ({self.strike}S {self.ball}B)")
                if self.ball >= 4: self.process_defense_walk(batter_num)
        else:  
            if random.random() < 0.45:  
                self.process_pitch_hit_or_out(my_stats, enemy_stats, penalty, matchup_mod, log_prefix, is_strike_context=True)
            else:
                self.strike += 1
                self.game_log.append(log_prefix + f"스트라이크! 타자가 배트를 내지 못했습니다. ({self.strike}S {self.ball}B)")
                if self.strike >= 3: self.process_defense_strikeout(batter_num)

    def process_pitch_hit_or_out(self, my_stats, enemy_stats, penalty, matchup_mod, log_prefix, is_strike_context: bool) -> None:
        hit_prob = 0.26 + (enemy_stats["hit"] - my_stats["defense"]) * 0.002 + penalty + matchup_mod
        hr_prob = 0.03 + (enemy_stats["homerun"] * 0.001) + (matchup_mod * 0.2)
        if not is_strike_context: 
            hit_prob *= 0.6; hr_prob *= 0.4  

        roll = random.random()
        batter_num = self.enemy_batter_number
        self.enemy_batter_number = 1 if batter_num == 9 else batter_num + 1
        self.strike = 0; self.ball = 0

        if roll < hr_prob:
            pts = (1 if self.base1 else 0) + (1 if self.base2 else 0) + (1 if self.base3 else 0) + 1
            self.enemy_score += pts
            self.base1 = self.base2 = self.base3 = False
            self.update_live_scoreboard(run=pts)
            self.game_log.append(log_prefix + f"💥 실투 타격! 상대 {batter_num}번 타자에게 {pts}점 홈런을 허용합니다.")
        elif roll < (hit_prob + hr_prob):
            gained = 0
            if self.base3: gained += 1
            if self.base2: gained += 1
            self.enemy_score += gained
            self.base3 = self.base1; self.base2 = False; self.base1 = True
            if gained > 0: self.update_live_scoreboard(run=gained)
            self.game_log.append(log_prefix + f"🌟 안타! 정타가 터지며 루상 주자가 진루합니다. (+{gained}점)")
        else:
            if self.base1 and self.out_count < 2 and random.random() < 0.25:
                self.out_count += 2
                self.base1 = False
                self.game_log.append(log_prefix + "😱 내야 땅볼! 병살타로 아웃카운트 2개가 동시에 올라갑니다.")
            else:
                self.out_count += 1
                self.game_log.append(log_prefix + f"⚾ 범타 유도! 상대 {batter_num}번 타자를 아웃 처리합니다.")
            self.check_three_out_change()

        if self.inning >= 9 and self.phase == "말" and not self.is_home_team:
            if self.enemy_score > self.our_score:
                self.game_log.append(f"❌ 아앗... {self.inning}회말 상대 팀에게 끝내기 점수를 내주며 패배했습니다.")
                self.end_kbo_game()

    def process_defense_walk(self, batter_num: int) -> None:
        self.strike = 0; self.ball = 0
        self.enemy_batter_number = 1 if batter_num == 9 else batter_num + 1
        self.game_log.append(f"🚶‍♂️ 볼넷! 상대 {batter_num}번 타자가 출루합니다.")
        if self.base1 and self.base2 and self.base3:
            self.enemy_score += 1
            self.update_live_scoreboard(run=1)
        elif self.base1 and self.base2: self.base3 = True
        elif self.base1: self.base2 = True
        else: self.base1 = True

    def process_defense_strikeout(self, batter_num: int) -> None:
        self.strike = 0; self.ball = 0
        self.enemy_batter_number = 1 if batter_num == 9 else batter_num + 1
        self.out_count += 1
        self.game_log.append(f"⚡ 삼진! 결정구로 상대 타자의 헛스윙을 유도했습니다.")
        self.check_three_out_change()

    def play_turn(self, user_choice: int) -> None:
        if self.game_over: return

        enemy_pitcher = self.get_current_enemy_pitcher()
        if enemy_pitcher.stamina <= 0 and enemy_pitcher.role != "마무리":
            self.change_enemy_pitcher()
            enemy_pitcher = self.get_current_enemy_pitcher()

        self.pitch_type = random.choice(["직구", "슬라이더", "체인지업", "커브", "포크볼", "싱커"])
        spec = PITCH_SPECS.get(self.pitch_type, {"speed_min": 135, "speed_max": 148, "desc": "예리하게 파고드는 변형 구종"})
        self.pitch_speed = random.randint(spec["speed_min"], spec["speed_max"])
        self.pitch_desc = spec["desc"]
        
        self.pitch_zone = random.randint(1, 9) if random.random() < 0.72 else 0
        self.guess_zone = random.randint(1, 9)
        enemy_pitcher.record_pitch(1)
        self.enemy_total_pitches += 1

        current_batter = self.my_batter_number
        my_stats = TEAMS[self.my_team]
        enemy_stats = TEAMS[self.enemy_team]
        penalty = enemy_pitcher.get_fatigue_penalty()
        matchup_mod = self.get_matchup_modifier(self.my_team, self.enemy_team)
        
        is_zone_matched = (self.pitch_zone == self.guess_zone) and (self.pitch_zone != 0)
        log_prefix = f"🔮 [상대 투수 {self.pitch_speed}km/h {self.pitch_type}] -> "
        batter_context = f"[{current_batter}번 타자] "

        if user_choice == 1:
            if self.pitch_zone == 0:  
                res = random.choices(["HIT", "OUT", "FOUL", "MISS"], weights=[30, 450, 220, 300])[0]
            else:
                weights = [150, 300, 250, 200, 100] if is_zone_matched else [30, 180, 400, 240, 150]
                res = random.choices(["HR", "HIT", "OUT", "FOUL", "MISS"], weights=weights)[0]
            self.process_swing_result(res, log_prefix, batter_context, current_batter, my_stats, enemy_stats, penalty, is_zone_matched, matchup_mod)

        elif user_choice == 2:
            if self.pitch_zone == 0:
                res = random.choices(["HIT", "OUT", "FOUL", "MISS"], weights=[50, 400, 250, 300])[0]
            else:
                weights = [450, 250, 200, 100] if is_zone_matched else [250, 400, 200, 150]
                res = random.choices(["HIT", "OUT", "FOUL", "MISS"], weights=weights)[0]
            self.process_swing_result(res, log_prefix, batter_context, current_batter, my_stats, enemy_stats, penalty, is_zone_matched, matchup_mod)

        elif user_choice == 3:
            if 1 <= self.pitch_zone <= 9:
                self.strike += 1
                self.game_log.append(log_prefix + batter_context + f"스트라이크 지켜봄. ({self.strike}S {self.ball}B)")
                if self.strike >= 3: self.process_our_strikeout(current_batter)
            else:
                self.ball += 1
                self.game_log.append(log_prefix + batter_context + f"볼 골라냄. ({self.strike}S {self.ball}B)")
                if self.ball >= 4: self.process_our_walk(current_batter)

        if self.inning >= 9 and self.phase == "말" and self.is_home_team:
            if self.get_home_score() > self.get_away_score():
                self.game_log.append(f"🎉 🎉 {self.inning}회말 끝내기 득점! 경기가 종료됩니다.")
                self.end_kbo_game()

    def process_swing_result(self, res, log_prefix, batter_context, current_batter, my_stats, enemy_stats, penalty, is_zone_matched, matchup_mod) -> None:
        match_msg = "🎯 [노림수 적중] " if is_zone_matched else ""
        if res in ["HR", "HIT"] and matchup_mod < 0 and random.random() < 0.20:
            res = "OUT"  
        
        if res == "MISS":
            self.strike += 1
            self.game_log.append(log_prefix + batter_context + f"헛스윙! ({self.strike}S {self.ball}B)")
            if self.strike >= 3: self.process_our_strikeout(current_batter)
        elif res == "FOUL":
            if self.strike < 2: self.strike += 1
            self.game_log.append(log_prefix + batter_context + f"파울. ({self.strike}S {self.ball}B)")
        else:
            self.strike = 0; self.ball = 0
            self.my_batter_number = 1 if current_batter == 9 else current_batter + 1
            
            if res == "HR":
                pts = (1 if self.base1 else 0) + (1 if self.base2 else 0) + (1 if self.base3 else 0) + 1
                self.our_score += pts
                self.base1 = self.base2 = self.base3 = False
                self.update_live_scoreboard(run=pts)
                self.game_log.append(log_prefix + match_msg + f"🔥 홈런 대폭발!! 담장을 완전히 넘기는 {pts}점 홈런!!")
            elif res == "HIT":
                gained = 0
                if self.base3: gained += 1
                if self.base2: gained += 1
                self.our_score += gained
                self.base3 = self.base1; self.base2 = False; self.base1 = True
                if gained > 0: self.update_live_scoreboard(run=gained)
                self.game_log.append(log_prefix + match_msg + f"🌟 안타! 주자 진루합니다. (+{gained}점)")
            elif res == "OUT":
                if self.base1 and self.out_count < 2 and random.random() < 0.30:
                    self.out_count += 2
                    self.base1 = False
                    self.game_log.append(log_prefix + f"😱 땅볼 정면 병살타 아웃.")
                elif self.base3 and self.out_count < 2 and random.random() < 0.45:
                    self.out_count += 1
                    self.base3 = False
                    self.our_score += 1
                    self.update_live_scoreboard(run=1)
                    self.game_log.append(log_prefix + f"🕊️ 희생플라이! 3루 주자가 홈을 밟았습니다.")
                else:
                    self.out_count += 1
                    self.game_log.append(log_prefix + f"⚾ 범타 플라이 아웃.")
                self.check_three_out_change()

    def process_our_strikeout(self, current_batter: int) -> None:
        self.strike = 0; self.ball = 0
        self.my_batter_number = 1 if current_batter == 9 else current_batter + 1
        self.out_count += 1
        self.game_log.append(f"⚡ 삼진 아웃으로 물러섭니다.")
        self.check_three_out_change()

    def process_our_walk(self, current_batter: int) -> None:
        self.strike = 0; self.ball = 0
        self.my_batter_number = 1 if current_batter == 9 else current_batter + 1
        self.game_log.append(f"🚶‍♂️ 볼넷 출루 성공.")
        if self.base1 and self.base2 and self.base3:
            self.our_score += 1
            self.update_live_scoreboard(run=1)
        elif self.base1 and self.base2: self.base3 = True
        elif self.base1: self.base2 = True
        else: self.base1 = True

    def check_three_out_change(self) -> None:
        if self.out_count >= 3:
            self.game_log.append("📢 쓰리아웃 체인지! 공수 교대합니다.")
            if self.inning >= 9 and self.phase == "초":
                if self.get_away_score() < self.get_home_score():
                    self.end_kbo_game()
                    return
            self.next_phase()

# =====================================================================
# [FRONTEND RENDERER] 4. UI 대시보드 렌더러
# =====================================================================
def main() -> None:
    st.markdown("""
        <style>
        .stButton>button { width: 100%; margin-bottom: 8px; font-size: 16px !important; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("⚾ 프로야구 시뮬레이터")

    if st.button("📜 구단 설정집 열람"):
        st.session_state.show_stories = True

    if st.session_state.get("show_stories", False):
        file_path = "assets/team_stories.txt"
        st.markdown("---")
        st.subheader("🕵️‍♂️ 구단별 설정 데이터")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                st.text_area("팀별 설정 스토리", value=f.read(), height=250, disabled=True)
        else:
            fallback_narrative = (
                "📍 assets/team_stories.txt 파일이 존재하지 않습니다.\n"
                "임시 저장된 기본 팀 정보를 로드합니다.\n\n"
                "- 레드 파이어스: 화끈한 타격 중심의 전통 구단.\n"
                "- 블루 웨이브스: 안정적인 투수력을 바탕으로 하는 수비 중심 구단."
            )
            st.text_area("기본 팀 정보", value=fallback_narrative, height=250, disabled=True)
        if st.button("❌ 닫기"):
            st.session_state.show_stories = False
            st.rerun()
        st.markdown("---")

    if "show_matrix" not in st.session_state: st.session_state.show_matrix = False
    if st.button("📊 팀별 상성 표 열람"): st.session_state.show_matrix = True

    if st.session_state.show_matrix:
        st.markdown("---")
        st.subheader("📊 구단 간 상성 판독표 (세로: 공격팀 / 가로: 수비팀)")
        df_matrix = pd.DataFrame.from_dict(MATCHUP_MATRIX, orient='index', columns=MATRIX_COLUMNS)
        
        def style_matrix_cells(val: str) -> str:
            if val == "우세": return "background-color: #1b5e20; color: #ccff90; font-weight: bold;"
            elif val == "열세": return "background-color: #b71c1c; color: #ff8a80; font-weight: bold;"
            elif val == "X": return "background-color: #424242; color: #ffffff; text-align: center; font-weight: bold;"
            return "background-color: #f5f5f5; color: #212121;"

        try: st.dataframe(df_matrix.style.map(style_matrix_cells), use_container_width=True)
        except AttributeError: st.dataframe(df_matrix.style.applymap(style_matrix_cells), use_container_width=True)
        
        if st.button("❌ 상성 표 닫기"):
            st.session_state.show_matrix = False; st.rerun()
        st.markdown("---")

    if "full_kbo_engine" not in st.session_state: st.session_state.full_kbo_engine = None

    if st.session_state.full_kbo_engine is None:
        st.markdown("### 🏟️ 구단 매칭 및 게임 시작")
        my_team = st.selectbox("플레이할 우리 팀 선택:", list(TEAMS.keys()))
        enemy_pool = [t for t in TEAMS.keys() if t != my_team]
        
        if st.button("경기 개시", type="primary"):
            st.session_state.full_kbo_engine = PureKboEngine(my_team, random.choice(enemy_pool))
            st.rerun()
    else:
        game: PureKboEngine = st.session_state.full_kbo_engine
        p_my = game.get_current_my_pitcher()
        p_en = game.get_current_enemy_pitcher()

        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            st.metric(label=f"우리 팀 {game.my_emoji}", value=f"{game.our_score} 점")
            st.caption(f"🔋 투수: {p_my.name} ({p_my.role}) | 체력: {p_my.stamina}/{p_my.max_stamina} | 투구: {game.our_total_pitches}구")
            if not game.game_over and p_my.role != "마무리":
                if st.button("🔄 불펜 투수 교체"): game.change_my_pitcher(); st.rerun()
        with col2:
            # 🚨 [버그 클린 완치] 게임 세트가 된 상태면 강제로 증가된 유령 카운트 표기를 무력화하고 경기 종료 시점 텍스트 표기 고정
            if game.game_over:
                st.markdown(f"<h3 style='text-align: center; color: #9E9E9E;'>경기 종료</h3>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; font-size:12px; font-weight:bold; color:#757575;'>[GAME SET]</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<h3 style='text-align: center; color: #E63946;'>{game.inning}회{game.phase}</h3>", unsafe_allow_html=True)
                current_is_our_turn = (not game.is_home_team and game.phase == "초") or (game.is_home_team and game.phase == "말")
                st.markdown(f"<p style='text-align: center; font-size:12px; font-weight:bold;'>{'[공격 턴]' if current_is_our_turn else '[수비 턴]'}</p>", unsafe_allow_html=True)
        with col3:
            st.metric(label=f"상대 팀 {game.enemy_emoji}", value=f"{game.enemy_score} 점")
            st.caption(f"🥎 투수: {p_en.name} ({p_en.role}) | 체력: {p_en.stamina}/{p_en.max_stamina} | 투구: {game.enemy_total_pitches}구")

        st.divider()

        away_team_name = game.enemy_team if game.is_home_team else game.my_team
        home_team_name = game.my_team if game.is_home_team else game.enemy_team

        display_away = []
        display_home = []
        for i in range(12):
            if game.game_over and i >= game.inning:
                display_away.append("")
                display_home.append("")
            else:
                display_away.append(game.away_inning_scores[i])
                display_home.append(game.home_inning_scores[i])

        scoreboard_layout = {
            "SCOREBOARD": [f"🚌 {away_team_name}", f"🏟️ {home_team_name}"],
            "1": [display_away[0], display_home[0]],
            "2": [display_away[1], display_home[1]],
            "3": [display_away[2], display_home[2]],
            "4": [display_away[3], display_home[3]],
            "5": [display_away[4], display_home[4]],
            "6": [display_away[5], display_home[5]],
            "7": [display_away[6], display_home[6]],
            "8": [display_away[7], display_home[7]],
            "9": [display_away[8], display_home[8]],
            "10": [display_away[9], display_home[9]],
            "11": [display_away[10], display_home[10]],
            "12": [display_away[11], display_home[11]],
            "R": [game.get_away_score(), game.get_home_score()]
        }
        st.table(pd.DataFrame(scoreboard_layout).set_index("SCOREBOARD"))

        if game.game_over:
            st.success(game.game_result_msg)
            if st.button("새 경기 시작하기 🔄", type="primary"):
                st.session_state.full_kbo_engine = None; st.rerun()
        else:
            cz1, cz2 = st.columns(2)
            with cz1:
                st.markdown("### 📊 카운트 상황")
                st.markdown(f"* **아웃:** {'🔴' * game.out_count}{'⚪' * (3-game.out_count)}")
                st.markdown(f"* **스트라이크:** {'🔥' * game.strike}{'⚪' * (3-game.strike)}")
                st.markdown(f"* **볼:** {'🟢' * game.ball}{'⚪' * (4-game.ball)}")
                
                if current_is_our_turn:
                    st.markdown(f"* **현재 타자:** `{game.my_batter_number}번 타자`")
                else:
                    st.markdown(f"* **상대 타자:** `{game.enemy_batter_number}번 타자` 상대 중")
            with cz2:
                b1_ico = "🏃" if game.base1 else "◯"
                b2_ico = "🏃" if game.base2 else "◯"
                b3_ico = "🏃" if game.base3 else "◯"
                st.code(f"   [{b2_ico}] 2루\n[{b3_ico}] 3루   [{b1_ico}] 1루\n     [X] 타석", language="text")

            st.divider()

            if current_is_our_turn:
                st.markdown("### 📢 공격 지시")
                bcol1, bcol2, bcol3, bcol4 = st.columns(4)
                with bcol1:
                    if st.button("💥 1. 풀스윙 강타"): game.play_turn(1); st.rerun()
                with bcol2:
                    if st.button("🌟 2. 가볍게 밀어치기"): game.play_turn(2); st.rerun()
                with bcol3:
                    if st.button("👀 3. 공 끝까지 거르기"): game.play_turn(3); st.rerun()
                with bcol4:
                    if st.button("🏃‍♂️ 4. 기습 도루 작전"): game.trigger_steal(); st.rerun()
            else:
                st.markdown("### 🛡️ 수비 방어")
                if st.button("⚾ 다음 공 1구 투구", type="primary"):
                    game.play_defense_one_pitch(); st.rerun()

        st.divider()
        st.markdown("### 🎙️ 실시간 경기 중계 기록")
        for log in reversed(game.game_log[-6:]): st.write(log)

if __name__ == "__main__":
    main()
