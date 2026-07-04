import random
import streamlit as st

# ==========================================
# 1. 페이지 설정 및 팀 데이터 (색상별 이모지)
# ==========================================
st.set_page_config(page_title="이 사장의 프로야구 시뮬레이터 Pro", page_icon="⚾", layout="centered")

TEAMS = {
    "🔴 레드 파이어스": "🔴",
    "🔵 블루 웨이브스": "🔵",
    "🟢 그린 몬스터즈": "🟢",
    "🟡 옐로우 타이거즈": "🟡",
    "🟣 퍼플 바이퍼스": "🟣",
    "🟠 오렌지 자이언츠": "🟠",
    "⚫ 블랙 나이츠": "⚫",
    "🟤 브라운 베어스": "🟤",
    "⚪ 화이트 이글스": "⚪",
    "💖 핑크 돌핀스": "💖"
}

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

# ==========================================
# 2. 게임 상태(Session State) 관리
# ==========================================
if "game_setup" not in st.session_state:
    st.session_state.game_setup = False  # 팀 선택 화면 상태

def start_new_game(my_team, enemy_team):
    st.session_state.my_team = my_team
    st.session_state.my_emoji = TEAMS[my_team]
    st.session_state.enemy_team = enemy_team
    st.session_state.enemy_emoji = TEAMS[enemy_team]
    
    # 경기 시작과 동시에 선공/후공(홈/원정) 무작위 결정
    st.session_state.is_home_team = random.choice([True, False])
    
    st.session_state.our_score = 0
    st.session_state.enemy_score = 0
    st.session_state.my_batter_number = 1
    st.session_state.inning = 1
    st.session_state.phase = "초"
    
    st.session_state.out_count = 0
    st.session_state.strike = 0
    st.session_state.ball = 0
    st.session_state.base1 = False
    st.session_state.base2 = False
    st.session_state.base3 = False
    
    st.session_state.game_log = [f"🪙 동전을 던져 진영을 결정했습니다! 우리 팀은 {'후공(홈팀)' if st.session_state.is_home_team else '선공(원정팀)'} 기라!"]
    st.session_state.game_over = False
    st.session_state.game_setup = True
    st.session_state.game_result_msg = ""
    
    setup_half_inning()

def setup_half_inning():
    if st.session_state.inning > 9 and st.session_state.our_score != st.session_state.enemy_score:
        end_game()
        return

    # 밸런스 패치: 점수 차가 너무 안 날 테지만 콜드게임 기준은 유지
    score_gap = abs(st.session_state.our_score - st.session_state.enemy_score)
    if st.session_state.inning in [5, 6] and score_gap >= 10:
        st.session_state.game_result_msg = f"🚨 [COLD GAME] {st.session_state.inning}회 종료 시점 {score_gap}점 차로 콜드게임 선언!"
        end_game()
        return
    elif st.session_state.inning in [7, 8] and score_gap >= 7:
        st.session_state.game_result_msg = f"🚨 [COLD GAME] {st.session_state.inning}회 종료 시점 {score_gap}점 차로 콜드게임 선언!"
        end_game()
        return

    if st.session_state.inning >= 9 and st.session_state.phase == "말" and st.session_state.is_home_team and st.session_state.our_score > st.session_state.enemy_score:
        end_game()
        return

    st.session_state.strike = 0
    st.session_state.ball = 0
    
    # 9회말 우리 팀(홈) 특별 위기 상황 이벤트 (연장전은 0아웃 클린슬레이트 자동 연동)
    if st.session_state.inning == 9 and st.session_state.phase == "말" and st.session_state.is_home_team:
        st.session_state.out_count = 2
        st.session_state.base1 = st.session_state.base2 = st.session_state.base3 = True
        st.session_state.game_log.append("🚨 [9회말 극장] 주자 만루! 사모님 타석이 다가옵니데이!")
    else:
        st.session_state.out_count = 0
        st.session_state.base1 = st.session_state.base2 = st.session_state.base3 = False

    current_is_our_turn = (not st.session_state.is_home_team and st.session_state.phase == "초") or (st.session_state.is_home_team and st.session_state.phase == "말")
    
    if not current_is_our_turn:
        # 상대 팀 AI 공격력 현실화 (0점: 50%, 1점: 25%, 2점: 15%, 3점: 7%, 4점: 3%)
        enemy_pts = random.choices([0, 1, 2, 3, 4], weights=[50, 25, 15, 7, 3])[0]
        
        if st.session_state.inning >= 9 and st.session_state.phase == "말":
            if enemy_pts > 0 and (st.session_state.enemy_score + enemy_pts) > st.session_state.our_score:
                st.session_state.enemy_score = st.session_state.our_score + 1
                st.session_state.game_log.append(f"➔ 앗! 상대 팀이 {st.session_state.inning}회말 끝내기 점수를 올렸습니다...")
                end_game()
                return
            else:
                st.session_state.enemy_score += enemy_pts
                st.session_state.game_log.append(f"🔮 상대 팀 {st.session_state.inning}회말 공격: +{enemy_pts}점")
        else:
            st.session_state.enemy_score += enemy_pts
            st.session_state.game_log.append(f"🔮 상대 팀 {st.session_state.inning}회{st.session_state.phase} 공격: +{enemy_pts}점")
        
        next_phase()

