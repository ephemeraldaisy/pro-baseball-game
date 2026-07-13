import random
import os
import pandas as pd
import streamlit as st
from typing import Dict, Any, List, Optional, Tuple

# =====================================================================
# [DOMAIN MODEL] 1. 구단 상수 정의 및 데이터 구조체
# =====================================================================
TEAMS: Dict[str, Dict[str, int]] = {
    "🔴 레드 파이어스": {"homerun": 5, "hit": 30, "out": -10, "strike_p": -30, "ball_p": 30, "steal_b": 25},
    "🔵 블루 웨이브스": {"homerun": 20, "hit": 40, "out": -20, "strike_p": 10, "ball_p": -10, "steal_b": -10},
    "🟢 그린 몬스터즈": {"homerun": 60, "hit": -20, "out": 20, "strike_p": 50, "ball_p": -50, "steal_b": -20},
    "🟡 옐로우 타이거즈": {"homerun": 30, "hit": 10, "out": -10, "strike_p": 20, "ball_p": -20, "steal_b": 15},
    "🟣 퍼플 바이퍼스": {"homerun": -30, "hit": 20, "out": -30, "strike_p": -50, "ball_p": 80, "steal_b": 5},
    "🟠 오렌지 자이언츠": {"homerun": 25, "hit": 0, "out": 10, "strike_p": 10, "ball_p": -10, "steal_b": -15},
    "🟤 브라운 베어스": {"homerun": 10, "hit": 20, "out": -10, "strike_p": -10, "ball_p": 10, "steal_b": 10},
    "⚪ 화이트 이글스": {"homerun": -10, "hit": 50, "out": -20, "strike_p": 10, "ball_p": 0, "steal_b": 5},
    "⚫ 블랙 나이츠": {"homerun": 0, "hit": 10, "out": -20, "strike_p": -20, "ball_p": 20, "steal_b": 0},
    "💖 핑크 돌핀스": {"homerun": 40, "hit": 30, "out": 10, "strike_p": 30, "ball_p": -20, "steal_b": 20}
}

MATCHUP_MATRIX: Dict[str, List[str]] = {
    "🔴레드":   ["노랑", "연두", "초록", "노랑", "연두", "오렌지", "연두", "빨강", "오렌지", "노랑"],
    "🔵블루":   ["오렌지", "노랑", "연두", "오렌지", "빨강", "노랑", "오렌지", "연두", "초록", "연두"],
    "🟢그린":   ["빨강", "오렌지", "노랑", "오렌지", "연두", "초록", "오렌지", "노랑", "연두", "빨강"],
    "🟡옐로우": ["노랑", "연두", "연두", "노랑", "오렌지", "연두", "초록", "오렌지", "빨강", "오렌지"],
    "🟣퍼플":   ["오렌지", "초록", "오렌지", "연두", "노랑", "연두", "노랑", "오렌지", "연두", "빨강"],
    "🟠오렌지": ["연두", "노랑", "빨강", "오렌지", "오렌지", "노랑", "연두", "초록", "노랑", "연두"],
    "🟤브라운": ["오렌지", "연두", "연두", "빨강", "노랑", "오렌지", "노랑", "연두", "노랑", "초록"],
    "⚪화이트": ["초록", "오렌지", "노랑", "연두", "연두", "빨강", "오렌지", "노랑", "오렌지", "노랑"],
    "⚫블랙":   ["연두", "빨강", "오렌지", "초록", "오렌지", "노랑", "노랑", "연두", "노랑", "오렌지"],
    "💖핑크":   ["노랑", "오렌지", "초록", "연두", "초록", "오렌지", "빨강", "노랑", "연두", "노랑"]
}

MATRIX_COLUMNS: List[str] = ["🔴레드", "🔵블루", "🟢그린", "🟡옐로우", "🟣퍼플", "🟠오렌지", "🟤브라운", "⚪화이트", "⚫블랙", "💖핑크"]

