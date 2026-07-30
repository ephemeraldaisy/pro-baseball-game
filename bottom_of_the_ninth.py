import random
import time
import streamlit as st

# =====================================================================
# 🚀 스페셜 미니게임: 9회말 2아웃 만루 클러치 히터 Engine & UI
# =====================================================================
class HomerunMiniGame:
    def __init__(self):
        self.inning = 9
        self.phase = "말"
        self.our_score = 3
        self.enemy_score = 4
        self.batter_number = 4  # 4번 타자
        self.out_count = 2      # 9회말 2아웃 만루 위기
        self.base1 = True
        self.base2 = True
        self.base3 = True
        self.strike = 0
        self.ball = 0
        self.game_over = False
        self.result_msg = ""
        self.tier_result = None
        self.diamond_change = 0
        self.game_log = ["🚨 [9회말 위기 상황] 3대4, 2아웃 주자 만루! 극적인 역전을 노리세요!"]

    def process_turn(self, user_choice: int) -> None:
        if self.game_over:
            return

        pitches = ["직구", "슬라이더", "체인지업", "포크볼"]
        pitch = random.choice(pitches)
        
        log_prefix = f"[{self.inning}회말 {self.batter_number}번 타자] 투수가 던진 공은 '[{pitch}]'! ➔ "
        at_bat_result = None

        # 1. 풀스윙 강타 시나리오
        if user_choice == 1:
            result = random.random()
            if (pitch == "직구" and result < 0.35) or (pitch != "직구" and result < 0.20):
                at_bat_result = "홈런"
            elif result < 0.50:
                at_bat_result = "2루타"
            elif result < 0.70:
                if self.strike < 2:
                    self.strike += 1
                self.game_log.append(log_prefix + f"파울! 엄청난 스윙이었지만 아쉽게 빗맞았습니다. ({self.strike}S {self.ball}B)")
            else:
                self.strike += 1
                self.game_log.append(log_prefix + f"헛스윙!!! 무지막지한 헛스윙! ({self.strike}S {self.ball}B)")

        # 2. 가볍게 밀어치기 시나리오
        elif user_choice == 2:
            result = random.random()
            if result < 0.30:
                at_bat_result = "2루타"
            elif result < 0.60:
                at_bat_result = "내야안타"
            elif result < 0.80:
                if self.strike < 2:
                    self.strike += 1
                self.game_log.append(log_prefix + f"내야 파울 플라이! 아슬아슬하게 파울 라인 밖입니다. ({self.strike}S {self.ball}B)")
            else:
                self.strike += 1
                self.game_log.append(log_prefix + f"스윙 인정 스트라이크! 배트가 나가다 멈췄습니다. ({self.strike}S {self.ball}B)")

        # 3. 공 거르기 시나리오 (눈야구)
        elif user_choice == 3:
            result = random.random()
            if result < 0.55:
                self.ball += 1
                if self.ball == 4:
                    at_bat_result = "볼넷"
                else:
                    self.game_log.append(log_prefix + f"낮게 깔리는 공을 잘 골라냈습니다! 볼(Ball)! ({self.strike}S {self.ball}B)")
            else:
                self.strike += 1
                self.game_log.append(log_prefix + f"루킹 스트라이크! 공을 지켜만 봤습니다. ({self.strike}S {self.ball}B)")

        # --- [주자 진루 및 득점 판정 엔진] ---
        if at_bat_result in ["홈런", "2루타", "내야안타", "볼넷"]:
            prev_strike = self.strike
            self.strike, self.ball = 0, 0

            # 1) 만루 홈런 (S급 승리)
            if at_bat_result == "홈런":
                pts = (1 if self.base1 else 0) + (1 if self.base2 else 0) + (1 if self.base3 else 0) + 1
                self.our_score += pts
                self.base1 = self.base2 = self.base3 = False
                self.game_log.append(f"🎉 깡!!!!! 장외 담장을 훌쩍 넘어가는 대형 끝내기 역전 만루홈런!!!!!! (+{pts}점)")
                self._set_game_over(True, "S급 승리", 1000, "🏆 [S급 승리!] 9회말 2사 만루 끝내기 만루홈런(Grand Slam) 폭발! (+1,000 💎)")
                return

            # 2) 싹쓸이 3타점 2루타 (A급 승리)
            elif at_bat_result == "2루타":
                pts = (1 if self.base3 else 0) + (1 if self.base2 else 0) + (1 if self.base1 else 0)
                self.our_score += pts
                self.base3 = False; self.base2 = True; self.base1 = False
                self.game_log.append(f"🌟 우중간을 찢는 총알 같은 타구! 싹쓸이 2루타!! (+{pts}점)")
                self._set_game_over(True, "A급 승리", 500, "🏆 [A급 승리!] 끝내기 싹쓸이 3타점 2루타 작렬! (+500 💎)")
                return

            # 3) 밀어내기 볼넷 / 몸에 맞은 공 (B급 승리)
            elif at_bat_result == "볼넷":
                self.our_score += 1
                self.game_log.append("🏃‍♂️ 밀어내기 볼넷/사구로 3루 주자 홈인! 끝내기 득점! (+1점)")
                self._set_game_over(True, "B급 승리", 200, "🏆 [B급 승리!] 밀어내기 볼넷 / 끝내기 출루 성취! (+200 💎)")
                return

            # 4) 포수 빗맞은 내야안타 or 폭투 끝내기 (C급 승리)
            elif at_bat_result == "내야안타":
                self.our_score += 1
                self.game_log.append("⚾ 포수 방면 빗맞은 내야안타! 3루 주자가 헤드퍼스트 슬라이딩으로 홈인! (+1점)")
                self._set_game_over(True, "C급 승리", 100, "🏆 [C급 승리!] 빗맞은 내야안타 끝내기 역전승! (+100 💎)")
                return

        # --- [삼진 및 아웃 판정 코너] ---
        elif self.strike >= 3:
            # 1) 3-2 풀카운트 헛스윙 삼진 (B급 패배)
            if self.ball == 3 and user_choice in [1, 2]:
                self.game_log.append("❌ 3-2 풀카운트 승부 끝에 방망이가 허공을 찌르는 헛스윙 삼진 아웃!")
                self._set_game_over(False, "B급 패배", -200, "😭 [B급 패배] 3-2 풀카운트 벼랑 끝 헛스윙 삼진 아웃... (-200 💎)")
                return
            # 2) 평범한 루킹 삼진 아웃 (C급 패배)
            else:
                self.game_log.append("❌ 꽉 찬 스트라이크를 바라만 보며 삼진 아웃!")
                self._set_game_over(False, "C급 패배", -100, "😭 [C급 패배] 허무한 루킹 삼진 아웃... (-100 💎)")
                return

        # --- [돌발 아웃 / 호수비 / 주루사 확률 이벤트 (아웃 발생 시)] ---
        else:
            # 무작위 확률 돌발 아웃 판정 (스윙 시 10% 확률)
            out_roll = random.random()
            if out_roll < 0.08:
                # A급 패배: 잘 맞은 타구가 야수 다이빙 캐치 호수비에 잡힘
                self.game_log.append("😱 잘 맞은 대형 타구!! 그러나 상대 외야수의 미친 다이빙 캐치에 잡힙니다!")
                self._set_game_over(False, "A급 패배", -500, "😭 [A급 패배] 잘 맞은 타구가 상대 호수비에 저지당함... (-500 💎)")
                return
            elif out_roll < 0.12 and (self.base1 or self.base2 or self.base3):
                # S급 패배: 끝내기 주루사 / 견제사
                self.game_log.append("🚨 아차! 투수의 전격 견제구에 3루 주자가 견제태그아웃 당합니다!")
                self._set_game_over(False, "S급 패배", -1000, "😭 [S급 패배] 충격적인 끝내기 견제사/주루사 발생! (-1,000 💎)")
                return

    def _set_game_over(self, is_win: bool, tier: str, diamond: int, msg: str) -> None:
        self.game_over = True
        self.tier_result = tier
        self.diamond_change = diamond
        self.result_msg = msg


