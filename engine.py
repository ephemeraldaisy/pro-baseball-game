import random
import streamlit as st
from typing import List
from data import TEAMS, MATCHUP_MATRIX, TEAM_ROSTERS, PITCH_SPECS, get_default_lineup

# =====================================================================
# [NAVER INFRASTRUCTURE LAYER] AI 전술 가이드
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
# [DOMAIN LAYER] PitcherDomain
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
# [CORE ENGINE] PureKboEngine
# =====================================================================
class PureKboEngine:
    def __init__(self, my_team: str, enemy_team: str, my_lineup: List[str] = None, starting_pitcher_idx: int = 0) -> None:
        self.my_team = my_team
        self.enemy_team = enemy_team
        self.my_emoji = my_team[:2]
        self.enemy_emoji = enemy_team[:2]
        self.is_home_team = random.choice([True, False])

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
            PitcherDomain(f"선발({chosen_sp_name})", "선발", my_stats["stamina"]),
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
        
        if self.is_attack:
            st.warning("공격 턴에는 고의사구 작전을 지시할 수 없습니다.")
            return

        p_my = self.get_current_my_pitcher()
        p_my.consume(1)
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
            
        bat = self.enemy_batter_number
        self.enemy_batter_number = 1 if bat == 9 else bat + 1
        
        self.check_three_out_change()

    def check_weather_events(self) -> bool:
        if self.inning < 5 and random.random() < 0.008:
            self.game_log.append("🚨 [🌧️ 폭우 기습] 갑작스러운 게릴라성 호우로 경기가 중단되었습니다!")
            self.game_log.append("❌ [노게임 선언] 5이닝 미만 진행으로 경기가 무효 처리됩니다.")
            self.game_over = True
            return True

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
            if 1 <= score_diff <= 3 and random.random() < 0.30:
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
        pitchers_list = self.my_pitchers if is_defense else self.enemy_pitchers 
        current_pitcher = self.our_pitcher if is_defense else self.enemy_pitcher 

        #체력 10 이하/ 한 이닝 5실점 이상 강제 교체
        is_forced_change = False
        if current_pitcher is not None: 
            stamina = getattr(current_pitcher, 'stamina', 100)
            inning_er = getattr(current_pitcher, 'inning_er', 0)
            if stamina <= 10 or inning_er >= 5:
                is_forced_change = True

        if not is_forced_change and current_pitcher is not None:
            current_idx = getattr(current_pitcher, 'index', -1)
            if current_idx != -1:
                return current_idx
        
        forbidden_indices = set()
        #8회 전 마무리 금지, 7회 전 셋업맨 금지
        if self.inning < 8:
            forbidden_indices.add(8) #마무리
        if self.inning < 7:
            forbidden_indices.add(6) #셋업맨 1, 2
            forbidden_indices.add(7)

        #4점차 이상 큰 격차 시 필승조 금지 
        if abs(score_diff) >= 4:
            forbidden_indices.add(5)
            forbidden_indices.add(6)
            forbidden_indices.add(7)
            forbidden_indices.add(8)

        rest_dict = (
            st.session_state.my_pitcher_rest_days if is_defense 
            else st.session_state.enemy_pitcher_rest_days
        )
        for p_idx, days in rest_dict.items():
            if days > 0 and 1 <= p_idx <= 4:  # 선발 투수(1~4번)만 금지 적용
                forbidden_indices.add(p_idx)
            
        #타깃 투수 산출
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
            self._check_and_apply_starter_rest(target, is_defense)
            return target

        search_candidates = [5, 6, 7, 8, 1, 2, 3, 4] if score_diff >= 0 else [1, 2, 3, 4, 5, 6, 7, 8]
        for idx in search_candidates:
            if idx not in used_set and idx not in forbidden_indices and idx < len(pitchers_list): 
                self._check_and_apply_starter_rest(idx, is_defense)
                return idx

        for idx in range(1, len(pitchers_list)):
            if idx not in used_set:
                self._check_and_apply_starter_rest(idx, is_defense)
                return idx
                
        return -99

    def _check_and_apply_starter_rest(self, pitch_idx: int, is_defense: bool) -> None:
        used_set = self.my_used_pitchers if is_defense else self.enemy_used_pitchers
        rest_dict = (
            st.session_state.my_pitcher_rest_days if is_defense 
            else st.session_state.enemy_pitcher_rest_days
        )
        
        used_set.add(pitch_idx)
        # 1번~4번 투수(선발 로테이션)만 등판 후 5일 휴식 등록!
        if 1 <= pitch_idx <= 5:
            rest_dict[pitch_idx] = 5

    @staticmethod 
    def advance_rest_days():
        """시즌 진행(1경기 완료) 시 휴식 중인 선발 투수들의 휴식일을 1일씩 감소"""
        for r_dict in [st.session_state.get("my_pitcher_rest_days", {}), st.session_state.get("enemy_pitcher_rest_days", {})]:
            for p_idx in list(r_dict.keys()):
                if r_dict[p_idx] > 0:
                    r_dict[p_idx] -= 1

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
            if random.random() < 0.15:
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
       
        elif user_choice == 3:
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
                
        elif user_choice == 4:
            if not self.base3:
                st.warning("3루에 주자가 없어 스퀴즈 번트가 불가능합니다.")
                return

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
                
            if random.random() < 0.01:
                hr_msg = f"🚀💥 [장외 대형 홈런!!] {b_ctx} 타구가 야구장 장외로 까마득하게 넘어갑니다! 엄청난 비거리! (+{pts}점)"
            else:
                hr_msg = f"🔥 {b_ctx} 홈런!! (+{pts}점)"

            self.game_log.append(log_prefix + match_msg + hr_msg)

            current_score_diff = self.our_score - self.enemy_score 

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
            if self.strike == 2:
                foul_cut_bonus = 0.20 + (my_stats.get("hit", 50) * 0.003)

                if is_contact_pest:
                    foul_cut_bonus += 0.15

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
                    
                    if random.random() < 0.03:
                        self.trigger_bench_clearing("2루 태그 과정에서 주자와 내야수가 과도하게 부딪히며 신경전이 벌어졌습니다!")
                    else:
                        self.game_log.append(log_prefix + "💥 2루수-1루수 이어지는 뼈아픈 병살타 아웃!")
                elif self.out_count < 2 and self.base3 and random.random() < 0.45:
                    self.out_count += 1
                    self.base3 = False
                    self.update_live_scoreboard(1)
                    
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
            if random.random() < 0.15: 
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
            if random.random() < 0.25:
                backup_list = TEAM_ROSTERS[self.my_team]["batters"].get("백업(4)", [])
                pr_player = next((p for p in backup_list if "대주자" in p or "잽싼" in p or "발" in p), backup_list[-1] if backup_list else "대주자 요원")
                
                self.hit_buff += 0.03
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
