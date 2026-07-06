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
    #투구수
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
    # [정식 경기 종료 판단 조건] 연장전 돌입 전 동점이 아니라면 정규이닝 종료
    if st.session_state.inning > 9 and st.session_state.our_score != st.session_state.enemy_score:
        end_game()
        return

    # 콜드게임 규칙 유지
    score_gap = abs(st.session_state.our_score - st.session_state.enemy_score)
    if st.session_state.inning in [5, 6] and score_gap >= 10:
        st.session_state.game_result_msg = f"🚨 [COLD GAME] {st.session_state.inning}회 종료 시점 {score_gap}점 차로 콜드게임 선언!"
        end_game()
        return
    elif st.session_state.inning in [7, 8] and score_gap >= 7:
        st.session_state.game_result_msg = f"🚨 [COLD GAME] {st.session_state.inning}회 종료 시점 {score_gap}점 차로 콜드게임 선언!"
        end_game()
        return

    # 홈팀인데 9회초 종료 기준 이미 이기고 있다면 9회말 없이 승리 (야구 규칙)
    if st.session_state.inning == 9 and st.session_state.phase == "말" and st.session_state.is_home_team and st.session_state.our_score > st.session_state.enemy_score:
        st.session_state.game_log.append("👍 9회초까지 이미 우리 팀이 이기고 있어 9회말 공격 없이 경기가 끝납니다!")
        end_game()
        return

    # 카운트 초기화
    st.session_state.strike = 0
    st.session_state.ball = 0
    
    # 9회말 상황 유지
    st.session_state.out_count = 0
    st.session_state.base1 = st.session_state.base2 = st.session_state.base3 = False

    # 현재가 우리 공격 턴인지 판별
    current_is_our_turn = (not st.session_state.is_home_team and st.session_state.phase == "초") or (st.session_state.is_home_team and st.session_state.phase == "말")
    
    if not current_is_our_turn:
        # 상대 팀 AI 공격 (0.5% 확률 메가 이닝 포함)
        base_pts = random.choices([0, 1, 2, 3, 4, -1], weights=[500, 250, 150, 70, 25, 5])[0]
        
        if base_pts == -1:
            enemy_pts = random.randint(5, 11)
            st.session_state.game_log.append(f"😱 [🚨 메가 이닝 발생] 상대 팀 방망이가 미쳐 날뜁니다! 무려 {enemy_pts}실점!!")
        else:
            enemy_pts = base_pts

        # 🔋 점수가 정해졌으니 투구수부터 먼저 계산합니다.
        if enemy_pts == 0:
            inning_pitches = random.randint(10, 15)
        elif enemy_pts == 1:
            inning_pitches = random.randint(16, 22)
        elif enemy_pts in [2, 3]:
            inning_pitches = random.randint(23, 30)
        else: # 4점 이상 혹은 메가 이닝
            inning_pitches = random.randint(31, 45)

        # 💥 계산된 이번 이닝 투구수를 총 투구수 변수에 누적해서 적립
        st.session_state.our_total_pitches += inning_pitches

        # 🌟 상대 팀이 '말' 공격(9회말 또는 연장말)일 때는 '끝내기 요건' 실시간 계산
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
            # 일반적인 이닝에서는 스코어만 더함
            st.session_state.enemy_score += enemy_pts

        # 🎙️ 중계 일지에 투구수 상황 기록
        st.session_state.game_log.append(
            f"🔮 상대 팀 {st.session_state.inning}회{st.session_state.phase} 공격 완료: "
            f"+{enemy_pts}점 (우리 투수 이번 이닝 {inning_pitches}구 던짐 / 총 {st.session_state.our_total_pitches}구)"
        )
        
        # 다음 페이즈로 이동
        next_phase()

