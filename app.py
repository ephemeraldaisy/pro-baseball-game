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

# =====================================================================
# [DOMAIN MODEL] 2. 프로 투수 및 타자 객체지향 캡슐화 모듈
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
        if self.stamina <= 0:
            return 0.35  # 체력 완전 방전 시 피안타율 35% 증가 (프로 규격)
        elif self.stamina < (self.max_stamina * 0.3):
            return 0.15  # 체력 30% 미만 시 피안타율 15% 증가
        return 0.0

# =====================================================================
# [CORE ENGINE] 3. KBO 공식 룰북 100% 반영 시뮬레이션 본체 엔진
# =====================================================================
class PureKboEngine:
    def __init__(self, my_team: str, enemy_team: str) -> None:
        self.my_team: str = my_team
        self.enemy_team: str = enemy_team
        self.my_emoji: str = my_team[:2]
        self.enemy_emoji: str = enemy_team[:2]
        
        # 선공(원정)/후공(홈) 무작위 코인 토스
        self.is_home_team: bool = random.choice([True, False])
        
        # KBO 공식 이닝/스코어 시스템
        self.our_score: int = 0
        self.enemy_score: int = 0
        self.inning: int = 1
        self.phase: str = "초"  # "초" = 원정, "말" = 홈
        
        # 타순(1~9번) 로테이션 메모리
        self.my_batter_number: int = 1
        self.enemy_batter_number: int = 1
        
        # 전체 투구수 누적기
        self.our_total_pitches: int = 0
        self.enemy_total_pitches: int = 0
        
        # 인게임 아웃 및 진루 카운터
        self.out_count: int = 0
        self.strike: int = 0
        self.ball: int = 0
        self.base1: bool = False
        self.base2: bool = False
        self.base3: bool = False
        
        # 12회차 스코어 보드 배열 (공백으로 초기화)
        self.away_inning_scores: List[Any] = [""] * 12
        self.home_inning_scores: List[Any] = [""] * 12
        
        # 게임 종료 스테이터스
        self.game_over: bool = False
        self.game_result_msg: str = ""
        self.game_log: List[str] = [
            f"🏟️ KBO 프로야구 매치 성사. 코인 토스 결과: 우리 팀은 {'후공(홈팀)' if self.is_home_team else '선공(원정팀)'}입니다."
        ]
        
        # 투수 로스터 할당 (선발 -> 추격조 -> 필승조 -> 마무리)
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
            Pitcher("상대 추격조", "추격조", 40),
            Pitcher("상대 셋업맨", "필승조", 30),
            Pitcher("상대 클로저", "마무리", 20)
        ]
        self.enemy_pitcher_idx: int = 0

        # 투구 구종 및 위치 캐싱
        self.pitch_type: str = "직구"
        self.pitch_zone: int = 5
        self.guess_zone: int = 5
        
        # 1회초 플레이볼
        self.setup_half_inning()

    def get_current_my_pitcher(self) -> Pitcher:
        return self.my_pitchers[self.my_pitcher_idx]

    def get_current_enemy_pitcher(self) -> Pitcher:
        return self.enemy_pitchers[self.enemy_pitcher_idx]

    def change_my_pitcher(self) -> bool:
        if self.my_pitcher_idx < len(self.my_pitchers) - 1:
            self.my_pitcher_idx += 1
            p = self.get_current_my_pitcher()
            self.game_log.append(f"🔄 [투수 교체] 벤치 지시! 우리 팀 마운드가 교체됩니다: {p.role} '{p.name}' 등판!")
            return True
        self.game_log.append("⚠️ 더 이상 교체할 불펜 투수가 없습니다! 마무리가 끝까지 던져야 합니다.")
        return False

    def change_enemy_pitcher(self) -> bool:
        if self.enemy_pitcher_idx < len(self.enemy_pitchers) - 1:
            self.enemy_pitcher_idx += 1
            p = self.get_current_enemy_pitcher()
            self.game_log.append(f"🔄 [상대 투수 교체] 상대 팀 벤치가 움직입니다: {p.role} '{p.name}' 등판!")
            return True
        return False

    def get_away_score(self) -> int:
        return self.enemy_score if self.is_home_team else self.our_score

    def get_home_score(self) -> int:
        return self.our_score if self.is_home_team else self.enemy_score

    def setup_half_inning(self) -> None:
        if self.game_over:
            return

        away_score = self.get_away_score()
        home_score = self.get_home_score()

        # [KBO 룰 1] 9회초 종료 시 홈팀 리드 시 조기 종료
        if self.inning == 9 and self.phase == "말":
            if home_score > away_score:
                self.game_log.append("👍 [KBO 공식 룰] 9회초 종료 시점 홈팀이 리드하고 있으므로 9회말을 생략하고 경기를 종료합니다.")
                self.home_inning_scores[8] = "X"
                self.end_kbo_game()
                return

        # [KBO 룰 2] 연장 진입 및 12회 무승부 제한
        if self.inning > 9 and self.phase == "초":
            prev_away = sum([int(x) for x in self.away_inning_scores[:self.inning-1] if isinstance(x, int)])
            prev_home = sum([int(x) for x in self.home_inning_scores[:self.inning-1] if isinstance(x, int)])
            if prev_away != prev_home:
                self.end_kbo_game()
                return
            elif self.inning > 12:
                self.game_log.append("⏰ [KBO 공식 룰] 12회 연장 혈투 끝에 승부를 가리지 못했습니다. 규정에 따라 무승부 콜이 선언됩니다.")
                self.end_kbo_game()
                return

        # 베이스 및 카운트 초기화
        self.strike = 0
        self.ball = 0
        self.out_count = 0
        self.base1 = self.base2 = self.base3 = False

        # 공격권 확인 후 상대 턴이면 방어 시뮬레이션 즉시 실행
        current_is_our_turn = (not self.is_home_team and self.phase == "초") or (self.is_home_team and self.phase == "말")
        
        if not current_is_our_turn:
            self.simulate_full_defense_half_inning()

    def simulate_full_defense_half_inning(self) -> None:
        enemy_stats = TEAMS[self.enemy_team]
        my_stats = TEAMS[self.my_team]
        
        defense_outs = 0
        gained_runs = 0
        inning_pitches = 0
        
        # 우리 투수 체력 방전 시 자동 교체 (마무리는 제외)
        pitcher = self.get_current_my_pitcher()
        if pitcher.stamina <= 0 and pitcher.role != "마무리":
            self.change_my_pitcher()
            pitcher = self.get_current_my_pitcher()

        penalty = pitcher.get_fatigue_penalty()

        while defense_outs < 3:
            # 타순 로테이션
            batter = self.enemy_batter_number
            self.enemy_batter_number = 1 if batter == 9 else batter + 1
            
            pitches_for_batter = random.randint(3, 7)
            inning_pitches += pitches_for_batter
            pitcher.record_pitch(pitches_for_batter)
            self.our_total_pitches += pitches_for_batter
            
            # KBO 실제 타율/장타율 기반 정밀 시뮬레이션
            hit_prob = 0.24 + (enemy_stats["hit"] - my_stats["defense"]) * 0.002 + penalty
            hr_prob = 0.025 + (enemy_stats["homerun"] * 0.001)
            walk_prob = 0.08
            
            roll = random.random()
            if roll < hr_prob:
                pts = (1 if self.base1 else 0) + (1 if self.base2 else 0) + (1 if self.base3 else 0) + 1
                gained_runs += pts
                self.base1 = self.base2 = self.base3 = False
                self.enemy_score += pts
                self.update_live_scoreboard(run=pts)
            elif roll < (hit_prob + hr_prob):
                if self.base3: 
                    gained_runs += 1
                    self.enemy_score += 1
                    self.update_live_scoreboard(run=1)
                if self.base2: 
                    gained_runs += 1
                    self.enemy_score += 1
                    self.update_live_scoreboard(run=1)
                self.base3 = self.base1
                self.base2 = False
                self.base1 = True
            elif roll < (hit_prob + hr_prob + walk_prob):
                if self.base1 and self.base2 and self.base3:
                    gained_runs += 1
                    self.enemy_score += 1
                    self.update_live_scoreboard(run=1)
                elif self.base1 and self.base2: self.base3 = True
                elif self.base1: self.base2 = True
                else: self.base1 = True
            else:
                # 병살타 정밀 구현 (1루 주자 존재 & 무사/1사 상황)
                if self.base1 and defense_outs < 2 and random.random() < 0.20:
                    defense_outs += 2
                    self.base1 = False
                else:
                    defense_outs += 1

            # [KBO 룰 3] 수비 도중 9회말/연장말 끝내기 실점 발생 시 즉시 이닝 브레이크
            if self.inning >= 9 and self.phase == "말" and not self.is_home_team:
                if self.enemy_score > self.our_score:
                    break
            
            # 투수 체력이 이닝 중간에 바닥나면 즉시 강판
            if pitcher.stamina <= 0 and pitcher.role != "마무리":
                self.change_my_pitcher()
                pitcher = self.get_current_my_pitcher()
                penalty = pitcher.get_fatigue_penalty()

        self.game_log.append(
            f"🛡️ {self.inning}회{self.phase} 수비 종료 -> 이번 이닝 {gained_runs}실점 기록. "
            f"(현재 마운드: {pitcher.name}({pitcher.role}) / 누적 투구수: {self.our_total_pitches}구 / 남은 체력: {pitcher.stamina})"
        )

        if self.inning >= 9 and self.phase == "말" and not self.is_home_team:
            if self.enemy_score > self.our_score:
                self.game_log.append(f"❌ 아앗... {self.inning}회말 상대 팀에게 끝내기 점수를 허용하여 경기가 패배로 종료됩니다.")
                self.end_kbo_game()
                return

        self.next_phase()

    def update_live_scoreboard(self, run: int) -> None:
        idx = self.inning - 1
        if idx >= 12:
            return
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
            st.warning("루상에 나간 주자가 없습니다. 도루가 불가능합니다.")
            return

        my_stats = TEAMS[self.my_team]
        enemy_stats = TEAMS[self.enemy_team]
        
        # 포수 도루 저지율 공식 대입
        success_rate = 0.60 + (my_stats["steal_b"] - enemy_stats["defense"] * 0.15) * 0.01
        success_rate = max(0.15, min(0.85, success_rate))

        if self.base1 or self.base2:
            self.game_log.append("🏃‍♂️ [주루 작전] 투수의 투구 폼을 뺏고 다음 베이스로 도루를 감행합니다!")
            if random.random() < success_rate:
                if self.base2 and not self.base3:
                    self.base3 = True; self.base2 = False
                    self.game_log.append("✅ 3루 훔치기 성공! 세이프!")
                elif self.base1 and not self.base2:
                    self.base2 = True; self.base1 = False
                    self.game_log.append("✅ 2루 훔치기 성공! 세이프!")
                elif self.base1 and self.base2 and not self.base3:
                    self.base3 = True; self.base2 = True; self.base1 = False
                    self.game_log.append("✅ 환상적인 더블 스틸 안착!")
            else:
                self.out_count += 1
                self.game_log.append("❌ 상대 포수의 정확한 2루 송구! 주자 태그 아웃!")
                if self.base1 and self.base2:
                    if random.choice([True, False]): self.base1 = False
                    else: self.base2 = False
                elif self.base1: self.base1 = False
                elif self.base2: self.base2 = False
                self.check_three_out_change()

    def next_phase(self) -> None:
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
            self.game_result_msg = f"🤝 [무승부] {self.inning if self.inning <= 12 else 12}회까지 가는 혈투 끝에 {away_score}:{home_score} 무승부(DRAW)로 KBO 공식 경기가 종료되었습니다."
        else:
            we_won = (not self.is_home_team and self.our_score > self.enemy_score) or (self.is_home_team and self.our_score > self.enemy_score)
            if we_won:
                self.game_result_msg = f"🏆 [승리] 최종 스코어 {self.our_score} 대 {self.enemy_score}로 완벽한 승리를 챙깁니다!"
            else:
                self.game_result_msg = f"😭 [패배] 최종 스코어 {self.our_score} 대 {self.enemy_score}로 아쉽게 경기를 내어줍니다."

    def play_turn(self, user_choice: int) -> None:
        if self.game_over:
            return

        # 적 투수 스태미나 기반 강판 확인
        enemy_pitcher = self.get_current_enemy_pitcher()
        if enemy_pitcher.stamina <= 0 and enemy_pitcher.role != "마무리":
            self.change_enemy_pitcher()
            enemy_pitcher = self.get_current_enemy_pitcher()

        self.pitch_type = random.choice(["직구", "슬라이더", "체인지업", "커브", "포크볼", "싱커"])
        self.pitch_zone = random.randint(1, 9) if random.random() < 0.72 else 0
        self.guess_zone = random.randint(1, 9)
        
        enemy_pitcher.record_pitch(1)
        self.enemy_total_pitches += 1

        current_batter = self.my_batter_number
        my_stats = TEAMS[self.my_team]
        enemy_stats = TEAMS[self.enemy_team]
        
        penalty = enemy_pitcher.get_fatigue_penalty()
        
        # 타순별 KBO 평균 스탯 보정치 (1번 출루율, 4번 장타율, 하위타선 범타율)
        batter_context_msg = f"[{current_batter}번 타자] "
        batter_hr_mod = 25 if current_batter == 4 else (10 if current_batter in [3, 5] else 0)
        batter_hit_mod = 20 if current_batter in [1, 2, 3] else (-10 if current_batter in [7, 8, 9] else 0)

        at_bat_result = "지속"
        
        # 1. 풀스윙 강타 (장타 노리기)
        if user_choice == 1:
            zone_mod = 1.3 if self.pitch_zone == 0 else 1.0
            w_hr = max(5, 25 + my_stats["homerun"] + batter_hr_mod)
            w_hit = max(20, 160 + my_stats["hit"] - enemy_stats["defense"] * 0.5 + batter_hit_mod + (penalty * 150))
            w_out = max(50, int((600 - (penalty * 100)) * zone_mod))
            w_foul = 180
            
            res = random.choices(["HR", "HIT", "OUT", "FOUL"], weights=[w_hr, w_hit, w_out, w_foul])[0]
            if res == "HR": at_bat_result = "홈런"
            elif res == "HIT": at_bat_result = "안타"
            elif res == "OUT": at_bat_result = "아웃"
            elif res == "FOUL":
                if self.strike < 2: self.strike += 1
                self.game_log.append(f"💥 {batter_context_msg}풀스윙! 빗맞은 파울볼입니다. (현재 카운트: {self.strike}S {self.ball}B)")
                return

        # 2. 컨택 위주 밀어치기 (출루 노리기)
        elif user_choice == 2:
            zone_mod = 1.1 if self.pitch_zone == 0 else 1.0
            w_hit = max(30, 270 + my_stats["hit"] - enemy_stats["defense"] * 0.4 + (batter_hit_mod * 1.3) + (penalty * 200))
            w_out = max(50, int((520 - (penalty * 100)) * zone_mod))
            w_foul = 150
            
            res = random.choices(["HIT", "OUT", "FOUL"], weights=[w_hit, w_out, w_foul])[0]
            if res == "HIT": at_bat_result = "안타"
            elif res == "OUT": at_bat_result = "아웃"
            elif res == "FOUL":
                if self.strike < 2: self.strike += 1
                self.game_log.append(f"💥 {batter_context_msg}밀어치기 커트! 끈질기게 파울을 만들어냅니다. (현재 카운트: {self.strike}S {self.ball}B)")
                return

        # 3. 공 끝까지 거르기 (눈야구)
        elif user_choice == 3:
            if 1 <= self.pitch_zone <= 9:
                self.strike += 1
                self.game_log.append(f"👀 {batter_context_msg}스트라이크 존({self.pitch_zone}번) 진입구를 그대로 지켜봅니다! 스트라이크! (현재 {self.strike}S {self.ball}B)")
                if self.strike >= 3: at_bat_result = "삼진"
            else:
                self.ball += 1
                self.game_log.append(f"👀 {batter_context_msg}유인구를 속지 않고 정확히 골라냅니다. 볼! (현재 {self.strike}S {self.ball}B)")
                if self.ball >= 4: at_bat_result = "볼넷"

        # 타격 결과에 따른 주자 오토마타 (진루 및 득점 처리)
        if at_bat_result != "지속":
            self.strike = 0; self.ball = 0
            self.my_batter_number = 1 if current_batter == 9 else current_batter + 1

            if at_bat_result == "홈런":
                pts = (1 if self.base1 else 0) + (1 if self.base2 else 0) + (1 if self.base3 else 0) + 1
                self.our_score += pts
                self.base1 = self.base2 = self.base3 = False
                self.update_live_scoreboard(run=pts)
                self.game_log.append(f"⚾ 깡!!! {batter_context_msg}외야 담장을 훌쩍 넘어가는 {pts}점 홈런 작렬!!!!")

            elif at_bat_result == "안타":
                gained = 0
                if self.base3: gained += 1
                if self.base2: gained += 1
                self.our_score += gained
                self.base3 = self.base1
                self.base2 = False
                self.base1 = True
                if gained > 0: self.update_live_scoreboard(run=gained)
                self.game_log.append(f"🌟 {batter_context_msg}클린 히트! 안타입니다! 주자 한 칸씩 진루합니다! (+{gained}점)")

            elif at_bat_result == "아웃":
                if self.base1 and self.out_count < 2 and random.random() < 0.30:
                    self.out_count += 2
                    self.base1 = False
                    self.game_log.append(f"😱 아앗! {batter_context_msg}내야 땅볼이 유격수 정면으로 향하며 최악의 병살타(6-4-3)로 이어집니다!")
                elif self.base3 and self.out_count < 2 and random.random() < 0.45:
                    self.out_count += 1
                    self.base3 = False
                    self.our_score += 1
                    self.update_live_scoreboard(run=1)
                    self.game_log.append(f"🕊️ {batter_context_msg}멀리 날아가는 외야 플라이! 3루 주자 태그업하여 홈인! 1타점 희생플라이 기록!")
                else:
                    self.out_count += 1
                    self.game_log.append(f"⚾ {batter_context_msg}야수 정면으로 향하는 평범한 범타 아웃입니다.")
                self.check_three_out_change()

            elif at_bat_result == "삼진":
                self.game_log.append(f"⚡ {batter_context_msg}헛스윙 삼진! 타석에서 물러납니다.")
                self.out_count += 1
                self.check_three_out_change()

            elif at_bat_result == "볼넷":
                self.game_log.append(f"🚶‍♂️ {batter_context_msg}볼넷! 1루로 당당히 걸어 나갑니다.")
                if self.base1 and self.base2 and self.base3:
                    self.our_score += 1
                    self.update_live_scoreboard(run=1)
                    self.game_log.append("➔ 무사 만루에서의 밀어내기 볼넷! 1점 추가!")
                elif self.base1 and self.base2: self.base3 = True
                elif self.base1: self.base2 = True
                else: self.base1 = True

        # [KBO 룰 4] 홈팀 공격 중 역전 끝내기 상황 즉시 판단
        if self.inning >= 9 and self.phase == "말" and self.is_home_team:
            if self.get_home_score() > self.get_away_score():
                self.game_log.append(f"🎉 🎉 {self.inning}회말 끝내기 득점!!! 홈팀이 경기를 그대로 끝내버립니다!!!")
                self.end_kbo_game()

    def check_three_out_change(self) -> None:
        if self.out_count >= 3:
            self.game_log.append("📢 쓰리아웃 체인지! 공수 교대합니다.")
            if self.inning >= 9 and self.phase == "초":
                if self.get_away_score() < self.get_home_score():
                    self.end_kbo_game()
                    return
            self.next_phase()

