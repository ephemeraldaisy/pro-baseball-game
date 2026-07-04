import random
import streamlit as st

# ==========================================
# 1. 페이지 기본 설정 및 스타일
# ==========================================
st.set_page_config(page_title="이 사장의 프로야구 시뮬레이터", page_icon="⚾", layout="centered")

st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        margin-bottom: 10px;
        font-size: 16px !important;
        font-weight: bold;
    }
    .reportview-container .main .block-container{
        padding-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 게임 상태(Session State) 초기화
# ==========================================
if "game_started" not in st.session_state:
    st.session_state.game_started = False

def reset_game():
    st.session_state.is_home_team = random.choice([True, False])
    st.session_state.our_score = 0
    st.session_state.enemy_score = 0
    st.session_state.my_batter_number = 1
    st.session_state.inning = 1
    st.session_state.phase = "초"  # "초" 또는 "말"
    
    # 이닝 내 상태 초기화
    st.session_state.out_count = 0
    st.session_state.strike = 0
    st.session_state.ball = 0
    st.session_state.base1 = False
    st.session_state.base2 = False
    st.session_state.base3 = False
    
    st.session_state.game_log = ["🎮 동전을 던져 진영을 결정했습니다!"]
    st.session_state.game_over = False
    st.session_state.game_started = True
    st.session_state.game_result_msg = ""
    
    # 1회초/말 상황에 맞게 초기 세팅
    setup_half_inning()

def setup_half_inning():
    """새로운 이닝(초 또는 말)이 시작될 때 필드를 세팅하는 함수"""
    # 경기 종료/연장 판정 커트라인 체크
    if st.session_state.inning > 9 and st.session_state.our_score != st.session_state.enemy_score:
        end_game()
        return

    # 콜드게임 체크
    score_gap = abs(st.session_state.our_score - st.session_state.enemy_score)
    if st.session_state.inning in [5, 6] and score_gap >= 10:
        st.session_state.game_result_msg = f"🚨 [COLD GAME] {st.session_state.inning}회 종료 시점 {score_gap}점 차로 콜드게임이 선언되었습니다!"
        end_game()
        return
    elif st.session_state.inning in [7, 8] and score_gap >= 7:
        st.session_state.game_result_msg = f"🚨 [COLD GAME] {st.session_state.inning}회 종료 시점 {score_gap}점 차로 콜드게임이 선언되었습니다!"
        end_game()
        return

    # 9회말 끝내기 조건 체크
    if st.session_state.inning >= 9 and st.session_state.phase == "말" and st.session_state.is_home_team and st.session_state.our_score > st.session_state.enemy_score:
        end_game()
        return

    # 주자 상황 세팅
    st.session_state.strike = 0
    st.session_state.ball = 0
    
    # 9회말 우리 팀(홈) 공격인 특별 위기 상황 이벤트 유지
    if st.session_state.inning == 9 and st.session_state.phase == "말" and st.session_state.is_home_team:
        st.session_state.out_count = 2
        st.session_state.base1 = True
        st.session_state.base2 = True
        st.session_state.base3 = True
        st.session_state.game_log.append("🚨 [9회말 극장 상황] 2아웃 주자 만루 찬스가 찾아왔습니다!")
    else:
        st.session_state.out_count = 0
        st.session_state.base1 = False
        st.session_state.base2 = False
        st.session_state.base3 = False

    # 컴퓨터(상대팀) 수비/공격 자동 시뮬레이션 처리
    current_is_our_turn = (not st.session_state.is_home_team and st.session_state.phase == "초") or (st.session_state.is_home_team and st.session_state.phase == "말")
    
    if not current_is_our_turn:
        # 상대 팀 공격 진행 (초스피드 렉 해결 버전)
        enemy_pts = random.choice([0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 5])
        
        if st.session_state.inning >= 9 and st.session_state.phase == "말":
            # 상대가 끝내기 요건을 충족하는지 바로 체크
            if enemy_pts > 0 and (st.session_state.enemy_score + enemy_pts) > st.session_state.our_score:
                st.session_state.enemy_score = st.session_state.our_score + 1
                st.session_state.game_log.append(f"➔ 앗! 상대 팀이 {st.session_state.inning}회말 끝내기 점수를 올렸습니다...")
                end_game()
                return
            else:
                st.session_state.enemy_score += enemy_pts
                st.session_state.game_log.append(f"🔮 상대 팀 {st.session_state.inning}회말 공격 완료: +{enemy_pts}점")
        else:
            st.session_state.enemy_score += enemy_pts
            st.session_state.game_log.append(f"🔮 상대 팀 {st.session_state.inning}회{st.session_state.phase} 공격 완료: +{enemy_pts}점")
        
        # 상대 턴이 끝났으니 즉시 다음 페이즈로 토스
        next_phase()

def next_phase():
    """초->말, 말->다음이닝 초로 페이즈를 전환하는 함수"""
    if st.session_state.phase == "초":
        st.session_state.phase = "말"
    else:
        st.session_state.phase = "초"
        st.session_state.inning += 1
    setup_half_inning()

def end_game():
    st.session_state.game_over = True
    if st.session_state.our_score > st.session_state.enemy_score:
        st.session_state.game_result_msg = "🎉 대승리!!! 오늘 경기 수당은 사모님 기라!! 고생하셨네예!!!"
    elif st.session_state.our_score < st.session_state.enemy_score:
        st.session_state.game_result_msg = "😭 아쉽게 패배하셨습니다... 다음 경기에 설욕하러 가이소!"
    else:
        st.session_state.game_result_msg = "🤝 치열한 대혈투 끝에 승부를 가리지 못하고 무승부로 끝났습니다!"

# ==========================================
# 3. 타석 스윙 액션 처리 (핵심 엔진)
# ==========================================
def play_turn(user_choice):
    pitches = ["직구", "슬라이더", "체인지업"]
    pitch = random.choice(pitches)
    st.session_state.game_log.append(f"⚾ 투수가 던진 공은 매서운 '[{pitch}]' 이었습니다!")

    at_bat_result = None

    # 1. 풀스윙
    if user_choice == 1:
        result = random.random()
        if (pitch == "직구" and result < 0.4) or (pitch != "직구" and result < 0.2):
            at_bat_result = "홈런"
        elif result < 0.7:
            st.session_state.game_log.append("➔ 파울! 엄청난 스윙이었지만 아쉽게 빗맞았습니다.")
            if st.session_state.strike < 2: st.session_state.strike += 1
        else:
            st.session_state.game_log.append("➔ 헛스윙!!! 공기를 가르는 무지막지한 스윙 기라!")
            st.session_state.strike += 1

    # 2. 밀어치기
    elif user_choice == 2:
        result = random.random()
        if result < 0.5:
            at_bat_result = "안타"
        elif result < 0.8:
            st.session_state.game_log.append("➔ 내야 파울 플라이 아웃성 타구지만 파울 라인 밖입니다!")
            if st.session_state.strike < 2: st.session_state.strike += 1
        else:
            st.session_state.game_log.append("➔ 헛스윙 스트라이크! 배트가 돌았네예!")
            st.session_state.strike += 1

    # 3. 거르기
    elif user_choice == 3:
        result = random.random()
        if result < 0.6:
            st.session_state.game_log.append("➔ 나이스 아이! 낮게 깔리는 공 잘 골라내셨네예! '볼(Ball)'!")
            st.session_state.ball += 1
            if st.session_state.ball == 4: at_bat_result = "볼넷"
        else:
            st.session_state.game_log.append("➔ 꼼짝 못 하고 당했네예! 루킹 '스트라이크(Strike)'!")
            st.session_state.strike += 1

    # 주자 진루 엔진 및 아웃 판정
    if at_bat_result in ["홈런", "안타", "볼넷"]:
        st.session_state.strike = 0
        st.session_state.ball = 0
        current_batter = st.session_state.my_batter_number
        st.session_state.my_batter_number = 1 if current_batter == 9 else current_batter + 1

        if at_bat_result == "홈런":
            pts = (1 if st.session_state.base1 else 0) + (1 if st.session_state.base2 else 0) + (1 if st.session_state.base3 else 0) + 1
            st.session_state.our_score += pts
            st.session_state.game_log.append(f"🔥 🎉 깡!!!!! {current_batter}번 타자 초대형 {pts}점짜리 홈런 대폭발!!!!!!!!")
            st.session_state.base1 = st.session_state.base2 = st.session_state.base3 = False

        elif at_bat_result == "안타":
            st.session_state.game_log.append(f"🌟 딱! {current_batter}번 타자가 안타를 치고 주자들을 밀어냅니다!")
            if st.session_state.base3: st.session_state.our_score += 1
            if st.session_state.base2: st.session_state.our_score += 1
            st.session_state.base3 = st.session_state.base1
            st.session_state.base2 = False
            st.session_state.base1 = True

        elif at_bat_result == "볼넷":
            st.session_state.game_log.append(f"🏃‍♂️ {current_batter}번 타자 눈야구 성공! 걸어나갑니다. 볼넷!")
            if st.session_state.base1 and st.session_state.base2 and st.session_state.base3:
                st.session_state.our_score += 1
                st.session_state.game_log.append("➔ 주자 만루 상황이라 밀어내기로 1점 추가!")
            elif st.session_state.base1 and st.session_state.base2: st.session_state.base3 = True
            elif st.session_state.base1: st.session_state.base2 = True
            else: st.session_state.base1 = True

    elif st.session_state.strike == 3:
        st.session_state.game_log.append(f"❌ 아쉽습니다! {st.session_state.my_batter_number}번 타자 삼진 아웃!")
        st.session_state.out_count += 1
        st.session_state.strike = 0
        st.session_state.ball = 0
        current_batter = st.session_state.my_batter_number
        st.session_state.my_batter_number = 1 if current_batter == 9 else current_batter + 1

        if st.session_state.out_count == 3:
            st.session_state.game_log.append(f"📢 쓰리아웃 체인지! 우리 팀의 이번 이닝 공격 종료.")
            # 말 공격 도중 3아웃인데 지고 있다면 즉시 종료 판정
            if st.session_state.phase == "말" and st.session_state.our_score < st.session_state.enemy_score:
                end_game()
                return
            next_phase()

    # 실시간 끝내기 승리 체크
    if st.session_state.inning >= 9 and st.session_state.phase == "말" and st.session_state.is_home_team and st.session_state.our_score > st.session_state.enemy_score:
        end_game()

# ==========================================
# 4. 웹 UI 그리기 (Streamlit 화면 배치)
# ==========================================
st.title("⚾ 이 사장의 프로야구 시뮬레이터 봇")

if not st.session_state.game_started:
    st.info("9회말 2아웃 만루 극장부터 지옥의 연장전 클린슬레이트까지 구현 완료 기라!")
    if st.button("경기 시작 (동전 던지기 🪙)", type="primary"):
        reset_game()
        st.rerun()
else:
    # 4-1. 상단 전광판 스코어 보드
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        st.metric(label="우리 팀 🇰🇷", value=f"{st.session_state.our_score} 점")
    with col2:
        st.markdown(f"<h3 style='text-align: center; color: gray;'>{st.session_state.inning}회{st.session_state.phase}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-size:12px;'>진영: {'홈팀(후공)' if st.session_state.is_home_team else '원정팀(선공)'}</p>", unsafe_allow_html=True)
    with col3:
        st.metric(label="상대 팀 🇨🇳", value=f"{st.session_state.enemy_score} 점")

    st.divider()

    if st.session_state.game_over:
        st.balloons() if st.session_state.our_score > st.session_state.enemy_score else None
        st.success(st.session_state.game_result_msg) if st.session_state.our_score >= st.session_state.enemy_score else st.error(st.session_state.game_result_msg)
        if st.button("새 경기 시작하기 🔄", type="primary"):
            reset_game()
            st.rerun()
    else:
        # 4-2. 중단 카운트 및 다이아몬드 현황
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"### 📊 현재 카운트")
            st.markdown(f"* **아웃:** {'🔴' * st.session_state.out_count}{'⚪' * (3-st.session_state.out_count)}")
            st.markdown(f"* **스트라이크:** {'🔥' * st.session_state.strike}{'⚪' * (3-st.session_state.strike)}")
            st.markdown(f"* **볼:** {'🟢' * st.session_state.ball}{'⚪' * (4-st.session_state.ball)}")
            st.markdown(f"* **현재 타석:** `{st.session_state.my_batter_number}번 타자` " + ("(👑 사모님!)" if st.session_state.my_batter_number == 4 else ""))

        with c2:
            st.markdown("### 🏃 주자 상황")
            b1 = "🏃" if st.session_state.base1 else "◯"
            b2 = "🏃" if st.session_state.base2 else "◯"
            b3 = "🏃" if st.session_state.base3 else "◯"
            st.code(f"""
                   [{b2}] 2루
            [{b3}] 3루         [{b1}] 1루
                    [X] 타석
            """, language="text")

        st.divider()

        # 4-3. 하단 플레이어 조작 버튼 (우리 팀 턴일 때만 활성화)
        st.markdown("### 📢 사모님의 작전 지시")
        
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            if st.button("🔥 1. 풀스윙 강타"):
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

    # 4-4. 중계방 로그 출력
    st.divider()
    st.markdown("### 🎙️ 캐스터 중계 일지")
    for log in reversed(st.session_state.game_log[-8:]):  # 최신 로그 8개만 역순 표시
        st.write(log)
