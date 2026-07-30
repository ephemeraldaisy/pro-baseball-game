import random
import time
import streamlit as st

# =====================================================================
# 🎯 스페셜 미니게임: 킹 오브 스트라이크아웃 (King of Strikeouts) Engine & UI
# =====================================================================
class KingOfStrikeoutEngine:
    def __init__(self, total_batters: int = 5):
        self.total_batters = total_batters
        self.current_batter = 1
        self.strikeouts = 0
        self.looking_k_count = 0
        self.consecutive_k = 0
        self.max_consecutive_k = 0
        self.earned_diamonds = 0
        
        # 현재 타석 상태
        self.strike = 0
        self.ball = 0
        self.target_zone = random.randint(1, 9)  # 심판/포수가 요구하는 9분할 핵심 존
        
        self.game_over = False
        self.result_msg = ""
        self.game_log = [
            f"🏟️ [삼진왕 챌린지 개시!] 총 {self.total_batters}명의 타자를 상대합니다. 코스를 완벽히 찔러 삼진을 잡아내세요!"
        ]

    def process_pitch(self, pitch_type: str, selected_zone: int) -> None:
        if self.game_over:
            return

        speeds = {
            "직구": random.randint(146, 155),
            "슬라이더": random.randint(135, 143),
            "체인지업": random.randint(128, 136),
            "커브": random.randint(118, 126)
        }
        speed = speeds.get(pitch_type, 140)

        # 🎯 존 조준 일치 여부 판정
        is_exact_target = (selected_zone == self.target_zone)
        log_prefix = f"[{self.current_batter}번 타자 / {self.strike}S {self.ball}B] {pitch_type}({speed}km/h) {selected_zone}번 코스 투구 ➔ "

        # 1. 완벽한 코스 제구 (Target Zone 일치)
        if is_exact_target:
            self.strike += 1
            if self.strike >= 3:
                # 삼진 완료!
                self.strikeouts += 1
                self.consecutive_k += 1
                if self.consecutive_k > self.max_consecutive_k:
                    self.max_consecutive_k = self.consecutive_k

                # 루킹 삼진 vs 헛스윙 삼진 무작위 판정
                is_looking = random.random() < 0.50
                if is_looking:
                    self.looking_k_count += 1
                    reward = 35
                    self.earned_diamonds += reward
                    self.game_log.append(
                        log_prefix + f"👀💥 [루킹 삼진!!] 꽉 찬 코스! 타자가 꼼짝없이 당했습니다! (K#{self.strikeouts}, +{reward} 💎)"
                    )
                else:
                    reward = 20
                    self.earned_diamonds += reward
                    self.game_log.append(
                        log_prefix + f"⚡ [헛스윙 삼진!] 날카로운 제구! 방망이가 허공을 가릅니다! (K#{self.strikeouts}, +{reward} 💎)"
                    )

                self._next_batter()
            else:
                reward = 10
                self.earned_diamonds += reward
                self.game_log.append(
                    log_prefix + f"🎯 [스트라이크 적중!] 칼날 제구! ({self.strike}S {self.ball}B, +{reward} 💎)"
                )

        # 2. 제구 약간 인접 (스트라이크 또는 파울)
        elif abs(selected_zone - self.target_zone) <= 2:
            roll = random.random()
            if roll < 0.60:
                self.strike += 1
                if self.strike >= 3:
                    self.strikeouts += 1
                    self.consecutive_k += 1
                    if self.consecutive_k > self.max_consecutive_k:
                        self.max_consecutive_k = self.consecutive_k

                    reward = 15
                    self.earned_diamonds += reward
                    self.game_log.append(
                        log_prefix + f"⚡ [삼진 아웃!] 빗맞은 커트로 3스트라이크! (K#{self.strikeouts}, +{reward} 💎)"
                    )
                    self._next_batter()
                else:
                    self.game_log.append(log_prefix + f"⚾ 파울볼! 타자가 간신히 커트합니다. ({self.strike}S {self.ball}B)")
            else:
                self.ball += 1
                if self.ball >= 4:
                    self.game_log.append(log_prefix + f"🚶‍♂️ [볼넷 허용] 제구가 흔들려 타자를 1루로 내보냅니다.")
                    self.consecutive_k = 0  # 스트릭 리셋
                    self._next_batter()
                else:
                    self.game_log.append(log_prefix + f"🔍 약간 빠지는 볼! ({self.strike}S {self.ball}B)")

        # 3. 완전한 제구 미스 (볼 또는 피안타)
        else:
            if random.random() < 0.30:
                # 피안타 발생!
                self.game_log.append(log_prefix + f"💥 [피안타!] 실투를 타자가 놓치지 않고 안타로 연결합니다!")
                self.consecutive_k = 0
                self._next_batter()
            else:
                self.ball += 1
                if self.ball >= 4:
                    self.game_log.append(log_prefix + f"🚶‍♂️ [볼넷 허용] 볼넷으로 출루 허용!")
                    self.consecutive_k = 0
                    self._next_batter()
                else:
                    self.game_log.append(log_prefix + f"❌ 제구 실패! 크게 빠지는 볼. ({self.strike}S {self.ball}B)")

        # 타석 지속 시 다음 타겟 존 변경
        if not self.game_over and self.strike < 3 and self.ball < 4:
            self.target_zone = random.randint(1, 9)

    def _next_batter(self) -> None:
        """다음 타자로 교체 및 게임 종료 판정"""
        self.strike = 0
        self.ball = 0
        self.target_zone = random.randint(1, 9)
        self.current_batter += 1

        if self.current_batter > self.total_batters:
            self.game_over = True
            
            # 연속 삼진(K-K-K) 스트릭 보너스
            bonus = 0
            if self.max_consecutive_k >= 3:
                bonus = 250
                bonus_msg = f"🔥 [연속 K-K-K 보너스!] 3연속 탈삼진 달성 +{bonus} 💎"
            elif self.strikeouts >= 4:
                bonus = 100
                bonus_msg = f"🌟 [닥터 K 보너스!] 4탈삼진 달성 +{bonus} 💎"
            else:
                bonus_msg = ""

            self.earned_diamonds += bonus
            self.result_msg = (
                f"🎉 [삼진왕 챌린지 종료] 총 {self.strikeouts}탈삼진 (루킹 {self.looking_k_count}개) | "
                f"최대 연속 삼진: {self.max_consecutive_k}개 | 총 획득 상금: +{self.earned_diamonds} 💎 {bonus_msg}"
            )