def next_phase():
    if st.session_state.phase == "초":
        st.session_state.phase = "말"
    else:
        st.session_state.phase = "초"
        st.session_state.inning += 1
    setup_half_inning()

def end_game():
    st.session_state.game_over = True
    if st.session_state.our_score > st.session_state.enemy_score:
        st.session_state.game_result_msg = f"🎉 {st.session_state.my_team} 대승리!!! 오늘 경기 수당은 사모님 기라!!"
    elif st.session_state.our_score < st.session_state.enemy_score:
        st.session_state.game_result_msg = f"😭 패배... 상대 {st.session_state.enemy_team}의 마구에 당했습니다. 복수하러 가이소!"
    else:
        st.session_state.game_result_msg = "🤝 12회 대혈투 끝에 무승부로 끝났습니다!"

# ==========================================
# 3. 매운맛 타격 액션 처리 (KBO 현실 밸런스 적용)
# ==========================================
def play_turn(user_choice):
    pitches = ["직구", "슬라이더", "체인지업"]
    pitch = random.choice(pitches)
    st.session_state.game_log.append(f"⚾ 투수가 구석을 찌르는 '[{pitch}]'을 던졌습니다!")

    at_bat_result = None
    result = random.random()

    # 1. 풀스윙 강타 (KBO 슬러거 모드)
    if user_choice == 1:
        if (pitch == "직구" and result < 0.15) or (pitch != "직구" and result < 0.08):
            at_bat_result = "홈런"
        elif result < 0.55:
            st.session_state.game_log.append("➔ 파울! 타이밍은 맞았는데 빗맞았습니다.")
            if st.session_state.strike < 2: st.session_state.strike += 1
        else:
            st.session_state.game_log.append("➔ 헛스윙 삼진 유도구에 완전히 속았습니다!")
            st.session_state.strike += 1

    # 2. 가볍게 밀어치기 (KBO 컨택트 모드)
    elif user_choice == 2:
        if result < 0.30:  # 3할 타자 확률
            at_bat_result = "안타"
        elif result < 0.70:
            st.session_state.game_log.append("➔ 범타! 빗맞은 타구가 파울 라인 밖으로 나갑니다.")
            if st.session_state.strike < 2: st.session_state.strike += 1
        else:
            st.session_state.game_log.append("➔ 스트라이크! 배트가 허공을 가릅니다.")
            st.session_state.strike += 1

    # 3. 공 끝까지 거르기 (선구안 모드)
    elif user_choice == 3:
        if result < 0.35:  # 투수들이 스트라이크를 더 많이 던짐
            st.session_state.game_log.append("➔ 볼! 유인구를 끈질기게 잘 참아냈습니다.")
            st.session_state.ball += 1
            if st.session_state.ball == 4: at_bat_result = "볼넷"
        else:
            st.session_state.game_log.append("➔ 앗! 스트라이크 존 한가운데 꽂히는 루킹 스트라이크!")
            st.session_state.strike += 1

    # 주자 진루 세부 엔진 (리얼 야구 방식)
    if at_bat_result in ["홈런", "안타", "볼넷"]:
        st.session_state.strike = 0
        st.session_state.ball = 0
        current_batter = st.session_state.my_batter_number
        st.session_state.my_batter_number = 1 if current_batter == 9 else current_batter + 1

        if at_bat_result == "홈런":
            pts = (1 if st.session_state.base1 else 0) + (1 if st.session_state.base2 else 0) + (1 if st.session_state.base3 else 0) + 1
            st.session_state.our_score += pts
            st.session_state.game_log.append(f"🔥 🎉 깡!!!!! {current_batter}번 타자 역대급 {pts}점짜리 홈런 대폭발!!!!!!!!")
            st.session_state.base1 = st.session_state.base2 = st.session_state.base3 = False

        elif at_bat_result == "안타":
            st.session_state.game_log.append(f"🌟 딱! {current_batter}번 타자의 안타! 주자 주루 플레이 개시!")
            # [리얼 진루] 3루 주자 무조건 홈인, 2루 주자는 안타시 홈인, 1루 주자는 3루까지 이동
            if st.session_state.base3: st.session_state.our_score += 1
            if st.session_state.base2: st.session_state.our_score += 1
            
            st.session_state.base3 = st.session_state.base1  # 1루 주자는 3루로
            st.session_state.base2 = False
            st.session_state.base1 = True  # 타자는 1루로

        elif at_bat_result == "볼넷":
            st.session_state.game_log.append(f"🏃‍♂️ {current_batter}번 타자 볼넷 출루!")
            if st.session_state.base1 and st.session_state.base2 and st.session_state.base3:
                st.session_state.our_score += 1
                st.session_state.game_log.append("➔ 밀어내기 만루 볼넷으로 1점 추가!")
            elif st.session_state.base1 and st.session_state.base2: st.session_state.base3 = True
            elif st.session_state.base1: st.session_state.base2 = True
            else: st.session_state.1 = True
            st.session_state.base1 = True

    elif st.session_state.strike == 3:
        st.session_state.game_log.append(f"❌ 앗 삼진! {st.session_state.my_batter_number}번 타자가 아쉽게 돌아섭니다.")
        st.session_state.out_count += 1
        st.session_state.strike = 0
        st.session_state.ball = 0
        current_batter = st.session_state.my_batter_number
        st.session_state.my_batter_number = 1 if current_batter == 9 else current_batter + 1

        if st.session_state.out_count == 3:
            st.session_state.game_log.append(f"📢 쓰리아웃 체인지!")
            if st.session_state.phase == "말" and st.session_state.our_score < st.session_state.enemy_score:
                end_game()
                return
            next_phase()

    if st.session_state.inning >= 9 and st.session_state.phase == "말" and st.session_state.is_home_team and st.session_state.our_score > st.session_state.enemy_score:
        end_game()

