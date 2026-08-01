import random
import streamlit as st

# =====================================================================
# ⚡ 9회말 2아웃 만루 클러치 히터 (등급별 보상/페널티 표 완전 반영)
# =====================================================================

GRADE_TABLE = {
    "S_WIN":  {"name": "S급 승리", "desc": "끝내기 대형 만루홈런 (Grand Slam)", "reward": 1000},
    "A_WIN":  {"name": "A급 승리", "desc": "끝내기 싹쓸이 3타점 2루타", "reward": 500},
    "B_WIN":  {"name": "B급 승리", "desc": "밀어내기 볼넷 / 끝내기 몸에 맞는 공", "reward": 200},
    "C_WIN":  {"name": "C급 승리", "desc": "포수 빗맞은 내야안타 or 포일/폭투/번트 끝내기", "reward": 100},
    "C_LOSE": {"name": "C급 패배", "desc": "평범한 외야 뜬공 / 루킹 삼진 아웃", "penalty": 100},
    "B_LOSE": {"name": "B급 패배", "desc": "3-2 풀카운트에서 헛스윙 삼진 아웃", "penalty": 200},
    "A_LOSE": {"name": "A급 패배", "desc": "잘 맞은 타구가 상대 야수 호수비에 잡힘", "penalty": 500},
    "S_LOSE": {"name": "S급 패배", "desc": "끝내기 주루사 / 견제사 (포수/투수 견제)", "penalty": 1000},
}

def init_clutch_game_state():
    """미니게임 세션 상태 초기화"""
    if "clutch_in_progress" not in st.session_state:
        st.session_state.clutch_in_progress = False
    if "clutch_inning" not in st.session_state:
        st.session_state.clutch_inning = 9
    if "clutch_phase" not in st.session_state:
        st.session_state.clutch_phase = "말"
    if "clutch_our_score" not in st.session_state:
        st.session_state.clutch_our_score = 3
    if "clutch_enemy_score" not in st.session_state:
        st.session_state.clutch_enemy_score = 5
    if "clutch_outs" not in st.session_state:
        st.session_state.clutch_outs = 2
    if "clutch_strikes" not in st.session_state:
        st.session_state.clutch_strikes = 0
    if "clutch_balls" not in st.session_state:
        st.session_state.clutch_balls = 0
    if "clutch_base1" not in st.session_state:
        st.session_state.clutch_base1 = True
    if "clutch_base2" not in st.session_state:
        st.session_state.clutch_base2 = True
    if "clutch_base3" not in st.session_state:
        st.session_state.clutch_base3 = True
    if "clutch_logs" not in st.session_state:
        st.session_state.clutch_logs = []
    if "clutch_result_grade" not in st.session_state:
        st.session_state.clutch_result_grade = None  # Grade Key
    if "clutch_pitcher_stamina" not in st.session_state:
        st.session_state.clutch_pitcher_stamina = 12
    if "clutch_top_defense_done" not in st.session_state:
        st.session_state.clutch_top_defense_done = False

def start_clutch_game():
    st.session_state.clutch_in_progress = True
    st.session_state.clutch_inning = 9
    st.session_state.clutch_phase = "말"
    
    # 9회말 시작 세팅: 2점 차 열세, 2아웃 만루
    st.session_state.clutch_enemy_score = random.randint(4, 6)
    st.session_state.clutch_our_score = st.session_state.clutch_enemy_score - 2
    st.session_state.clutch_outs = 2
    st.session_state.clutch_strikes = 0
    st.session_state.clutch_balls = 0
    st.session_state.clutch_base1 = True
    st.session_state.clutch_base2 = True
    st.session_state.clutch_base3 = True
    st.session_state.clutch_pitcher_stamina = random.randint(10, 15)
    st.session_state.clutch_result_grade = None
    st.session_state.clutch_top_defense_done = False
    
    st.session_state.clutch_logs = [
        f"🚨 [9회말 2아웃 만루] {st.session_state.clutch_enemy_score}:{st.session_state.clutch_our_score} 2점 차 열세!",
        f"⚾ 상대 마무리 투수 등판! 결과를 통해 등급별 다이아 보상 및 페널티가 부여됩니다."
    ]

