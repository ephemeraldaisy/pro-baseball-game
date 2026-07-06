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
    st.session_state.game_setup = False

def start_new_game(my_team, enemy_team):
    st.session_state.my_team = my_team
    st.session_state.my_emoji = TEAMS[my_team]
    st.session_state.enemy_team = enemy_team
    st.session_state.enemy_emoji = TEAMS[enemy_team]
    
    st.session_state.is_home_team = random.choice([True, False])
    
    st.session_state.our_score = 0
    st.session_state.enemy_score = 0
    st.session_state.my_batter_number = 1
    st.session_state.inning = 1
    st.session_state.phase = "초"
    
    # 투구수 초기화
    st.session_state.our_total_pitches = 0 
    st.session_state.enemy_total_pitches = 0 
    
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

    score_gap = abs(st.session_state.our_score - st.session_state.enemy_score)
    if st.session_state.inning in [5, 6] and score_gap >= 10:
        st.session_state.game_result_msg = f"🚨 [COLD GAME] {st.session_state.inning}회 종료 시점 {score_gap}점 차로 콜드게임 선언!"
        end_game()
        return
    elif st.session_state.inning in [7, 8] and score_gap >= 7:
        st.session_state.game_result_msg = f"🚨 [COLD GAME] {st.session_state.inning}회 종료 시점 {score_gap}점 차로 콜드게임 선언!"
        end_game()
        return

    if st.session_state.inning == 9 and st.session_state.phase == "말" and st.session_state.is_home_team and st.session_state.our_score > st.session_state.enemy_score:
        st.session_state.game_log.append("👍 9회초까지 이미 우리 팀이 이기고 있어 9회말 공격 없이 경기가 끝납니다!")
        end_game()
        return

    # 새로운 이닝 시작 시 카운터 및 주자 깔끔하게 리셋 (보통 게임처럼 공정하게 시작)
    st.session_state.strike = 0
    st.session_state.ball = 0
    st.session_state.out_count = 0
    st.session_state.base1 = st.session_state.base2 = st.session_state.base3 = False

    current_is_our_turn = (not st.session_state.is_home_team and st.session_state.phase == "초") or (st.session_state.is_home_team and st.session_state.phase == "말")
    
    if not current_is_our_turn:
        base_pts = random.choices([0, 1, 2, 3, 4, -1], weights=[500, 250, 150, 70, 25, 5])[0]
        
        if base_pts == -1:
            enemy_pts = random.randint(5, 11)
            st.session_state.game_log.append(f"😱 [🚨 메가 이닝 발생] 상대 팀 방망이가 미쳐 날뜁니다! 무려 {enemy_pts}실점!!")
        else:
            enemy_pts = base_pts

        # =======================================================
        # [수정 위치] setup_half_inning() 함수 중간의 투구수 계산 구역
        # =======================================================
        # 밸런스 패치: 1클릭 1구에 맞춰 상대 AI가 소모시키는 우리 투구수도 대폭 하향 조정!
        if enemy_pts == 0:
            inning_pitches = random.randint(3, 5)   # 3아웃 초스피드 이닝 고증
        elif enemy_pts == 1:
            inning_pitches = random.randint(5, 8)
        elif enemy_pts in [2, 3]:
            inning_pitches = random.randint(8, 12)
        else: 
            inning_pitches = random.randint(12, 18) # 메가 이닝도 최대 18구 정도로 방어

        st.session_state.our_total_pitches += inning_pitches

        if st.session_state.inning >= 9 and st.session_state.phase == "말":
            if enemy_pts > 0 and (st.session_state.enemy_score + enemy_pts) > st.session_state.our_score:
                st.session_state.enemy_score = st.session_state.our_score + 1
                st.session_state.game_log.append(
                    f"❌ 앗! 상대 팀이 {st.session_state.inning}회말 짜릿한 끝내기 득점을 올렸습니다... "
                    f"(우리 투수 최종 {st.session_state.our_total_pitches}구 역투)"
                )
                end_game()
                return
            else:
                st.session_state.enemy_score += enemy_pts
        else:
            st.session_state.enemy_score += enemy_pts

        st.session_state.game_log.append(
            f"🔮 상대 팀 {st.session_state.inning}회{st.session_state.phase} 공격 완료: "
            f"+{enemy_pts}점 (우리 투수 이번 이닝 {inning_pitches}구 던짐 / 총 {st.session_state.our_total_pitches}구)"
        )
        
        next_phase()

