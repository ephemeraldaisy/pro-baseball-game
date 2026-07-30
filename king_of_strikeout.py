import random
import time
import streamlit as st

# =====================================================================
# 🎯 스페셜 미니게임: 오늘은 삼진왕 (King of Strikeouts) Engine & UI
# =====================================================================
class KingOfStrikeoutEngine:
    def __init__(self, total_batters: int = 3):
        self.total_batters = total_batters  # 1이닝 (3타자 상대)
        self.current_batter = 1
        self.strikeouts = 0
        self.looking_k_count = 0
        self.exact_zone_hits = 0  # 존 일치 스트라이크 카운트
        self.current_batter_pitches = 0  # 현재 타자 상대 투구수 (삼구삼진 판정용)
        self.has_three_pitch_k = True    # 3타자 모두 삼구삼진인지 여부
        
        # 현재 타석 카운트
        self.strike = 0
        self.ball = 0
        self.target_zone = random.randint(1, 9)  # 포수 요구 9분할 존
        
        self.earned_diamonds = 0
        self.tier_name = ""
        self.game_over = False
        self.result_msg = ""
        self.game_log = [
            f"🏟️ [오늘은 삼진왕 개시!] 1이닝 3명의 타자를 상대합니다. 포수 미트에 정확히 공을 찔러 삼진을 잡아내세요!"
        ]

    def process_pitch(self, pitch_type: str, selected_zone: int) -> None:
        if self.game_over:
            return

        self.current_batter_pitches += 1
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
            self.exact_zone_hits += 1
            self.strike += 1
            if self.strike >= 3:
                self.strikeouts += 1

                # 3구 삼진 체크
                if self.current_batter_pitches > 3:
                    self.has_three_pitch_k = False

                # 루킹 삼진 vs 헛스윙 삼진 판정
                is_looking = random.random() < 0.50
                if is_looking:
                    self.looking_k_count += 1
                    self.game_log.append(
                        log_prefix + f"👀💥 [루킹 삼진!!] 꽉 찬 코스! 타자가 꼼짝없이 당했습니다! (K#{self.strikeouts})"
                    )
                else:
                    self.game_log.append(
                        log_prefix + f"⚡ [헛스윙 삼진!] 날카로운 제구! 방망이가 허공을 가릅니다! (K#{self.strikeouts})"
                    )

                self._next_batter()
            else:
                self.game_log.append(
                    log_prefix + f"🎯 [스트라이크 적중!] 칼날 제구! ({self.strike}S {self.ball}B)"
                )

        # 2. 제구 약간 인접 (스트라이크 또는 파울)
        elif abs(selected_zone - self.target_zone) <= 2:
            roll = random.random()
            if roll < 0.60:
                self.strike += 1
                if self.strike >= 3:
                    self.strikeouts += 1
                    self.has_three_pitch_k = False
                    self.game_log.append(
                        log_prefix + f"⚡ [삼진 아웃!] 빗맞은 커트로 3스트라이크! (K#{self.strikeouts})"
                    )
                    self._next_batter()
                else:
                    self.game_log.append(log_prefix + f"⚾ 파울볼! 타자가 간신히 커트합니다. ({self.strike}S {self.ball}B)")
            else:
                self.ball += 1
                if self.ball >= 4:
                    self.has_three_pitch_k = False
                    self.game_log.append(log_prefix + f"🚶‍♂️ [볼넷 허용] 제구가 흔들려 타자를 출루시킵니다.")
                    self._next_batter()
                else:
                    self.game_log.append(log_prefix + f"🔍 약간 빠지는 볼! ({self.strike}S {self.ball}B)")

        # 3. 완전한 제구 미스 (볼 또는 피안타)
        else:
            self.has_three_pitch_k = False
            if random.random() < 0.30:
                self.game_log.append(log_prefix + f"💥 [피안타!] 실투를 타자가 놓치지 않고 안타로 연결합니다!")
                self._next_batter()
            else:
                self.ball += 1
                if self.ball >= 4:
                    self.game_log.append(log_prefix + f"🚶‍♂️ [볼넷 허용] 볼넷으로 출루 허용!")
                    self._next_batter()
                else:
                    self.game_log.append(log_prefix + f"❌ 제구 실패! 크게 빠지는 볼. ({self.strike}S {self.ball}B)")

        # 타석 지속 시 다음 타겟 존 무작위 변경
        if not self.game_over and self.strike < 3 and self.ball < 4:
            self.target_zone = random.randint(1, 9)

    def _next_batter(self) -> None:
        """다음 타자 교체 및 1이닝(3타자) 완료 판정"""
        self.strike = 0
        self.ball = 0
        self.current_batter_pitches = 0
        self.target_zone = random.randint(1, 9)
        self.current_batter += 1

        if self.current_batter > self.total_batters:
            self._evaluate_final_tier()

    def _evaluate_final_tier(self) -> None:
        """1이닝(3타자) 종료 후 최종 피칭 티어 및 보상 정산"""
        self.game_over = True

        # SSS급: 3타자 연속 루킹 삼진 (Perfect K x 3) + 삼구삼진 (+400 💎)
        if self.strikeouts == 3 and self.looking_k_count == 3 and self.has_three_pitch_k:
            self.tier_name = "SSS급 [신(God)의 피칭: 삼구삼진 K-K-K]"
            self.earned_diamonds = 400

        # SS급: 3타자 연속 삼진 (헛스윙/루킹 혼합) (+300 💎)
        elif self.strikeouts == 3:
            self.tier_name = "SS급 [닥터 K: 삼진 아티스트]"
            self.earned_diamonds = 300

        # S급: 한 이닝 삼진 2개 달성 (루킹 삼진 1개 이상) (+120 💎)
        elif self.strikeouts == 2 and self.looking_k_count >= 1:
            self.tier_name = "S급 [클러치 에이스]"
            self.earned_diamonds = 120

        # A급: 한 이닝 삼진 1개 달성 OR 존 일치 스트라이크 3개 이상 (+50 💎)
        elif self.strikeouts >= 1 or self.exact_zone_hits >= 3:
            self.tier_name = "A급 [안정적인 피칭]"
            self.earned_diamonds = 50

        # B급: 삼진 없이 존 일치 스트라이크 1~2개 (+15 💎)
        else:
            self.tier_name = "B급 [아쉬운 제구력]"
            self.earned_diamonds = 15

        self.result_msg = (
            f"🎉 [오늘은 삼진왕 종료] 달성 티어: **{self.tier_name}** | "
            f"기록: {self.strikeouts}탈삼진 (루킹 {self.looking_k_count}개) | "
            f"존 적중: {self.exact_zone_hits}회 ➔ 보상: **+{self.earned_diamonds} 💎**"
        )


