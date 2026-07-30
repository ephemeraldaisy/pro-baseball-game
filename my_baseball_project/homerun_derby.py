import random
import time
import streamlit as st

# =====================================================================
# 🚀 스페셜 미니게임: 홈런 더비 (Home Run Derby) Engine & UI
# =====================================================================
class HomerunDerbyEngine:
    def __init__(self, total_pitches: int = 10):
        self.total_pitches = total_pitches
        self.current_pitch = 0
        self.homeruns = 0
        self.out_count = 0
        self.total_distance = 0
        self.max_distance = 0
        self.earned_diamonds = 0
        self.game_over = False
        self.result_msg = ""
        self.game_log = [
            f"🏟️ [홈런 더비 개시!] 총 {self.total_pitches}구의 투구가 주어집니다. 담장을 넘겨 다이아를 쓸어담으세요!"
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

        # 스윙 유형 및 투구 구질에 따른 홈런 및 비거리 성공률 연산
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

            # 장외 대형 홈런 연출 (138m 이상)
            if distance >= 138:
                reward = 50
                self.earned_diamonds += reward
                self.game_log.append(
                    log_prefix + f"🚀💥 [장외 대형 홈런!!] 비거리 {distance}m! 관중석을 완전히 넘겼습니다! (+{reward} 💎)"
                )
            else:
                reward = 15
                self.earned_diamonds += reward
                self.game_log.append(
                    log_prefix + f"🔥 [홈런!] 깡!! 비거리 {distance}m 담장을 뛰어넘습니다! (+{reward} 💎)"
                )

        # 2. 담장 맞고 나오는 펜스 직격 타구 (아쉽게 홈런 실패)
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

        # 종료 조건 체크
        if self.current_pitch >= self.total_pitches:
            self.game_over = True
            
            # 퍼펙트 / 우수 성적 보너스 다이아
            bonus = 0
            if self.homeruns >= 8:
                bonus = 300
                bonus_msg = f"🏆 [퍼펙트 더비!] {self.homeruns}홈런 달성 보너스 +{bonus} 💎"
            elif self.homeruns >= 5:
                bonus = 100
                bonus_msg = f"🌟 [우수 타자!] {self.homeruns}홈런 달성 보너스 +{bonus} 💎"
            else:
                bonus_msg = ""

            self.earned_diamonds += bonus
            self.result_msg = (
                f"🎉 [홈런 더비 종료] 총 {self.homeruns}홈런 | 최대 비거리: {self.max_distance}m | "
                f"총 획득 상금: +{self.earned_diamonds} 💎 {bonus_msg}"
            )


# =====================================================================
# 🖥️ Streamlit 전용 UI 렌더링 함수
# =====================================================================
def render_homerun_derby_ui():
    st.subheader("🚀 미니게임: 챌린지 홈런 더비")

    # 세션 내 게임 인스턴스 초기화
    if "homerun_derby_instance" not in st.session_state or st.session_state.homerun_derby_instance is None:
        st.info("💡 주어진 10구의 기회 동안 담장을 넘겨 다이아 💎 보상을 획득하세요!")
        
        c_i1, c_i2 = st.columns(2)
        with c_i1:
            st.markdown("""
            **🎟️ 보상 안내**
            - 일반 홈런: **+15 💎**
            - 138m 이상 장외 대형 홈런: **+50 💎**
            - 5홈런 이상 보너스: **+100 💎**
            - 8홈런 이상 퍼펙트 보너스: **+300 💎**
            """)
        with c_i2:
            st.metric("현재 보유 다이아", f"{st.session_state.nc_diamonds} 💎")

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
    m2.metric("홈런 개수", f"🔥 {game.homeruns} 개")
    m3.metric("최대 비거리", f"📏 {game.max_distance} m")
    m4.metric("획득 다이아", f"💎 +{game.earned_diamonds}")

    st.divider()

    # 게임 완료 시 결과 처리
    if game.game_over:
        st.success(game.result_msg)

        # 다이아 지급 세션 반영 (중복 지급 방지)
        if not getattr(game, 'reward_claimed', False):
            st.session_state.nc_diamonds += game.earned_diamonds
            game.reward_claimed = True
            st.toast(f"🎉 총 +{game.earned_diamonds} 💎 가 지갑에 추가되었습니다!", icon="💎")

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