#작전용 도루와 로직
def trigger_steal():
    """🏃 65% 확률 작전용 도루 엔진"""
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
        
        # 아웃카운트 증가에 따른 공수교대 체크
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
# 3. 타격 액션 및 진루 처리 (병살타 엔진 장착)
# ==========================================
def play_turn(user_choice):
    if st.session_state.game_over:
        return

    # 🔋 [메커니즘 1] 한 번 휘두르거나 고를 때마다 늘어날 상대 투수의 투구수 기본 세팅
    enemy_pitch_count = 0

    # 1. 유저의 작전 선택에 따른 확률 결과 계산
    if user_choice == 1:    # 💥 1. 풀스윙 강타
        result = random.choices(
            ["HIT", "OUT", "STRIKE", "BALL", "FOUL"], 
            weights=[200, 400, 250, 50, 100]
        )[0]
        # 풀스윙은 보통 1구~3구 안으로 승부가 많이 남
        enemy_pitch_count = random.randint(1, 3)

    elif user_choice == 2:  # 🌟 2. 가볍게 밀어치기
        result = random.choices(
            ["HIT", "OUT", "STRIKE", "BALL", "FOUL"], 
            weights=[300, 400, 150, 50, 100]
        )[0]
        # 밀어치기도 커트하거나 지켜보며 2구~4구 정도 소모
        enemy_pitch_count = random.randint(2, 4)

    elif user_choice == 3:  # 👀 3. 공 끝까지 거르기 (★BSO 먹통 해결 구역★)
        result = random.choices(
            ["HIT", "OUT", "STRIKE", "BALL", "FOUL"], 
            weights=[100, 100, 150, 550, 100]  # 지난번 상향한 볼넷 확률 유지!
        )[0]
        # 공을 끝까지 지켜보므로 상대 투수 공을 최소 3구~6구까지 많이 뺍니다.
        enemy_pitch_count = random.randint(3, 6)

    # 💥 [상대 투수 투구수 누적] 우리 세션 상태에 상대 투수 총 투구수 변수가 없다면 자동 생성 후 적립!
    if "enemy_total_pitches" not in st.session_state:
        st.session_state.enemy_total_pitches = 0
    st.session_state.enemy_total_pitches += enemy_pitch_count

    # 2. ⚾ [BSO 트리거 엔진] 어떤 버튼(1, 2, 3번)을 눌렀든 무조건 이 카운트 필터를 거치게 만듭니다!
    log_msg = ""
    
    if result == "HIT":
        # 안타 처리 로직 (기존 형님 코드의 안타 함수나 로직 호출)
        # 예시: hit_result = process_hit()
        log_msg = "🔥 시원한 안타! 주자 나갑니다!"
        st.session_state.strike = 0
        st.session_state.ball = 0
        
    elif result == "OUT":
        # 일반 아웃 또는 병살타 체크 구역
        st.session_state.out_count += 1
        log_msg = " Ah... 아쉽게도 아웃입니다."
        st.session_state.strike = 0
        st.session_state.ball = 0
        if st.session_state.out_count >= 3:
            st.session_state.game_log.append(f" 쓰리아웃 체인지! 상대 투수 현재 총 {st.session_state.enemy_total_pitches}구 던짐.")
            setup_half_inning()
            return

    elif result == "STRIKE":
        st.session_state.strike += 1
        log_msg = f"❌ 스트라이크! (현재 {st.session_state.strike}S)"
        if st.session_state.strike >= 3:
            st.session_state.out_count += 1
            log_msg = " ⚡ 루킹 삼진 아웃!! 앗 아아..."
            st.session_state.strike = 0
            st.session_state.ball = 0
            if st.session_state.out_count >= 3:
                st.session_state.game_log.append(f" 쓰리아웃 체인지! 상대 투수 현재 총 {st.session_state.enemy_total_pitches}구 던짐.")
                setup_half_inning()
                return

    elif result == "BALL":
        st.session_state.ball += 1
        log_msg = f"👀 볼 고릅니다! (현재 {st.session_state.ball}B)"
        if st.session_state.ball >= 4:
            # 볼넷 처리 로직 (주자 진루)
            log_msg = " 🚶 걸어 나갑니다! 기적의 볼넷 완성!"
            st.session_state.strike = 0
            st.session_state.ball = 0
            # 여기에 기존 형님 코드의 볼넷 진루 함수 호출 집어넣으시면 됩니다!

    elif result == "FOUL":
        if st.session_state.strike < 2:
            st.session_state.strike += 1
        log_msg = f" 파울! (현재 {st.session_state.strike}S {st.session_state.ball}B)"

    # 🎙️ [통합 중계 로그 출력] 상대 투수의 투구수 상황까지 실시간으로 브리핑!
    action_names = {1: "풀스윙 강타", 2: "가볍게 밀어치기", 3: "공 끝까지 거르기"}
    st.session_state.game_log.append(
        f" 작전[{action_names[user_choice]}]: {log_msg} "
        f"(상대 투수 {enemy_pitch_count}구 던짐 / 총 {st.session_state.enemy_total_pitches}구)"
    )

    # 주자 진루 엔진 및 아웃 판정
    if at_bat_result in ["홈런", "안타", "볼넷"]:
        st.session_state.strike = st.session_state.ball = 0
        current_batter = st.session_state.my_batter_number
        st.session_state.my_batter_number = 1 if current_batter == 9 else current_batter + 1

        if at_bat_result == "홈런":
            pts = (1 if st.session_state.base1 else 0) + (1 if st.session_state.base2 else 0) + (1 if st.session_state.base3 else 0) + 1
            st.session_state.our_score += pts
            st.session_state.game_log.append(f"🔥 🎉 깡!!!!! {current_batter}번 타자 대형 {pts}점짜리 홈런 대폭발!!!!!!!!")
            st.session_state.base1 = st.session_state.base2 = st.session_state.base3 = False

        elif at_bat_result == "안타":
            st.session_state.game_log.append(f"🌟 딱! {current_batter}번 타자의 안타! 주자 주루 플레이 개시!")
            if st.session_state.base3: st.session_state.our_score += 1
            if st.session_state.base2: st.session_state.our_score += 1
            st.session_state.base3 = st.session_state.base1
            st.session_state.base2 = False
            st.session_state.base1 = True

        elif at_bat_result == "볼넷":
            st.session_state.game_log.append(f"🏃‍♂️ {current_batter}번 타자 볼넷 출루!")
            if st.session_state.base1 and st.session_state.base2 and st.session_state.base3:
                st.session_state.our_score += 1
                st.session_state.game_log.append("➔ 밀어내기 만루 볼넷으로 1점 추가!")
            elif st.session_state.base1 and st.session_state.base2: st.session_state.base3 = True
            elif st.session_state.base1: st.session_state.base2 = True
            else: st.session_state.base1 = True
            st.session_state.base1 = True

    elif st.session_state.strike == 3:
        st.session_state.game_log.append(f"❌ 삼진! {st.session_state.my_batter_number}번 타자가 아쉽게 돌아섭니다.")
        st.session_state.out_count += 1
        st.session_state.strike = st.session_state.ball = 0
        current_batter = st.session_state.my_batter_number
        st.session_state.my_batter_number = 1 if current_batter == 9 else current_batter + 1
        
        # 쓰리아웃 체인지 체크
        check_three_out_change()

    # 🌟 [끝내기 조건] 우리 팀이 '말' 공격이고 점수가 앞서는 순간 즉시 끝내기 승리 처리
    if st.session_state.inning >= 9 and st.session_state.phase == "말" and st.session_state.is_home_team and st.session_state.our_score > st.session_state.enemy_score:
        end_game()

