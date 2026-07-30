import random
import time
import streamlit as st

# =====================================================================
# 🚀 스페셜 미니게임: 9회말 2아웃 만루 역전 홈런 게임 (모듈화 완료)
# =====================================================================
class HomerunMiniGame:
    def __init__(self):
        self.inning = 9
        self.phase = "말"
        self.our_score = 3
        self.enemy_score = 4
        self.batter_number = 4  # 4번 타자 (사모님)
        self.out_count = 2      # 9회말 2아웃 만루 위기
        self.base1 = True
        self.base2 = True
        self.base3 = True
        self.strike = 0
        self.ball = 0
        self.game_over = False
        self.result_msg = ""
        self.game_log = ["🚨 [9회말 위기 상황] 3대4, 2아웃 주자 만루! 역전 홈런을 노리세요!"]

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
            if (pitch == "직구" and result < 0.4) or (pitch != "직구" and result < 0.2):
                at_bat_result = "홈런"
            elif result < 0.7:
                if self.strike < 2:
                    self.strike += 1
                self.game_log.append(log_prefix + f"파울! 엄청난 스윙이었지만 아쉽게 빗맞았습니다. ({self.strike}S {self.ball}B)")
            else:
                self.strike += 1
                self.game_log.append(log_prefix + f"헛스윙!!! 무지막지한 헛스윙! ({self.strike}S {self.ball}B)")

        # 2. 가볍게 밀어치기 시나리오
        elif user_choice == 2:
            result = random.random()
            if result < 0.5:
                at_bat_result = "안타"
            elif result < 0.8:
                if self.strike < 2:
                    self.strike += 1
                self.game_log.append(log_prefix + f"내야 파울 플라이! 아슬아슬하게 파울 라인 밖입니다. ({self.strike}S {self.ball}B)")
            else:
                self.strike += 1
                self.game_log.append(log_prefix + f"스윙 인정 스트라이크! 배트가 나가다 멈췄습니다. ({self.strike}S {self.ball}B)")

        # 3. 공 거르기 시나리오
        elif user_choice == 3:
            result = random.random()
            if result < 0.6:
                self.ball += 1
                if self.ball == 4:
                    at_bat_result = "볼넷"
                else:
                    self.game_log.append(log_prefix + f"낮게 깔리는 공을 잘 골라냈습니다! 볼(Ball)! ({self.strike}S {self.ball}B)")
            else:
                self.strike += 1
                self.game_log.append(log_prefix + f"루킹 스트라이크! 공을 지켜만 봤습니다. ({self.strike}S {self.ball}B)")

        # --- [주자 진루 및 득점 처리] ---
        if at_bat_result in ["홈런", "안타", "볼넷"]:
            self.strike, self.ball = 0, 0
            self.batter_number = 5 if self.batter_number == 4 else self.batter_number + 1

            if at_bat_result == "홈런":
                pts = (1 if self.base1 else 0) + (1 if self.base2 else 0) + (1 if self.base3 else 0) + 1
                self.our_score += pts
                self.base1 = self.base2 = self.base3 = False
                self.game_log.append(f"🎉 깡!!!!! 대형 {pts}점짜리 끝내기 역전 홈런!!!!!! (+{pts}점)")

            elif at_bat_result == "안타":
                pts = (1 if self.base3 else 0) + (1 if self.base2 else 0)
                self.our_score += pts
                self.base3 = self.base1
                self.base2 = False
                self.base1 = True
                self.game_log.append(f"🌟 딱! 깨끗한 타구음의 안타! (+{pts}점)")

            elif at_bat_result == "볼넷":
                if self.base1 and self.base2 and self.base3:
                    self.our_score += 1
                    self.game_log.append("🏃‍♂️ 밀어내기 볼넷 득점! (+1점)")
                elif self.base1 and self.base2:
                    self.base3 = True
                elif self.base1:
                    self.base2 = True
                else:
                    self.base1 = True

        # --- [삼진 및 아웃 처리] ---
        elif self.strike >= 3:
            self.out_count += 1
            self.strike, self.ball = 0, 0
            self.game_log.append(f"❌ 삼진 아웃!!! {self.batter_number}번 타자가 물러납니다.")
            self.batter_number = 5 if self.batter_number == 4 else self.batter_number + 1

        # --- [경기 끝내기 / 연장전 전환 판정] ---
        if self.our_score > self.enemy_score:
            self.game_over = True
            self.result_msg = f"🏆 [끝내기 승리!] 최종 스코어 {self.our_score}:{self.enemy_score} 대역전승 달성! (다이아 보상 획득)"
            return

        if self.out_count >= 3:
            if self.our_score < self.enemy_score:
                self.game_over = True
                self.result_msg = f"😭 [경기 패배] 최종 스코어 {self.our_score}:{self.enemy_score} 역전 실패..."
            elif self.our_score == self.enemy_score:
                # 10회 연장전 진입
                self.inning += 1
                self.out_count = 0
                self.strike, self.ball = 0, 0
                self.base1 = self.base2 = self.base3 = False
                
                # 상대 팀 연장초 실점 시뮬레이션
                enemy_pts = random.choice([0, 1])
                self.enemy_score += enemy_pts
                self.game_log.append(f"🔥 [{self.inning}회 연장전 진입] 상대팀 연장 초 {enemy_pts}점 추가 (현재 {self.our_score}:{self.enemy_score})")


# =====================================================================
# 🖥️ Streamlit 전용 UI 렌더링 함수
# =====================================================================
def render_homerun_game_ui():
    st.subheader("⚾ 9회말 2아웃 만루 역전 홈런 게임")
    
    # 1. 게임 인스턴스 초기화 및 입장료 처리
    if "homerun_game_instance" not in st.session_state or st.session_state.homerun_game_instance is None:
        st.info("9회말 2아웃 만루, 1점 지고 있는 상황입니다. 타석에서 극적인 역전승을 이끌어내고 다이아를 획득하세요!")
        if st.button("🚀 게임 시작 (입장료 50 💎)", type="primary"):
            if st.session_state.nc_diamonds >= 50:
                st.session_state.nc_diamonds -= 50
                st.session_state.homerun_game_instance = HomerunMiniGame()
                st.rerun()
            else:
                st.error("다이아가 부족합니다! 비밀 상점에서 충전하세요.")
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

    # 3. 게임 종료 처리 (결과 및 보상)
    if game.game_over:
        if "승리" in game.result_msg:
            st.success(game.result_msg)
            # 보상 중복 지급 방지
            if not getattr(game, 'reward_given', False):
                st.session_state.nc_diamonds += 300
                game.reward_given = True
                st.toast("🎉 역전승 성공! 상금 +300 💎 획득!", icon="💎")
        else:
            st.error(game.result_msg)
            
        if st.button("메인으로 돌아가기"):
            st.session_state.homerun_game_instance = None
            st.rerun()
            
    # 4. 게임 진행 중 타석 액션 버튼
    else:
        st.markdown("### 📢 타석 작전 선택")
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("💥 풀스윙 강타 (홈런 노리기)", key="hr_swing"):
                game.process_turn(1)
                st.rerun()
        with b2:
            if st.button("🌟 가볍게 밀어치기 (안타 확률)", key="hr_contact"):
                game.process_turn(2)
                st.rerun()
        with b3:
            if st.button("👀 공 끝까지 보고 거르기 (볼넷)", key="hr_wait"):
                game.process_turn(3)
                st.rerun()

        st.divider()
        st.markdown("### 📜 미니게임 로그")
        for log in reversed(game.game_log[-5:]):
            st.write(log)