def trigger_steal():
    if not st.session_state.base1 and not st.session_state.base2:
        st.warning("루상에 나간 주자가 있어야 도루를 시도하제예!")
        return
    
    if random.random() < 0.65:
        st.session_state.game_log.append("🚀 [도루 성공] 사모님의 완벽한 작전! 베이스를 훔쳤습니다!")
        if st.session_state.base2 and not st.session_state.base3:
            st.session_state.base3 = True
            st.session_state.base2 = False
        elif st.session_state.base1 and not st.session_state.base2:
            st.session_state.base2 = True
            st.session_state.base1 = False
    else:
        st.session_state.game_log.append("❌ [도루 실패] 포수의 칼송구에 그만 런다운 걸려 아웃!")
        if st.session_state.base2: st.session_state.base2 = False
        elif st.session_state.base1: st.session_state.base1 = False
        st.session_state.out_count += 1
        
        if st.session_state.out_count >= 3:
            st.session_state.game_log.append("📢 도루 실패로 쓰리아웃 체인지!")
            next_phase()
            
    st.rerun()

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
# 3. 타격 액션 및 진루 처리 (에러 완전 박멸 버전)
# ==========================================

def play_turn(user_choice):
    if st.session_state.game_over:
        return

    # 🟢 [핵심 패치 1] 형님 말씀대로 버튼 딱 한 번 클릭에 정직하게 무조건 '1구'만 증가!
    enemy_pitch_count = 1
    st.session_state.enemy_total_pitches += enemy_pitch_count

    # 2. 유저 작전별 '공 1구'에 대한 주사위 확률 (현실적인 볼카운트 싸움용 세팅)
    if user_choice == 1:    # 💥 1. 풀스윙 강타 (공격적, 헛스윙 삼진이나 인플레이 타구 위주)
        result = random.choices(
            ["HOMERUN", "HIT", "OUT", "STRIKE", "BALL", "FOUL"], 
            weights=[30, 120, 250, 400, 50, 150]
        )[0]

    elif user_choice == 2:  # 🌟 2. 가볍게 밀어치기 (정교하게 공을 맞추고 커트하는 성향)
        result = random.choices(
            ["HIT", "OUT", "STRIKE", "BALL", "FOUL"], 
            weights=[150, 200, 250, 100, 300] # 파울 확률을 높여 투구수를 유도
        )[0]

    elif user_choice == 3:  # 👀 3. 공 끝까지 거르기 (방망이 안 나가고 신중하게 공 고르기)
        result = random.choices(
            ["STRIKE", "BALL"], 
            weights=[400, 600] # 배트를 휘두르지 않으므로 오직 스트라이크와 볼만 나옴!
        )[0]

    # 3. ⚾ BSO 카운트 처리 및 아웃 시 즉시 다음 타자 전환 로직
    log_msg = ""
    current_batter = st.session_state.my_batter_number
    
    if result == "HOMERUN":
        # 홈런 패널티/보너스 및 진루 처리
        pts = (1 if st.session_state.base1 else 0) + (1 if st.session_state.base2 else 0) + (1 if st.session_state.base3 else 0) + 1
        st.session_state.our_score += pts
        st.session_state.game_log.append(f"🔥 🎉 깡!!!!! {current_batter}번 타자 대형 {pts}점짜리 홈런 대폭발!!!!!!!! (상대 투수 총 {st.session_state.enemy_total_pitches}구)")
        st.session_state.base1 = st.session_state.base2 = st.session_state.base3 = False
        # 타석 종료 ➔ 카운트 리셋 및 즉시 다음 타자!
        st.session_state.strike = st.session_state.ball = 0
        st.session_state.my_batter_number = 1 if current_batter == 9 else current_batter + 1

    elif result == "HIT":
        if st.session_state.base3: st.session_state.our_score += 1
        if st.session_state.base2: st.session_state.our_score += 1
        st.session_state.base3 = st.session_state.base1
        st.session_state.base2 = False
        st.session_state.base1 = True
        st.session_state.game_log.append(f"🌟 딱! {current_batter}번 타자의 안타! 주자 나갑니다! (상대 투수 총 {st.session_state.enemy_total_pitches}구)")
        # 타석 종료 ➔ 카운트 리셋 및 즉시 다음 타자!
        st.session_state.strike = st.session_state.ball = 0
        st.session_state.my_batter_number = 1 if current_batter == 9 else current_batter + 1
        
    elif result == "OUT":
        st.session_state.out_count += 1
        st.session_state.game_log.append(f" Ah... {current_batter}번 타자 아쉽게도 내야 땅볼 아웃입니다. (상대 투수 총 {st.session_state.enemy_total_pitches}구)")
        # 타석 종료 ➔ 카운트 리셋 및 즉시 다음 타자!
        st.session_state.strike = st.session_state.ball = 0
        st.session_state.my_batter_number = 1 if current_batter == 9 else current_batter + 1
        
        if st.session_state.out_count >= 3:
            check_three_out_change()
            return

    elif result == "STRIKE":
        st.session_state.strike += 1
        log_msg = f"❌ 스트라이크! (현재 {st.session_state.strike}S {st.session_state.ball}B)"
        
        # 🔥 [삼진 로직 체인지] 스트라이크가 3개가 되는 순간 즉시 아웃 처리 및 타자 교체!
        if st.session_state.strike >= 3:
            st.session_state.out_count += 1
            st.session_state.game_log.append(f"⚡ 앗 아아... {current_batter}번 타자 3구 삼진 아웃!! (상대 투수 총 {st.session_state.enemy_total_pitches}구)")
            st.session_state.strike = 0
            st.session_state.ball = 0
            st.session_state.my_batter_number = 1 if current_batter == 9 else current_batter + 1
            
            if st.session_state.out_count >= 3:
                check_three_out_change()
                return

    elif result == "BALL":
        st.session_state.ball += 1
        log_msg = f"🟢 볼 골라냅니다! (현재 {st.session_state.strike}S {st.session_state.ball}B)"
        
        # 🔥 [볼넷 로직 체인지] 볼이 4개가 되는 순간 즉시 출루 및 다음 타자 교체!
        if st.session_state.ball >= 4:
            st.session_state.game_log.append(f"🚶‍♂️ {current_batter}번 타자 끈질긴 눈야구로 볼넷 출루! (상대 투수 총 {st.session_state.enemy_total_pitches}구)")
            if st.session_state.base1 and st.session_state.base2 and st.session_state.base3:
                st.session_state.our_score += 1
                st.session_state.game_log.append("➔ 밀어내기 만루 볼넷으로 1점 추가!")
            elif st.session_state.base1 and st.session_state.base2: st.session_state.base3 = True
            elif st.session_state.base1: st.session_state.base2 = True
            else: st.session_state.base1 = True
            
            st.session_state.strike = 0
            st.session_state.ball = 0
            st.session_state.my_batter_number = 1 if current_batter == 9 else current_batter + 1

    elif result == "FOUL":
        # 2스트라이크 미만일 때만 스트라이크 카운트 증가
        if st.session_state.strike < 2:
            st.session_state.strike += 1
        log_msg = f"💥 커트합니다, 파울! (현재 {st.session_state.strike}S {st.session_state.ball}B)"

    # 스트라이크/볼/파울 같은 진행형 카운트만 중계창에 브리핑 출력
    action_names = {1: "풀스윙 강타", 2: "가볍게 밀어치기", 3: "공 끝까지 거르기"}
    if log_msg:
        st.session_state.game_log.append(f" 작전[{action_names[user_choice]}]: {log_msg}")

    # 연장전 끝내기 조건 체크
    if st.session_state.inning >= 9 and st.session_state.phase == "말" and st.session_state.is_home_team and st.session_state.our_score > st.session_state.enemy_score:
        end_game()