def check_three_out_change():
    """쓰리아웃이 되었을 때 야구 정식 요건에 맞춰 공수교대 또는 패배를 선언하는 함수"""
    if st.session_state.out_count >= 3:
        st.session_state.game_log.append(f"📢 쓰리아웃 체인지! 우리 팀의 이번 이닝 공격이 끝났습니다.")
        
        # 🌟 [패배 요건 수정 2] 점수가 지고 있다고 바로 지는 게 아니라, 우리 공격 스케줄이 완벽하게 끝났을 때만 패배 확정!
        if st.session_state.inning >= 9:
            # 요건 A: 우리가 선공(초)인데 9회초 공격이 다 끝났음에도 점수가 밀릴 때 패배 확정
            if st.session_state.phase == "초" and st.session_state.our_score < st.session_state.enemy_score:
                end_game()
                return
            # 요건 B: 우리가 후공(말)인데 9회말(또는 연장말) 공격이 다 끝났음에도 점수가 밀릴 때 패배 확정
            elif st.session_state.phase == "말" and st.session_state.our_score < st.session_state.enemy_score:
                end_game()
                return
        
        # 패배 요건에 해당 안 되면 안전하게 다음 페이즈로 전환
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

    st.divider()

    if st.session_state.game_over:
        #GAME SET 메시지
        st.markdown("<h1 style='text-align: center; color: #FF4B4B; font-size: 60px; font-weight: bold; letter-spacing: 5px;'>💥 GAME SET 💥</h1>", unsafe_allow_html=True)
        
        if st.session_state.our_score > st.session_state.enemy_score:
            st.balloons()
            st.success(st.session_state.game_result_msg)
            st.image("assets/congratulations.gif", use_container_width=True)
            st.markdown(
                """
                <div style="
                    position: fixed;
                    top: 0; left: 0; width: 100vw; height: 100vh;
                    pointer-events: none; z-index: 9999;
                    overflow: hidden;
                ">
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

        #패배하면 똥세례 
        else:
            st.error(st.session_state.game_result_msg)
            # 1. 킹받는 패배 전용 똥 움짤 배치
            st.image("assets/rainbowpoo.gif", use_container_width=True)
            
            # 2. 웹 브라우저 전체 화면에 💩 이모지가 비처럼 흘러내리는 똥세례 효과 (HTML/CSS 치트키)
            st.markdown(
                """
                <div style="
                    position: fixed;
                    top: 0; left: 0; width: 100vw; height: 100vh;
                    pointer-events: none; z-index: 9999;
                    overflow: hidden;
                ">
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
        col_b1, col_b2, col_b3, col_b4= st.columns(4)
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