# =====================================================================
# 🖥️ Streamlit 전용 UI 렌더링 함수
# =====================================================================
def render_king_of_strikeout_ui():
    st.subheader("🎯 미니게임: 오늘은 삼진왕 (1이닝 3타자 챌린지)")

    # 세션 인스턴스 초기화
    if "king_k_instance" not in st.session_state or st.session_state.king_k_instance is None:
        st.info("💡 1이닝 동안 3명의 타자를 상대로 포수의 수신호(타겟 존)에 칼날 제구를 찔러 넣어 최종 티어 보상을 획득하세요!")

        st.markdown("""
        | 티어 명칭 | 달성 조건 | 최종 정산 보상 |
        | :--- | :--- | :--- |
        | **SSS급 [신(God)의 피칭]** | 3타자 **연속 루킹 삼진** (Perfect K x 3, 삼구삼진) | **+400 💎** |
        | **SS급 [닥터 K: 삼진 아티스트]** | 3타자 **연속 삼진** (헛스윙/루킹 혼합) | **+300 💎** |
        | **S급 [클러치 에이스]** | 한 이닝 **삼진 2개** (루킹 삼진 1개 이상) | **+120 💎** |
        | **A급 [안정적인 피칭]** | 한 이닝 **삼진 1개** (또는 존 적중 3회 이상) | **+50 💎** |
        | **B급 [아쉬운 제구력]** | 삼진 없이 **존 적중 1~2개** | **+15 💎** |
        """)

        if st.button("🎯 오늘은 삼진왕 도전 (입장료 30 💎)", type="primary", key="btn_start_king_k"):
            if st.session_state.nc_diamonds >= 30:
                st.session_state.nc_diamonds -= 30
                st.session_state.king_k_instance = KingOfStrikeoutEngine(total_batters=3)
                st.rerun()
            else:
                st.error("❌ 보유 다이아가 부족합니다! (비밀 상점 이용 필요)")
        return

    game: KingOfStrikeoutEngine = st.session_state.king_k_instance

    # 실시간 스코어보드
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("상대 타자", f"{game.current_batter} / {game.total_batters} 명")
    m2.metric("탈삼진(K)", f"⚡ {game.strikeouts} 개 (루킹 {game.looking_k_count})")
    m3.metric("존 적중 횟수", f"🎯 {game.exact_zone_hits} 회")
    m4.metric("현재 보유 다이아", f"{st.session_state.nc_diamonds} 💎")

    st.divider()

    # 게임 완료 시 결과 정산
    if game.game_over:
        st.success(game.result_msg)

        if not getattr(game, 'reward_claimed', False):
            st.session_state.nc_diamonds += game.earned_diamonds
            game.reward_claimed = True
            st.toast(f"🎉 {game.tier_name} 달성! +{game.earned_diamonds} 💎 지급 완료!", icon="💎")

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