# =====================================================================
# 🖥️ Streamlit 전용 UI 렌더링 함수
# =====================================================================
def render_homerun_game_ui():
    st.subheader("⚾ 9회말 2아웃 만루 역전 클러치 히터")

    # 1. 게임 인스턴스 초기화 및 판돈 안내
    if "homerun_game_instance" not in st.session_state or st.session_state.homerun_game_instance is None:
        st.info("🔥 **[High Risk, High Return]** 9회말 2사 만루 극적 승부! 결과에 따라 다이아가 폭등하거나 차감됩니다.")

        st.markdown("""
        | 구분 | 시나리오 (상황) | 보상 / 페널티 |
        | :--- | :--- | :--- |
        | **S급 승리** | 끝내기 대형 만루홈런 (Grand Slam) | **+1,000 💎** |
        | **A급 승리** | 끝내기 싹쓸이 3타점 2루타 | **+500 💎** |
        | **B급 승리** | 밀어내기 볼넷 / 끝내기 몸에 맞은 공 | **+200 💎** |
        | **C급 승리** | 포수 빗맞은 내야안타 or 포일/폭투 끝내기 | **+100 💎** |
        | **C급 패배** | 평범한 외야 뜬공 / 루킹 삼진 아웃 | **-100 💎** |
        | **B급 패배** | 3-2 풀카운트에서 헛스윙 삼진 아웃 | **-200 💎** |
        | **A급 패배** | 잘 맞은 타구가 상대 야수 호수비에 잡힘 | **-500 💎** |
        | **S급 패배** | 끝내기 주루사 / 견제사 (포수/투수 견제) | **-1,000 💎** |
        """)

        if st.button("🚀 클러치 승부 도전 (기본 입장료 없음)", type="primary", key="btn_start_clutch"):
            st.session_state.homerun_game_instance = HomerunMiniGame()
            st.rerun()
        return

    # 2. 게임 진행 중 화면 렌더링
    game: HomerunMiniGame = st.session_state.homerun_game_instance

    # 점수판 및 스탯
    c1, c2, c3 = st.columns(3)
    c1.metric("우리팀 점수", f"{game.our_score} 점")
    c2.metric("이닝 / 아웃", f"{game.inning}회말 ({game.out_count} 아웃)")
    c3.metric("상대팀 점수", f"{game.enemy_score} 점")

    # 카운트 보드 시각화
    st.write(f"**카운트**: 스트라이크 {'🟡' * game.strike} | 볼 {'🟢' * game.ball} | 아웃 {'🔴' * game.out_count}")
    st.write(f"**루상 주자**: 1루 ({'🏃' if game.base1 else '◯'}) | 2루 ({'🏃' if game.base2 else '◯'}) | 3루 ({'🏃' if game.base3 else '◯'})")
    st.write(f"**현재 타석**: {game.batter_number}번 타자")

    st.divider()

    # 3. 게임 종료 처리 (티어별 다이아 정산)
    if game.game_over:
        if "승리" in game.tier_result:
            st.success(game.result_msg)
        else:
            st.error(game.result_msg)

        # 중복 지급/차감 방지 플래그
        if not getattr(game, 'reward_given', False):
            st.session_state.nc_diamonds += game.diamond_change
            # 음수 차감 시 0 아래로 내려가지 않도록 안전장치
            if st.session_state.nc_diamonds < 0:
                st.session_state.nc_diamonds = 0
            game.reward_given = True

            toast_icon = "💎" if game.diamond_change > 0 else "💸"
            st.toast(f"정산 완료: {game.diamond_change:+} 💎 (현재 보유: {st.session_state.nc_diamonds} 💎)", icon=toast_icon)

        if st.button("메인으로 돌아가기", key="btn_exit_clutch"):
            st.session_state.homerun_game_instance = None
            st.rerun()

    # 4. 게임 진행 중 타석 액션 버튼
    else:
        st.markdown("### 📢 타석 작전 선택")
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("💥 풀스윙 강타 (만루홈런 / 2루타 노리기)", key="hr_swing"):
                game.process_turn(1)
                st.rerun()
        with b2:
            if st.button("🌟 가볍게 밀어치기 (안타 확률 우수)", key="hr_contact"):
                game.process_turn(2)
                st.rerun()
        with b3:
            if st.button("👀 공 끝까지 보고 거르기 (볼넷 노리기)", key="hr_wait"):
                game.process_turn(3)
                st.rerun()

        st.divider()
        st.markdown("### 📜 미니게임 중계 로그")
        for log in reversed(game.game_log[-5:]):
            st.write(log)
