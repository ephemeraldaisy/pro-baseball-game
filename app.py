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

# 📊 10x10 하이퍼 대기업 상성 매트릭스 (세로: 공격구단 / 가로: 수비구단)
# 값 정의: "우세" (+보정), "열세" (-보정), "백중" (기본), "X" (자매칭 제한)
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
    "직구": {"speed_min": 142, "speed_max": 155, "desc": "포수 미트가 찢어지는 파열음과 함께 정면으로 내리꽂히는 속구"},
    "슬라이더": {"speed_min": 130, "speed_max": 142, "desc": "홈플레이트 근처에서 타자 바깥쪽으로 날카롭게 휘어 나가는 궤적"},
    "체인지업": {"speed_min": 125, "speed_max": 136, "desc": "직구와 완전히 같은 폼에서 나오다가 춤추듯 가라앉는 타이밍 오프 구종"},
    "커브": {"speed_min": 115, "speed_max": 126, "desc": "하늘에서 떨어지듯 큰 포물선을 그리며 낙차가 크게 떨어지는 폭포수 궤적"}
}

# =====================================================================
# [DOMAIN MODEL] 2. 프로 투수 객체지향 인스턴스 캡슐화
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
# [CORE ENGINE] 3. 10x10 상성 연동 KBO 공식 룰북 시뮬레이션 엔진
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
            f"🏟️ KBO 리그 경기 개시. 코인 토스 결과: 우리 팀은 {'후공(홈팀)' if self.is_home_team else '선공(원정팀)'}입니다."
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

    # 📊 [대기업 핵심 튜닝] 10x10 상성 스탯 변조기 연산 커널
    def get_matchup_modifier(self, attack_team: str, defense_team: str) -> float:
        row = MATCHUP_MATRIX.get(attack_team)
        if not row: return 0.0
        
        keys = list(TEAMS.keys())
        try:
            def_idx = keys.index(defense_team)
            status = row[def_idx]
            if status == "우세": return 0.05   # 안타/홈런 확률 +5% 버프
            if status == "열세": return -0.05  # 안타/홈런 확률 -5% 디버프
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
            self.game_log.append(f"🔄 [투수 교체] 감독님 지시! 우리 마운드 교체: {p.role} '{p.name}' 등판!")
            return True
        return False

    def change_enemy_pitcher(self) -> bool:
        if self.enemy_pitcher_idx < len(self.enemy_pitchers) - 1:
            self.enemy_pitcher_idx += 1
            p = self.get_current_enemy_pitcher()
            self.game_log.append(f"🔄 [상대 투수 강판] 상대 벤치 불펜 가동: {p.role} '{p.name}' 등판!")
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
                self.game_log.append("👍 [KBO 공식 룰] 9회초 종료 시점 홈팀 리드로 9회말 없이 경기를 조기 종료합니다.")
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
            self.game_log.append("🏃‍♂️ [도루 시도] 주자가 과감하게 시동을 걸고 베이스 러닝을 감행합니다!")
            if random.random() < success_rate:
                if self.base2 and not self.base3:
                    self.base3 = True; self.base2 = False
                    self.game_log.append("✅ 슬라이딩 세이프! 3루 도루 성공!")
                elif self.base1 and not self.base2:
                    self.base2 = True; self.base1 = False
                    self.game_log.append("✅ 포수의 태그 포착보다 빨랐습니다! 2루 도루 성공!")
                elif self.base1 and self.base2 and not self.base3:
                    self.base3 = True; self.base2 = True; self.base1 = False
                    self.game_log.append("✅ 허를 찌르는 더블 스틸 완벽 안착!")
            else:
                self.out_count += 1
                self.game_log.append("❌ 적 포수의 미사일 송구 송전! 루상에서 주자 태그 아웃!")
                if self.base1 and self.base2:
                    if random.choice([True, False]): self.base1 = False
                    else: self.base2 = False
                elif self.base1: self.base1 = False
                elif self.base2: self.base2 = False
                self.check_three_out_change()

    def next_phase(self) -> None:
        if self.phase == "초": self.phase = "말"
        else: self.phase = "초"; self.inning += 1
        self.setup_half_inning()

    def end_kbo_game(self) -> None:
        self.game_over = True
        away_score = self.get_away_score()
        home_score = self.get_home_score()

        if away_score == home_score:
            self.game_result_msg = f"🤝 [무승부] 연장 12회 대혈투 끝에 {away_score}:{home_score} 최종 무승부(DRAW)로 경기가 종료되었습니다."
        else:
            we_won = (not self.is_home_team and self.our_score > self.enemy_score) or (self.is_home_team and self.our_score > self.enemy_score)
            if we_won: self.game_result_msg = f"🏆 [경기 세트] 최종 스코어 {self.our_score} 대 {self.enemy_score}로 대승리를 거두었습니다!"
            else: self.game_result_msg = f"😭 [경기 세트] 최종 스코어 {self.our_score} 대 {self.enemy_score}로 패배했습니다."

    # 🟢 [우리 수비 턴 1구 처리]
    def play_defense_one_pitch(self) -> None:
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

        # 상성 매트릭스 변수 추출 (상대 공격 vs 우리 수비)
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
                self.game_log.append(log_prefix + f"볼! {self.pitch_desc}. 존을 완전히 벗어납니다. ({self.strike}S {self.ball}B)")
                if self.ball >= 4: self.process_defense_walk(batter_num)
        else:  
            if random.random() < 0.45:  
                self.process_pitch_hit_or_out(my_stats, enemy_stats, penalty, matchup_mod, log_prefix, is_strike_context=True)
            else:
                self.strike += 1
                self.game_log.append(log_prefix + f"스트라이크 루킹! {self.pitch_desc}. 허를 찔린 타자가 얼어붙습니다. ({self.strike}S {self.ball}B)")
                if self.strike >= 3: self.process_defense_strikeout(batter_num)

    def process_pitch_hit_or_out(self, my_stats, enemy_stats, penalty, matchup_mod, log_prefix, is_strike_context: bool) -> None:
        # 상성 모디파이어(matchup_mod) 결합 커널 연산
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
            self.game_log.append(log_prefix + f"💥 배트 정중앙 크러시!! 패스트볼을 그대로 받아쳐 담장을 훌쩍 넘기는 백투백급 {pts}점 홈런 허용!")
        elif roll < (hit_prob + hr_prob):
            gained = 0
            if self.base3: gained += 1
            if self.base2: gained += 1
            self.enemy_score += gained
            self.base3 = self.base1; self.base2 = False; self.base1 = True
            if gained > 0: self.update_live_scoreboard(run=gained)
            self.game_log.append(log_prefix + f"🌟 빗맞은 타구가 키를 넘깁니다! 텍사스성 우전 안타로 주자 적시 베이스 진입! (+{gained}점)")
        else:
            if self.base1 and self.out_count < 2 and random.random() < 0.25:
                self.out_count += 2
                self.base1 = False
                self.game_log.append(log_prefix + "😱 3遊간 유격수 정면 땅볼! 완벽한 내야 더블플레이 포메이션 병살타 유도 대성공!")
            else:
                self.out_count += 1
                self.game_log.append(log_prefix + f"⚾ 펜스 앞 우익수 런닝 캐치범타! 상대 {batter_num}번 타자의 장타를 수비력이 잡아냅니다.")
            self.check_three_out_change()

        if self.inning >= 9 and self.phase == "말" and not self.is_home_team:
            if self.enemy_score > self.our_score:
                self.game_log.append(f"❌ 아앗... {self.inning}회말 상대 홈팀의 전원 홈인 끝내기로 경기가 종료됩니다.")
                self.end_kbo_game()

    def process_defense_walk(self, batter_num: int) -> None:
        self.strike = 0; self.ball = 0
        self.enemy_batter_number = 1 if batter_num == 9 else batter_num + 1
        self.game_log.append(f"🚶‍♂️ 제구 난조 포어볼! 상대 {batter_num}번 타자 스트레이트 볼넷으로 루상에 출루합니다.")
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
        self.game_log.append(f"⚡ 완벽한 결정구 삼진!! 타자의 배트가 허공을 가르며 하이파이브 삼진 아웃 처리!")
        self.check_three_out_change()

    # 🔴 [우리 공격 턴 1구 처리]
    def play_turn(self, user_choice: int) -> None:
        if self.game_over: return

        enemy_pitcher = self.get_current_enemy_pitcher()
        if enemy_pitcher.stamina <= 0 and enemy_pitcher.role != "마무리":
            self.change_enemy_pitcher()
            enemy_pitcher = self.get_current_enemy_pitcher()

        self.pitch_type = random.choice(["직구", "슬라이더", "체인지업", "커브", "포크볼", "싱커"])
        spec = PITCH_SPECS.get(self.pitch_type, {"speed_min": 135, "speed_max": 148, "desc": "예리한 각도로 파고드는 변형 구종"})
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
        
        # 상성 매트릭스 변수 추출 (우리 공격 vs 상대 수비)
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
                self.game_log.append(log_prefix + batter_context + f"루킹 스트라이크! {self.pitch_desc}. 배트를 아끼고 궤적을 지켜봅니다. ({self.strike}S {self.ball}B)")
                if self.strike >= 3: self.process_our_strikeout(current_batter)
            else:
                self.ball += 1
                self.game_log.append(log_prefix + batter_context + f"볼넷 유도 성공! 낮게 떨어지는 브레이킹 볼 유인구를 칼같이 골라냈습니다. ({self.strike}S {self.ball}B)")
                if self.ball >= 4: self.process_our_walk(current_batter)

        if self.inning >= 9 and self.phase == "말" and self.is_home_team:
            if self.get_home_score() > self.get_away_score():
                self.game_log.append(f"🎉 🎉 {self.inning}회말 끝내기 승리 역전 대폭발!!! 홈팬들이 그라운드로 쏟아져 나옵니다!")
                self.end_kbo_game()

    def process_swing_result(self, res, log_prefix, batter_context, current_batter, my_stats, enemy_stats, penalty, is_zone_matched, matchup_mod) -> None:
        match_msg = "🎯 [노림수 완벽 적중!] " if is_zone_matched else ""
        
        # 실시간 상성 주사위 2차 롤링 보정 연산
        if res in ["HR", "HIT"] and matchup_mod < 0 and random.random() < 0.20:
            res = "OUT"  # 구단 상성 열세로 인한 아쉬운 정면 타구 가웃 보정
        
        if res == "MISS":
            self.strike += 1
            self.game_log.append(log_prefix + batter_context + f"헛스윙 삼진 유도구! {self.pitch_desc}에 타격 타이밍이 아예 늦었습니다. ({self.strike}S {self.ball}B)")
            if self.strike >= 3: self.process_our_strikeout(current_batter)
        elif res == "FOUL":
            if self.strike < 2: self.strike += 1
            self.game_log.append(log_prefix + batter_context + f"파울볼 커트! 타이밍은 맞았으나 빗맞으며 관중석으로 날아갑니다. ({self.strike}S {self.ball}B)")
        else:
            self.strike = 0; self.ball = 0
            self.my_batter_number = 1 if current_batter == 9 else current_batter + 1
            
            if res == "HR":
                pts = (1 if self.base1 else 0) + (1 if self.base2 else 0) + (1 if self.base3 else 0) + 1
                self.our_score += pts
                self.base1 = self.base2 = self.base3 = False
                self.update_live_scoreboard(run=pts)
                self.game_log.append(log_prefix + match_msg + f"🔥 대폭발 완벽한 손맛!! 실투를 그대로 정타로 연결해 담장 밖 백스크린을 부숴버리는 대형 {pts}점 홈런!!")
            elif res == "HIT":
                gained = 0
                if self.base3: gained += 1
                if self.base2: gained += 1
                self.our_score += gained
                self.base3 = self.base1; self.base2 = False; self.base1 = True
                if gained > 0: self.update_live_scoreboard(run=gained)
                self.game_log.append(log_prefix + match_msg + f"🌟 라인드라이브성 단타! 깨끗한 좌전 안타가 터지며 베이스 러너들이 일제히 질주합니다! (+{gained}점)")
            elif res == "OUT":
                if self.base1 and self.out_count < 2 and random.random() < 0.30:
                    self.out_count += 2
                    self.base1 = False
                    self.game_log.append(log_prefix + f"😱 최악의 궤적 내야 땅볼! 적 2루수-유격수-1루수로 흐르는 KBO 표준 더블플레이 병살타 아웃.")
                elif self.base3 and self.out_count < 2 and random.random() < 0.45:
                    self.out_count += 1
                    self.base3 = False
                    self.our_score += 1
                    self.update_live_scoreboard(run=1)
                    self.game_log.append(log_prefix + f"🕊️ 깊숙한 외야 플라이 아웃! 그 사이 3루 주자 홈플레이트 슬라이딩 슬인! 1타점 희생타 작동 완료!")
                else:
                    self.out_count += 1
                    self.game_log.append(log_prefix + f"⚾ 중견수 정면 범타 플라이 아웃! 잘 맞은 타구였으나 수비 시프트 정면이었습니다.")
                self.check_three_out_change()

    def process_our_strikeout(self, current_batter: int) -> None:
        self.strike = 0; self.ball = 0
        self.my_batter_number = 1 if current_batter == 9 else current_batter + 1
        self.out_count += 1
        self.game_log.append(f"⚡ 루킹 삼진 아웃! {current_batter}번 타자, 투수의 낙차 큰 브레이킹 볼에 꼼짝 못 하고 배트를 둔 채 돌아섭니다.")
        self.check_three_out_change()

    def process_our_walk(self, current_batter: int) -> None:
        self.strike = 0; self.ball = 0
        self.my_batter_number = 1 if current_batter == 9 else current_batter + 1
        self.game_log.append(f"🚶‍♂️ 출루 성공! {current_batter}번 타자, 끈질긴 풀카운트 싸움 끝에 귀중한 볼넷을 골라 걸어 나갑니다.")
        if self.base1 and self.base2 and self.base3:
            self.our_score += 1
            self.update_live_scoreboard(run=1)
        elif self.base1 and self.base2: self.base3 = True
        elif self.base1: self.base2 = True
        else: self.base1 = True

    def check_three_out_change(self) -> None:
        if self.out_count >= 3:
            self.game_log.append("📢 쓰리아웃 체인지! 공수 교대합니다. 장비를 챙겨 마운드와 타석을 체인지합니다.")
            if self.inning >= 9 and self.phase == "초":
                if self.get_away_score() < self.get_home_score():
                    self.end_kbo_game()
                    return
            self.next_phase()