# ==========================================
# 4. 웹 UI (팀 선택 화면 및 게임 화면)
# ==========================================
st.title("⚾ KBO 매운맛 프로야구 시뮬레이터")

if not st.session_state.game_setup:
    st.markdown("### 🏟️ 구단 선택 및 리그 매칭")
    my_choice = st.selectbox("사모님이 이끌어갈 우리 팀을 고르이소:", list(TEAMS.keys()))
    
    # 내 팀 제외하고 상대 팀 무작위 배정 준비
    remaining_teams = [t for t in TEAMS.keys() if t != my_choice]
    
    if st.button("경기 대진표 확정 및 입장 🎟️", type="primary"):
        enemy_choice = random.choice(remaining_teams)
        start_new_game(my_choice, enemy_choice)
        st.rerun()
else:
    # 전광판 레이아웃
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        st.metric(label=f"우리 팀 {st.session_state.my_emoji}", value=f"{st.session_state.our_score} 점")
        st.caption(st.session_state.my_team)
    with col2:
        st.markdown(f"<h3 style='text-align: center; color: red;'>{st.session_state.inning}회{st.session_state.phase}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-size:12px;'>진영: {'🏠 홈팀(후공)' if st.session_state.is_home_team else '🚌 원정팀(선공)'}</p>", unsafe_allow_html=True)
    with col3:
        st.metric(label=f"상대 팀 {st.session_state.enemy_emoji}", value=f"{st.session_state.enemy_score} 점")
        st.caption(st.session_state.enemy_team)

    st.divider()

    if st.session_state.game_over:
        if st.session_state.our_score > st.session_state.enemy_score:
            st.balloons()
            st.success(st.session_state.game_result_msg)
        else:
            st.error(st.session_state.game_result_msg)
            
        if st.button("다른 구단 선택하러 가기 🔄", type="primary"):
            st.session_state.game_setup = False
            st.rerun()
    else:
        # 야구 카운트 정보
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"### 📊 카운트 보드")
            st.markdown(f"* **아웃:** {'🔴' * st.session_state.out_count}{'⚪' * (3-st.session_state.out_count)}")
            st.markdown(f"* **스트라이크:** {'🔥' * st.session_state.strike}{'⚪' * (3-st.session_state.strike)}")
            st.markdown(f"* **볼:** {'🟢' * st.session_state.ball}{'⚪' * (4-st.session_state.ball)}")
            st.markdown(f"* **타순:** `{st.session_state.my_batter_number}번 타자 타석` " + ("(👑 사모님!)" if st.session_state.my_batter_number == 4 else ""))

        with c2:
            st.markdown("### 🏃 루상 주자")
            b1 = "🏃" if st.session_state.base1 else "◯"
            b2 = "🏃" if st.session_state.base2 else "◯"
            b3 = "🏃" if st.session_state.base3 else "◯"
            st.code(f"""
                   [{b2}] 2루
            [{b3}] 3루         [{b1}] 1루
                    [X] 타석
            """, language="text")

        st.divider()

        st.markdown("### 📢 사모님의 작전 지시")
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            if st.button("💥 1. 풀스윙 강타"):
                play_turn(1)
                st.rerun()
        with col_b2:
            if st.button("🌟 2. 가볍게 밀어치기"):
                play_turn(2)
                st.rerun()
        with col_b3:
            if st.button("👀 3. 공 끝까지 거르기"):
                play_turn(3)
                st.rerun()

    st.divider()
    st.markdown("### 🎙️ 실시간 중계 일지")
    for log in reversed(st.session_state.game_log[-8:]):
        st.write(log)