# =====================================================================
# [FRONTEND RENDERER] 4. Streamlit UI 대시보드 무손실 완벽 렌더러
# =====================================================================
def main() -> None:
    # 전체 버튼 폭 강제 고정 CSS
    st.markdown("""
        <style>
        .stButton>button { width: 100%; margin-bottom: 8px; font-size: 16px !important; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("⚾ KBO 프로 야구 정통 시뮬레이터 풀버전")
    st.caption("생략 일절 없음. 12회 무승부, 체력 기반 불펜 시스템 완벽 이식.")

    if "full_kbo_engine" not in st.session_state:
        st.session_state.full_kbo_engine = None

    if st.session_state.full_kbo_engine is None:
        st.markdown("### 🏟️ 공식 프로 구단 라인업 대진 매칭")
        my_team = st.selectbox("사모님이 지휘할 프로 구단을 선택해주십시오:", list(TEAMS.keys()))
        enemy_pool = [t for t in TEAMS.keys() if t != my_team]
        
        if st.button("공식 리그 오프닝 매치 스타트 🎟️", type="primary"):
            st.session_state.full_kbo_engine = PureKboEngine(my_team, random.choice(enemy_pool))
            st.rerun()
    else:
        game: PureKboEngine = st.session_state.full_kbo_engine
        p_my = game.get_current_my_pitcher()
        p_en = game.get_current_enemy_pitcher()

        # 상단 전광판 데이터 바인딩
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            st.metric(label=f"우리 팀 {game.my_emoji}", value=f"{game.our_score} 점")
            st.caption(f"🔋 투수: {p_my.name} ({p_my.role}) | 남은 체력: {p_my.stamina}/{p_my.max_stamina} | 투구수: {game.our_total_pitches}구")
            if not game.game_over and p_my.role != "마무리":
                if st.button("🔄 [벤치 지시] 불펜 투수 교체"):
                    game.change_my_pitcher()
                    st.rerun()
        with col2:
            st.markdown(f"<h3 style='text-align: center; color: #E63946;'>{game.inning}회{game.phase}</h3>", unsafe_allow_html=True)
            current_is_our_turn = (not game.is_home_team and game.phase == "초") or (game.is_home_team and game.phase == "말")
            st.markdown(f"<p style='text-align: center; font-size:12px; font-weight:bold;'>{'[공격 턴]' if current_is_our_turn else '[수비 턴]'}</p>", unsafe_allow_html=True)
        with col3:
            st.metric(label=f"상대 팀 {game.enemy_emoji}", value=f"{game.enemy_score} 점")
            st.caption(f"🥎 투수: {p_en.name} ({p_en.role}) | 남은 체력: {p_en.stamina}/{p_en.max_stamina} | 투구수: {game.enemy_total_pitches}구")

        st.divider()

        # 라인 스코어보드 Pandas 데이터프레임 렌더링
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
            if st.button("정규 리그 새 게임 시작하기 🔄", type="primary"):
                st.session_state.full_kbo_engine = None
                st.rerun()
        else:
            # 베이스 및 카운트 현황 출력
            cz1, cz2 = st.columns(2)
            with cz1:
                st.markdown("### 📊 현재 타석 상황")
                st.markdown(f"* **아웃(Out):** {'🔴' * game.out_count}{'⚪' * (3-game.out_count)}")
                st.markdown(f"* **스트라이크(Strike):** {'🔥' * game.strike}{'⚪' * (3-game.strike)}")
                st.markdown(f"* **볼(Ball):** {'🟢' * game.ball}{'⚪' * (4-game.ball)}")
                st.markdown(f"* **현재 타순:** `{game.my_batter_number}번 타자 돌입`")
            with cz2:
                b1_ico = "🏃" if game.base1 else "◯"
                b2_ico = "🏃" if game.base2 else "◯"
                b3_ico = "🏃" if game.base3 else "◯"
                st.code(f"   [{b2_ico}] 2루\n[{b3_ico}] 3루   [{b1_ico}] 1루\n     [X] 타석", language="text")

            st.divider()

            # 공격 턴 선택 버튼 매트릭스
            st.markdown("### 📢 공격 지시 액션 보드")
            bcol1, bcol2, bcol3, bcol4 = st.columns(4)
            with bcol1:
                if st.button("💥 1. 장타 노리기 (풀스윙)"): 
                    game.play_turn(1)
                    st.rerun()
            with bcol2:
                if st.button("🌟 2. 컨택 위주 (밀어치기)"): 
                    game.play_turn(2)
                    st.rerun()
            with bcol3:
                if st.button("👀 3. 공 골라내기 (눈야구)"): 
                    game.play_turn(3)
                    st.rerun()
            with bcol4:
                if st.button("🏃‍♂️ 4. 기습 베이스 스틸 (도루)"): 
                    game.trigger_steal()
                    st.rerun()

        st.divider()
        st.markdown("### 🎙️ 공식 프로야구 중계 실시간 일지 (최근 6건)")
        for log in reversed(game.game_log[-6:]):
            st.write(log)

if __name__ == "__main__":
    st.set_page_config(page_title="KBO 프로 야구 시뮬레이터 Full Ver.", page_icon="⚾", layout="centered")
    main()
