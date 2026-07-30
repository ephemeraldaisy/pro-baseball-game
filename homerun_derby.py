import random
import time
import streamlit as st

# =====================================================================
# 🚀 스페셜 미니게임: 챌린지 홈런 더비 (Home Run Derby) Engine & UI
# =====================================================================
class HomerunDerbyEngine:
    def __init__(self, total_pitches: int = 10):
        self.total_pitches = total_pitches
        self.current_pitch = 0
        self.homeruns = 0
        self.long_homeruns = 0  # 138m 이상 대형 장외 홈런 카운트
        self.out_count = 0
        self.total_distance = 0
        self.max_distance = 0
        
        self.earned_diamonds = 0
        self.tier_name = ""
        self.game_over = False
        self.result_msg = ""
        self.game_log = [
            f"🏟️ [홈런 더비 개시!] 총 {self.total_pitches}구의 기회가 주어집니다. 10구 후 최종 티어 보상을 쟁취하세요!"
        ]

    def process_swing(self, swing_type: str) -> None:
        """
        swing_type:
          - "풀스윙": 비거리 극대화, 장외홈런 확률 상승 (타이밍 난이도 상)
          - "밀어치기": 안정적인 넘기기 (비거리 보통)
          - "라인드라이브": 낮은 탄도, 라인드라이브성 홈런 노리기
        """
        if self.game_over:
            return

        self.current_pitch += 1
        pitch_types = ["직구", "슬라이더", "체인지업", "포크볼"]
        pitch = random.choice(pitch_types)
        speed = random.randint(138, 156)

        log_prefix = f"[{self.current_pitch}/{self.total_pitches}구] 투수 {speed}km/h {pitch} 투구 ➔ "

        # 스윙 유형별 성공 확률 및 비거리 범위
        hr_prob = 0.50
        max_dist_range = (115, 135)

        if swing_type == "풀스윙":
            hr_prob = 0.45 if pitch == "직구" else 0.35
            max_dist_range = (125, 150)  # 대형 장외 홈런 가능
        elif swing_type == "밀어치기":
            hr_prob = 0.60
            max_dist_range = (110, 128)
        elif swing_type == "라인드라이브":
            hr_prob = 0.55
            max_dist_range = (112, 132)

        roll = random.random()

        # 1. 홈런 성공 판정
        if roll < hr_prob:
            self.homeruns += 1
            distance = random.randint(max_dist_range[0], max_dist_range[1])
            self.total_distance += distance
            if distance > self.max_distance:
                self.max_distance = distance

            # 138m 이상 대형 장외 홈런 카운트
            if distance >= 138:
                self.long_homeruns += 1
                self.game_log.append(
                    log_prefix + f"🚀💥 [대형 장외 홈런!!] 비거리 {distance}m! 관중석을 완전히 넘겼습니다! (장외 #{self.long_homeruns})"
                )
            else:
                self.game_log.append(
                    log_prefix + f"🔥 [홈런!] 깡!! 비거리 {distance}m 담장을 뛰어넘습니다!"
                )

        # 2. 펜스 직격 (아쉽게 아웃)
        elif roll < hr_prob + 0.25:
            self.out_count += 1
            distance = random.randint(100, 114)
            self.game_log.append(
                log_prefix + f"📐 [펜스 직격!] 비거리 {distance}m! 아쉽게 펜스 상단을 맞고 떨어집니다. (아웃)"
            )

        # 3. 빗맞은 파울 / 뜬공 아웃
        else:
            self.out_count += 1
            out_logs = [
                "빗맞은 내야 높이 뜬 공!",
                "헛스윙! 공기를 가르는 타격!",
                "파울 라인 밖으로 벗어나는 타구!"
            ]
            self.game_log.append(log_prefix + f"❌ {random.choice(out_logs)} (아웃)")

        # 10구 종료 시 최종 가중치 정산 및 티어 부여
        if self.current_pitch >= self.total_pitches:
            self._evaluate_final_tier()

    def _evaluate_final_tier(self) -> None:
        """10구 종료 후 최종 홈런 수 및 장외 홈런 수 기반 가중치 정산"""
        self.game_over = True

        # SSS급: 8홈런 이상 + 장외 2개 이상 (+500 💎)
        if self.homeruns >= 8 and self.long_homeruns >= 2:
            self.tier_name = "SSS급 [신(God)의 영역]"
            self.earned_diamonds = 500

        # SS급: 8홈런 이상 (일반 홈런 위주) (+350 💎)
        elif self.homeruns >= 8:
            self.tier_name = "SS급 [전설의 거포]"
            self.earned_diamonds = 350

        # S급: 5~7홈런 달성 (+200 💎)
        elif self.homeruns >= 5:
            self.tier_name = "S급 [클러치 슬러거]"
            self.earned_diamonds = 200

        # A급: 3~4홈런 달성 (+80 💎)
        elif self.homeruns >= 3:
            self.tier_name = "A급 [준수한 담장 넘기기]"
            self.earned_diamonds = 80

        # B급: 1~2홈런 이하 (+20 💎)
        else:
            self.tier_name = "B급 [아쉬운 타격감]"
            self.earned_diamonds = 20

        self.result_msg = (
            f"🎉 [홈런 더비 완료] 달성 티어: **{self.tier_name}** | "
            f"기록: {self.homeruns}홈런 (장외 {self.long_homeruns}개) | "
            f"최대 비거리: {self.max_distance}m ➔ 보상: **+{self.earned_diamonds} 💎**"
        )