# =====================================================================
# 🖥️ Streamlit 전용 UI 렌더링 함수
# =====================================================================
def render_king_of_strikeout_ui():
    st.subheader("🎯 미니게임: 킹 오브 스트라이크아웃 (King of Strikeouts)")

    # 세션 인스턴스 초기화
    if "king_k_instance" not in st.session_state or st.session_state.king_k_instance is None:
        st.info("💡 5명의 타자를 상대로 포수의 수신호(타겟 존)에 정확히 공을 찔러 넣어 탈삼진 다이아 💎 보상을 획득하세요!")

        c_i1, c_i2 = st.columns(2)
        with c_i1:
            st.markdown("""
            **🎟️ 보상 안내**
            - 존 일치 스트라이크: **+10 💎**
            - 헛스윙 삼진: **+20 💎**
            - 루킹 삼진(Perfect K): **+35 💎**
            - 3연속 삼진(K-K-K) 보너스: **+250 💎**
            """)
        with c_i2:
            st.metric("현재 보유 다이아", f"{st.session_state.nc_diamonds} 💎")

        if st.button("🎯 삼진왕 도전 (입장료 30 💎)", type="primary", key="btn_start_king_k"):
            if st.session_state.nc_diamonds >= 30:
                st.session_state.nc_diamonds -= 30
                st.session_state.king_k_instance = KingOfStrikeoutEngine(total_batters=5)
                st.rerun()
            else:
                st.error("❌ 보유 다이아가 부족합니다! (비밀 상점 이용 필요)")
        return

    game: KingOfStrikeoutEngine = st.session_state.king_k_instance

    # 실시간 스코어보드
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("상대 타자", f"{game.current_batter} / {game.total_batters} 명")
    m2.metric("탈삼진(K)", f"⚡ {game.strikeouts} 개")
    m3.metric("연속 K 스트릭", f"🔥 {game.consecutive_k} 개")
    m4.metric("획득 다이아", f"💎 +{game.earned_diamonds}")

    st.divider()

    # 게임 완료 시 결과 처리
    if game.game_over:
        st.success(game.result_msg)

        if not getattr(game, 'reward_claimed', False):
            st.session_state.nc_diamonds += game.earned_diamonds
            game.reward_claimed = True
            st.toast(f"🎉 총 +{game.earned_diamonds} 💎 가 지갑에 추가되었습니다!", icon="💎")

        if st.button("메인 모드로 돌아가기", key="btn_exit_king_k"):
            st.session_state.king_k_instance = None
            st.rerun()

    # 게임 진행 중 피칭 조작
    else:
        st.markdown(f"### 🎯 포수의 요구 타겟 존: **`[{game.target_zone}번 존]`**")
        st.caption(f"현재 카운트: 스트라이크 {'🟡' * game.strike} | 볼 {'🟢' * game.ball}")

        col_left, col_right = st.columns([2, 1])

        with col_left:
            st.write(" **9분할 스트라이크 존 코스 선택**")
            # 3x3 존 그리드 버튼 생성
            for row in range(3):
                grid_cols = st.columns(3)
                for col in range(3):
                    zone_num = row * 3 + col + 1
                    is_target = (zone_num == game.target_zone)
                    btn_label = f"🎯 {zone_num}번 존" if is_target else f"{zone_num}번"
                    
                    if grid_cols[col].button(btn_label, key=f"btn_zone_{zone_num}"):
                        st.session_state.selected_pitch_zone = zone_num

        with col_right:
            st.write(" **구질 선택 및 투구**")
            pitch_choice = st.radio("구질 선택", ["직구", "슬라이더", "체인지업", "커브"], key="radio_pitch_type")
            
            sel_zone = st.session_state.get("selected_pitch_zone", game.target_zone)
            st.caption(f"선택된 코스: **{sel_zone}번**")

            if st.button("⚾ 공 던지기!", type="primary", key="btn_throw_pitch"):
                game.process_pitch(pitch_choice, sel_zone)
                st.rerun()

        st.divider()
        st.markdown("### 📜 삼진왕 실시간 중계")
        for log in reversed(game.game_log[-5:]):
            st.write(log)
