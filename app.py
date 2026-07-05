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
    
    # 9회말 우리 팀(홈) 특별 위기 상황 이벤트 유지
    if st.session_state.inning == 9 and st.session_state.phase == "말" and st.session_state.is_home_team and st.session_state.our_score <= st.session_state.enemy_score:
        st.session_state.out_count = 2
        st.session_state.base1 = st.session_state.base2 = st.session_state.base3 = True
        st.session_state.game_log.append("🚨 [9회말 극장] 주자 만루 찬스! 사모님 타석이 다가옵니데이!")
    else:
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
    pitches = ["직구", "슬라이더", "체인지업"]
    pitch = random.choice(pitches)
    st.session_state.game_log.append(f"⚾ 투수가 구석을 찌르는 '[{pitch}]'을 던졌습니다!")

    at_bat_result = None
    result = random.random()

    # 1. 풀스윙 강타
    if user_choice == 1:
        if (pitch == "직구" and result < 0.15) or (pitch != "직구" and result < 0.08):
            at_bat_result = "홈런"
        elif result < 0.55:
            st.session_state.game_log.append("➔ 파울! 타이밍은 맞았는데 빗맞았습니다.")
            if st.session_state.strike < 2: st.session_state.strike += 1
        else:
            st.session_state.game_log.append("➔ 헛스윙 삼진 유도구에 완전히 속았습니다!")
            st.session_state.strike += 1

    # 2. 가볍게 밀어치기 (병살타 탑재)
    elif user_choice == 2:
        if result < 0.30:
            at_bat_result = "안타"
        elif result < 0.45:
            # 병살타 조건: 0아웃 혹은 1아웃이면서, 1루에 주자가 있을 때
            if st.session_state.out_count < 2 and st.session_state.base1:
                st.session_state.game_log.append(" Ground Ball!! 내야 땅볼 타구!")
                st.session_state.game_log.append("⚡ [병살타] 유격수 ➔ 2루수 ➔ 1루수 더블 플레이!!! 아웃카운트 2개 소멸!")
                
                st.session_state.out_count += 2
                st.session_state.strike = st.session_state.ball = 0
                st.session_state.base1 = False
                
                if st.session_state.base3:
                    st.session_state.our_score += 1
                    st.session_state.game_log.append("➔ 그 와중에 3루 주자는 홈인하여 1점 만회!")
                st.session_state.base3 = st.session_state.base2
                st.session_state.base2 = False
                
                current_batter = st.session_state.my_batter_number
                st.session_state.my_batter_number = 1 if current_batter == 9 else current_batter + 1
                
                # 아웃카운트 변동으로 쓰리아웃 체인지 체크
                check_three_out_change()
                st.rerun()
                return
            else:
                st.session_state.game_log.append("➔ 범타! 힘없는 타구가 파울 플라이가 되었습니다.")
                if st.session_state.strike < 2: st.session_state.strike += 1
        elif result < 0.75:
            st.session_state.game_log.append("➔ 범타! 힘없는 타구가 파울 플라이가 되었습니다.")
            if st.session_state.strike < 2: st.session_state.strike += 1
        else:
            st.session_state.game_log.append("➔ 스트라이크! 배트가 허공을 가릅니다.")
            st.session_state.strike += 1

    # 3. 공 끝까지 거르기
    elif user_choice == 3:
        if result < 0.35:
            st.session_state.game_log.append("➔ 볼! 유인구를 끈질기게 잘 참아냈습니다.")
            st.session_state.ball += 1
            if st.session_state.ball == 4: at_bat_result = "볼넷"
        else:
            st.session_state.game_log.append("➔ 앗! 스트라이크 존 한가운데 꽂히는 루킹 스트라이크!")
            st.session_state.strike += 1

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
st.title("⚾ KBO 매운맛 프로야구 시뮬레이터")

if not st.session_state.game_setup:
    st.markdown("### 🏟️ 구단 선택 및 리그 매칭")
    my_choice = st.selectbox("사모님이 이끌어갈 우리 팀을 고르이소:", list(TEAMS.keys()))
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
        else:
            st.error(st.session_state.game_result_msg)
            
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