# =====================================================================
# [CORE ENGINE] 2. 시뮬레이터 핵심 비즈니스 로직 클래스 (OOP)
# =====================================================================
class BaseballGameEngine:
    def __init__(self, my_team: str, enemy_team: str) -> None:
        self.my_team: str = my_team
        self.enemy_team: str = enemy_team
        self.my_emoji: str = my_team[:2]
        self.enemy_emoji: str = enemy_team[:2]
        
        # 진영 결정
        self.is_home_team: bool = random.choice([True, False])
        
        # 스코어 및 이닝 관리
        self.our_score: int = 0
        self.enemy_score: int = 0
        self.inning: int = 1
        self.phase: str = "초"  # "초" or "말"
        
        # 타순 및 투구수
        self.my_batter_number: int = 1
        self.our_total_pitches: int = 0
        self.enemy_total_pitches: int = 0
        
        # 카운트 및 주자 상황
        self.out_count: int = 0
        self.strike: int = 0
        self.ball: int = 0
        self.base1: bool = False
        self.base2: bool = False
        self.base3: bool = False
        
        # 스코어보드 어레이 (1~12회)
        self.away_inning_scores: List[Any] = [""] * 12
        self.home_inning_scores: List[Any] = [""] * 12
        
        # 시스템 상태
        self.game_over: bool = False
        self.game_result_msg: str = ""
        self.game_log: List[str] = [
            f"🪙 동전을 던져 진영을 결정했습니다! 우리 팀은 {'후공(홈팀)' if self.is_home_team else '선공(원정팀)'} 기라!"
        ]
        
        # 당해 턴 투구 정보 상태 저장
        self.pitch_type: str = "직구"
        self.pitch_zone: int = 5
        self.guess_zone: int = 5
        
        # 첫 이닝 빌드업 시작
        self.setup_half_inning()

    def check_cold_game(self) -> bool:
        score_gap = abs(self.our_score - self.enemy_score)
        if self.inning in [5, 6] and score_gap >= 10:
            self.game_result_msg = f"🚨 [COLD GAME] {self.inning}회 종료 시점 {score_gap}점 차로 콜드게임 선언!"
            self.end_game()
            return True
        elif self.inning in [7, 8] and score_gap >= 7:
            self.game_result_msg = f"🚨 [COLD GAME] {self.inning}회 종료 시점 {score_gap}점 차로 콜드게임 선언!"
            self.end_game()
            return True
        return False

    def setup_half_inning(self) -> None:
        if self.game_over:
            return

        # 연장전 종료 조건 체크
        if self.inning > 9 and self.phase == "초":
            if self.our_score != self.enemy_score:
                self.end_game()
                return

        # 콜드게임 규정 체크
        if self.check_cold_game():
            return

        # 9회말 조기 종료 고증 (우리가 홈팀인데 이미 이기고 있는 상태로 9회초 종료 시)
        if self.inning == 9 and self.phase == "말":
            if self.is_home_team and self.our_score > self.enemy_score:
                self.game_log.append("👍 9회초까지 이미 우리 팀이 이기고 있어 9회말 공격 없이 경기가 끝납니다! (9회말 X)")
                self.home_inning_scores[8] = "X"
                self.end_game()
                return

        # 카운트 및 주자 상황 초기화
        self.strike = 0
        self.ball = 0
        self.out_count = 0
        self.base1 = self.base2 = self.base3 = False

        # 현재 수비 턴 여부 연산
        current_is_our_turn = (not self.is_home_team and self.phase == "초") or (self.is_home_team and self.phase == "말")
        
        # 수비 시뮬레이션 알고리즘 엔진 작동
        if not current_is_our_turn:
            self.simulate_defense_half_inning()

    def simulate_defense_half_inning(self) -> None:
        enemy_buff = TEAMS.get(self.enemy_team, {"ball_p": 0, "out": 0})
        
        # 상성 매트릭스 다이스 매핑
        base_weights = [510, 240, 150, 70, 25, 5]
        
        is_enemy_dominant = (
            (self.enemy_team == "🔴 레드 파이어스" and self.my_team == "🟢 그린 몬스터즈") or
            (self.enemy_team == "🔵 블루 웨이브스" and self.my_team == "⚫ 블랙 나이츠") or
            (self.enemy_team == "🟢 그린 몬스터즈" and self.my_team == "🟠 오렌지 자이언츠") or
            (self.enemy_team == "🟡 옐로우 타이거즈" and self.my_team == "🟤 브라운 베어스") or
            (self.enemy_team == "🟣 퍼플 바이퍼스" and self.my_team == "🔵 블루 웨이브스") or
            (self.enemy_team == "🟠 오렌지 자이언츠" and self.my_team == "⚪ 화이트 이글스") or
            (self.enemy_team == "🟤 브라운 베어스" and self.my_team == "💖 핑크 돌핀스") or
            (self.enemy_team == "⚪ 화이트 이글스" and self.my_team == "🔴 레드 파이어스") or
            (self.enemy_team == "⚫ 블랙 나이츠" and self.my_team == "🟡 옐로우 타이거즈") or
            (self.enemy_team == "💖 핑크 돌핀스" and self.my_team == "🟣 퍼플 바이퍼스")
        )
        
        is_we_dominant = (
            (self.my_team == "🔴 레드 파이어스" and self.enemy_team == "🟢 그린 몬스터즈") or
            (self.my_team == "🔵 블루 웨이브스" and self.enemy_team == "⚫ 블랙 나이츠") or
            (self.my_team == "🟢 그린 몬스터즈" and self.enemy_team == "🟠 오렌지 자이언츠") or
            (self.my_team == "🟡 옐로우 타이거즈" and self.enemy_team == "🟤 브라운 베어스") or
            (self.my_team == "🟣 퍼플 바이퍼스" and self.enemy_team == "🔵 블루 웨이브스") or
            (self.my_team == "🟠 오렌지 자이언츠" and self.enemy_team == "⚪ 화이트 이글스") or
            (self.my_team == "🟤 브라운 베어스" and self.enemy_team == "💖 핑크 돌phin스") or
            (self.my_team == "⚪ 화이트 이글스" and self.enemy_team == "🔴 레드 파이어스") or
            (self.my_team == "⚫ 블랙 나이츠" and self.enemy_team == "🟡 옐로우 타이거즈") or
            (self.my_team == "💖 핑크 돌핀스" and self.enemy_team == "🟣 퍼플 바이퍼스")
        )

        if is_enemy_dominant:
            base_weights = [350, 280, 200, 110, 50, 10]
        elif is_we_dominant:
            base_weights = [680, 180, 90, 40, 10, 0]

        base_pts = random.choices([0, 1, 2, 3, 4, -1], weights=base_weights)[0]
        defense_type = "일반"
        def_log = ""

        if base_pts == -1:
            enemy_pts = random.randint(5, 10)
            def_log = f"😱 [🚨 메가 이닝 발생] 상대 팀 타선이 불타오릅니다! 난타전 끝에 {enemy_pts}실점..."
        else:
            enemy_pts = base_pts
            if enemy_pts == 0:
                defense_type = random.choice(["KKK", "일반", "병살"])
                if is_we_dominant and random.random() < 0.40:
                    defense_type = "KKK"
                
                if defense_type == "KKK":
                    def_log = "🛡️ 마운드의 우리 투수가 미쳐 날뜁니다! 세 타자를 연속 KKK 3삼진으로 완벽하게 돌려세웁니다!"
                elif defense_type == "일반":
                    def_log = random.choice([
                        "🛡️ 우리 투수가 삼자범퇴로 상대 타선을 꽁꽁 틀어막았습니다! (무실점)",
                        "🛡️ 우리 투수가 안정된 제구력으로 상대 타선을 깔끔한 삼자범퇴로 요리했습니다!"
                    ])
                else:
                    def_log = "🛡️ 루상에 주자가 나갔으나, 내야진의 환상적인 '더블플레이(병살타)'가 터지며 위기를 실점 없이 넘깁니다!"
            elif enemy_pts == 1:
                def_log = random.choice([
                    "💥 아쉽게 상대 팀에게 솔로 홈런 한 방을 허용하며 1실점합니다.",
                    "💥 아쉽게 상대 팀에게 적시타를 허용하여 1실점 합니다.",
                    "📐 외야 깊숙한 희생플라이로 3루 주자가 홈을 밟으며 1점을 내어줍니다.",
                    "🏃‍♂️ 발 빠른 2루 주자가 단타 한 방에 홈까지 파고들어 아쉽게 실점합니다.",
                    "굴러온 수비 실책으로 주자를 내보내더니, 결국 내야 땅볼 때 홈을 허용하며 1실점합니다."
                ])
            elif enemy_pts == 2:
                def_log = random.choice([
                    "🚀 담장을 훌쩍 넘어가는 투런 홈런을 얻어맞으며 순식간에 2실점합니다.",
                    "🔥 좌우중간을 완전히 가르는 싹쓸이 2루타! 루상의 주자 2명이 모두 홈을 밟습니다.",
                    "연속 안타를 얻어맞으며 수비진이 흔들립니다. 순식간에 2점을 내어줍니다.",
                    "안타에 수비 실책까지 겹치면서, 주자 2명이 연달아 홈으로 들어옵니다.",
                    "솔로 홈런 후에 백투백 홈런을 얻어맞아 2실점합니다."
                ])
            elif enemy_pts == 3:
                def_log = random.choice([
                    "🚀 비거리 대폭발! 벼락같은 쓰리런 홈런을 얻어맞으며 순식간에 3실점합니다.",
                    "🔥 주자 만루 상황, 우익수 키를 넘기는 싹쓸이 3루타가 터지며 주자 3명이 모두 홈인합니다!",
                    "연속 안타에 볼넷까지, 마운드가 완전히 무너지며 이번 이닝에만 3점을 헌납합니다.",
                    "투런 홈런 후에 백투백 홈런을 얻어맞아 3실점합니다."
                ])
            else:
                def_log = random.choice([
                    "😱 이보다 더 최악일 수 없습니다! 담장을 넘어가는 만루 홈런(그랜드 슬램)을 허용하며 4실점합니다!",
                    "🥶 마운드가 완전히 폭발합니다. 백투백 홈런을 포함해 안타를 무차별로 얻어맞으며 4점을 내어줍니다.",
                    "쓰리런 홈런 후에 백투백 홈런을 얻어맞아 4실점합니다."
                ])

        # 투구수 연산 알고리즘 고증
        team_pitch_modifier = int(enemy_buff["ball_p"] / 10)
        if enemy_pts == 0:
            if defense_type == "KKK":
                inning_pitches = random.randint(9, 14) + team_pitch_modifier
            else:
                inning_pitches = random.randint(6, 12) + team_pitch_modifier
        elif enemy_pts == 1:
            inning_pitches = random.randint(13, 18) + team_pitch_modifier
        elif enemy_pts in [2, 3]:
            inning_pitches = random.randint(17, 24) + team_pitch_modifier
        else:
            inning_pitches = random.randint(25, 32) + team_pitch_modifier

        if is_enemy_dominant:
            inning_pitches += 3

        inning_pitches = max(5, inning_pitches)
        self.our_total_pitches += inning_pitches

        # 9회말 상대 끝내기 연출 조건부 분기 검증
        if self.inning >= 9 and self.phase == "말" and not self.is_home_team:
            if (self.enemy_score + enemy_pts) > self.our_score:
                self.enemy_score = self.our_score + 1
                self.game_log.append(f"❌ Ah... {self.inning}회말 상대 팀에게 짜릿한 '끝내기 안타'를 얻어맞고 패배했습니다. (최종 {self.our_total_pitches}구 역투)")
                self.update_scoreboard(self.enemy_score)
                self.end_game()
                return
            else:
                self.enemy_score += enemy_pts
                self.update_scoreboard(enemy_pts)
                self.game_log.append(f"🎉 {def_log} ➔ {self.inning}회말 심장이 쫄깃한 마지막 반격을 무사히 막아내며 경기 세트!!")
                self.end_game()
                return
        else:
            self.enemy_score += enemy_pts
            self.update_scoreboard(enemy_pts)

        self.game_log.append(
            f"🔮 {self.inning}회{self.phase} 수비 결과: {def_log} "
            f"(우리 투수 이닝 {inning_pitches}구 소모 / 총 {self.our_total_pitches}구)"
        )
        self.next_phase()

    def update_scoreboard(self, score_to_add: int) -> None:
        idx = self.inning - 1
        if idx >= 12:
            return
        if self.is_home_team:  # 우리가 홈이면 상대는 원정(Away)에 누적
            if self.away_inning_scores[idx] == "":
                self.away_inning_scores[idx] = score_to_add
            else:
                if isinstance(self.away_inning_scores[idx], int):
                    self.away_inning_scores[idx] += score_to_add
        else:
            if self.home_inning_scores[idx] == "":
                self.home_inning_scores[idx] = score_to_add
            else:
                if isinstance(self.home_inning_scores[idx], int):
                    self.home_inning_scores[idx] += score_to_add

    def trigger_steal(self) -> None:
        if not (self.base1 or self.base2 or self.base3):
            st.warning("루상에 나간 주자가 있어야 도루를 시도하제예!")
            return

        my_buff = TEAMS.get(self.my_team, {"steal_b": 0})
        enemy_buff = TEAMS.get(self.enemy_team, {"out": 0})
        
        success_rate = 0.60 + (my_buff["steal_b"] - enemy_buff["out"]) * 0.005
        success_rate = max(0.10, min(0.90, success_rate))

        if self.base1 or self.base2:
            self.game_log.append("🏃‍♂️ [작전 발동] 주자가 다음 베이스를 향해 기민하게 스타트를 끊습니다! (일반 도루 시도)")
            if random.random() < success_rate:
                if self.base2 and not self.base3:
                    self.base3 = True
                    self.base2 = False
                    self.game_log.append("🎉 2루 주자 3루 안착 성공!")
                elif self.base1 and not self.base2:
                    self.base2 = True
                    self.base1 = False
                    self.game_log.append("🎉 1루 주자 2루 안착 성공!")
                elif self.base1 and self.base2 and not self.base3:
                    self.base3 = True
                    self.base2 = True
                    self.base1 = False
                    self.game_log.append("🎉 더블 스틸 성공! 주자 2, 3루!")
            else:
                self.out_count += 1
                self.game_log.append("❌ 포수의 칼 같은 송구에 주자가 걸려 아웃되었습니다!")
                if self.base1 and self.base2:
                    if random.choice([True, False]): self.base1 = False
                    else: self.base2 = False
                elif self.base1: self.base1 = False
                elif self.base2: self.base2 = False
                self.check_three_out_change()
            return

        elif self.base3:
            self.game_log.append("🚨 [독단적 허를 찌르기!] 루상이 고요한 틈을 타 3루 주자가 홈으로 번개처럼 쇄도합니다!!! 낭만의 홈스틸 감행!!!")
            home_steal_rate = success_rate * 0.35
            if random.random() < home_steal_rate:
                self.our_score += 1
                self.base3 = False
                
                # 전광판 가변 주입
                idx = self.inning - 1
                if idx < 12:
                    target_scores = self.home_inning_scores if self.is_home_team else self.away_inning_scores
                    if target_scores[idx] == "" or target_scores[idx] == 0:
                        target_scores[idx] = 1
                    else:
                        target_scores[idx] += 1
                
                self.game_log.append("🎉 🎉 [HOME STEAL SUCCESS!!!] 홈플레이트 슬라이딩 세이프!!! (+1점)")
                self.strike = 0
                self.ball = 0
                
                if self.inning >= 9 and self.phase == "말" and self.is_home_team and self.our_score > self.enemy_score:
                    self.game_log.append(f"🎉 {self.inning}회말!!! 우리 팀 타석에서 짜릿한 홈스틸 끝내기 득점이 터지며 경기를 그대로 끝냅니다!!")
                    self.end_game()
            else:
                self.out_count += 1
                self.base3 = False
                self.game_log.append("❌ [HOME STEAL FAIL] 포수 태그 아웃. 3루 주자 횡사.")
                self.check_three_out_change()

    def next_phase(self) -> None:
        if self.inning == 9 and self.phase == "초":
            if self.is_home_team and self.our_score > self.enemy_score:
                self.game_log.append("👍 9회초까지 이미 우리 팀이 이기고 있어 9회말 공격 없이 경기가 끝납니다! (9회말 X)")
                self.home_inning_scores[8] = "X"
                self.end_game()
                return
                
        idx = self.inning - 1
        if idx < 12:
            if self.away_inning_scores[idx] == "": self.away_inning_scores[idx] = 0
            if self.home_inning_scores[idx] == "": self.home_inning_scores[idx] = 0
                
        if self.phase == "초":
            self.phase = "말"
        else:
            self.phase = "초"
            self.inning += 1
        self.setup_half_inning()

    def end_game(self) -> None:
        self.game_over = True
        if self.inning >= 10 and self.phase == "초":
            self.inning = 9
            self.phase = "말"

        if self.our_score > self.enemy_score:
            self.game_result_msg = f"🎉 {self.my_team} 대승리!!! 오늘 경기 수당은 사모님 기라!!"
        elif self.our_score < self.enemy_score:
            self.game_result_msg = f"😭 패배... 상대 {self.enemy_team}의 마구에 당했습니다. 복수하러 가이소!"
        else:
            self.game_result_msg = "🤝 12회 대혈투 끝에 무승부로 끝났습니다!"

    def play_turn(self, user_choice: int) -> None:
        if self.game_over:
            return

        self.pitch_type = random.choice(["직구", "슬라이더", "체인지업", "커브", "포크볼", "스플리터"])
        self.pitch_zone = random.randint(1, 9) if random.random() < 0.70 else 0
        self.guess_zone = random.randint(1, 9)
        
        self.game_log.append(f"🔮 투수가 {self.pitch_type}를 선택해 {self.pitch_zone}번 구역으로 던졌습니다!")
        self.enemy_total_pitches += 1

        current_batter = self.my_batter_number
        my_buff = TEAMS.get(self.my_team, {"homerun": 0, "hit": 0, "out": 0, "strike_p": 0, "ball_p": 0})
        enemy_buff = TEAMS.get(self.enemy_team, {"homerun": 0, "hit": 0, "out": 0, "strike_p": 0, "ball_p": 0})
        defense_penalty = 15 if self.enemy_team in ["⚪ 화이트 이글스", "⚫ 블랙 나이츠"] else 0

        # 타순별 고증 데이터 할당
        batter_context_msg = ""
        batter_homerun_mod = 0
        batter_hit_mod = 0
        batter_ball_mod = 0

        if current_batter == 1:
            batter_context_msg = "🏃‍♂️ [1번 출루머신] "
            batter_hit_mod = 20
            batter_ball_mod = 30
        elif current_batter in [2, 3]:
            batter_context_msg = "🔥 [요즘 대세! 강한 2/3번 핵심 타자] "
            batter_homerun_mod = 25
            batter_hit_mod = 35
        elif current_batter == 4:
            batter_context_msg = "👑 [전통의 4번 해결사: 사모님 타석!] "
            batter_homerun_mod = 40
            batter_hit_mod = -10
        elif current_batter in [5, 6]:
            batter_context_msg = "⚔️ [5/6번 클러치 히터] "
            batter_homerun_mod = 15
        elif current_batter in [7, 8]:
            batter_context_msg = "🛡️ [7/8번 하위 타선 폭탄 돌리기] "
            batter_hit_mod = -20
        elif current_batter == 9:
            batter_context_msg = "🎯 [9번 가교 타자] "
            batter_hit_mod = 15
            batter_ball_mod = 20
        
        at_bat_result = "지속"
        
        # 1. 풀스윙 강타 모듈
        if user_choice == 1:
            zone_mod = 1.5 if self.pitch_zone == 0 else 1.0
            w_homerun = max(10, 80 + my_buff["homerun"] + batter_homerun_mod)
            w_hit = max(10, 170 + my_buff["hit"] - defense_penalty + batter_hit_mod)
            w_out = max(10, int((550 + my_buff["out"]) * zone_mod))
            w_foul = 200
            
            result = random.choices(["HOMERUN", "HIT", "OUT", "FOUL"], weights=[w_homerun, w_hit, w_out, w_foul])[0]
            if result == "HOMERUN": at_bat_result = "홈런"
            elif result == "HIT": at_bat_result = "안타"
            elif result == "OUT": at_bat_result = "아웃"
            elif result == "FOUL":
                if self.strike < 2:
                    self.strike += 1
                    self.game_log.append(f"💥 작전[풀스윙]: {batter_context_msg}파울! 스트라이크 추가. (현재 {self.strike}S {self.ball}B)")
                else:
                    self.game_log.append(f"💥 작전[풀스윙]: {batter_context_msg}2S 이후 끈질긴 커트 파울! (현재 {self.strike}S {self.ball}B)")
                return

        # 2. 가볍게 밀어치기 모듈
        elif user_choice == 2:
            zone_mod = 1.3 if self.pitch_zone == 0 else 1.0
            w_hit = max(10, 350 + (my_buff["hit"] * 1.2) - defense_penalty + (batter_hit_mod * 1.5))
            w_out = max(10, int((450 + my_buff["out"]) * zone_mod))
            w_foul = 200
            
            result = random.choices(["HIT", "OUT", "FOUL"], weights=[w_hit, w_out, w_foul])[0]
            if result == "HIT": at_bat_result = "안타"
            elif result == "OUT": at_bat_result = "아웃"
            elif result == "FOUL":
                if self.strike < 2:
                    self.strike += 1
                    self.game_log.append(f"💥 작전[밀어치기]: {batter_context_msg}빗맞은 파울! 스트라이크 추가. (현재 {self.strike}S {self.ball}B)")
                else:
                    self.game_log.append(f"💥 작전[밀어치기]: {batter_context_msg}2S 이후 끈질기게 파울 커트 연발! (현재 {self.strike}S {self.ball}B)")
                return

        # 3. 공 끝까지 거르기 하드웨어 칼판정 알고리즘
        elif user_choice == 3:
            if 1 <= self.pitch_zone <= 9:
                self.strike += 1
                self.game_log.append(f"👀 작전[거르기]: {batter_context_msg}❌ 스트라이크 존({self.pitch_zone}번)으로 들어오는 공을 지켜보았습니다! (현재 {self.strike}S {self.ball}B)")
                if self.strike >= 3:
                    self.game_log.append(f"⚡ Ah... {batter_context_msg}{current_batter}번 타자 스탠딩 루킹 삼진 아웃!!")
                    at_bat_result = "삼진"
            elif self.pitch_zone == 0:
                self.ball += 1
                self.game_log.append(f"👀 작전[거르기]: {batter_context_msg}🟢 볼! 존 바깥 유인구를 눈으로 정확히 골라냅니다! (현재 {self.strike}S {self.ball}B)")
                if self.ball >= 4:
                    at_bat_result = "볼넷"

        # 주자 런너 오토마타 시스템 프로세싱
        if at_bat_result != "지속":
            self.strike = 0
            self.ball = 0
            self.my_batter_number = 1 if current_batter == 9 else current_batter + 1

            if at_bat_result == "홈런":
                pts = (1 if self.base1 else 0) + (1 if self.base2 else 0) + (1 if self.base3 else 0) + 1
                self.our_score += pts
                self.game_log.append(f"🔥 🎉 깡!!!!! {batter_context_msg}{current_batter}번 타자 대형 {pts}점짜리 홈런 대폭발!!!!!!!!")
                self.base1 = self.base2 = self.base3 = False
                self.inject_live_score(pts)

            elif at_bat_result == "안타":
                gained_run = 0
                if self.base3: gained_run += 1
                if self.base2: gained_run += 1
                self.our_score += gained_run
                
                self.base3 = self.base1
                self.base2 = False
                self.base1 = True
                self.game_log.append(f"🌟 딱! {batter_context_msg}{current_batter}번 타자의 안타! 주자 나갑니다!")
                if gained_run > 0:
                    self.inject_live_score(gained_run)

            elif at_bat_result == "아웃":
                if self.base1 and self.out_count < 2 and random.random() < 0.40:
                    self.out_count += 2
                    self.base1 = False
                    self.game_log.append(f"😱 아앗! {batter_context_msg}{current_batter}번 타자 내야 땅볼! 유격수-2루수-1루수 '병살타(투아웃)'!")
                elif self.base3 and self.out_count < 2 and random.random() < 0.50:
                    self.out_count += 1
                    self.base3 = False
                    self.our_score += 1
                    self.game_log.append(f"🕊️ [희생 플라이] {batter_context_msg}{current_batter}번 타자의 큰 타구! 3루 주자 태그업 홈인!")
                    self.inject_live_score(1)
                else:
                    self.out_count += 1
                    self.game_log.append(f" Ah... {batter_context_msg}{current_batter}번 타자 범타 아웃입니다.")
                self.check_three_out_change()

            elif at_bat_result == "삼진":
                self.out_count += 1
                self.check_three_out_change()

            elif at_bat_result == "볼넷":
                self.game_log.append(f"🚶‍♂️ {batter_context_msg}{current_batter}번 타자 볼넷 출루!")
                if self.base1 and self.base2 and self.base3:
                    self.our_score += 1
                    self.game_log.append("➔ 밀어내기 만루 볼넷으로 1점 추가!")
                    self.inject_live_score(1)
                elif self.base1 and self.base2: self.base3 = True
                elif self.base1: self.base2 = True
                else: self.base1 = True

        # 끝내기 최종 조건 정밀 검증
        if self.inning >= 9 and self.phase == "말" and self.is_home_team and self.our_score > self.enemy_score and not self.game_over:
            self.game_log.append(f"🎉 {self.inning}회말!!! 우리 팀 타석에서 짜릿한 '끝내기 득점'이 터지며 경기를 그대로 끝냅니다!!")
            self.end_game()

    def inject_live_score(self, run: int) -> None:
        idx = self.inning - 1
        if idx >= 12:
            return
        target_board = self.home_inning_scores if self.is_home_team else self.away_inning_scores
        if target_board[idx] == "":
            target_board[idx] = run
        else:
            if isinstance(target_board[idx], int):
                target_board[idx] += run

    def check_three_out_change(self) -> None:
        if self.out_count >= 3:
            self.game_log.append("📢 쓰리아웃 체인지! 공수 교대합니다.")
            if self.inning >= 9:
                if self.phase == "초" and self.our_score < self.enemy_score:
                    self.end_game()
                    return
                elif self.phase == "말" and self.our_score < self.enemy_score:
                    self.end_game()
                    return
            self.next_phase()