# =====================================================================
# 🖥️ Streamlit 전용 UI 렌더링 함수
# =====================================================================
def render_homerun_derby_ui():
    st.subheader("🚀 미니게임: 챌린지 홈런 더비")

    # 세션 내 게임 인스턴스 초기화
    if "homerun_derby_instance" not in st.session_state or st.session_state.homerun_derby_instance is None:
        st.info("💡 주어진 10구 동안 담장을 넘겨 성적에 맞는 최종 티어 다이아 💎 보상을 획득하세요!")
        
        st.markdown("""
        | 티어 명칭 | 달성 조건 | 최종 정산 보상 |
        | :--- | :--- | :--- |
        | **SSS급 [신(God)의 영역]** | 10구 중 **8홈런 이상** + **대형 장외 홈런 2개 이상** | **+500 💎** |
        | **SS급 [전설의 거포]** | 10구 중 **8홈런 이상** (일반 홈런 위주) | **+350 💎** |
        | **S급 [클러치 슬러거]** | 10구 중 **5~7홈런** 달성 | **+200 💎** |
        | **A급 [준수한 담장 넘기기]** | 10구 중 **3~4홈런** 달성 | **+80 💎** |
        | **B급 [아쉬운 타격감]** | 10구 중 **1~2홈런 이하** | **+20 💎** |
        """)

        if st.button("🚀 홈런 더비 참가 (입장료 50 💎)", type="primary", key="btn_start_hr_derby"):
            if st.session_state.nc_diamonds >= 50:
                st.session_state.nc_diamonds -= 50
                st.session_state.homerun_derby_instance = HomerunDerbyEngine(total_pitches=10)
                st.rerun()
            else:
                st.error("❌ 보유 다이아가 부족합니다! (비밀 상점 이용 필요)")
        return

    game: HomerunDerbyEngine = st.session_state.homerun_derby_instance

    # 실시간 현황 스코어보드
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("남은 기회", f"{game.total_pitches - game.current_pitch} / {game.total_pitches}구")
    m2.metric("홈런 (장외)", f"🔥 {game.homeruns} 개 ({game.long_homeruns}장외)")
    m3.metric("최대 비거리", f"📏 {game.max_distance} m")
    m4.metric("현재 보유 다이아", f"{st.session_state.nc_diamonds} 💎")

    st.divider()

    # 게임 완료 시 결과 정산
    if game.game_over:
        st.success(game.result_msg)

        # 다이아 지급 세션 반영 (중복 지급 방지)
        if not getattr(game, 'reward_claimed', False):
            st.session_state.nc_diamonds += game.earned_diamonds
            game.reward_claimed = True
            st.toast(f"🎉 {game.tier_name} 달성! +{game.earned_diamonds} 💎 지급 완료!", icon="💎")

        if st.button("메인 모드로 돌아가기", key="btn_exit_hr_derby"):
            st.session_state.homerun_derby_instance = None
            st.rerun()

    # 게임 진행 중 타격 조작 버튼
    else:
        st.markdown("### 💥 타격 방식 선택")
        b1, b2, b3 = st.columns(3)

        with b1:
            if st.button("🚀 풀스윙 강타 (장외 홈런 노리기)", key="btn_derby_full"):
                game.process_swing("풀스윙")
                st.rerun()
        with b2:
            if st.button("🌟 가볍게 밀어치기 (안정적)", key="btn_derby_push"):
                game.process_swing("밀어치기")
                st.rerun()
        with b3:
            if st.button("⚡ 라인드라이브 (맞춤 타격)", key="btn_derby_line"):
                game.process_swing("라인드라이브")
                st.rerun()

        st.divider()
        st.markdown("### 📜 더비 실시간 중계")
        for log in reversed(game.game_log[-5:]):
            st.write(log)