# =====================================================================
# [FRONTEND RENDERER] 4. Streamlit UI 대시보드 무손실 완벽 렌더러
# =====================================================================
def main() -> None:
    st.markdown("""
        <style>
        .stButton>button { width: 100%; margin-bottom: 8px; font-size: 16px !important; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("⚾ KBO 프로 야구 정통 시뮬레이터 Ver 4.0")
    st.caption("Riot/NC 아키텍처 규격 / 10x10 가변 상성 행렬 주사위 / assets 파일 스트림 탑재")

    # 📜 [패치 코어] 깃허브 assets/team_stories.txt 동적 버퍼 리더기
    if st.button("📜 깃허브 자산(assets/team_stories.txt) 연동 열람"):
        st.session_state.show_stories = True

    if st.session_state.get("show_stories", False):
        file_path = "assets/team_stories.txt"
        st.markdown("---")
        st.subheader("🕵️‍♂️ 깃허브 저장소 assets 로드 데이터")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                st.text_area("팀별 기밀 설정 스토리지 뷰어", value=f.read(), height=250, disabled=True)
        else:
            # 프로 규격의 폴백 리얼리티 스트링 주입
            fallback_narrative = (
                "📍 [SERVER NOTICE] assets/team_stories.txt 자산이 로컬 경로에 유실되었습니다.\n"
                "대기업 롤서버 아키텍처 폴백 시스템 가동 -> 임시 인메모리 데이터를 안전하게 렌더링합니다.\n\n"
                "- 레드 파이어스: 1982년 원년 창단 구단, 거친 기동력 서사.\n"
                "- 블루 웨이브스: 묵직한 정통파 마운드 중심의 왕조 구축 서사."
            )
            st.text_area("임시 캐시 레이어 데이터 (폴백 가동)", value=fallback_narrative, height=250, disabled=True)
        if st.button("❌ 자산 뷰어 격리 닫기"):
            st.session_state.show_stories = False
            st.rerun()
        st.markdown("---")

    # 📊 [패치 코어] 10x10 상성 대장부 데이터프레임 매핑 시각화 구역
    if "show_matrix" not in st.session_state: st.session_state.show_matrix = False
    if st.button("📊 하이퍼 10x10 팀별 가변 상성 매트릭스 개방"): st.session_state.show_matrix = True

    if st.session_state.show_matrix:
        st.markdown("---")
        st.subheader("📊 10대 구단 프로 상성 대장부 (세로: 공격팀 / 가로: 수비팀)")
        df_matrix = pd.DataFrame.from_dict(MATCHUP_MATRIX, orient='index', columns=MATRIX_COLUMNS)
        
        def style_matrix_cells(val: str) -> str:
            if val == "우세": return "background-color: #1b5e20; color: #ccff90; font-weight: bold;"
            elif val == "열세": return "background-color: #b71c1c; color: #ff8a80; font-weight: bold;"
            elif val == "X": return "background-color: #424242; color: #ffffff; text-align: center; font-weight: bold;"
            return "background-color: #f5f5f5; color: #212121;"

        try: st.dataframe(df_matrix.style.map(style_matrix_cells), use_container_width=True)
        except AttributeError: st.dataframe(df_matrix.style.applymap(style_matrix_cells), use_container_width=True)
        
        if st.button("❌ 상성 매트릭스 패널 닫기"):
            st.session_state.show_matrix = False; st.rerun()
        st.markdown("---")

    if "full_kbo_engine" not in st.session_state: st.session_state.full_kbo_engine = None

    if st.session_state.full_kbo_engine is None:
        st.markdown("### 🏟 *공식 프로 매치 메이킹 차원 문 전개*")
        my_team = st.selectbox("감독님이 플레이어 진영으로 지휘할 구단 선택:", list(TEAMS.keys()))
        enemy_pool = [t for t in TEAMS.keys() if t != my_team]
        
        if st.button("KBO 공식 정규 시즌 매치 스타트 🎟️", type="primary"):
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
                if st.button("🔄 [벤치 사인] 불펜 투수 전격 교체"): game.change_my_pitcher(); st.rerun()
        with col2:
            st.markdown(f"<h3 style='text-align: center; color: #E63946;'>{game.inning}회{game.phase}</h3>", unsafe_allow_html=True)
            current_is_our_turn = (not game.is_home_team and game.phase == "초") or (game.is_home_team and game.phase == "말")
            st.markdown(f"<p style='text-align: center; font-size:12px; font-weight:bold;'>{'[공격 작전 지시]' if current_is_our_turn else '[실시간 수비 방어]'}</p>", unsafe_allow_html=True)
        with col3:
            st.metric(label=f"상대 팀 {game.enemy_emoji}", value=f"{game.enemy_score} 점")
            st.caption(f"🥎 투수: {p_en.name} ({p_en.role}) | 체력: {p_en.stamina}/{p_en.max_stamina} | 투구: {game.enemy_total_pitches}구")

        st.divider()

        away_team_name = game.enemy_team if game.is_home_team else game.my_team
        home_team_name = game.my_team if game.is_home_team else game.enemy_team

        scoreboard_layout = {
            "KBO BOARD": [f"🚌 {away_team_name}", f"🏟️ {home_team_name}"],
            "1": [game.away_inning_scores[0], game.home_inning_scores[0]],
            "2": [game.away_inning_scores[1], game.home_inning_scores[1]],
            "3": [game.away_inning_scores[2], game.home_inning_scores[2]],
            "4": [game.away_inning_scores[3], game.home_inning_scores[3]],
            "5": [game.away_inning_scores[4], game.home_inning_scores[4]],
            "6": [game.away_inning_scores[5], game.home_inning_scores[5]],
            "7": [game.away_inning_scores[6], game.home_inning_scores[6]],
            "8": [game.away_inning_scores[7], game.home_inning_scores[7]],
            "9": [game.away_inning_scores[8], game.home_inning_scores[8]],
            "10": [game.away_inning_scores[9], game.home_inning_scores[9]],
            "11": [game.away_inning_scores[10], game.home_inning_scores[10]],
            "12": [game.away_inning_scores[11], game.home_inning_scores[11]],
            "R": [game.get_away_score(), game.get_home_score()]
        }
        st.table(pd.DataFrame(scoreboard_layout).set_index("KBO BOARD"))

        if game.game_over:
            st.success(game.game_result_msg)
            if st.button("정규 매치 새로 개시하기 🔄", type="primary"):
                st.session_state.full_kbo_engine = None; st.rerun()
        else:
            cz1, cz2 = st.columns(2)
            with cz1:
                st.markdown("### 📊 실시간 카운트 상황")
                st.markdown(f"* **아웃(Out):** {'🔴' * game.out_count}{'⚪' * (3-game.out_count)}")
                st.markdown(f"* **스트라이크(Strike):** {'🔥' * game.strike}{'⚪' * (3-game.strike)}")
                st.markdown(f"* **볼(Ball):** {'🟢' * game.ball}{'⚪' * (4-game.ball)}")
                st.markdown(f"* **현재 상성 버프:** `{(game.get_matchup_modifier(game.my_team, game.enemy_team) * 100):+.1f}%` 적용 중")
            with cz2:
                b1_ico = "🏃" if game.base1 else "◯"
                b2_ico = "🏃" if game.base2 else "◯"
                b3_ico = "🏃" if game.base3 else "◯"
                st.code(f"   [{b2_ico}] 2루\n[{b3_ico}] 3루   [{b1_ico}] 1루\n     [X] 타석", language="text")

            st.divider()

            if current_is_our_turn:
                st.markdown("### 📢 공격 지시 작션 사인")
                bcol1, bcol2, bcol3, bcol4 = st.columns(4)
                with bcol1:
                    if st.button("💥 1. 입자 붕괴 장타 (풀스윙)"): game.play_turn(1); st.rerun()
                with bcol2:
                    if st.button("🌟 2. 정밀 배트 컨트롤 (밀어치기)"): game.play_turn(2); st.rerun()
                with bcol3:
                    if st.button("👀 3. 인과율 선구안 (거르기)"): game.play_turn(3); st.rerun()
                with bcol4:
                    if st.button("🏃‍♂️ 4. 초질량 기습 주루 (도루)"): game.trigger_steal(); st.rerun()
            else:
                st.markdown("### 🛡️ 수비 방어 작전 사인")
                if st.button("⚾ 다음 공 1구 투구 지시 (Real-time Pitch)", type="primary"):
                    game.play_defense_one_pitch(); st.rerun()

        st.divider()
        st.markdown("### 🎙️ 공식 KBO 경기 중계 리얼타임 일지")
        for log in reversed(game.game_log[-6:]): st.write(log)

if __name__ == "__main__":
    main()