# =====================================================================
# [VIEW / UI RENDERER] 3. Streamlit 화면 렌더링 프론트엔드 구역
# =====================================================================
def render_css() -> None:
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
            margin-bottom: 10px;
            font-size: 16px !important;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

def draw_matrix_table() -> None:
    df = pd.DataFrame.from_dict(MATCHUP_MATRIX, orient='index', columns=MATRIX_COLUMNS)
    
    def color_cells(val: str) -> str:
        if val == "초록": return "background-color: #2e7d32; color: white; font-weight: bold;"
        elif val == "연두": return "background-color: #aed581; color: black; font-weight: bold;"
        elif val == "노랑": return "background-color: #fff59d; color: black;"
        elif val == "오렌지": return "background-color: #ffb74d; color: black;"
        elif val == "빨강": return "background-color: #e53935; color: white; font-weight: bold;"
        return ""

    try:
        st.dataframe(df.style.map(color_cells), use_container_width=True)
    except AttributeError:
        st.dataframe(df.style.applymap(color_cells), use_container_width=True)

def main() -> None:
    render_css()
    st.title("⚾ 순야보: 순수한 야구를 보여주마!")
    st.subheader("이 사장님의 프로야구 시뮬레이터 Pro Level")

    # 1. 설정집 메뉴 바인딩
    if st.button("📜 구단 설정집 열람"):
        st.session_state.show_stories = True

    if st.session_state.get("show_stories", False):
        file_path = "assets/team_stories.txt"
        st.markdown("---")
        st.subheader("🕵️‍♂️ 10대 구단 비사(秘史) 및 성격 설정집")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                st.text_area("구단별 성격 및 스토리", value=f.read(), height=300, disabled=True)
        else:
            st.error("⚠️ assets/team_stories.txt 파일을 찾을 수 없습니다!")
        if st.button("❌ 설정집 닫기"):
            st.session_state.show_stories = False
            st.rerun()
        st.markdown("---")

    # 2. 상성 대장부 데이터 레이아웃
    if "show_matrix" not in st.session_state:
        st.session_state.show_matrix = False

    if st.button("📊 KBO 10대 구단 10x10 상성 대장부 열람"):
        st.session_state.show_matrix = True

    if st.session_state.show_matrix:
        st.markdown("---")
        st.subheader("📊 10대 구단 가변 상성 판독표 (세로: 공격 / 가로: 수비)")
        st.caption("💡 팁: 초록(극상성 우세) / 연두(우세) / 노랑(백중세) / 오렌지(열세) / 빨강(천적 극열세)")
        draw_matrix_table()
        if st.button("❌ 상성 대장부 닫기"):
            st.session_state.show_matrix = False
            st.rerun()
        st.markdown("---")

    # 3. 게임 매칭 엔진 제어 구조체
    if "engine" not in st.session_state:
        st.session_state.engine = None

    if st.session_state.engine is None:
        st.markdown("### 🏟️ 구단 선택 및 리그 매칭")
        my_team_selected = st.selectbox("사모님이 이끌어갈 우리 팀을 고르소:", list(TEAMS.keys()))
        remaining_teams = [t for t in TEAMS.keys() if t != my_team_selected]
        
        if st.button("경기 대진표 확정 및 입장 🎟️", type="primary"):
            enemy_team_selected = random.choice(remaining_teams)
            # 신규 게임을 엔진 인스턴스로 바인딩
            st.session_state.engine = BaseballGameEngine(my_team_selected, enemy_team_selected)
            st.rerun()
    else:
        game: BaseballGameEngine = st.session_state.engine

        # 라이브 대시보드 스코어 출력
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            st.metric(label=f"우리 팀 {game.my_emoji}", value=f"{game.our_score} 점")
            st.caption(game.my_team)
            st.markdown(f"🔋 **우리 투수 총 투구수:** `{game.our_total_pitches}구`")
        with col2:
            st.markdown(f"<h3 style='text-align: center; color: red;'>{game.inning}회{game.phase}</h3>", unsafe_allow_html=True)
            current_is_our_turn = (not game.is_home_team and game.phase == "초") or (game.is_home_team and game.phase == "말")
            st.markdown(f"<p style='text-align: center; font-size:12px; font-weight:bold; color:#1E90FF;'>🔥 {'[우리 공격 턴]' if current_is_our_turn else '[상대 공격 턴]'}</p>", unsafe_allow_html=True)
        with col3:
            st.metric(label=f"상대 팀 {game.enemy_emoji}", value=f"{game.enemy_score} 점")
            st.caption(game.enemy_team)
            st.markdown(f"🥎 **상대 투수 총 투구수:** `{game.enemy_total_pitches}구`")

        st.divider()

        # 라인 스코어보드 어셈블러
        away_name = game.enemy_team if game.is_home_team else game.my_team
        home_name = game.my_team if game.is_home_team else game.enemy_team

        scoreboard_data = {
            "TEAM": [f"🚌 {away_name} (원정)", f"🏟️ {home_name} (홈)"],
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
            "R": [
                game.enemy_score if game.is_home_team else game.our_score,
                game.our_score if game.is_home_team else game.enemy_score
            ]
        }
        st.markdown("### 🏟️ 실시간 라인 스코어보드")
        st.table(pd.DataFrame(scoreboard_data).set_index("TEAM"))

        st.markdown(f"### ⚾ 투수 구종: **{game.pitch_type}**")
        if game.pitch_zone == 0:
            st.error("🚨 [PITCH OUT!] 투수가 스트라이크 존을 완전히 벗어나는 유인구(BALL)를 던졌습니다!")
        else:
            st.success("🎯 [STRIKE ZONE] 공이 스트라이크 존 안으로 들어옵니다!")

        # 9분할 스트라이크 존 그리드 그래픽 렌더러
        cols_zone = [st.columns(3), st.columns(3), st.columns(3)]
        zone_matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        st.write("🔽 **스트라이크 존 (⚾: 공 꽂힌 곳 / 👁️: 타자 노림수)**")
        for i in range(3):
            for j in range(3):
                z_val = zone_matrix[i][j]
                icon = "⚾" if game.pitch_zone == z_val else ("👁️" if game.guess_zone == z_val else "🟩")
                with cols_zone[i][j]:
                    st.button(f"{icon} ({z_val}번)", key=f"zone_btn_{z_val}", disabled=True)

        # 게임 오버 전광판 및 이스터에그 특수 연출 구역
        if game.game_over:
            st.markdown("<h1 style='text-align: center; color: #FF4B4B; font-size: 60px; font-weight: bold; letter-spacing: 5px;'>💥 GAME SET 💥</h1>", unsafe_allow_html=True)
            if game.our_score > game.enemy_score:
                st.balloons()
                st.success(game.game_result_msg)
                st.markdown("""
                    <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 9999; overflow: hidden;">
                        <span style="position: absolute; font-size: 50px; left: 10%; animation: congratulations 3s linear 3;">🎉</span>
                        <span style="position: absolute; font-size: 40px; left: 25%; animation: congratulations 4s linear 3; animation-delay: 1s;">🎉</span>
                        <span style="position: absolute; font-size: 60px; left: 40%; animation: congratulations 2.5s linear 3; animation-delay: 0.5s;">🎉</span>
                        <span style="position: absolute; font-size: 45px; left: 60%; animation: congratulations 3.5s linear 3; animation-delay: 1.5s;">🎉</span>
                        <span style="position: absolute; font-size: 55px; left: 75%; animation: congratulations 2.8s linear 3; animation-delay: 0.2s;">🎉</span>
                        <span style="position: absolute; font-size: 50px; left: 90%; animation: congratulations 3.2s linear 3; animation-delay: 0.8s;">🎉</span>
                    </div>
                    <style>
                        @keyframes congratulations {
                            0% { top: -10%; transform: rotate(0deg); }
                            100% { top: 110%; transform: rotate(360deg); }
                        }
                    </style>
                """, unsafe_allow_html=True)
                st.markdown("<h3 style='text-align: center; color: #8B4513;'>🎉 승리의 축포를 날리자아아앗!!! 🎉</h3>", unsafe_allow_html=True)
            else:
                st.error(game.game_result_msg)
                st.markdown("""
                    <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 9999; overflow: hidden;">
                        <span style="position: absolute; font-size: 50px; left: 10%; animation: poop 3s linear 3;">💩</span>
                        <span style="position: absolute; font-size: 40px; left: 25%; animation: poop 4s linear 3; animation-delay: 1s;">💩</span>
                        <span style="position: absolute; font-size: 60px; left: 40%; animation: poop 2.5s linear 3; animation-delay: 0.5s;">💩</span>
                        <span style="position: absolute; font-size: 45px; left: 60%; animation: poop 3.5s linear 3; animation-delay: 1.5s;">💩</span>
                        <span style="position: absolute; font-size: 55px; left: 75%; animation: poop 2.8s linear 3; animation-delay: 0.2s;">💩</span>
                        <span style="position: absolute; font-size: 50px; left: 90%; animation: poop 3.2s linear 3; animation-delay: 0.8s;">💩</span>
                    </div>
                    <style>
                        @keyframes poop {
                            0% { top: -10%; transform: rotate(0deg); }
                            100% { top: 110%; transform: rotate(360deg); }
                        }
                    </style>
                """, unsafe_allow_html=True)
                st.markdown("<h3 style='text-align: center; color: #8B4513;'>💩 패배의 똥세례를 받아라아아앗!!! 💩</h3>", unsafe_allow_html=True)

            st.divider()
            if st.button("다른 구단 선택하러 가기 🔄", type="primary"):
                st.session_state.engine = None
                st.rerun()
        else:
            # 실시간 카운트 현황판 디자인 컴포넌트
            c1, c2 = st.columns([1, 1])
            with c1:
                st.markdown("### 📊 카운트 보드")
                st.markdown(f"* **아웃:** {'🔴' * game.out_count}{'⚪' * (3-game.out_count)}")
                st.markdown(f"* **스트라이크:** {'🔥' * game.strike}{'⚪' * (3-game.strike)}")
                st.markdown(f"* **볼:** {'🟢' * game.ball}{'⚪' * (4-game.ball)}")
                
                batter_tag = ""
                if game.my_batter_number == 4: batter_tag = "(👑 사모님!)"
                elif game.my_batter_number in [2, 3]: batter_tag = "(🔥 대세 강타자!)"
                elif game.my_batter_number == 1: batter_tag = "(🏃‍♂️ 출루머신)"
                elif game.my_batter_number == 9: batter_tag = "(🎯 상위연결)"
                st.markdown(f"* **타순:** `{game.my_batter_number}번 타자 타석` {batter_tag}")
                
            with c2:
                st.markdown("### 🏃 루상 주자")
                b1_char = "🏃" if game.base1 else "◯"
                b2_char = "🏃" if game.base2 else "◯"
                b3_char = "🏃" if game.base3 else "◯"
                st.code(f"""
                       [{b2_char}] 2루
                [{b3_char}] 3루         [{b1_char}] 1루
                        [X] 타석
                """, language="text")

            st.divider()

            # 사용자 작전 인터랙션 컨트롤러
            st.markdown("### 📢 사모님의 작전 지시")
            col_b1, col_b2, col_b3, col_b4 = st.columns(4)
            with col_b1:
                if st.button("💥 1. 풀스윙 강타"):
                    game.play_turn(1)
                    st.rerun()
            with col_b2:
                if st.button("🌟 2. 가볍게 밀어치기"):
                    game.play_turn(2)
                    st.rerun()
            with col_b3:
                if st.button("👀 3. 공 끝까지 거르기"):
                    game.play_turn(3)
                    st.rerun()
            with col_b4:
                if st.button("🏃‍♂️ 4. 기습 도루 작전"):
                    game.trigger_steal()
                    st.rerun()

        st.divider()
        st.markdown("### 🎙️ 실시간 중계 일지")
        for log in reversed(game.game_log[-8:]):
            st.write(log)

if __name__ == "__main__":
    st.set_page_config(page_title="이 사장의 프로야구 시뮬레이터 Pro", page_icon="⚾", layout="centered")
    main()
