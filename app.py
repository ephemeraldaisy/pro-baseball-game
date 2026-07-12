import random
import streamlit as st
import os 
import pandas as pd 

# ==========================================
# 1. 페이지 설정 및 팀 데이터 (능력치 및 도루 성향 통합)
# ==========================================
st.set_page_config(page_title="이 사장의 프로야구 시뮬레이터 Pro", page_icon="⚾", layout="centered")

# [상성 확장] 도루 가변 연동을 위해 각 팀의 주력/도루 보너스("steal_b") 지표 추가!
TEAMS = {
    "🔴 레드 파이어스": {"homerun": 5, "hit": 30, "out": -10, "strike_p": -30, "ball_p": 30, "steal_b": 25},   # 기회주의, 도루 최강
    "🔵 블루 웨이브스": {"homerun": 20, "hit": 40, "out": -20, "strike_p": 10, "ball_p": -10, "steal_b": -10}, # 묵직함, 주력 느림
    "🟢 그린 몬스터즈": {"homerun": 60, "hit": -20, "out": 20, "strike_p": 50, "ball_p": -50, "steal_b": -20},  # 괴물, 대도 불가[cite: 1]
    "🟡 옐로우 타이거즈": {"homerun": 30, "hit": 10, "out": -10, "strike_p": 20, "ball_p": -20, "steal_b": 15},   # 야성미, 준수한 발[cite: 1]
    "🟣 퍼플 바이퍼스": {"homerun": -30, "hit": 20, "out": -30, "strike_p": -50, "ball_p": 80, "steal_b": 5},   # 끈질긴 기동력[cite: 1]
    "🟠 오렌지 자이언츠": {"homerun": 25, "hit": 0, "out": 10, "strike_p": 10, "ball_p": -10, "steal_b": -15},  # 거인, 둔함[cite: 1]
    "🟤 브라운 베어스": {"homerun": 10, "hit": 20, "out": -10, "strike_p": -10, "ball_p": 10, "steal_b": 10},   # 타짜 베이스 러닝[cite: 1]
    "⚪ 화이트 이글스": {"homerun": -10, "hit": 50, "out": -20, "strike_p": 10, "ball_p": 0, "steal_b": 5},     # 번개 같은 기동력[cite: 1]
    "⚫ 블랙 나이츠": {"homerun": 0, "hit": 10, "out": -20, "strike_p": -20, "ball_p": 20, "steal_b": 0},      # 단단한 주루[cite: 1]
    "💖 핑크 돌핀스": {"homerun": 40, "hit": 30, "out": 10, "strike_p": 30, "ball_p": -20, "steal_b": 20}      # 신나면 뜀, 도파민 주루[cite: 1]
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

#구종과 타자 예상 위치
if "pitch_type" not in st.session_state: st.session_state.pitch_type = "직구"
if "pitch_zone" not in st.session_state: st.session_state.pitch_zone = 5 # 1~9번 구역 (5번은 한가운데)
if "guess_zone" not in st.session_state: st.session_state.guess_zone = 5

if "away_inning_scores" not in st.session_state:
    st.session_state.away_inning_scores = [""] * 12
if "home_inning_scores" not in st.session_state:
    st.session_state.home_inning_scores = [""] * 12

def start_new_game(my_team, enemy_team):
    st.session_state.my_team = my_team        
    st.session_state.enemy_team = enemy_team  
    
    st.session_state.my_emoji = my_team[:2]
    st.session_state.enemy_emoji = enemy_team[:2]
    
    st.session_state.is_home_team = random.choice([True, False])
    
    st.session_state.our_score = 0
    st.session_state.enemy_score = 0
    st.session_state.my_batter_number = 1
    st.session_state.inning = 1
    st.session_state.phase = "초"
    
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

# [대수술 1] 가변 수비 로그 연출 및 9회말 상대 끝내기 요건 고증
def setup_half_inning():
    #연장전이 시작될 때 초라면, 말에서 승패가 갈렸는지 확인  
    if st.session_state.inning > 9 and st.session_state.phase == "초":
        if st.session_state.our_score != st.session_state.enemy_score:
            end_game()
            return 

    #콜드게임 규정 
    score_gap = abs(st.session_state.our_score - st.session_state.enemy_score)
    if st.session_state.inning in [5, 6] and score_gap >= 10:
        st.session_state.game_result_msg = f"🚨 [COLD GAME] {st.session_state.inning}회 종료 시점 {score_gap}점 차로 콜드게임 선언!"
        end_game()
        return
    elif st.session_state.inning in [7, 8] and score_gap >= 7:
        st.session_state.game_result_msg = f"🚨 [COLD GAME] {st.session_state.inning}회 종료 시점 {score_gap}점 차로 콜드게임 선언!"
        end_game()
        return

    # 우리가 홈팀(후공)인데 9회초 종료 시점 이기고 있으면 9회말 삭제 및 조기종료
    if st.session_state.inning == 9 and st.session_state.phase == "말":
        if st.session_state.is_home_team and st.session_state.our_score > st.session_state.enemy_score:
            st.session_state.game_log.append("👍 9회초까지 이미 우리 팀이 이기고 있어 9회말 공격 없이 경기가 끝납니다! (9회말 X)")
            end_game()
            return

    #타석 초기화 
    st.session_state.strike = 0
    st.session_state.ball = 0
    st.session_state.out_count = 0
    st.session_state.base1 = st.session_state.base2 = st.session_state.base3 = False

    current_is_our_turn = (not st.session_state.is_home_team and st.session_state.phase == "초") or (st.session_state.is_home_team and st.session_state.phase == "말")
    
    # 💥 [가변 수비 로그 및 상성 매트릭스 엔진 활성화]
    if not current_is_our_turn:
        my_team = st.session_state.my_team
        enemy_team = st.session_state.enemy_team
        
        # 장부 정보 연동
        enemy_buff = TEAMS.get(enemy_team, {"ball_p": 0, "out": 0})
        my_buff = TEAMS.get(my_team, {"out": 0})
        
        # -----------------------------------------------------------
        # 📊 [Matrix 고증] 상성에 따른 실점 확률 주사위(weights) 조율 파트
        # -----------------------------------------------------------
        # 기본 확률: [0점, 1점, 2점, 3점, 4점, 메가이닝]
        base_weights = [510, 240, 150, 70, 25, 5]
        
        # 상대(공격)가 우리(수비)에게 강한 천적 구도일 때 (예: 레드가 그린을 만났을 때)
        # 10x10 상성 대장부 서사를 기반으로 가변 조정
        is_enemy_dominant = (
            (enemy_team == "🔴 레드 파이어스" and my_team == "🟢 그린 몬스터즈") or
            (enemy_team == "🔵 븍루 웨이브스" and my_team == "⚫ 블랙 나이츠") or
            (enemy_team == "🟢 그린 몬스터즈" and my_team == "🟠 오렌지 자이언츠") or
            (enemy_team == "🟡 옐로우 타이거즈" and my_team == "🟤 브라운 베어스") or
            (enemy_team == "🟣 퍼플 바이퍼스" and my_team == "🔵 블루 웨이브스") or
            (enemy_team == "🟠 오렌지 자이언츠" and my_team == "⚪ 화이트 이글스") or
            (enemy_team == "🟤 브라운 베어스" and my_team == "💖 핑크 돌핀스") or
            (enemy_team == "⚪ 화이트 이글스" and my_team == "🔴 레드 파이어스") or
            (enemy_team == "⚫ 블랙 나이츠" and my_team == "🟡 옐로우 타이거즈") or
            (enemy_team == "💖 핑크 돌핀스" and my_team == "🟣 퍼플 바이퍼스")
        )
        
        # 우리가 상대(공격)를 꽁꽁 틀어막는 우세 구도일 때 (역상성)
        is_we_dominant = (
            (my_team == "🔴 레드 파이어스" and enemy_team == "🟢 그린 몬스터즈") or
            (my_team == "🔵 블루 웨이브스" and enemy_team == "⚫ 블랙 나이츠") or
            (my_team == "🟢 그린 몬스터즈" and enemy_team == "🟠 오렌지 자이언츠") or
            (my_team == "🟡 옐로우 타이거즈" and enemy_team == "🟤 브라운 베어스") or
            (my_team == "🟣 퍼플 바이퍼스" and enemy_team == "🔵 블루 웨이브스") or
            (my_team == "🟠 오렌지 자이언츠" and enemy_team == "⚪ 화이트 이글스") or
            (my_team == "🟤 브라운 베어스" and enemy_team == "💖 핑크 돌핀스") or
            (my_team == "⚪ 화이트 이글스" and enemy_team == "🔴 레드 파이어스") or
            (my_team == "⚫ 블랙 나이츠" and enemy_team == "🟡 옐로우 타이거즈") or
            (my_team == "💖 핑크 돌핀스" and enemy_team == "🟣 퍼플 바이퍼스")
        )

        if is_enemy_dominant:
            # 천적을 만나 아우토반 뚫리듯 실점 확률 폭등! (0점 확률 깎고, 대량실점 확률 업)
            base_weights = [350, 280, 200, 110, 50, 10]
        elif is_we_dominant:
            # 우리가 킬러 자석! 상성 우위로 탈탈 털어버림 (0점 확률 폭발)
            base_weights = [680, 180, 90, 40, 10, 0]

        # 최종 실점 주사위 굴리기
        base_pts = random.choices([0, 1, 2, 3, 4, -1], weights=base_weights)[0]
        
        if base_pts == -1:
            enemy_pts = random.randint(5, 10)
            def_log = f"😱 [🚨 메가 이닝 발생] 상대 팀 타선이 불타오릅니다! 난타전 끝에 {enemy_pts}실점..."
        else:
            enemy_pts = base_pts
            
            # 🟢 [대개조] 0점 무실점일 때 고증 엔진 가동
            if enemy_pts == 0:
                # KKK 삼진쇼 / 일반 삼자범퇴 / 병살타 무작위 세부 분화
                defense_type = random.choice(["KKK", "일반", "병살"])
                if is_we_dominant and random.random() < 0.40: 
                    defense_type = "KKK" # 상성 우위면 삼진쇼 확률 추가 보정
                
                if defense_type == "KKK":
                    def_log = "🛡️ 마운드의 우리 투수가 미쳐 날뜁니다! 세 타자를 연속 KKK 3삼진으로 완벽하게 돌려세웁니다!"
                elif defense_type == "일반":
                    def_log = random.choice([
                        "🛡️ 우리 투수가 삼자범퇴로 상대 타선을 꽁꽁 틀어막았습니다! (무실점)",
                        "🛡️ 우리 투수가 안정된 제구력으로 상대 타선을 깔끔한 삼자범퇴로 요리했습니다!"
                    ])
                else:
                    def_log = "🛡️ 루상에 주자가 나갔으나, 내야진의 환상적인 '더블플레이(병살타)'가 터지며 위기를 실점 없이 넘깁니다!"

            # 형님의 피와 살이 담긴 실점 멘트 가변 연동
            elif enemy_pts == 1:
                def_log = random.choice([
                    "💥 아쉽게 상대 팀에게 솔로 홈런 한 방을 허용하며 1실점합니다.",
                    "💥 아쉽게 상대 팀에게 적시타를 허용하여 1실점 합니다.",
                    "📐 외야 깊숙한 희생플라이로 3루 주자가 홈을 밟으며 1점을 내어줍니다.",
                    "🏃‍♂️ 발 빠른 2루 주자가 단타 한 방에 홈까지 파고들어 아쉽게 실점합니다.",
                    " 실책으로 주자를 내보내더니, 결국 내야 땅볼 때 홈을 허용하며 1실점합니다.",
                    "굴러온 수비 실책으로 주자를 내보내더니, 결국 내야 땅볼 때 홈을 허용하며 1실점합니다."
                ])
            elif enemy_pts == 2:
                def_log = random.choice([
                    "🚀 담장을 훌쩍 넘어가는 투런 홈런을 얻어맞으며 순식간에 2실점합니다.",
                    "🔥 좌우중간을 완전히 가르는 싹쓸이 2루타! 루상의 주자 2명이 모두 홈을 밟습니다.",
                    "연속 안타를 얻어맞으며 수비진이 흔들립니다. 순식간에 2점을 내어줍니다.",
                    " 무사 만루 대위기! 밀어내기 볼넷에 이어 희생플라이까지 나오며 2실점합니다.",
                    " 안타에 수비 실책까지 겹치면서, 주자 2명이 연달아 홈으로 들어옵니다.",
                    " 적시타를 허용한 뒤 외야수의 홈 송구가 뒤로 빠지면서 주자 두 명이 모두 득점합니다.",
                    "솔로 홈런 후에 백투백 홈런을 얻어맞아 2실점합니다."
                ])
            elif enemy_pts == 3:
                def_log = random.choice([
                    "🚀 비거리 대폭발! 벼락같은 쓰리런 홈런을 얻어맞으며 순식간에 3실점합니다.",
                    "🔥 주자 만루 상황, 우익수 키를 넘기는 싹쓸이 3루타가 터지며 주자 3명이 모두 홈인합니다!",
                    " 연속 안타에 볼넷까지, 마운드가 완전히 무너지며 이번 이닝에만 3점을 헌납합니다.",
                    " 아웃카운트를 잡지 못하고 밀어내기 볼넷에 이어 2타점 적시타까지 허용, 3실점째 기록합니다.",
                    " 결정적인 수비 실책으로 이닝이 끝나지 않더니, 결국 3타점 2루타로 연결되며 피눈물을 흘립니다.",
                    "투런 홈런 후에 백투백 홈런을 얻어맞아 3실점합니다."
                ])
            elif enemy_pts == 4: 
                def_log = random.choice([
                    "😱 이보다 더 최악일 수 없습니다! 담장을 넘어가는 만루 홈런(그랜드 슬램)을 허용하며 4실점합니다!",
                    "🥶 마운드가 완전히 폭발합니다. 백투백 홈런을 포함해 안타를 무차별로 얻어맞으며 4점을 내어줍니다.",
                    "🫨 타자 일순하며 수비진의 멘탈이 흔들립니다. 적시타와 실책이 겹치며 이번 이닝 대거 4실점합니다.",
                    " 만루 위기에서 싹쓸이 2루타를 맞은 뒤, 곧바로 추가 적시타까지 터지며 4실점합니다.",
                    " 투수 교체 카드도 통하지 않았습니다. 연속 볼넷과 장타가 이어지며 허무하게 4점을 실점합니다.",
                    "쓰리런 홈런 후에 백투백 홈런을 얻어맞아 4실점합니다."
                ])              
            else:
                def_log = random.choice([
                    "🚨 마운드가 처참하게 무너져 내립니다! 타자 일순하며 무차별 폭격을 당해 대거 5실점 이상을 허용합니다.",
                    "🥶 이닝이 끝나지 않는 악몽이 계속됩니다. 안타, 볼넷, 홈런 가릴 것 없이 얻어맞으며 빅이닝을 내어줍니다.",
                    "😱 수비진의 연쇄 실책과 투수진의 난조가 겹쳤습니다! 상대의 대폭발에 속절없이 대량 실점합니다.",
                    "🔥 상대 타선이 그야말로 활산처럼 타오릅니다. 투수를 교체해 보아도 불을 끄지 못하고 대거 실점합니다.",
                    "💣 만루 홈런을 포함해 장타가 쉴 새 없이 터집니다. 이번 이닝에만 무더기 점수를 내주며 경기 흐름이 완전히 넘어갑니다.",
                    "😭 실점의 늪에 빠졌습니다. 상대 팀의 완벽한 작전 수행과 폭발적인 타력에 마운드가 난타당하며 빅이닝을 헌납합니다.",
                    "만루홈런(그랜드슬램) 후에 백투백 홈런을 얻어맞아 4실점합니다."
                ])

        # -----------------------------------------------------------
        # 🥎 투구수 WEIGHT 고증 및 가변 조율 구역
        # -----------------------------------------------------------
        team_pitch_modifier = int(enemy_buff["ball_p"] / 10)
        
        if enemy_pts == 0:
            # KKK 삼진쇼가 떴을 때 분기 수식: 무조건 정직하게 '최소 9구 이상' 저격 고정!
            if "KKK" in locals() or ("defense_type" in locals() and defense_type == "KKK"):
                inning_pitches = random.randint(9, 14) + team_pitch_modifier
            else:
                # 일반 삼자범퇴는 초구 타격 아웃 고증으로 최소 5구까지 연동 허용
                inning_pitches = random.randint(6, 12) + team_pitch_modifier
        elif enemy_pts == 1:
            inning_pitches = random.randint(13, 18) + team_pitch_modifier
        elif enemy_pts in [2, 3]:
            inning_pitches = random.randint(17, 24) + team_pitch_modifier
        else: 
            inning_pitches = random.randint(25, 32) + team_pitch_modifier

        # 천적 구도일 때 투구수 스트레스 가중치 추가 보정 (+3구)
        if is_enemy_dominant:
            inning_pitches += 3

        inning_pitches = max(5, inning_pitches)
        st.session_state.our_total_pitches += inning_pitches

        # 🔥 [끝내기 고증] 9회말 상대 끝내기 연출 요건
        if st.session_state.inning >= 9 and st.session_state.phase == "말" and not st.session_state.is_home_team:
            if (st.session_state.enemy_score + enemy_pts) > st.session_state.our_score:
                st.session_state.enemy_score = st.session_state.our_score + 1
                st.session_state.game_log.append(f"❌ Ah... {st.session_state.inning}회말 상대 팀에게 짜릿한 '끝내기 안타'를 얻어맞고 패배했습니다. (최종 {st.session_state.our_total_pitches}구 역투)")
                end_game()
                return
            else:
                st.session_state.enemy_score += enemy_pts
                st.session_state.game_log.append(f"🎉 {def_log} ➔ {st.session_state.inning}회말 심장이 쫄깃한 마지막 반격을 무사히 막아내며 경기 세트!! 마무리 만세!!")
                end_game()
                return
        else:
            st.session_state.enemy_score += enemy_pts


        idx = st.session_state.inning - 1
        if idx < 12:
            if st.session_state.is_home_team: # 우리가 홈이면 상대는 원정(Away)
                if st.session_state.away_inning_scores[idx] == "":
                    st.session_state.away_inning_scores[idx] = enemy_pts
                else:
                    st.session_state.away_inning_scores[idx] += enemy_pts
            else:
                if st.session_state.home_inning_scores[idx] == "":
                    st.session_state.home_inning_scores[idx] = enemy_pts
                else:
                    st.session_state.home_inning_scores[idx] += enemy_pts

        # 완성된 수비 로그 전광판 중계 일지에 수급
        st.session_state.game_log.append(
            f"🔮 {st.session_state.inning}회{st.session_state.phase} 수비 결과: {def_log} "
            f"(우리 투수 이닝 {inning_pitches}구 소모 / 총 {st.session_state.our_total_pitches}구)"
        )
        
        next_phase()

# [대수술 2] 도루 상성(우리 주력 vs 상대 수비) 완벽 가변 반영

def trigger_steal():
    # 1. 아예 주자가 없으면 튕겨냅니다.
    if not st.session_state.base1 and not st.session_state.base2 and not st.session_state.base3:
        st.warning("루상에 나간 주자가 있어야 도루를 시도하제예!")
        return
    
    my_team = st.session_state.my_team
    enemy_team = st.session_state.enemy_team
    my_buff = TEAMS.get(my_team, {"steal_b": 0})
    enemy_buff = TEAMS.get(enemy_team, {"out": 0})

    # =====================================================================
    # 🎯 [우선순위 엔진] 3루 주자가 있어도 '다른 루(1, 2루)'에 주자가 있다면 일반 도루 우선!
    # =====================================================================
    if st.session_state.base1 or st.session_state.base2:
        st.session_state.game_log.append("🏃‍♂️ [작전 발동] 1, 2루 주자가 다음 베이스를 향해 기민하게 스타트를 끊습니다! (일반 도루 시도)")
        
        # --- 여기에 형님이 기존에 쓰시던 일반 1, 2루 도루 주사위 연산 로직을 넣으시면 됩니다 ---
        # (예시 스케치)
        if random.random() < 0.60:  # 일반 도루는 성공률이 좀 더 높음
            if st.session_state.base2 and not st.session_state.base3:
                st.session_state.base3 = True
                st.session_state.base2 = False
                st.session_state.game_log.append("🎉 2루 주자 3루 안착 성공!")
            if st.session_state.base1 and not st.session_state.base2:
                st.session_state.base2 = True
                st.session_state.base1 = False
                st.session_state.game_log.append("🎉 1루 주자 2루 안착 성공!")
        else:
            st.session_state.out_count += 1
            st.session_state.game_log.append("❌ 포수의 칼 같은 송구에 주자가 걸려 아웃되었습니다!")
            if st.session_state.out_count >= 3:
                st.session_state.game_log.append("🚫 쓰리아웃 체인지!")
                next_phase()
        st.rerun()
        return

    # =====================================================================
    # 🚨 다른 루가 텅 비고 오직 '3루 주자 단독'인 최후의 상황에만 홈스틸 발동!
    # =====================================================================
    elif st.session_state.base3:
        st.session_state.game_log.append("🚨 [독단적 허를 찌르기!] 루상이 고요한 틈을 타 3루 주자가 홈으로 번개처럼 쇄도합니다!!! 낭만의 홈스틸 감행!!!")
        
        if random.random() < 0.20: # 20% 성공 확률
            st.session_state.our_score += 1
            st.session_state.base3 = False
            
            idx = st.session_state.inning - 1
            if idx < 12:
                if st.session_state.is_home_team:
                    if st.session_state.home_inning_scores[idx] == "" or st.session_state.home_inning_scores[idx] == 0: st.session_state.home_inning_scores[idx] = 1
                    else: st.session_state.home_inning_scores[idx] += 1
                else:
                    if st.session_state.away_inning_scores[idx] == "" or st.session_state.away_inning_scores[idx] == 0: st.session_state.away_inning_scores[idx] = 1
                    else: st.session_state.away_inning_scores[idx] += 1
                        
            st.session_state.game_log.append("🎉 🎉 [HOME STEAL SUCCESS!!!] 허를 찔린 투수가 멍하니 바라보는 사이 홈플레이트 슬라이딩 세이프!!! 대성공!!! (+1점)")
            st.session_state.strike = 0 
            st.session_state.ball = 0
            st.rerun()
        else:
            st.session_state.out_count += 1
            st.session_state.base3 = False
            st.session_state.game_log.append("❌ [HOME STEAL FAIL] 포수가 미리 홈 베이스를 커버하며 태그 아웃. 3루 주자 횡사. (아웃 +1)")
            
            if st.session_state.out_count >= 3:
                st.session_state.game_log.append("🚫 쓰리아웃 체인지! 이닝이 종료됩니다.")
                next_phase()
            else:
                st.rerun()
        return

def next_phase():
    if st.session_state.inning == 9 and st.session_state.phase == "초":
        if st.session_state.is_home_team and st.session_state.our_score > st.session_state.enemy_score:
            st.session_state.game_log.append("👍 9회초까지 이미 우리 팀이 이기고 있어 9회말 공격 없이 경기가 끝납니다! (9회말 X)")
            st.session_state.home_inning_scores[8] = "X"
            end_game()
            return
            
    idx = st.session_state.inning - 1
    if idx < 12:
        if st.session_state.away_inning_scores[idx] == "": st.session_state.away_inning_scores[idx] = 0
        if st.session_state.home_inning_scores[idx] == "": st.session_state.home_inning_scores[idx] = 0
            
    if st.session_state.phase == "초":
        st.session_state.phase = "말"
    else:
        st.session_state.phase = "초"
        st.session_state.inning += 1
    setup_half_inning()

def end_game():
    st.session_state.game_over = True
    
    if st.session_state.inning >= 10:
        if st.session_state.inning == 10 and st.session_state.phase == "초":
            st.session_state.inning = 9
            st.session_state.phase = "말"

    if st.session_state.our_score > st.session_state.enemy_score:
        st.session_state.game_result_msg = f"🎉 {st.session_state.my_team} 대승리!!! 오늘 경기 수당은 사모님 기라!!"
    elif st.session_state.our_score < st.session_state.enemy_score:
        st.session_state.game_result_msg = f"😭 패배... 상대 {st.session_state.enemy_team}의 마구에 당했습니다. 복수하러 가이소!"
    else:
        st.session_state.game_result_msg = "🤝 12회 대혈투 끝에 무승부로 끝났습니다!"

# ==========================================
# 3. 타격 액션 및 진루 처리 (병살타 / 희생플라이 고증 대개조)
# ==========================================
def play_turn(user_choice):
    if st.session_state.game_over:
        return

    # 1. 투수가 던질 구종을 무작위로 선택
    st.session_state.pitch_type = random.choice(["직구", "슬라이더", "체인지업", "커브", "포크볼", "스플리터"])
    
    # 2. 스트라이크 존 9분할 박스 중 공이 꽂힐 실제 위치 결정 (1~9)
    if random.random() < 0.70:
        st.session_state.pitch_zone = random.randint(1, 9)
    else:
        st.session_state.pitch_zone = 0
    
    # 3. (옵션) 타자의 예상 노림수 구역도 매번 랜덤하게 바뀌게 하거나, 
    # 사모님이 버튼으로 직접 고르게 하려면 이 줄은 빼셔도 됩니다!
    st.session_state.guess_zone = random.randint(0, 9)
    
    # 중계 로그에 투수가 뭘 던졌는지 살짝 흘려주는 센스!
    st.session_state.game_log.append(f"🔮 투수가 {st.session_state.pitch_type}를 선택해 {st.session_state.pitch_zone}번 구역으로 던졌습니다!")

    enemy_pitch_count = 1
    st.session_state.enemy_total_pitches += enemy_pitch_count

    current_batter = st.session_state.my_batter_number
    log_msg = ""
    at_bat_result = "지속"

    my_team = st.session_state.my_team
    enemy_team = st.session_state.enemy_team

    my_buff = TEAMS.get(my_team, {"homerun": 0, "hit": 0, "out": 0, "strike_p": 0, "ball_p": 0})
    enemy_buff = TEAMS.get(enemy_team, {"homerun": 0, "hit": 0, "out": 0, "strike_p": 0, "ball_p": 0})

    defense_penalty = 15 if enemy_team in ["⚪ 화이트 이글스", "⚫ 블랙 나이츠"] else 0

    # ------------------------------------------------------------------
    # ⚾ [트렌드 고증] 요즘 프로야구 1번~9번 타순별 가변 버프/패널티 및 서사 부여
    # ------------------------------------------------------------------
    batter_context_msg = ""
    batter_homerun_mod = 0
    batter_hit_mod = 0
    batter_ball_mod = 0

    if current_batter == 1:
        batter_context_msg = "🏃‍♂️ [1번 출루머신] "
        batter_hit_mod = 20  # 안타 확률 업
        batter_ball_mod = 30 # 눈야구 보너스
    elif current_batter in [2, 3]:
        # ★요즘 KBO 대세: 가장 잘 치는 타자를 2, 3번에 전진 배치!
        batter_context_msg = "🔥 [요즘 대세! 강한 2/3번 핵심 타자] "
        batter_homerun_mod = 25 # 홈런 대폭 증가
        batter_hit_mod = 35     # 안타 대폭 증가
    elif current_batter == 4:
        batter_context_msg = "👑 [전통의 4번 해결사: 사모님 타석!] "
        batter_homerun_mod = 40 # 홈런 확률 극대화 (한방 타작)
        batter_hit_mod = -10    # 모 아니면 도 (정확도 소폭 감소)
    elif current_batter in [5, 6]:
        batter_context_msg = "⚔️ [5/6번 클러치 히터] "
        batter_homerun_mod = 15
    elif current_batter in [7, 8]:
        batter_context_msg = "🛡️ [7/8번 하위 타선 폭탄 돌리기] "
        batter_hit_mod = -20    # 백업/하위 타선 패널티 (안타 확률 감소)
    elif current_batter == 9:
        # ★요즘 야구 9번: 단순 식물 타자가 아닌, 1번으로 연결하는 가교 타자!
        batter_context_msg = "🎯 [9번 가교 타자] "
        batter_hit_mod = 15     # 안타 확률 살짝 보정
        batter_ball_mod = 20    # 상위 타선 연결용 눈야구 보너스
    
    # 초기값 설정
    at_bat_result = "지속"
    log_msg = ""
    
    # 💥 1. 풀스윙 강타 (배트를 휘둘렀으므로 스트라이크/볼 판정 없이 타격 결과만 냅니다!)
    if user_choice == 1:
        zone_mod = 1.5 if st.session_state.pitch_zone == 0 else 1.0
        w_homerun = max(10, 80 + my_buff["homerun"] + batter_homerun_mod)
        w_hit = max(10, 170 + my_buff["hit"] - defense_penalty + batter_hit_mod)
        w_out = max(10, int((550 + my_buff["out"]) * zone_mod))
        w_foul = 200
        
        result = random.choices(
            ["HOMERUN", "HIT", "OUT", "FOUL"], 
            weights=[w_homerun, w_hit, w_out, w_foul]
        )[0]
        
        if result == "HOMERUN": at_bat_result = "홈런"
        elif result == "HIT": at_bat_result = "안타"
        elif result == "OUT": at_bat_result = "아웃"
        elif result == "FOUL":
            if st.session_state.strike < 2:
                st.session_state.strike += 1
                st.session_state.game_log.append(f"💥 작전[풀스윙]: {batter_context_msg}파울! 스트라이크 추가. (현재 {st.session_state.strike}S {st.session_state.ball}B)")
            else:
                st.session_state.game_log.append(f"💥 작전[풀스윙]: {batter_context_msg}2S 이후 끈질긴 커트 파울! (현재 {st.session_state.strike}S {st.session_state.ball}B)")
            st.rerun()  # 🚨 파울 처리 후 즉시 턴 종료 (밑으로 흘러내려가기 방지!)
            return

    # 🌟 2. 가볍게 밀어치기 (배트를 휘둘렀으므로 타격 결과만!)
    elif user_choice == 2:
        zone_mod = 1.3 if st.session_state.pitch_zone == 0 else 1.0
        w_hit = max(10, 350 + (my_buff["hit"] * 1.2) - defense_penalty + (batter_hit_mod * 1.5))
        w_out = max(10, int((450 + my_buff["out"]) * zone_mod))
        w_foul = 200
        
        result = random.choices(
            ["HIT", "OUT", "FOUL"], 
            weights=[w_hit, w_out, w_foul]
        )[0]
        
        if result == "HIT": at_bat_result = "안타"
        elif result == "OUT": at_bat_result = "아웃"
        elif result == "FOUL":
            if st.session_state.strike < 2:
                st.session_state.strike += 1
                st.session_state.game_log.append(f"💥 작전[밀어치기]: {batter_context_msg}빗맞은 파울! 스트라이크 추가. (현재 {st.session_state.strike}S {st.session_state.ball}B)")
            else:
                st.session_state.game_log.append(f"💥 작전[밀어치기]: {batter_context_msg}2S 이후 끈질기게 파울 커트 연발! (현재 {st.session_state.strike}S {st.session_state.ball}B)")
            st.rerun()  # 🚨 즉시 턴 종료!
            return

    # 👀 3. 공 끝까지 거르기 (🚨 운빨 주사위 완전 삭제! 실제 공 위치로만 칼판정!)
    elif user_choice == 3:
        # 🎯 투수가 1~9번(스트라이크 존)에 던졌는데 참았다? -> 100% 루킹 스트라이크!
        if 1 <= st.session_state.pitch_zone <= 9:
            st.session_state.strike += 1
            log_msg = f"❌ 스트라이크 존({st.session_state.pitch_zone}번)으로 들어오는 공을 지켜보았습니다! (현재 {st.session_state.strike}S {st.session_state.ball}B)"
            if st.session_state.strike >= 3:
                st.session_state.game_log.append(f"⚡ Ah... {batter_context_msg}{current_batter}번 타자 스탠딩 루킹 삼진 아웃!!")
                at_bat_result = "삼진"
                
        # 🟢 투수가 0번(볼)에 던졌는데 참았다? -> 100% 볼넷 카운트 상승! (오심 완전 치료!)
        elif st.session_state.pitch_zone == 0:
            st.session_state.ball += 1
            log_msg = f"🟢 볼! 존 바깥 유인구를 눈으로 정확히 골라냅니다! (현재 {st.session_state.strike}S {st.session_state.ball}B)"
            if st.session_state.ball >= 4:
                at_bat_result = "볼넷"

        if log_msg:
            st.session_state.game_log.append(f"👀 작전[거르기]: {batter_context_msg}{log_msg}")
    # =======================================================
    # 🏃‍♂️ [진루 및 타자 교체 엔진 연동] - 오리지널 로직 100% 동일
    # =======================================================
    if at_bat_result != "지속":
        st.session_state.strike = 0
        st.session_state.ball = 0
        st.session_state.my_batter_number = 1 if current_batter == 9 else current_batter + 1

        if at_bat_result == "홈런":
            pts = (1 if st.session_state.base1 else 0) + (1 if st.session_state.base2 else 0) + (1 if st.session_state.base3 else 0) + 1
            st.session_state.our_score += pts
            st.session_state.game_log.append(f"🔥 🎉 깡!!!!! {batter_context_msg}{current_batter}번 타자 대형 {pts}점짜리 홈런 대폭발!!!!!!!!")
            st.session_state.base1 = st.session_state.base2 = st.session_state.base3 = False
            
            # 📊 [전광판 강제 연동 추가] 점수 실시간 주입
            idx = st.session_state.inning - 1
            if idx < 12:
                if st.session_state.is_home_team:
                    if st.session_state.home_inning_scores[idx] == "": st.session_state.home_inning_scores[idx] = pts
                    else: st.session_state.home_inning_scores[idx] += pts
                else:
                    if st.session_state.away_inning_scores[idx] == "": st.session_state.away_inning_scores[idx] = pts
                    else: st.session_state.away_inning_scores[idx] += pts

        elif at_bat_result == "안타":
            gained_run = 0
            if st.session_state.base3: gained_run += 1
            if st.session_state.base2: gained_run += 1
            st.session_state.our_score += gained_run
            
            st.session_state.base3 = st.session_state.base1
            st.session_state.base2 = False
            st.session_state.base1 = True
            st.session_state.game_log.append(f"🌟 딱! {batter_context_msg}{current_batter}번 타자의 안타! 주자 나갑니다!")
            
            # 📊 [전광판 강제 연동 추가] 안타로 인한 득점 주입
            if gained_run > 0:
                idx = st.session_state.inning - 1
                if idx < 12:
                    if st.session_state.is_home_team:
                        if st.session_state.home_inning_scores[idx] == "": st.session_state.home_inning_scores[idx] = gained_run
                        else: st.session_state.home_inning_scores[idx] += gained_run
                    else:
                        if st.session_state.away_inning_scores[idx] == "": st.session_state.away_inning_scores[idx] = gained_run
                        else: st.session_state.away_inning_scores[idx] += gained_run

        elif at_bat_result == "아웃":
            if st.session_state.base1 and st.session_state.out_count < 2 and random.random() < 0.40:
                # 🚨 [병살타 고증 완치] 타자 아웃(+1) + 1루 주자도 아웃(+1) = 총 투아웃 추가!
                st.session_state.out_count += 2
                st.session_state.base1 = False  # 🔥 1루 주자 완벽 삭제! 유령 주자 차단!
                st.session_state.game_log.append(f"😱 아앗! {batter_context_msg}{current_batter}번 타자 내야 땅볼! 유격수-2루수-1루수 '병살타(투아웃)'!")
            
            elif st.session_state.base3 and st.session_state.out_count < 2 and random.random() < 0.50:
                st.session_state.out_count += 1
                st.session_state.base3 = False  # 🔥 3루 주자는 홈인했으니 3루 비우기!
                st.session_state.our_score += 1
                st.session_state.game_log.append(f"🕊️ [희생 플라이] {batter_context_msg}{current_batter}번 타자의 큰 타구! 3루 주자 태그업 홈인!")
                
                # 📊 전광판 실시간 1점 주입
                idx = st.session_state.inning - 1
                if idx < 12:
                    if st.session_state.is_home_team:
                        if st.session_state.home_inning_scores[idx] == "": st.session_state.home_inning_scores[idx] = 1
                        else: st.session_state.home_inning_scores[idx] += 1
                    else:
                        if st.session_state.away_inning_scores[idx] == "": st.session_state.away_inning_scores[idx] = 1
                        else: st.session_state.away_inning_scores[idx] += 1
            else:
                # ⚾ 일반 범타 아웃 (주자는 그대로 유지, 타자만 아웃)
                st.session_state.out_count += 1
                st.session_state.game_log.append(f" Ah... {batter_context_msg}{current_batter}번 타자 범타 아웃입니다.")
            
            # 쓰리아웃 체인지 확인 및 화면 즉시 새로고침
            check_three_out_change()
            st.rerun()

        elif at_bat_result == "삼진":
            st.session_state.out_count += 1
            # ⚡ 삼진 당했으니 화면 전광판 카운트 바로 비워주기
            check_three_out_change()
            st.rerun()

        elif at_bat_result == "볼넷":
            st.session_state.game_log.append(f"🚶‍♂️ {batter_context_msg}{current_batter}번 타자 볼넷 출루!")
            gained_bb_run = 0
            if st.session_state.base1 and st.session_state.base2 and st.session_state.base3:
                st.session_state.our_score += 1
                gained_bb_run = 1
                st.session_state.game_log.append("➔ 밀어내기 만루 볼넷으로 1점 추가!")
            elif st.session_state.base1 and st.session_state.base2: st.session_state.base3 = True
            elif st.session_state.base1: st.session_state.base2 = True
            else: st.session_state.base1 = True
            
            # 📊 [전광판 강제 연동 추가] 밀어내기 출루 1점 주입
            if gained_bb_run > 0:
                idx = st.session_state.inning - 1
                if idx < 12:
                    if st.session_state.is_home_team:
                        if st.session_state.home_inning_scores[idx] == "": st.session_state.home_inning_scores[idx] = 1
                        else: st.session_state.home_inning_scores[idx] += 1
                    else:
                        if st.session_state.away_inning_scores[idx] == "": st.session_state.away_inning_scores[idx] = 1
                        else: st.session_state.away_inning_scores[idx] += 1

    idx = st.session_state.inning - 1
    if idx < 12:
        
        if st.session_state.is_home_team:
            # 1. 기록 전 현재 전광판의 총점(R)을 기억
            prev_score = sum([x for x in st.session_state.home_inning_scores if type(x) in [int, float]])
            # 2. 이번 타석 직후 실제 올라간 순수 득점(런) 계산
            actual_gained_run = st.session_state.our_score - prev_score
            
            if actual_gained_run > 0:
                if st.session_state.home_inning_scores[idx] == "":
                    st.session_state.home_inning_scores[idx] = actual_gained_run
                else:
                    st.session_state.home_inning_scores[idx] += actual_gained_run

        else:
            prev_score = sum([x for x in st.session_state.away_inning_scores if type(x) in [int, float]])
            actual_gained_run = st.session_state.our_score - prev_score
            if actual_gained_run > 0:
                if st.session_state.away_inning_scores[idx] == "":
                    st.session_state.away_inning_scores[idx] = actual_gained_run
                else:
                    st.session_state.away_inning_scores[idx] += actual_gained_run
                    

    # ------------------------------------------------------------------
    # 🚨 [버그 박살] 실제 경기 진행 중에만 끝내기가 작동하도록 조건 정밀화
    # ------------------------------------------------------------------
    if (st.session_state.inning >= 9 and 
        st.session_state.phase == "말" and 
        st.session_state.is_home_team and 
        st.session_state.our_score > st.session_state.enemy_score and 
        not st.session_state.game_over):  # 이미 게임이 끝난 상태면 무시!
        
        st.session_state.game_log.append(f"🎉 {st.session_state.inning}회말!!! 우리 팀 타석에서 짜릿한 '끝내기 득점'이 터지며 경기를 그대로 끝냅니다!!")
        end_game()

def check_three_out_change():
    if st.session_state.out_count >= 3:
        st.session_state.game_log.append(f"📢 쓰리아웃 체인지! 공수 교대합니다.")
        
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
st.title("⚾ 순야보: 순수한 야구를 보여주마!")
st.subheader("이 사장님의 프로야구 시뮬레이터")

if st.button("📜 구단 설정집 열람"):
    st.session_state.show_stories = True

if st.session_state.get("show_stories", False):
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

# --- [📊 KBO 10대 구단 10x10 상성 대장부 열람 버튼 구역] ---
if "show_matrix" not in st.session_state:
    st.session_state.show_matrix = False

if st.button("📊 KBO 10대 구단 10x10 상성 대장부 열람"):
    st.session_state.show_matrix = True

if st.session_state.show_matrix:
    st.markdown("---")
    st.subheader("📊 10대 구단 가변 상성 판독표 (세로: 공격 / 가로: 수비)")
    st.caption("💡 팁: 초록(극상성 우세) / 연두(우세) / 노랑(백중세) / 오렌지(열세) / 빨강(천적 극열세)")

    # 엑셀 데이터 파이썬 가변 맵 (setup_half_inning 내부의 상성 판정과 100% 일치)
    matrix_data = {
        "🔴레드":   ["노랑", "연두", "초록", "노랑", "연두", "오렌지", "연두", "빨강", "오렌지", "노랑"],
        "🔵블루":   ["오렌지", "노랑", "연두", "오렌지", "빨강", "노랑", "오렌지", "연두", "초록", "연두"],
        "🟢그린":   ["빨강", "오렌지", "노랑", "오렌지", "연두", "초록", "오렌지", "노랑", "연두", "빨강"],
        "🟡옐로우": ["노랑", "연두", "연두", "노랑", "오렌지", "연두", "초록", "오렌지", "빨강", "오렌지"],
        "🟣퍼플":   ["오렌지", "초록", "오렌지", "연두", "노랑", "연두", "노랑", "오렌지", "연두", "빨강"],
        "🟠오렌지": ["연두", "노랑", "빨강", "오렌지", "오렌지", "노랑", "연두", "초록", "노랑", "연두"],
        "🟤브라운": ["오렌지", "연두", "연두", "빨강", "노랑", "오렌지", "노랑", "연두", "노랑", "초록"],
        "⚪화이트": ["초록", "오렌지", "노랑", "연두", "연두", "빨강", "오렌지", "노랑", "오렌지", "노랑"],
        "⚫블랙":   ["연두", "빨강", "오렌지", "초록", "오렌지", "노랑", "노랑", "연두", "노랑", "오렌지"],
        "💖핑크":   ["노랑", "오렌지", "초록", "연두", "초록", "오렌지", "빨강", "노랑", "연두", "노랑"]
    }
    columns_teams = ["🔴레드", "🔵블루", "🟢그린", "🟡옐로우", "🟣퍼플", "🟠오렌지", "🟤브라운", "⚪화이트", "⚫블랙", "💖핑크"]
    
    df = pd.DataFrame.from_dict(matrix_data, orient='index', columns=columns_teams)

    # 셀 마다 조건부로 무지개 전광판 색상 도포하는 가변 함수
    def color_cells(val):
        if val == "초록": return "background-color: #2e7d32; color: white; font-weight: bold;"
        elif val == "연두": return "background-color: #aed581; color: black; font-weight: bold;"
        elif val == "노랑": return "background-color: #fff59d; color: black;"
        elif val == "오렌지": return "background-color: #ffb74d; color: black;"
        elif val == "빨강": return "background-color: #e53935; color: white; font-weight: bold;"
        return ""

    # 스트림릿 화면에 엑셀 판때기 렌더링
    try: 
        st.dataframe(df.style.map(color_cells), use_container_width=True)
    except AttributeError:
        st.dataframe(df.style.applymap(color_cells), use_container_width=True)
    

    if st.button("❌ 상성 대장부 닫기"):
        st.session_state.show_matrix = False
        st.rerun()
    st.markdown("---")

if not st.session_state.game_setup:
    st.markdown("### 🏟️ 구단 선택 및 리그 매칭")
    my_team = st.selectbox("사모님이 이끌어갈 우리 팀을 고르소:", list(TEAMS.keys()))
    remaining_teams = [t for t in TEAMS.keys() if t != my_team]
    
    if st.button("경기 대진표 확정 및 입장 🎟️", type="primary"):
        enemy_team = random.choice(remaining_teams)
        start_new_game(my_team, enemy_team)
        st.rerun()
else:
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        st.metric(label=f"우리 팀 {st.session_state.my_emoji}", value=f"{st.session_state.our_score} 점")
        st.caption(st.session_state.my_team)
        st.markdown(f"🔋 **우리 투수 총 투구수:** `{st.session_state.our_total_pitches}구`")
    with col2:
        st.markdown(f"<h3 style='text-align: center; color: red;'>{st.session_state.inning}회{st.session_state.phase}</h3>", unsafe_allow_html=True)
        # [UI 개조] 현재 타석 진영 정보를 더 가변적이고 직관적으로 표현
        current_is_our_turn = (not st.session_state.is_home_team and st.session_state.phase == "초") or (st.session_state.is_home_team and st.session_state.phase == "말")
        st.markdown(f"<p style='text-align: center; font-size:12px; font-weight:bold; color:#1E90FF;'>🔥 {'[우리 공격 턴]' if current_is_our_turn else '[상대 공격 턴]'}</p>", unsafe_allow_html=True)
    with col3:
        st.metric(label=f"상대 팀 {st.session_state.enemy_emoji}", value=f"{st.session_state.enemy_score} 점")
        st.caption(st.session_state.enemy_team)
        st.markdown(f"🥎 **상대 투수 총 투구수:** `{st.session_state.enemy_total_pitches}구`")

    st.divider()

    away_name = st.session_state.enemy_team if st.session_state.is_home_team else st.session_state.my_team
    home_name = st.session_state.my_team if st.session_state.is_home_team else st.session_state.enemy_team

    scoreboard_data = {
    "TEAM": [f"🚌 {away_name} (원정)", f"🏟️ {home_name} (홈)"],
    "1": [st.session_state.away_inning_scores[0], st.session_state.home_inning_scores[0]],
    "2": [st.session_state.away_inning_scores[1], st.session_state.home_inning_scores[1]],
    "3": [st.session_state.away_inning_scores[2], st.session_state.home_inning_scores[2]],
    "4": [st.session_state.away_inning_scores[3], st.session_state.home_inning_scores[3]],
    "5": [st.session_state.away_inning_scores[4], st.session_state.home_inning_scores[4]],
    "6": [st.session_state.away_inning_scores[5], st.session_state.home_inning_scores[5]],
    "7": [st.session_state.away_inning_scores[6], st.session_state.home_inning_scores[6]],
    "8": [st.session_state.away_inning_scores[7], st.session_state.home_inning_scores[7]],
    "9": [st.session_state.away_inning_scores[8], st.session_state.home_inning_scores[8]],
    "10": [st.session_state.away_inning_scores[9], st.session_state.home_inning_scores[9]],
    "11": [st.session_state.away_inning_scores[10], st.session_state.home_inning_scores[10]],
    "12": [st.session_state.away_inning_scores[11], st.session_state.home_inning_scores[11]],
    "R": [
        st.session_state.enemy_score if st.session_state.is_home_team else st.session_state.our_score,
        st.session_state.our_score if st.session_state.is_home_team else st.session_state.enemy_score
    ]
}

    df_sb = pd.DataFrame(scoreboard_data).set_index("TEAM")

    st.markdown("### 🏟️ 실시간 라인 스코어보드")
    st.table(df_sb)

    st.markdown(f"### ⚾ 투수 구종: **{st.session_state.pitch_type}**")

    if st.session_state.pitch_zone == 0:
        st.error("🚨 [PITCH OUT!] 투수가 스트라이크 존을 완전히 벗어나는 유인구(BALL)를 던졌습니다!")
    else:
        st.success("🎯 [STRIKE ZONE] 공이 스트라이크 존 안으로 들어옵니다!")

    cols = [st.columns(3), st.columns(3), st.columns(3)]
    zone_matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]
    st.write("🔽 **스트라이크 존 (⚾: 공 꽂힌 곳 / 👁️: 타자 노림수)**")
    for i in range(3):
        with cols[i][0]:
            z = zone_matrix[i][0]
            icon = "⚾" if st.session_state.pitch_zone == z else ("👁️" if st.session_state.guess_zone == z else "🟩")
            st.button(f"{icon} ({z}번)", key=f"zone_{z}", disabled=True)
        with cols[i][1]:
            z = zone_matrix[i][1]
            icon = "⚾" if st.session_state.pitch_zone == z else ("👁️" if st.session_state.guess_zone == z else "🟩")
            st.button(f"{icon} ({z}번)", key=f"zone_{z}", disabled=True)
        with cols[i][2]:
            z = zone_matrix[i][2]
            icon = "⚾" if st.session_state.pitch_zone == z else ("👁️" if st.session_state.guess_zone == z else "🟩")
            st.button(f"{icon} ({z}번)", key=f"zone_{z}", disabled=True)

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
            st.session_state.away_inning_scores = [""] * 12
            st.session_state.home_inning_scores = [""] * 12

            st.session_state.game_over = False

            st.session_state.inning = 1
            st.session_state.phase = "초"
            st.session_state.our_score = 0
            st.session_state.enemy_score = 0
            st.session_state.out_count = 0
            st.session_state.strike = 0
            st.session_state.ball = 0
            st.session_state.base1 = st.session_state.base2 = st.session_state.base3 = False
            st.session_state.game_log = []

            if "game_setup" in st.session_state:
                st.session_state.game_setup = False

            st.rerun()

    
        
    else:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"### 📊 카운트 보드")
            st.markdown(f"* **아웃:** {'🔴' * st.session_state.out_count}{'⚪' * (3-st.session_state.out_count)}")
            st.markdown(f"* **스트라이크:** {'🔥' * st.session_state.strike}{'⚪' * (3-st.session_state.strike)}")
            st.markdown(f"* **볼:** {'🟢' * st.session_state.ball}{'⚪' * (4-st.session_state.ball)}")
            st.markdown(f"* **타순:** `{st.session_state.my_batter_number}번 타자 타석` " + 
            ("(👑 사모님!)" if st.session_state.my_batter_number == 4 else 
             "(🔥 대세 강타자!)" if st.session_state.my_batter_number in [2, 3] else 
             "(🏃‍♂️ 출루머신)" if st.session_state.my_batter_number == 1 else 
             "(🎯 상위연결)" if st.session_state.my_batter_number == 9 else ""))
            
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
