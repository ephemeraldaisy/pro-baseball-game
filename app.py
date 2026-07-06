import random
import streamlit as st
import os 

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
    
    # 🚨 [이닝 뻥튀기 버그 방지 패치] 
    # 정규이닝(9회) 안에서 승부가 났는데 이닝이 10으로 먼저 올라갔다면 9회로 보정해 줍니다.
    if st.session_state.inning >= 10:
        # 연장전 대혈투 끝에 끝난 게 아니라, 9회 점수 차로 일반 종료된 케이스라면
        score_gap = abs(st.session_state.our_score - st.session_state.enemy_score)
        # 연장 동점이 깨진 게 아니라 정규이닝 종료 요건이라면 9회로 유지
        if st.session_state.inning == 10 and st.session_state.phase == "초":
            st.session_state.inning = 9
            st.session_state.phase = "말" # 9회말로 정정하여 표기

    # 기존 승패 메시지 출력 로직 (그대로 유지)
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

    # 🟢 버튼 딱 한 번 클릭에 정직하게 무조건 '1구'만 증가!
    enemy_pitch_count = 1
    st.session_state.enemy_total_pitches += enemy_pitch_count

    current_batter = st.session_state.my_batter_number
    log_msg = ""
    at_bat_result = "지속"  # 타석이 끝났는지 판단하는 트리거

    # =======================================================
    # [방향 전환] 1번, 2번 작전은 카운트 없이 '즉시 타석 결판'! (단, 파울은 고증 적용)
    # =======================================================
    if user_choice == 1:    # 💥 1. 풀스윙 강타
        result = random.choices(
            ["HOMERUN", "HIT", "OUT", "FOUL"], 
            weights=[80, 170, 550, 200]  # 카운트 없이 바로 결과 유도!
        )[0]
        
        if result == "HOMERUN": at_bat_result = "홈런"
        elif result == "HIT": at_bat_result = "안타"
        elif result == "OUT": at_bat_result = "아웃"
        elif result == "FOUL":
            # ⚾ [파울 고증] 2스트라이크 미만이면 스트라이크 1개 추가!
            if st.session_state.strike < 2:
                st.session_state.strike += 1
                st.session_state.game_log.append(f"💥 작전[풀스윙 강타]: 아슬아슬하게 파울 홈런! 스트라이크가 추가됩니다. (현재 {st.session_state.strike}S {st.session_state.ball}B / 상대 투수 총 {st.session_state.enemy_total_pitches}구)")
            else:
                st.session_state.game_log.append(f"💥 작전[풀스윙 강타]: 2S 이후 아슬아슬한 파울 홈런! 타석을 이어갑니다. (현재 {st.session_state.strike}S {st.session_state.ball}B / 상대 투수 총 {st.session_state.enemy_total_pitches}구)")
            return

    elif user_choice == 2:  # 🌟 2. 가볍게 밀어치기
        result = random.choices(
            ["HIT", "OUT", "FOUL"], 
            weights=[350, 450, 200]  # 안타율이 조금 더 높은 정교한 타격
        )[0]
        
        if result == "HIT": at_bat_result = "안타"
        elif result == "OUT": at_bat_result = "아웃"
        elif result == "FOUL":
            # ⚾ [파울 고증] 2스트라이크 미만이면 스트라이크 1개 추가!
            if st.session_state.strike < 2:
                st.session_state.strike += 1
                st.session_state.game_log.append(f"💥 작전[가볍게 밀어치기]: 빗맞은 타구 파울! 스트라이크가 추가됩니다. (현재 {st.session_state.strike}S {st.session_state.ball}B / 상대 투수 총 {st.session_state.enemy_total_pitches}구)")
            else:
                st.session_state.game_log.append(f"💥 작전[가볍게 밀어치기]: 2S 이후 끈질기게 커트, 파울! 타석을 이어갑니다. (현재 {st.session_state.strike}S {st.session_state.ball}B / 상대 투수 총 {st.session_state.enemy_total_pitches}구)")
            return

    # =======================================================
    # [핵심 패치] 3번 작전을 눌러야만 전광판 볼 카운트가 트리거됨!
    # =======================================================
    elif user_choice == 3:  # 👀 3. 공 끝까지 거르기
        # 배트를 전혀 휘두르지 않으므로 오직 스트라이크와 볼만 쌓입니다.
        result = random.choices(
            ["STRIKE", "BALL"], 
            weights=[400, 600] # 볼 고를 확률 60%
        )[0]

        if result == "STRIKE":
            st.session_state.strike += 1
            log_msg = f"❌ 스트라이크를 지켜봅니다! (현재 {st.session_state.strike}S {st.session_state.ball}B)"
            
            # 3스트라이크가 되면 삼진 아웃 확정!
            if st.session_state.strike >= 3:
                st.session_state.game_log.append(f"⚡ 앗 아아... {current_batter}번 타자 공만 보다가 루킹 삼진 아웃!! (상대 투수 총 {st.session_state.enemy_total_pitches}구)")
                at_bat_result = "삼진"

        elif result == "BALL":
            st.session_state.ball += 1
            log_msg = f"🟢 훌륭한 선구안! 볼을 골라냅니다! (현재 {st.session_state.strike}S {st.session_state.ball}B)"
            
            # 4볼이 되면 볼넷 출루 확정!
            if st.session_state.ball >= 4:
                at_bat_result = "볼넷"

        # 볼/스트라이크 진행 상황 실시간 중계 브리핑
        if log_msg:
            st.session_state.game_log.append(f" 작전[공 끝까지 거르기]: {log_msg}")


    # =======================================================
    # 🏃‍♂️ [통합 진루 및 타자 교체 엔진] 타석이 결판났을 때만 가동!
    # =======================================================
    if at_bat_result != "지속":
        # 타석이 완전히 끝났으므로 전광판 볼카운트는 깨끗이 청소!
        st.session_state.strike = 0
        st.session_state.ball = 0
        # 즉시 다음 타자로 넘기기 설정
        st.session_state.my_batter_number = 1 if current_batter == 9 else current_batter + 1

        if at_bat_result == "홈런":
            pts = (1 if st.session_state.base1 else 0) + (1 if st.session_state.base2 else 0) + (1 if st.session_state.base3 else 0) + 1
            st.session_state.our_score += pts
            st.session_state.game_log.append(f"🔥 🎉 깡!!!!! {current_batter}번 타자 대형 {pts}점짜리 홈런 대폭발!!!!!!!! (상대 투수 총 {st.session_state.enemy_total_pitches}구)")
            st.session_state.base1 = st.session_state.base2 = st.session_state.base3 = False

        elif at_bat_result == "안타":
            if st.session_state.base3: st.session_state.our_score += 1
            if st.session_state.base2: st.session_state.our_score += 1
            st.session_state.base3 = st.session_state.base1
            st.session_state.base2 = False
            st.session_state.base1 = True
            st.session_state.game_log.append(f"🌟 딱! {current_batter}번 타자의 안타! 주자 나갑니다! (상대 투수 총 {st.session_state.enemy_total_pitches}구)")

        elif at_bat_result == "아웃":
            st.session_state.out_count += 1
            st.session_state.game_log.append(f" Ah... {current_batter}번 타자 내야 땅볼 아웃입니다. (상대 투수 총 {st.session_state.enemy_total_pitches}구)")
            check_three_out_change()

        elif at_bat_result == "삼진":
            st.session_state.out_count += 1
            check_three_out_change()

        elif at_bat_result == "볼넷":
            st.session_state.game_log.append(f"🚶‍♂️ {current_batter}번 타자 끈질긴 눈야구로 볼넷 출루! (상대 투수 총 {st.session_state.enemy_total_pitches}구)")
            if st.session_state.base1 and st.session_state.base2 and st.session_state.base3:
                st.session_state.our_score += 1
                st.session_state.game_log.append("➔ 밀어내기 만루 볼넷으로 1점 추가!")
            elif st.session_state.base1 and st.session_state.base2: st.session_state.base3 = True
            elif st.session_state.base1: st.session_state.base2 = True
            else: st.session_state.base1 = True

    # 🌟 9회말 끝내기 요건 체크
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

# 📜 여기에 딱 배치하면 게임 시작하기 전에 언제든 열어볼 수 있습니다!
if st.button("📜 KBO 스타일 구단 설정집 열람"):
    st.session_state.show_stories = True

if st.session_state.show_stories:
    file_path = "assets/team_stories.txt"
    st.markdown("---")
    st.subheader("🕵️‍♂️ 10대 구단 비사(秘史) 및 성격 설정집")
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            stories_text = f.read()
        st.text_area("구단별 성격 및 스토리", value=stories_text, height=300, disabled=True)
    else:
        st.error("⚠️ assets/team_stories.txt 파일을 찾을 수 없습니다!")
        
    if st.button("❌ 설정집 닫기"):
        st.session_state.show_stories = False
        st.rerun()
    st.markdown("---")

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