def check_three_out_change():
    if st.session_state.out_count >= 3:
        st.session_state.game_log.append(f"📢 쓰리아웃 체인지! 우리 팀의 이번 이닝 공격이 끝났습니다.")
        
        if st.session_state.inning >= 9:
            if st.session_state.phase == "초" and st.session_state.our_score < st.session_state.enemy_score:
                end_game()
                return
            elif st.session_state.phase == "말" and st.session_state.our_score < st.session_state.enemy_score:
                end_game()
                return
        
        next_phase()

# ==========================================
# 4. 웹 UI (팀 선택 화면 및 게임 화면)
# ==========================================
st.title("⚾ KBO 스타일 매운맛 프로야구 시뮬레이터")

if not st.session_state.game_setup:
    st.markdown("### 🏟️ 구단 선택 및 리그 매칭")
    my_choice = st.selectbox("사모님이 이끌어갈 우리 팀을 고르소:", list(TEAMS.keys()))
    remaining_teams = [t for t in TEAMS.keys() if t != my_choice]
    
    if st.button("경기 대진표 확정 및 입장 🎟️", type="primary"):
        enemy_choice = random.choice(remaining_teams)
        start_new_game(my_choice, enemy_choice)
        st.rerun()
else:
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        st.metric(label=f"우리 팀 {st.session_state.my_emoji}", value=f"{st.session_state.our_score} 점")
        st.caption(st.session_state.my_team)
        st.markdown(f"🔋 **우리 투수 총 투구수:** `{st.session_state.our_total_pitches}구`")
    with col2:
        st.markdown(f"<h3 style='text-align: center; color: red;'>{st.session_state.inning}회{st.session_state.phase}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-size:12px;'>진영: {'🏠 홈팀(후공)' if st.session_state.is_home_team else '🚌 원정팀(선공)'}</p>", unsafe_allow_html=True)
    with col3:
        st.metric(label=f"상대 팀 {st.session_state.enemy_emoji}", value=f"{st.session_state.enemy_score} 점")
        st.caption(st.session_state.enemy_team)
        st.markdown(f"🥎 **상대 투수 총 투구수:** `{st.session_state.enemy_total_pitches}구`") # UI에 상대 투구수 추가 지표 노출

    st.divider()

    if st.session_state.game_over:
        st.markdown("<h1 style='text-align: center; color: #FF4B4B; font-size: 60px; font-weight: bold; letter-spacing: 5px;'>💥 GAME SET 💥</h1>", unsafe_allow_html=True)
        
        if st.session_state.our_score > st.session_state.enemy_score:
            st.balloons()
            st.success(st.session_state.game_result_msg)
            st.image("assets/congratulations.gif", use_container_width=True)
            st.markdown(
                """
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
                """,
                unsafe_allow_html=True
            )
            st.markdown("<h3 style='text-align: center; color: #8B4513;'>🎉 승리의 축포를 날리자아아앗!!! 🎉</h3>", unsafe_allow_html=True)
        else:
            st.error(st.session_state.game_result_msg)
            st.image("assets/rainbowpoo.gif", use_container_width=True)
            st.markdown(
                """
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
                """,
                unsafe_allow_html=True
            )
            st.markdown("<h3 style='text-align: center; color: #8B4513;'>💩 패배의 똥세례를 받아라아아앗!!! 💩</h3>", unsafe_allow_html=True)

        st.divider()
        if st.button("다른 구단 선택하러 가기 🔄", type="primary"):
            st.session_state.game_setup = False
            st.rerun()
    else:
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
        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
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
        with col_b4:
            if st.button("🏃‍♂️ 4. 기습 도루 작전"):
                trigger_steal()

    st.divider()
    st.markdown("### 🎙️ 실시간 중계 일지")
    for log in reversed(st.session_state.game_log[-8:]):
        st.write(log)
