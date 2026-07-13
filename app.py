import random
import os
import pandas as pd
import streamlit as st
from typing import Dict, Any, List

# =====================================================================
# [KBO OFFICIAL DATA LAYER] 1. KBO 10대 구단 프로 밸런스 스탯
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
    "슬라이더": {"speed_min": 130, "speed_max": 142, "desc": "홈플레이트 근처에서 날카롭게 휘어 나가는 궤적"},
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
        if self.stamina <= 0: return 0.25  
        elif self.stamina < (self.max_stamina * 0.3): return 0.10  
        return 0.0

# =====================================================================
# [CORE ENGINE] 3. 데이터 트래킹 인터페이스 탑재 시뮬레이션 엔진
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
        
        # 📈 [인디 극복 패치] 진짜 분석관용 실시간 투구 기록 저장소
        self.pitch_history: List[str] = ["- 아직 투구 기록이 없습니다."]
        
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
            if status == "우세": return 0.03   
            if status == "열세": return -0.03  
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
        success_rate = 0.62 + (my_stats["steal_b"] - enemy_stats["defense"] * 0.15) * 0.01
        success_rate = max(0.20, min(0.80, success_rate))

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

    # 🟢 [수비 턴 감독 지시형 1구 처리 커널]
    def play_defense_one_pitch(self, defense_choice: int) -> None:
        if self.game_over: return

        pitcher = self.get_current_my_pitcher()
        if pitcher.stamina <= 0 and pitcher.role != "마무리":
            self.change_my_pitcher()
            pitcher = self.get_current_my_pitcher()

        pitcher.record_pitch(1)
        self.our_total_pitches += 1
        
        enemy_stats = TEAMS[self.enemy_team]
        my_stats = TEAMS[self.my_team]
        penalty = pitcher.get_fatigue_penalty()
        matchup_mod = self.get_matchup_modifier(self.enemy_team, self.my_team)

        # 구종 난수 매핑
        self.pitch_type = random.choice(["직구", "슬라이더", "체인지업", "커브"])
        spec = PITCH_SPECS[self.pitch_type]
        self.pitch_speed = random.randint(spec["speed_min"], spec["speed_max"])
        self.pitch_desc = spec["desc"]

        # 감독의 구질 지시 사인을 궤적 데이터에 물리 동기화
        if defense_choice == 1:  # 정면 돌파 속구 지시
            self.pitch_zone = random.randint(1, 9)
            strike_chance = 0.80
        elif defense_choice == 2:  # 유인용 변화구 지시 (볼 유도)
            self.pitch_zone = 0
            strike_chance = 0.10
        else:  # 맞춰잡는 제구 중시
            self.pitch_zone = random.randint(1, 9)
            strike_chance = 0.60

        batter_num = self.enemy_batter_number
        log_prefix = f"🥎 [{pitcher.name} {self.pitch_speed}km/h {self.pitch_type}] -> "

        # 인게임 물리 메커니즘 연산
        if self.pitch_zone == 0:  
            # 유인구 작전 성공 시 타자의 타격 억제력 가중 연산
            swing_roll = 0.12 if defense_choice == 2 else 0.22
            if random.random() < swing_roll:  
                self.process_pitch_hit_or_out(my_stats, enemy_stats, penalty, matchup_mod, log_prefix, is_strike_context=False)
            else:
                self.ball += 1
                self.game_log.append(log_prefix + f"볼! 유인구 작전에 타자가 배트를 멈췄습니다. ({self.strike}S {self.ball}B)")
                if self.ball >= 4: self.process_defense_walk(batter_num)
        else:  
            # 정면 승부 시 안타 확률 보정 제어
            hit_trigger = 0.38 if defense_choice == 1 else 0.44
            if random.random() < hit_trigger:  
                self.process_pitch_hit_or_out(my_stats, enemy_stats, penalty, matchup_mod, log_prefix, is_strike_context=True)
            else:
                self.strike += 1
                self.game_log.append(log_prefix + f"스트라이크! 존 구석을 칼같이 찌르는 투구. ({self.strike}S {self.ball}B)")
                if self.strike >= 3: self.process_defense_strikeout(batter_num)

    def process_pitch_hit_or_out(self, my_stats, enemy_stats, penalty, matchup_mod, log_prefix, is_strike_context: bool) -> None:
        hit_prob = 0.27 + (enemy_stats["hit"] - my_stats["defense"]) * 0.0015 + penalty + matchup_mod
        hr_prob = 0.035 + (enemy_stats["homerun"] * 0.0008) + (matchup_mod * 0.01)
        if not is_strike_context: 
            hit_prob *= 0.5; hr_prob *= 0.25  

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
        self.game_log.append(f"🚶‍♂️ 볼넷! 제구 난조로 상대 {batter_num}번 타자에게 포어볼 출루를 허용합니다.")
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

    # 🔴 [공격 턴 세분화 작전 지시 커널]
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

        # 📈 [인디 극복 패치] 히스토리 데이터 큐 적재 연산
        history_entry = f"{self.pitch_type} ({self.pitch_speed}km/h) - 존: {self.pitch_zone if self.pitch_zone != 0 else '외곽'}"
        self.pitch_history.append(history_entry)
        if len(self.pitch_history) > 4: self.pitch_history.pop(0)

        current_batter = self.my_batter_number
        my_stats = TEAMS[self.my_team]
        enemy_stats = TEAMS[self.enemy_team]
        penalty = enemy_pitcher.get_fatigue_penalty()
        matchup_mod = self.get_matchup_modifier(self.my_team, self.enemy_team)
        
        is_zone_matched = (self.pitch_zone == self.guess_zone) and (self.pitch_zone != 0)
        log_prefix = f"🔮 [상대 투수 {self.pitch_speed}km/h {self.pitch_type}] -> "
        batter_context = f"[{current_batter}번 타자] "

        # 1. 그린라이트 강공 (장타 노리기)
        if user_choice == 1:
            if self.pitch_zone == 0:  
                res = random.choices(["HIT", "OUT", "FOUL", "MISS"], weights=[20, 480, 200, 300])[0]
            else:
                weights = [180, 320, 220, 180, 100] if is_zone_matched else [40, 200, 400, 220, 140]
                res = random.choices(["HR", "HIT", "OUT", "FOUL", "MISS"], weights=weights)[0]
            self.process_swing_result(res, log_prefix, batter_context, current_batter, my_stats, enemy_stats, penalty, is_zone_matched, matchup_mod, is_squeeze=False)

        # 2. 팀 배팅 (컨택 위주 밀어치기)
        elif user_choice == 2:
            if self.pitch_zone == 0:
                res = random.choices(["HIT", "OUT", "FOUL", "MISS"], weights=[40, 420, 240, 300])[0]
            else:
                weights = [600, 150, 150, 100] if is_zone_matched else [320, 380, 180, 120]
                res = random.choices(["HIT", "OUT", "FOUL", "MISS"], weights=weights)[0]
            self.process_swing_result(res, log_prefix, batter_context, current_batter, my_stats, enemy_stats, penalty, is_zone_matched, matchup_mod, is_squeeze=False)

        # 3. 볼카운트 웨이팅 (눈야구)
        elif user_choice == 3:
            if 1 <= self.pitch_zone <= 9:
                self.strike += 1
                self.game_log.append(log_prefix + batter_context + f"스트라이크 지켜봄. 사인이 떨어져 웨이팅했습니다. ({self.strike}S {self.ball}B)")
                if self.strike >= 3: self.process_our_strikeout(current_batter)
            else:
                self.ball += 1
                self.game_log.append(log_prefix + batter_context + f"볼 골라냄. 유인구 거르기 대성공. ({self.strike}S {self.ball}B)")
                if self.ball >= 4: self.process_our_walk(current_batter)

        # 4. 기습 스퀴즈 번트 (3루 주자 강제 홈인 작전)
        elif user_choice == 4:
            if not self.base3:
                st.warning("3루에 주자가 없어 스퀴즈 번트가 불가능합니다.")
                return
            # 번트 안타 성공률 주사위 연산
            if random.random() < 0.65:
                self.strike = 0; self.ball = 0
                self.my_batter_number = 1 if current_batter == 9 else current_batter + 1
                self.our_score += 1
                self.update_live_scoreboard(run=1)
                self.base3 = False
                # 주자 한 칸씩 시프트
                if self.base2: self.base3 = True; self.base2 = False
                if self.base1: self.base2 = True; self.base1 = False
                self.out_count += 1 # 타자 주자는 희생 아웃
                self.game_log.append(log_prefix + f"📉 {batter_context}기습 스퀴즈 번트 성공!!! 3루 주자 홈인! 타자는 1루에서 아웃카운트와 교환합니다. (+1점)")
                self.check_three_out_change()
            else:
                self.strike += 1
                self.game_log.append(log_prefix + f"❌ 번트 파울 혹은 포수 플라이 미스! 작전이 무위로 돌아갑니다. ({self.strike}S {self.ball}B)")
                if self.strike >= 3: self.process_our_strikeout(current_batter)

        # 5. 런앤히트 (히트앤런 - 삼진 시 도루자로 연동되는 초고차원 리스크 작전)
        elif user_choice == 5:
            if not (self.base1 or self.base2):
                st.warning("루상에 진루한 주자가 없어 런앤히트 작전이 불가능합니다.")
                return
            if 1 <= self.pitch_zone <= 9: # 스트라이크 존 공 인입 시 타격 컨택 유도 가중
                res = random.choices(["HIT", "OUT", "FOUL"], weights=[450, 400, 150])[0]
                self.process_swing_result(res, log_prefix, batter_context, current_batter, my_stats, enemy_stats, penalty, is_zone_matched, matchup_mod, is_squeeze=False)
            else: # 볼 존 인입 시 작전 실패로 삼진 및 주자 주루 아웃 패널티 가중
                self.out_count += 2
                self.strike = 0; self.ball = 0
                self.my_batter_number = 1 if current_batter == 9 else current_batter + 1
                self.base1 = self.base2 = self.base3 = False
                self.game_log.append(log_prefix + f"😱 작전 미스! 볼 존 유인구에 타자가 헛스윙 삼진을 당한 사이, 스타트를 끊은 주자까지 2루에서 저지당하며 루전 스텝 아웃(더블아웃)됩니다!")
                self.check_three_out_change()

        if self.inning >= 9 and self.phase == "말" and self.is_home_team:
            if self.get_home_score() > self.get_away_score():
                self.game_log.append(f"🎉 🎉 {self.inning}회말 끝내기 득점! 경기가 종료됩니다.")
                self.end_kbo_game()

    def process_swing_result(self, res, log_prefix, batter_context, current_batter, my_stats, enemy_stats, penalty, is_zone_matched, matchup_mod, is_squeeze: bool) -> None:
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
                if self.base1 and self.out_count < 2 and random.random() < 0.25:
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
        self.game_log.append(f"🚶‍♂️ 볼넷! {current_batter}번 타자가 정밀한 선구안으로 포어볼을 골라 출루합니다.")
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

    if st.button("💡 게임 팁 및 전술 가이드 열람"):
        st.session_state.show_tips = True

    if st.session_state.get("show_tips", False):
        tips_path = "assets/game_tips.txt"
        st.markdown("---")
        st.subheader("💡 인게임 벤치 전술 가이드북")
        if os.path.exists(tips_path):
            with open(tips_path, "r", encoding="utf-8") as f:
                st.text_area("공식 가이드 연동 데이터", value=f.read(), height=250, disabled=True)
        else:
            st.error("⚠️ assets/game_tips.txt 자산을 탐색하지 못했습니다. 파일 생성 상태를 확인해주십시오.")
        if st.button("❌ 가이드 닫기"):
            st.session_state.show_tips = False
            st.rerun()
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
            if game.game_over:
                st.markdown(f"<h3 style='text-align: center; color: #9E9E9E;'>경기 종료</h3>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; font-size:12px; font-weight:bold; color:#757575;'>[GAME SET]</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<h3 style='text-align: center; color: #E63946;'>{game.inning}회{game.phase}</h3>", unsafe_allow_html=True)
                current_is_our_turn = (not game.is_home_team and game.phase == "초") or (game.is_home_team and game.phase == "말")
                st.markdown(f"<p style='text-align: center; font-size:12px; font-weight:bold;'>{'[공격 작전 지시]' if current_is_our_turn else '[수비 작전 지시]'}</p>", unsafe_allow_html=True)
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
            with cz2:
                b1_ico = "🏃" if game.base1 else "◯"
                b2_ico = "🏃" if game.base2 else "◯"
                b3_ico = "🏃" if game.base3 else "◯"
                st.code(f"   [{b2_ico}] 2루\n[{b3_ico}] 3루   [{b1_ico}] 1루\n     [X] 타석", language="text")

            # 📈 [인디 극복 패치] 상대 투구 실시간 분석 트래커 레이아웃 바인딩
            if current_is_our_turn:
                st.markdown("### 🔍 상대 투수 실시간 투구 기록 분석 (최근 3구)")
                for h in game.pitch_history:
                    st.caption(f"└ {h}")

            st.divider()

            # 🧠 [작전 다양화 패치] 단순 난수 주사위가 아닌 진짜 야구 작전판 인입
            if current_is_our_turn:
                st.markdown("### 📢 공격 지시 전술 사령판")
                bcol1, bcol2, bcol3 = st.columns(3)
                with bcol1:
                    if st.button("💥 그린라이트 (풀스윙 강공)"): game.play_turn(1); st.rerun()
                    if st.button("🏃‍♂️ 기습 스퀴즈 번트 (3루 전용)"): game.play_turn(4); st.rerun()
                with bcol2:
                    if st.button("🌟 팀 배팅 (컨택 진루타)"): game.play_turn(2); st.rerun()
                    if st.button("🔥 런앤히트 (주자 강제 기동)"): game.play_turn(5); st.rerun()
                with bcol3:
                    if st.button("👀 볼카운트 웨이팅 (눈야구)"): game.play_turn(3); st.rerun()
                    if st.button("🏃 기습 단독 도루"): game.trigger_steal(); st.rerun()
            else:
                st.markdown("### 🛡️ 수비 방어 볼배합 지시판")
                dcol1, dcol2, dcol3 = st.columns(3)
                with dcol1:
                    if st.button("⚾ 1. 패스트볼 정면 승부"): game.play_defense_one_pitch(1); st.rerun()
                with dcol2:
                    if st.button("🥎 2. 유인구 배정 (볼 유도)"): game.play_defense_one_pitch(2); st.rerun()
                with dcol3:
                    if st.button("🔮 3. 맞춰잡는 제구 중시"): game.play_defense_one_pitch(3); st.rerun()

        st.divider()
        st.markdown("### 🛡️ 실시간 경기 중계 기록")
        for log in reversed(game.game_log[-6:]): st.write(log)

if __name__ == "__main__":
    main()