def render_homerun_game_ui():
    init_clutch_game_state()

    st.subheader("⚡ 9회말 2아웃 만루 클러치 히터 (시나리오 등급제)")
    st.caption("결과 시나리오(S~C급)에 따라 최대 +1,000💎 보상 또는 -1,000💎 페널티가 적용됩니다!")

    # -----------------------------------------------------------------
    # 1️⃣ 게임 시작 전 (등급표 안내 화면)
    # -----------------------------------------------------------------
    if not st.session_state.clutch_in_progress:
        st.markdown(f"💰 **보유 다이아**: `{st.session_state.get('nc_diamonds', 0)} 💎`")
        
        with st.expander("📊 시나리오별 보상 / 페널티 표 열람", expanded=True):
            st.markdown("""
            | 구분 | 시나리오 (상황) | 보상 / 페널티 |
            | :--- | :--- | :---: |
            | **S급 승리** | 끝내기 대형 만루홈런 (Grand Slam) | **+1,000 💎** |
            | **A급 승리** | 끝내기 싹쓸이 3타점 2루타 | **+500 💎** |
            | **B급 승리** | 밀어내기 볼넷 / 끝내기 몸에 맞는 공 | **+200 💎** |
            | **C급 승리** | 포수 빗맞은 내야안타 or 포일/폭투/번트 끝내기 | **+100 💎** |
            | **C급 패배** | 평범한 외야 뜬공 / 루킹 삼진 아웃 | **-100 💎** |
            | **B급 패배** | 3-2 풀카운트에서 헛스윙 삼진 아웃 | **-200 💎** |
            | **A급 패배** | 잘 맞은 타구가 상대 야수 호수비에 잡힘 | **-500 💎** |
            | **S급 패배** | 끝내기 주루사 / 견제사 (포수/투수 견제) | **-1,000 💎** |
            """)

        if st.button("🔥 도전자 등판 (입장료 무료)", type="primary", key="btn_start_clutch"):
            start_clutch_game()
            st.rerun()
        return

    # -----------------------------------------------------------------
    # 2️⃣ 게임 진행 중 스코어보드
    # -----------------------------------------------------------------
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.metric("🚌 상대 팀", f"{st.session_state.clutch_enemy_score} 점")
    with sc2:
        st.metric("🏟️ 현 이닝", f"{st.session_state.clutch_inning}회{st.session_state.clutch_phase}")
    with sc3:
        st.metric("🏠 우리 팀", f"{st.session_state.clutch_our_score} 점")

    b1 = "1️⃣" if st.session_state.clutch_base1 else "⚪"
    b2 = "2️⃣" if st.session_state.clutch_base2 else "⚪"
    b3 = "3️⃣" if st.session_state.clutch_base3 else "⚪"

    st.markdown(
        f"**OUT:** {'🔴' * st.session_state.clutch_outs}{'⚪' * (3 - st.session_state.clutch_outs)} | "
        f"**STRIKE:** {'🟡' * st.session_state.clutch_strikes}{'⚪' * (3 - st.session_state.clutch_strikes)} | "
        f"**BALL:** {'🟢' * st.session_state.clutch_balls}{'⚪' * (4 - st.session_state.clutch_balls)} | "
        f"🏃 **주자:** [{b3} {b2} {b1}] | "
        f"🔋 **투수 체력:** [{st.session_state.clutch_pitcher_stamina}/30]"
    )
    st.divider()

    # -----------------------------------------------------------------
    # 3️⃣ 게임 결과 처리 (표 반영)
    # -----------------------------------------------------------------
    if st.session_state.clutch_result_grade is not None:
        grade_key = st.session_state.clutch_result_grade
        
        if grade_key == "DRAW":
            st.info("🤝 **[11회말 무승부 종료]** 보상 없이 무승부로 처리됩니다. (0💎)")
        else:
            g_data = GRADE_TABLE[grade_key]
            is_win = "WIN" in grade_key
            is_ext = st.session_state.clutch_inning > 9
            
            if is_win:
                st.balloons()
                base_reward = g_data["reward"]
                final_reward = int(base_reward * 1.5) if is_ext else base_reward
                ext_tag = " (연장전 +50% 가산!)" if is_ext else ""
                
                st.success(f"🎉 **[{g_data['name']}]** {g_data['desc']}! **+{final_reward} 💎** 획득!{ext_tag}")
                st.session_state.nc_diamonds += final_reward
            else:
                penalty = g_data["penalty"]
                st.error(f"😭 **[{g_data['name']}]** {g_data['desc']}... **-{penalty} 💎** 차감!")
                st.session_state.nc_diamonds = max(0, st.session_state.nc_diamonds - penalty)

        if st.button("🔄 다시 도전하기", type="primary"):
            st.session_state.clutch_in_progress = False
            st.rerun()

        st.markdown("### 📜 경기 로그")
        for log in reversed(st.session_state.clutch_logs):
            st.write(log)
        return

    # -----------------------------------------------------------------
    # 4️⃣ 10회초 / 11회초 수비 단계 (투구 지시)
    # -----------------------------------------------------------------
    if st.session_state.clutch_phase == "초" and not st.session_state.clutch_top_defense_done:
        inn = st.session_state.clutch_inning
        st.warning(f"⚔️ **[{inn}회초 연장 수비]** 동점 상태입니다! 투수 마운드 지시를 내리세요.")
        
        def_choice = st.radio(
            f"⚾ {inn}회초 마운드 지시:",
            ["🛡️ 정밀 코너워크 (안전 승부)", "💥 구위 강속구 (힘 대 힘 승부)", "🔮 헛스윙 유도 (유인구 배합)"],
            key=f"radio_{inn}th_top"
        )
        
        if st.button(f"⚾ {inn}회초 수비 집행", type="primary", key=f"btn_exec_{inn}th"):
            runs_allowed = random.choices([0, 1, 2], weights=[65, 25, 10])[0]
            st.session_state.clutch_enemy_score += runs_allowed
            st.session_state.clutch_top_defense_done = True
            
            # 연장 말 세팅 (노아웃 빈 베이스)
            st.session_state.clutch_phase = "말"
            st.session_state.clutch_outs = 0
            st.session_state.clutch_strikes = 0
            st.session_state.clutch_balls = 0
            st.session_state.clutch_base1 = st.session_state.clutch_base2 = st.session_state.clutch_base3 = False
            
            if runs_allowed > 0:
                st.session_state.clutch_logs.append(f"🚨 상대 팀이 {inn}회초 {runs_allowed}점을 올렸습니다! 스코어 {st.session_state.clutch_enemy_score}:{st.session_state.clutch_our_score}")
            else:
                st.session_state.clutch_logs.append(f"🔥 {inn}회초 무실점 수비 성공!!")
            st.session_state.clutch_logs.append(f"🏟️ [{inn}회말 노아웃 빈 베이스] 주자 없는 0아웃 상태에서 역전 끝내기를 노립니다!")
            st.rerun()

        st.markdown("### 📜 경기 로그")
        for log in reversed(st.session_state.clutch_logs):
            st.write(log)
        return

    # -----------------------------------------------------------------
    # 5️⃣ 공격 타석 선택
    # -----------------------------------------------------------------
    st.markdown("### 📢 타석 작전 선택")
    c1, c2, c3, c4 = st.columns(4)
    
    user_action = None
    with c1:
        if st.button("💥 풀스윙 (강공)", key="btn_c_swing"): user_action = "SWING"
    with c2:
        if st.button("🌟 밀어치기 (컨택)", key="btn_c_contact"): user_action = "CONTACT"
    with c3:
        if st.button("👀 웨이팅 (눈야구)", key="btn_c_wait"): user_action = "WAIT"
    with c4:
        has_runner = st.session_state.clutch_base1 or st.session_state.clutch_base2 or st.session_state.clutch_base3
        if st.button("🏃‍♂️ 기습 번트", disabled=not has_runner, key="btn_c_bunt"): user_action = "BUNT"

    if user_action:
        # 확률적 견제사 / 주루사 발동 (S급 패배 리스크: -1,000💎)
        if has_runner and random.random() < 0.02:
            st.session_state.clutch_result_grade = "S_LOSE"
            st.session_state.clutch_logs.append("💥 [대참사! S급 패배] 주자가 상대 투수/포수 견제구에 완벽히 횡사당해 경기 종료! (끝내기 주루사/견제사)")
            st.rerun()

        st.session_state.clutch_pitcher_stamina = max(0, st.session_state.clutch_pitcher_stamina - 1)
        stamina_bonus = 0.12 if st.session_state.clutch_pitcher_stamina <= 3 else 0.0

        # --- [액션 1: 풀스윙] ---
        if user_action == "SWING":
            roll = random.random() - stamina_bonus
            if roll < 0.08:  # 🚀 만루 홈런 ➔ S급 승리 (+1,000💎)
                if st.session_state.clutch_base1 and st.session_state.clutch_base2 and st.session_state.clutch_base3:
                    st.session_state.clutch_our_score += 4
                    st.session_state.clutch_result_grade = "S_WIN"
                    st.session_state.clutch_logs.append("🚀💥 [S급 승리!] 타구가 장외로 까마득하게 넘어가는 끝내기 대형 만루홈런(Grand Slam)!!!")
                else:
                    st.session_state.clutch_our_score += 2
                    st.session_state.clutch_result_grade = "A_WIN"
                    st.session_state.clutch_logs.append("🔥 [A급 승리!] 담장을 넘기는 끝내기 대형 홈런!")
                st.rerun()

            elif roll < 0.28:  # 🌟 싹쓸이 2루타 ➔ A급 승리 (+500💎)
                runs = (1 if st.session_state.clutch_base1 else 0) + (1 if st.session_state.clutch_base2 else 0) + (1 if st.session_state.clutch_base3 else 0)
                st.session_state.clutch_our_score += runs
                if st.session_state.clutch_our_score > st.session_state.clutch_enemy_score:
                    st.session_state.clutch_result_grade = "A_WIN"
                    st.session_state.clutch_logs.append("🌟 [A급 승리!] 우중간을 가르는 끝내기 싹쓸이 3타점 2루타!!")
                    st.rerun()
                else:
                    st.session_state.clutch_base3 = True; st.session_state.clutch_base1 = st.session_state.clutch_base2 = False
                    st.session_state.clutch_logs.append(f"🔥 우중간 2루타 적중! (+{runs}점)")

            elif roll < 0.48:  # 😱 상대 호수비 ➔ A급 패배 (-500💎)
                st.session_state.clutch_outs += 1
                if st.session_state.clutch_outs >= 3:
                    st.session_state.clutch_result_grade = "A_LOSE"
                    st.session_state.clutch_logs.append("😱 [A급 패배] 총알 같은 잘 맞은 타구가 상대 외야수의 미친 슈퍼 캐치 호수비에 잡힙니다!")
                    st.rerun()
                else:
                    st.session_state.clutch_logs.append("😱 잘 맞은 타구가 상대 다이빙 캐치 호수비에 잡힙니다!")

            else:
                st.session_state.clutch_strikes += 1
                st.session_state.clutch_logs.append(f"💨 헛스윙 파울! ({st.session_state.clutch_strikes}S {st.session_state.clutch_balls}B)")

        # --- [액션 2: 밀어치기 컨택] ---
        elif user_action == "CONTACT":
            roll = random.random() - stamina_bonus
            if roll < 0.35:  # 빗맞은 내야안타 / 폭투 끝내기 ➔ C급 승리 (+100💎)
                st.session_state.clutch_our_score += 1
                if st.session_state.clutch_our_score > st.session_state.clutch_enemy_score:
                    st.session_state.clutch_result_grade = "C_WIN"
                    st.session_state.clutch_logs.append("⚾ [C급 승리!] 포수 빗맞은 내야안타 / 상대 폭투로 극적인 끝내기 득점!")
                    st.rerun()
                else:
                    st.session_state.clutch_logs.append("⚾ 내야안타 출루 성공! (+1점)")
            else:  # 평범한 외야 뜬공 ➔ C급 패배 (-100💎)
                st.session_state.clutch_outs += 1
                if st.session_state.clutch_outs >= 3:
                    st.session_state.clutch_result_grade = "C_LOSE"
                    st.session_state.clutch_logs.append("⚾ [C급 패배] 평범한 외야 뜬공으로 아웃 처리되며 경기 종료.")
                    st.rerun()
                else:
                    st.session_state.clutch_logs.append("⚾ 평범한 외야 플라이 아웃!")

        # --- [액션 3: 웨이팅] ---
        elif user_action == "WAIT":
            if random.random() < 0.50:
                st.session_state.clutch_balls += 1
                st.session_state.clutch_logs.append(f"👀 예리한 선구안! 볼을 골라냅니다. ({st.session_state.clutch_strikes}S {st.session_state.clutch_balls}B)")
                if st.session_state.clutch_balls >= 4:  # 밀어내기 볼넷 / 사구 ➔ B급 승리 (+200💎)
                    st.session_state.clutch_balls = 0
                    st.session_state.clutch_strikes = 0
                    st.session_state.clutch_our_score += 1
                    if st.session_state.clutch_our_score > st.session_state.clutch_enemy_score:
                        st.session_state.clutch_result_grade = "B_WIN"
                        st.session_state.clutch_logs.append("🚶‍♂️ [B급 승리!] 밀어내기 볼넷 / 끝내기 몸에 맞는 공으로 승리!")
                        st.rerun()
            else:
                st.session_state.clutch_strikes += 1
                st.session_state.clutch_logs.append(f"👀 스트라이크 지켜봅니다. ({st.session_state.clutch_strikes}S {st.session_state.clutch_balls}B)")

        # --- [액션 4: 기습 번트] ---
        elif user_action == "BUNT":
            if random.random() < 0.50:
                st.session_state.clutch_our_score += 1
                if st.session_state.clutch_our_score > st.session_state.clutch_enemy_score:
                    st.session_state.clutch_result_grade = "C_WIN"
                    st.session_state.clutch_logs.append("📉 [C급 승리!] 기습 스퀴즈 번트 성공으로 극적인 끝내기 득점!")
                    st.rerun()
            else:
                st.session_state.clutch_outs += 1
                st.session_state.clutch_logs.append("❌ 번트 실패! 아웃 처리됩니다.")

        # --- 카운트 삼진 아웃 판정 ---
        if st.session_state.clutch_strikes >= 3:
            is_fullcount = (st.session_state.clutch_balls == 3)
            st.session_state.clutch_outs += 1
            st.session_state.clutch_strikes = 0
            st.session_state.clutch_balls = 0
            
            if st.session_state.clutch_outs >= 3:
                if is_fullcount:  # 3-2 풀카운트 헛스윙 삼진 ➔ B급 패배 (-200💎)
                    st.session_state.clutch_result_grade = "B_LOSE"
                    st.session_state.clutch_logs.append("⚡ [B급 패배] 3-2 풀카운트에서 헛스윙 삼진 아웃!")
                else:  # 루킹 삼진 ➔ C급 패배 (-100💎)
                    st.session_state.clutch_result_grade = "C_LOSE"
                    st.session_state.clutch_logs.append("👀 [C급 패배] 루킹 삼진 아웃!")
                st.rerun()
            else:
                st.session_state.clutch_logs.append("⚡ 삼진 아웃!")

        # -------------------------------------------------------------
        # 6️⃣ 연장전 및 무승부 판정 체크
        # -------------------------------------------------------------
        our = st.session_state.clutch_our_score
        enemy = st.session_state.clutch_enemy_score
        current_inn = st.session_state.clutch_inning

        if st.session_state.clutch_outs >= 3 and st.session_state.clutch_result_grade is None:
            if our == enemy:
                if current_inn < 11:
                    st.session_state.clutch_inning += 1
                    st.session_state.clutch_phase = "초"
                    st.session_state.clutch_top_defense_done = False
                    st.session_state.clutch_outs = 0
                    st.session_state.clutch_strikes = 0
                    st.session_state.clutch_balls = 0
                    st.session_state.clutch_logs.append(f"📢 [{current_inn}회말 종료] 스코어 동점! {st.session_state.clutch_inning}회 연장전으로 들어갑니다!")
                else:
                    # 11회말까지 동점이면 보상 없는 무승부
                    st.session_state.clutch_result_grade = "DRAW"
            else:
                st.session_state.clutch_result_grade = "C_LOSE"

        st.rerun()

    st.divider()
    st.markdown("### 📜 경기 로그")
    for log in reversed(st.session_state.clutch_logs):
        st.write(log)
