import os
import json
import base64
import random
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 💡 분리된 모듈 및 미니게임 임포트
from data import (
    TEAMS, MATCHUP_MATRIX, TEAM_ROSTERS, MATRIX_COLUMNS, 
    color_matchup_cells, render_roster_viewer, get_default_lineup
)
from engine import PureKboEngine, PitcherDomain, HyperClovaX_AI
from homerun_derby import render_homerun_derby_ui
from bottom_of_the_ninth import render_homerun_game_ui
from king_of_strikeout import render_king_of_strikeout_ui

#리그 순위표 연산
def get_league_standings_df() -> pd.DataFrame:
    if "league_records" not in st.session_state:
        st.session_state.league_records = {team: {"W": 0, "L": 0, "D": 0} for team in TEAMS.keys()}

    records = st.session_state.league_records
    data = []

    for team, stat in records.items():
        w, l, d = stat["W"], stat["L"], stat["D"]
        total_games = w + l
        win_rate = w / total_games if total_games > 0 else 0.000
        data.append({"구단": team, "경기수": w + l + d, "승": w, "패": l, "무": d, "승률": round(win_rate, 3)})

    df = pd.DataFrame(data).sort_values(by=["승률", "승"], ascending=[False, False]).reset_index(drop=True)
    
    top_w, top_l = df.loc[0, "승"], df.loc[0, "패"]
    df["승차"] = [f"{((top_w - row['승']) + (row['패'] - top_l)) / 2.0:.1f}" if i > 0 else "-" for i, row in df.iterrows()]
    df.index = df.index + 1
    return df

#타 구단 8개 팀 무작위 시뮬레이션 
def simulate_other_teams_matches(my_team: str, enemy_team: str) -> list:
    if "league_records" not in st.session_state:
        get_league_standings_df()

    other_teams = [t for t in TEAMS.keys() if t not in [my_team, enemy_team]]
    random.shuffle(other_teams)
    results_log = []

    for i in range(0, 8, 2):
        t1, t2 = other_teams[i], other_teams[i+1]
        s1, s2 = random.randint(0, 9), random.randint(0, 9)
        if s1 == s2: s1 += 1  # 무승부 방지 승부
        
        winner, loser = (t1, t2) if s1 > s2 else (t2, t1)
        st.session_state.league_records[winner]["W"] += 1
        st.session_state.league_records[loser]["L"] += 1
        results_log.append(f"🏟️ {t1} {s1} : {s2} {t2} ➔ ({winner[:2]} 승리)")

    return results_log
    
def main() -> None:
    st.set_page_config(layout="wide")
    st.markdown("<style>.stButton>button { width: 100%; font-size: 14px !important; font-weight: bold; }</style>", unsafe_allow_html=True)

    # =================================================================
    # 💡 [세션 상태 기본값 초기화]
    # =================================================================
    if "main_screen_passed" not in st.session_state: st.session_state.main_screen_passed = False
    if "game_mode" not in st.session_state: st.session_state.game_mode = "🏆 페넌트레이스 (144경기)"
    if "pennant_game_count" not in st.session_state: st.session_state.pennant_game_count = 1
    if "pennant_wins" not in st.session_state: st.session_state.pennant_wins = 0
    if "pennant_loses" not in st.session_state: st.session_state.pennant_loses = 0
    if "my_team" not in st.session_state: st.session_state.my_team = "💖 핑크 돌핀스"
    if "contract_team" not in st.session_state: st.session_state.contract_team = "💖 핑크 돌핀스"
    if "nc_diamonds" not in st.session_state: st.session_state.nc_diamonds = 1000
    if "full_kbo_engine" not in st.session_state: st.session_state.full_kbo_engine = None

    #로그인 상태 
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if "user_id" not in st.session_state: st.session_state.user_id = ""
    if "user_accounts" not in st.session_state: st.session_state.user_accounts = {} # 간단한 로컬 계정 저장소

    df_matchup = pd.DataFrame.from_dict(MATCHUP_MATRIX, orient='index', columns=list(MATCHUP_MATRIX.keys()))

    # =================================================================
    # 🏠 [STEP 0] 메인 스크린 (타이틀 / 리세마라 / 이어하기)
    # =================================================================
    if not st.session_state.main_screen_passed:
        st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>⚾ 순수한 야구 시뮬레이터 PRO</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center;'>KBO 스타일 10대 구단 하이퍼 매니지먼트 & 리세마라</h4>", unsafe_allow_html=True)
        st.divider()

        #ID & PW 입력
        if not st.session_state.logged_in:
            st.subheader("🔑 감독 계정 로그인 / 회원가입") 
            st.caption("사용하실 아이디와 비밀번호를 직접 입력해 주세요. (최초 입력 시 자동 가입됩니다)")
            l_col1, l_col2 = st.columns(2)
            with l_col1:
                input_id = st.text_input("감독 아이디 (ID)", key="input_login_id", placeholder="예: baseball_pro99")
            with l_col2:
                input_pw = st.text_input("비밀번호 (PW)", type="password", key="input_login_pw", placeholder="비밀번호 입력")

            b_col1, b_col2 = st.columns(2)
            with b_col1:
                if st.button("🚀 로그인 / 시작하기", type="primary", key="btn_do_login"):
                    if input_id.strip() and input_pw.strip():
                        accounts = st.session_state.user_accounts
                        if input_id in accounts:
                            # 기존 계정 PW 검증
                            if accounts[input_id]["pw"] == input_pw:
                                st.session_state.logged_in = True
                                st.session_state.user_id = input_id
                                # 계정에 저장된 다이아 및 데이터 복구
                                user_data = accounts[input_id]
                                st.session_state.nc_diamonds = user_data.get("diamonds", 1000)
                                st.session_state.my_team = user_data.get("my_team", "💖 핑크 돌핀스")
                                st.session_state.contract_team = user_data.get("contract_team", "💖 핑크 돌핀스")
                                st.session_state.pennant_game_count = user_data.get("pennant_game_count", 1)
                                st.session_state.pennant_wins = user_data.get("pennant_wins", 0)
                                st.session_state.pennant_loses = user_data.get("pennant_loses", 0)
                                if "league_records" in user_data:
                                    st.session_state.league_records = user_data["league_records"]
                                
                                st.toast(f"환영합니다, {input_id} 감독님! 로그인이 완료되었습니다.", icon="🎉")
                                st.rerun()
                            else:
                                st.error("❌ 비밀번호가 일치하지 않습니다!")
                        else:
                            # 신규 계정 자동 가입 처리
                            accounts[input_id] = {
                                "pw": input_pw,
                                "diamonds": 1000,
                                "my_team": "💖 핑크 돌핀스",
                                "contract_team": "💖 핑크 돌핀스",
                                "pennant_game_count": 1,
                                "pennant_wins": 0,
                                "pennant_loses": 0
                            }
                            st.session_state.logged_in = True
                            st.session_state.user_id = input_id
                            st.session_state.nc_diamonds = 1000
                            st.toast(f"✨ 신규 감독({input_id}) 등록 완료! 기본 지원금이 지급됩니다.", icon="💎")
                            st.rerun()
                    else:
                        st.warning("아이디와 비밀번호를 모두 입력해 주세요!")
            st.stop() # 로그인 전에는 아래 화면 차단

        st.success(f"👤 현재 접속 중인 감독 계정: **{st.session_state.user_id}**님 (보유 다이아: {st.session_state.nc_diamonds} 💎)")
        st.markdown("---")
        
        m_col1, m_col2 = st.columns(2)

        with m_col1:
            st.subheader("✨ 새로하기 (리세마라)")
            st.caption("초보 감독 취임 지원금 패키지를 받고 시작합니다! 마음에 드는 다이아 수량이 나올 때까지 리세마라하세요.")
            st.write(f"현재 준비된 시작 다이아: **{st.session_state.nc_diamonds} 💎**")
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("🎲 다이아 리세마라 (재뽑기)", key="btn_gacha_re"):
                    st.session_state.nc_diamonds = random.randint(1000, 5000)
                    if st.session_state.user_id in st.session_state.user_accounts:
                        st.session_state.user_accounts[st.session_state.user_id]["diamonds"] = st.session_state.nc_diamonds
                    st.toast(f"🎉 리세마라 결과: {st.session_state.nc_diamonds} 다이아 획득!", icon="💎")
                    st.rerun()
            with c_btn2:
                if st.button("🚀 이 다이아로 시작하기", type="primary", key="btn_start_new"):
                    st.session_state.main_screen_passed = True
                    st.toast("🎮 게임 모드 선택 화면으로 이동합니다!", icon="⚾")
                    st.rerun()

        with m_col2:
            st.subheader("📂 이어하기 (세이브 코드)")
            st.caption("발급받은 암호 코드를 입력하여 페넌트레이스 진행도 및 보유 다이아를 복구합니다.")
            input_code = st.text_input("세이브 코드 입력", key="main_save_input", placeholder="코드를 붙여넣으세요")
            if st.button("🔓 코드 검증 및 로드", key="btn_main_load"):
                if input_code.strip():
                    try:
                        decoded_bytes = base64.b64decode(input_code.encode('utf-8'))
                        data = json.loads(decoded_bytes.decode('utf-8'))
                        
                        st.session_state.nc_diamonds = data.get("diamonds", 1000)
                        st.session_state.my_team = data.get("my_team", "💖 핑크 돌핀스")
                        st.session_state.contract_team = data.get("contract_team", data.get("my_team", "💖 핑크 돌핀스"))
                        st.session_state.pennant_game_count = data.get("pennant_game_count", 1)
                        st.session_state.pennant_wins = data.get("pennant_wins", 0)
                        st.session_state.pennant_loses = data.get("pennant_loses", 0)
                        
                        st.session_state.main_screen_passed = True
                        st.toast("🎉 데이터 복구 완료! 페넌트레이스를 이어갑니다.", icon="💾")
                        st.rerun()
                    except Exception:
                        st.error("❌ 유효하지 않은 암호 코드입니다.")
                else:
                    st.warning("코드를 입력해 주세요!")

        if st.button("🔒 로그아웃 (다른 계정으로 전환)", key="btn_do_logout"):
            st.session_state.logged_in = False
            st.session_state.user_id = ""
            st.rerun()

        st.stop() # 메인 스크린에서는 진입 전까지 하단 렌더링을 차단합니다.

    # =================================================================
    # 🛠️ 사이드바 (상점 / 세이브·로드 / 설정 열람)
    # =================================================================
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🏆 PBS 리그 순위표")
        if st.button("📊 실시간 구단 순위 열람", key="btn_sb_standings"):
            st.dataframe(get_league_standings_df(), width="stretch")

        st.markdown("---")
        st.markdown("### 🚨 감독 계약 관리")
        if st.button("💸 구단 감독 사임하기 (위약금 3,000💎)", key="btn_resign_manager"):
            if st.session_state.nc_diamonds >= 3000:
                st.session_state.nc_diamonds -= 3000
                old_team = st.session_state.contract_team
                st.session_state.contract_team = None
                st.session_state.full_kbo_engine = None
                st.session_state.pennant_game_count = 1
                st.session_state.pennant_wins = 0
                st.session_state.pennant_loses = 0
                st.toast(f"🚨 위약금 3,000💎을 지불하고 {old_team} 감독직에서 사임했습니다.", icon="💸")
                st.rerun()
            else:
                st.sidebar.error("❌ 보유 다이아가 부족하여 위약금(3,000💎)을 낼 수 없습니다!")
                
        st.header("💎 비밀 상점 (P2W)")
        st.write(f"보유 다이아: {st.session_state.nc_diamonds} 💎")
        
        if st.button("💳 N Pay로 5000 다이아 충전 (11만원)"):
            st.session_state.nc_diamonds += 5000
            st.toast("💸 지갑 전사 발동! 5000 다이아가 즉시 충전되었습니다핑!", icon="💎")
            st.rerun()
            
        st.markdown("---")
        
        if st.session_state.full_kbo_engine and not st.session_state.full_kbo_engine.game_over:
            game = st.session_state.full_kbo_engine
            current_is_our_turn = (not game.is_home_team and game.phase == "초") or (game.is_home_team and game.phase == "말")
            
            if current_is_our_turn:
                st.markdown("#### 🌸 [공격 턴 전용 아이템]")
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown("🔥 **타격 확률 극대화**  \n`안타 확률 +2.0%` (100💎)")
                with col2:
                    if st.button("구매", key="buy_buff_hit"):
                        if st.session_state.nc_diamonds >= 100:
                            st.session_state.nc_diamonds -= 100
                            game.hit_buff += 0.085
                            st.toast("🔥 타자들에게 각성제를 주입했습니다! 안타 확률 가산!", icon="💪")
                            st.rerun()
                        else: st.error("다이아 부족!")

                col1_d, col2_d = st.columns([3, 1])
                with col1_d:
                    st.markdown("🤫 **멘탈 교란 찌라시**  \n`적 투수 체력 -20` (150💎)")
                with col2_d:
                    if st.button("구매", key="buy_debuff_scandal"):
                        if st.session_state.nc_diamonds >= 150:
                            st.session_state.nc_diamonds -= 150
                            p_en = game.get_current_enemy_pitcher()
                            p_en.stamina = max(5, p_en.stamina - 20)
                            st.toast("🚨 적 투수 라커룸에 찌라시를 투척했습니다! 제구력 흔들림!", icon="🤫")
                            st.rerun()
                        else: st.error("다이아 부족!")
            else:
                st.markdown("#### 🔋 [수비 턴 전용 아이템]")
                col3, col4 = st.columns([3, 1])
                with col3:
                    st.markdown("💉 **특수 링거 수액**  \n`현재 투수 체력 +25` (150💎)")
                with col4:
                    if st.button("구매", key="buy_buff_stamina_1"):
                        if st.session_state.nc_diamonds >= 150:
                            st.session_state.nc_diamonds -= 150
                            p = game.get_current_my_pitcher()
                            p.stamina = min(p.max_stamina, p.stamina + 25)
                            st.toast("🔋 마운드로 특수 링거 공수 완료! 투수 기력 충전!", icon="💪")
                            st.rerun()
                        else: st.error("다이아 부족!")

                col3_d, col4_d = st.columns([3, 1])
                with col3_d:
                    st.markdown("🔊 **관중 매수 야유**  \n`적 안타 확률 -2%` (120💎)")
                with col4_d:
                    if st.button("구매", key="buy_debuff_crowd"):
                        if st.session_state.nc_diamonds >= 120:
                            st.session_state.nc_diamonds -= 120
                            game.hit_buff -= 0.05
                            st.toast("📢 전원 확성기 기동! 상대 팀의 집중력이 흐트러집니다!", icon="👿")
                            st.rerun()
                        else: st.error("다이아 부족!")

        st.markdown("---")
        st.markdown("### 💾 세이브 / 로드")
        
        with st.expander("🔑 세이브 코드 발급"):
            save_data = {
                "diamonds": st.session_state.nc_diamonds,
                "my_team": st.session_state.my_team,
                "contract_team": st.session_state.contract_team,
                "pennant_game_count": st.session_state.pennant_game_count,
                "pennant_wins": st.session_state.pennant_wins,
                "pennant_loses": st.session_state.pennant_loses
            }
            if st.session_state.full_kbo_engine:
                game = st.session_state.full_kbo_engine
                save_data.update({
                    "enemy_team": game.enemy_team, "is_home_team": game.is_home_team,
                    "our_score": game.our_score, "enemy_score": game.enemy_score,
                    "away_stats": game.away_stats, "home_stats": game.home_stats,
                    "inning": game.inning, "phase": game.phase,
                    "my_batter_number": game.my_batter_number, "enemy_batter_number": game.enemy_batter_number,
                    "our_total_pitches": game.our_total_pitches, "enemy_total_pitches": game.enemy_total_pitches,
                    "strike": game.strike, "ball": game.ball, "out_count": game.out_count,
                    "base1": game.base1, "base2": game.base2, "base3": game.base3,
                    "away_inning_scores": game.away_inning_scores, "home_inning_scores": game.home_inning_scores,
                    "game_log": game.game_log, "pitch_history": game.pitch_history,
                    "chzzk_chats": game.chzzk_chats, "hit_buff": game.hit_buff,
                    "manager_ejected": game.manager_ejected, "my_pitcher_idx": game.my_pitcher_idx,
                    "my_used_pitchers": list(game.my_used_pitchers),
                    "my_pitchers": [{"name": p.name, "role": p.role, "max_stamina": p.max_stamina, "stamina": p.stamina, "pitches_thrown": p.pitches_thrown} for p in game.my_pitchers],
                    "enemy_pitcher_idx": game.enemy_pitcher_idx, "enemy_used_pitchers": list(game.enemy_used_pitchers),
                    "enemy_pitchers": [{"name": p.name, "role": p.role, "max_stamina": p.max_stamina, "stamina": p.stamina, "pitches_thrown": p.pitches_thrown} for p in game.enemy_pitchers]
                })

            json_str = json.dumps(save_data, ensure_ascii=False)
            encoded_code = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
            st.code(encoded_code, language="text")
            st.caption("위 코드를 더블클릭해 복사해 보관하세요!")

        with st.expander("🔓 코드 불러오기"):
            input_code_sb = st.text_input("코드 입력", key="save_code_sb_input", placeholder="세이브 코드를 붙여넣으세요")
            if st.button("📂 데이터 로드 실행", key="btn_sb_load"):
                if input_code_sb.strip():
                    try:
                        decoded_bytes = base64.b64decode(input_code_sb.encode('utf-8'))
                        data = json.loads(decoded_bytes.decode('utf-8'))
                        
                        st.session_state.nc_diamonds = data.get("diamonds", 1000)
                        st.session_state.my_team = data.get("my_team", "💖 핑크 돌핀스")
                        st.session_state.contract_team = data.get("contract_team", data.get("my_team", "💖 핑크 돌핀스"))
                        st.session_state.pennant_game_count = data.get("pennant_game_count", 1)
                        st.session_state.pennant_wins = data.get("pennant_wins", 0)
                        st.session_state.pennant_loses = data.get("pennant_loses", 0)

                        if "enemy_team" in data:
                            loaded_game = PureKboEngine(data["my_team"], data["enemy_team"])
                            loaded_game.is_home_team = data["is_home_team"]
                            loaded_game.our_score = data["our_score"]
                            loaded_game.enemy_score = data["enemy_score"]
                            loaded_game.away_stats = data["away_stats"]
                            loaded_game.home_stats = data["home_stats"]
                            loaded_game.inning = data["inning"]
                            loaded_game.phase = data["phase"]
                            loaded_game.my_batter_number = data["my_batter_number"]
                            loaded_game.enemy_batter_number = data["enemy_batter_number"]
                            loaded_game.our_total_pitches = data["our_total_pitches"]
                            loaded_game.enemy_total_pitches = data["enemy_total_pitches"]
                            loaded_game.strike = data["strike"]
                            loaded_game.ball = data["ball"]
                            loaded_game.out_count = data["out_count"]
                            loaded_game.base1 = data["base1"]
                            loaded_game.base2 = data["base2"]
                            loaded_game.base3 = data["base3"]
                            loaded_game.away_inning_scores = data["away_inning_scores"]
                            loaded_game.home_inning_scores = data["home_inning_scores"]
                            loaded_game.game_log = data["game_log"]
                            loaded_game.pitch_history = data["pitch_history"]
                            loaded_game.chzzk_chats = data["chzzk_chats"]
                            loaded_game.hit_buff = data["hit_buff"]
                            loaded_game.manager_ejected = data.get("manager_ejected", False)

                            loaded_game.my_pitcher_idx = data["my_pitcher_idx"]
                            loaded_game.my_used_pitchers = set(data["my_used_pitchers"])
                            loaded_game.my_pitchers = [PitcherDomain(p["name"], p["role"], p["max_stamina"]) for p in data["my_pitchers"]]
                            for i, p in enumerate(loaded_game.my_pitchers): p.stamina = data["my_pitchers"][i]["stamina"]
                            
                            loaded_game.enemy_pitcher_idx = data["enemy_pitcher_idx"]
                            loaded_game.enemy_used_pitchers = set(data["enemy_used_pitchers"])
                            loaded_game.enemy_pitchers = [PitcherDomain(p["name"], p["role"], p["max_stamina"]) for p in data["enemy_pitchers"]]
                            for i, p in enumerate(loaded_game.enemy_pitchers): p.stamina = data["enemy_pitchers"][i]["stamina"]

                            st.session_state.full_kbo_engine = loaded_game
                        st.toast("🎉 세이브 데이터 로드 완료!", icon="💾")
                        st.rerun()
                    except Exception: st.error("❌ 유효하지 않은 암호 코드입니다.")

        st.markdown("---")
        st.markdown("### 📊 상성 매트릭스 전체 열람")
        if st.button("상성 표 열람"):
            df_matrix = pd.DataFrame.from_dict(MATCHUP_MATRIX, orient='index', columns=MATRIX_COLUMNS)
            st.dataframe(df_matrix, width="stretch")

        st.divider()
        st.header("📖 구단 유니버스")
        team_lore = st.selectbox("세계관 열람:", list(TEAMS.keys()))
        if st.button("스토리 보기"):
            if os.path.exists("assets/team_stories.txt"):
                with open("assets/team_stories.txt", "r", encoding="utf-8") as f:
                    st.text_area(f"{team_lore} 설정", value=f.read(), height=200, disabled=True)
            else: st.error("⚠️ assets/team_stories.txt 파일 누락.")

        st.divider()
        st.header("💡 전술 매뉴얼")
        if st.button("가이드 열람"):
            if os.path.exists("assets/game_tips.txt"):
                with open("assets/game_tips.txt", "r", encoding="utf-8") as f:
                    st.text_area("공식 가이드", value=f.read(), height=200, disabled=True)
            else: st.error("⚠️ assets/game_tips.txt 파일 누락.")

        st.divider()
        st.header("👤 선수 로스터")
        if st.button("이번 시즌 선수단"):
            if os.path.exists("assets/team-roster.txt"):
                with open("assets/team-roster.txt", "r", encoding="utf-8") as f:
                    st.text_area("팀별 로스터", value=f.read(), height=200, disabled=True)
            else: st.error("⚠️ assets/team-roster.txt 파일 누락.")

        st.divider()
        st.header("팀별 디폴트 타순")
        if st.button("기본 선발 라인업과 선발투수"):
            if os.path.exists("assets/default-lineup.txt"):
                with open("assets/default-lineup.txt", "r", encoding="utf-8") as f:
                    st.text_area("팀별 주전", value=f.read(), height=200, disabled=True)
            else: st.error("⚠️ assets/default-lineup.txt 파일 누락.")

    # =================================================================
    # 🎮 [STEP 1] 게임 모드 선택 및 메인 분기 (페넌트레이스 / 미니게임)
    # =================================================================
    st.sidebar.markdown("### 🎮 게임 모드")
    mode_choice = st.sidebar.radio(
        "모드 선택", 
        ["🏆 페넌트레이스 (144경기)", "🕹️ 미니게임 3종"], 
        key="radio_mode_select"
    )

    # -----------------------------------------------------------------
    # 🏆 [모드 1] 페넌트레이스 (144경기 장기 시즌 & 위약금 시스템)
    # -----------------------------------------------------------------
    if mode_choice == "🏆 페넌트레이스 (144경기)":
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"📊 **시즌 진행도**: `{st.session_state.pennant_game_count} / 144 경기`")
        st.sidebar.markdown(f"📈 **현재 성적**: `{st.session_state.pennant_wins}승 {st.session_state.pennant_loses}패`")

        # 경기 개시 전 팀 선택 및 라인업 세팅
        if st.session_state.full_kbo_engine is None:
            selected_team = st.selectbox(
                "우리 팀 선택 (디폴트 신생팀: 💖 핑크 돌핀스):", 
                list(TEAMS.keys()), 
                index=list(TEAMS.keys()).index(st.session_state.my_team)
            )

            # 🚨 [감독 사퇴 / 이적 위약금 시스템]
            if selected_team != st.session_state.contract_team:
                st.error(
                    f"🚨 **[감독 계약 파기 위약금 경고]**\n\n"
                    f"현재 **{st.session_state.contract_team}**과 144경기 계약 상태입니다!\n"
                    f"144경기를 다 채우기 전에 **{selected_team}**(으)로 이적하려면 **위약금 3,000 💎**가 차감됩니다."
                )
                if st.button("💸 3,000 다이아 지불하고 감독 이적하기", key="btn_pay_penalty"):
                    if st.session_state.nc_diamonds >= 3000:
                        st.session_state.nc_diamonds -= 3000
                        st.session_state.contract_team = selected_team
                        st.session_state.my_team = selected_team
                        st.session_state.pennant_game_count = 1
                        st.session_state.pennant_wins = 0
                        st.session_state.pennant_loses = 0
                        st.toast(f"✅ 위약금을 지불하고 {selected_team} 감독으로 취임했습니다!", icon="💸")
                        st.rerun()
                    else:
                        st.error("❌ 보유 다이아가 부족하여 위약금을 낼 수 없습니다! (비밀상점 충전 필요)")
            else:
                st.session_state.my_team = selected_team

            sp_list = TEAM_ROSTERS[st.session_state.my_team]["pitchers"]["선발(5)"]
            selected_sp_idx = st.selectbox("⚾ **오늘의 선발 투수 지명**",
                options=list(range(len(sp_list))),
                format_func=lambda x: f"{x+1}선발: {sp_list[x]} (체력: {TEAMS[st.session_state.my_team]['stamina']})",
                key=f"select_sp_{st.session_state.my_team}"
            )
            
            st.markdown(f"#### 📊 {st.session_state.my_team}의 구단별 상성표 요약")
            if st.session_state.my_team in df_matchup.index:
                my_status = df_matchup.loc[[st.session_state.my_team]]
                try: styled_status = my_status.style.map(color_matchup_cells)
                except AttributeError: styled_status = my_status.style.applymap(color_matchup_cells)
                st.dataframe(styled_status, width="stretch")

            # 오늘의 선발 라인업 (1~9번 타순 커스텀)
            saved_key = f"saved_lineup_{st.session_state.my_team}"
            default_lineup = get_default_lineup(st.session_state.my_team)
            initial_lineup = st.session_state.get(saved_key, default_lineup) 
            
            with st.expander("⚙️ 오늘의 선발 라인업 (1~9번 타순 수동 커스텀)", expanded=True):
                st.caption("💡 각 드롭다운에서 원하는 타자 및 타순을 조합할 수 있습니다.")
                all_batters = []
                for p_list in TEAM_ROSTERS[st.session_state.my_team]["batters"].values():
                    all_batters.extend(p_list)
                    
                custom_lineup = []
                col_l1, col_l2 = st.columns(2)
                for idx in range(9):
                    target_col = col_l1 if idx < 5 else col_l2
                    with target_col:
                        default_player = initial_lineup[idx] if idx < len(initial_lineup) else all_batters[idx % len(all_batters)]
                        d_idx = all_batters.index(default_player) if default_player in all_batters else 0
                        
                        sel = st.selectbox(
                            f"**{idx+1}번 타자**", options=all_batters, index=d_idx,
                            key=f"start_lineup_select_{idx}_{st.session_state.my_team}"
                        )
                        custom_lineup.append(sel)

                st.markdown("---")
                b_col1, b_col2 = st.columns(2)
                with b_col1:
                    if st.button("💾 현재 타순을 이 팀의 기본 오더로 저장", key=f"btn_save_lineup_{st.session_state.my_team}"):
                        st.session_state[saved_key] = custom_lineup
                        st.toast(f"✅ {st.session_state.my_team}의 선발 타순이 저장되었습니다!", icon="💾")
                with b_col2:
                    if st.button("🔄 기본 추천 타순으로 초기화", key=f"btn_reset_lineup_{st.session_state.my_team}"):
                        if saved_key in st.session_state: del st.session_state[saved_key]
                        st.toast("🔄 추천 타순으로 초기화되었습니다.", icon="🧹")
                        st.rerun()
            
            has_duplicates = len(set(custom_lineup)) != len(custom_lineup)
            if has_duplicates:
                seen = set()
                duplicates = set(p for p in custom_lineup if p in seen or seen.add(p))
                dup_names = ", ".join(duplicates)
                st.warning(f"⚠️ **라인업 중복 경고**: [{dup_names}] 선수가 중복 선택되었습니다! 서로 다른 9명의 타자로 구성해 주세요.")
            else:
                st.info(f"⚾ **선발 투수**: {sp_list[selected_sp_idx]} | "
                    f"📋 **선발 타순**: {' ➔ '.join([f'{i+1}.{p.split()[-1]}' for i, p in enumerate(custom_lineup)])}")
            
            if st.button("⚾️ PLAY BALL!", type="primary", disabled=has_duplicates, key="btn_play_ball_main"):
                enemy_team = random.choice([t for t in TEAMS.keys() if t != st.session_state.my_team])
                st.session_state.full_kbo_engine = PureKboEngine(
                    my_team=st.session_state.my_team, 
                    enemy_team=enemy_team, 
                    my_lineup=custom_lineup,
                    starting_pitcher_idx=selected_sp_idx 
                )
                st.rerun()

        # -------------------------------------------------------------
        # 경기 진행 중 화면 (페넌트레이스 모드)
        # -------------------------------------------------------------
        else:
            game: PureKboEngine = st.session_state.full_kbo_engine
            st.session_state.my_team = game.my_team
            p_my = game.get_current_my_pitcher()
            p_en = game.get_current_enemy_pitcher()

            with st.expander("📋 오늘의 양 팀 선발 라인업 및 실시간 타순 열람", expanded=False):
                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    st.markdown(f"#### 🏠 {game.my_team} 선발 라인업")
                    st.write(f"⚾ **선발 투수**: {p_my.name}")
                    st.markdown("---")
                    for i, batter in enumerate(game.my_lineup):
                        is_current = (game.is_attack and game.my_batter_number == (i+1))
                        marker = " 👈 [현재 타석]" if is_current else ""
                        st.write(f"**{i+1}번 타자**: {batter}{marker}")
                with col_u2:
                    st.markdown(f"#### 🚌 {game.enemy_team} 선발 라인업")
                    st.write(f"⚾ **선발 투수**: {p_en.name}")
                    st.markdown("---")
                    for i, batter in enumerate(game.enemy_lineup):
                        is_current = (not game.is_attack and game.enemy_batter_number == (i+1))
                        marker = " 👈 [현재 타석]" if is_current else ""
                        st.write(f"**{i+1}번 타자**: {batter}{marker}")

            st.markdown(f"##### 📊 실시간 상성 파트너: {game.my_team} vs {game.enemy_team}")
            if game.my_team in df_matchup.index:
                my_status = df_matchup.loc[[game.my_team]]
                try: styled_status = my_status.style.map(color_matchup_cells)
                except AttributeError: styled_status = my_status.style.applymap(color_matchup_cells)
                st.dataframe(styled_status, width="stretch")

            c1, c2, c3 = st.columns([2, 1, 2])
            with c1:
                st.metric(label=f"우리 팀 {game.my_emoji}", value=f"{game.our_score} 점")
                st.caption(f"🔋 {p_my.name} | 체력: [{p_my.stamina}/{p_my.max_stamina}] | 총 {game.our_total_pitches}구")
                if not game.game_over and p_my.role != "마무리":
                    with st.expander("🔄 투수 수동 교체 (드롭다운)"):
                        available_pitchers = {
                            f"{i}: {p.name} ({p.role}) - 체력 {p.stamina}/{p.max_stamina}": i 
                            for i, p in enumerate(game.my_pitchers) 
                            if i not in game.my_used_pitchers and i != game.my_pitcher_idx
                        }
                        if available_pitchers:
                            chosen_label = st.selectbox("올릴 투수를 선택하세요", list(available_pitchers.keys()), key="manual_pitcher_select")
                            if st.button("마운드 지명 교체", key="btn_confirm_manual_pitcher"):
                                target_idx = available_pitchers[chosen_label]
                                game.my_pitcher_idx = target_idx
                                game.my_used_pitchers.add(target_idx)
                                new_p = game.get_current_my_pitcher()
                                game.game_log.append(f"🔄 [감독 직접 교체] 벤치의 지시로 마운드 교체! [{new_p.role}] '{new_p.name}' 등판!")
                                st.rerun()
                        else: st.caption("🚨 더 이상 교체 가능한 대기 투수가 없습니다!")
            with c2:
                if game.game_over:
                    st.markdown("<h3 style='text-align: center; color: #9E9E9E;'>경기 종료</h3>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<h3 style='text-align: center; color: #E63946;'>{game.inning}회{game.phase}</h3>", unsafe_allow_html=True)
                    current_is_our_turn = (not game.is_home_team and game.phase == "초") or (game.is_home_team and game.phase == "말")
                    st.markdown(f"<p style='text-align: center; font-size:12px;'>{'[공격 턴]' if current_is_our_turn else '[수비 턴]'}</p>", unsafe_allow_html=True)
            with c3:
                st.metric(label=f"상대 팀 {game.enemy_emoji}", value=f"{game.enemy_score} 점")
                st.caption(f"🥎 {p_en.name} | 체력: [{p_en.stamina}/{p_en.max_stamina}] | 총 {game.enemy_total_pitches}구")

            away_name = game.enemy_team if game.is_home_team else game.my_team
            home_name = game.my_team if game.is_home_team else game.enemy_team
            display_away, display_home = [], []

            for i in range(12):
                if game.game_over:
                    if i == 8 and game.home_inning_scores[i] == "X":
                        display_away.append(game.away_inning_scores[i]); display_home.append("X")
                    elif i >= game.inning:
                        display_away.append(""); display_home.append("")
                    else:
                        display_away.append(game.away_inning_scores[i]); display_home.append(game.home_inning_scores[i])
                else:
                    display_away.append("" if i >= game.inning else game.away_inning_scores[i])
                    display_home.append("" if i >= game.inning else game.home_inning_scores[i])
            
            sb = {
                "BOARD": [f"🚌 {away_name}", f"🏟️ {home_name}"],
                "1": [display_away[0], display_home[0]], "2": [display_away[1], display_home[1]], "3": [display_away[2], display_home[2]],
                "4": [display_away[3], display_home[3]], "5": [display_away[4], display_home[4]], "6": [display_away[5], display_home[5]],
                "7": [display_away[6], display_home[6]], "8": [display_away[7], display_home[7]], "9": [display_away[8], display_home[8]],
                "10": [display_away[9], display_home[9]], "11": [display_away[10], display_home[10]],
                "R": [game.away_stats["R"], game.home_stats["R"]], "H": [game.away_stats["H"], game.home_stats["H"]],
                "E": [game.away_stats["E"], game.home_stats["E"]], "B": [game.away_stats["B"], game.home_stats["B"]]
            }
            st.table(pd.DataFrame(sb).set_index("BOARD"))

            if game.game_over:
                st.success(game.game_result_msg)
                
                # 📊 페넌트레이스 경기 수 및 승패 기록 연동
                if not getattr(game, 'pennant_recorded', False):
                    st.session_state.pennant_game_count += 1
                    if "league_records" not in st.session_state: get_league_standings_df()

                    if game.our_score > game.enemy_score: 
                        st.session_state.pennant_wins += 1
                        st.session_state.league_records[game.my_team]["W"] += 1
                        st.session_state.league_records[game.enemy_team]["L"] += 1
                    elif game.our_score < game.enemy_score: 
                        st.session_state.pennant_loses += 1
                        st.session_state.league_records[game.my_team]["L"] += 1
                        st.session_state.league_records[game.enemy_team]["W"] += 1
                    else:
                        st.session_state.league_records[game.my_team]["D"] += 1
                        st.session_state.league_records[game.enemy_team]["D"] += 1

                    game.other_results_cache = simulate_other_teams_matches(game.my_team, game.enemy_team)
                    game.pennant_recorded = True

                if hasattr(game, 'other_results_cache'):
                    with st.expander("📺 오늘 자 KBO 타 구단 경기 결과 (4경기)", expanded=True):
                        for res_text in game.other_results_cache:
                            st.write(res_text)
        
                # 📊 실시간 리그 순위표 표시
                with st.expander("🏆 실시간 PBS 페넌트레이스 리그 순위표", expanded=True):
                    st.dataframe(get_league_standings_df(), width="stretch")
        
                    if st.button("다음 경기 준비하기 (시즌 진행)", type="primary", key="btn_next_pennant_game"):
                        st.session_state.full_kbo_engine = None
                        st.rerun()
            else:
                col_main, col_chat = st.columns([3, 1])
                
                with col_main:
                    cz1, cz2 = st.columns(2)
                    with cz1:
                        st.markdown(f"#### **🚨 COUNT BOARD**")
                        st.markdown(f"**OUT :** {'🔴' * game.out_count}{'⚪' * (3-game.out_count)}")
                        st.markdown(f"**STRIKE :** {'🟡' * game.strike}{'⚪' * (3-game.strike)}")
                        st.markdown(f"**BALL :** {'🟢' * game.ball}{'⚪' * (4-game.ball)}")
                    with cz2:
                        fig, ax = plt.subplots(figsize=(3, 3), facecolor='#1e1e1e')
                        ax.set_facecolor('#1e1e1e')
                        ax.set_xlim(-1.5, 1.5); ax.set_ylim(-0.5, 2.8); ax.axis('off')

                        inning_text = f"TOP {game.inning}" if game.phase == "초" else f"BOT {game.inning}"
                        ax.text(0, 2.7, inning_text, color='#ff922b', fontsize=12, ha='center', va='center', weight='bold', bbox=dict(facecolor='#2b2b2b', edgecolor='#ff922b', boxstyle='round,pad=0.4', lw=1.5))

                        base_coords = {"home": (0, 0), "base1": (1, 1), "base2": (0, 2), "base3": (-1, 1)}
                        base_states = {"base1": game.base1, "base2": game.base2, "base3": game.base3}

                        for b_name, (x, y) in base_coords.items():
                            if b_name == "home":
                                ax.add_patch(patches.Rectangle((x-0.1, y-0.1), 0.2, 0.2, angle=45, edgecolor='#aaaaaa', facecolor='#ffffff', lw=1.5))
                                continue
                            is_runner = base_states[b_name]
                            bg_color = '#ff6b6b' if is_runner else '#3d3d3d'
                            edge_color = '#ffcbd1' if is_runner else '#777777'
                            ax.add_patch(patches.Rectangle((x-0.18, y-0.18), 0.36, 0.36, angle=45, rotation_point='center', edgecolor=edge_color, facecolor=bg_color, lw=2.0 if is_runner else 1.0))
                            label_map = {"base1": "1B", "base2": "2B", "base3": "3B"}
                            ax.text(x, y, label_map[b_name], color='#ffffff' if is_runner else '#aaaaaa', fontsize=9, ha='center', va='center', weight='bold')

                        ax.plot([0, 1, 0, -1, 0], [0, 1, 2, 1, 0], color='#555555', linestyle='--', linewidth=1, zorder=0)
                        current_is_our_turn = (not game.is_home_team and game.phase == "초") or (game.is_home_team and game.phase == "말")
                        active_batter = f"OUR BATTER: {game.my_batter_number}" if current_is_our_turn else f"ENEMY BATTER: {game.enemy_batter_number}"
                        ax.text(0, -0.4, active_batter, color='#51cf66', fontsize=11, ha='center', va='center', weight='bold', bbox=dict(facecolor='#2b2b2b', edgecolor='#51cf66', boxstyle='round,pad=0.3', lw=1))

                        st.pyplot(fig, width="stretch")
                        plt.close(fig)
                    st.info(HyperClovaX_AI.get_recommendation(game.pitch_history, game.base3, game.inning, current_is_our_turn))

                    # 감독 퇴장 시 수석코치 AI 자동 전술 진행
                    if game.manager_ejected:
                        st.error("🟥 감독 퇴장 상태입니다! 수석코치 AI가 전술을 위임받아 진행합니다.")
                        if st.button("🤖 [수석코치 AI] 다음 구 진행", type="primary", key="btn_coach_ai", width="stretch"):
                            my_p = game.get_current_my_pitcher()
                            has_timeout = game.my_timeouts_left > 0
                            should_use_timeout = False
                            if has_timeout:
                                if not current_is_our_turn and my_p.stamina <= (my_p.max_stamina * 0.3): should_use_timeout = True
                                elif current_is_our_turn and (game.base2 or game.base3) and random.random() < 0.20: should_use_timeout = True
                    
                            if should_use_timeout: game.use_my_timeout()
                            else:
                                if current_is_our_turn:
                                    valid_choices = [1, 2, 3]
                                    has_runner = game.base1 or game.base2 or game.base3
                                    if has_runner: valid_choices.append(5)
                                    if game.base3: valid_choices.append(4)
                                    
                                    ai_choice = random.choice(valid_choices)
                                    if has_runner and random.random() < 0.10: game.trigger_steal()
                                    else: game.play_turn(ai_choice)
                                else:
                                    choice = random.choice([1, 2, 3, 4])
                                    if choice == 4: game.play_intentional_walk()
                                    else: game.play_defense_one_pitch(choice)
                            st.rerun()

                    elif current_is_our_turn:
                        st.caption(f"🔍 구질 히스토리: {', '.join(game.pitch_history)}")
                        st.markdown("### 📢 공격 작전")
                        b1, b2, b3, b4 = st.columns(4)
                        with b1:
                            if st.button("💥 강공 (풀스윙)", key="btn_swing_1"): game.play_turn(1); st.rerun()
                            if st.button("🏃‍♂️ 스퀴즈 번트", key="btn_bunt_4"): game.play_turn(4); st.rerun()
                        with b2:
                            if st.button("🌟 밀어치기", key="btn_push_2"): game.play_turn(2); st.rerun()
                            if st.button("🔥 런앤히트", key="btn_runhit_5"): game.play_turn(5); st.rerun()
                        with b3:
                            if st.button("👀 웨이팅", key="btn_wait_3"): game.play_turn(3); st.rerun()
                            if st.button("🏃 도루", key="btn_steal"): game.trigger_steal(); st.rerun()
                        with b4:
                            if st.button(f"⏱️ 타임 (잔여 {game.my_timeouts_left}회)", width="stretch", key="btn_attack_timeout"): game.use_my_timeout(); st.rerun()
                    else:
                        st.markdown("### 🛡️ 수비 볼배합")
                        d1, d2, d3, d4, d5 = st.columns(5)
                        with d1:
                            if st.button("⚾ 정면 승부", key="btn_def_1"): game.play_defense_one_pitch(1); st.rerun()
                        with d2:
                            if st.button("🥎 유인구", key="btn_def_2"): game.play_defense_one_pitch(2); st.rerun()
                        with d3:
                            if st.button("🔮 제구 위주", key="btn_def_3"): game.play_defense_one_pitch(3); st.rerun()
                        with d4:
                            if st.button("🛑 고의사구", key="btn_def_4"): game.play_intentional_walk(); st.rerun()
                        with d5: 
                            if st.button(f"⏱️ 타임 (잔여 {game.my_timeouts_left}회)", width="stretch", key="btn_def_timeout"): game.use_my_timeout(); st.rerun()

                    st.divider()
                    st.markdown("### 📜 게임 로그")
                    for log in reversed(game.game_log[-5:]): st.write(log)

                with col_chat:
                    st.markdown("#### 📺 실시간 관중 채팅")
                    if not game.game_over:
                        users = ["야구천재", "방구석펩", "침착한스트리머", "로켓단", "다이아수저", "삼진에진심인편", "치지직조율사", "치킨치킨",
                            "물개아님돌고래임", "돔구장건설요청", "내주머니속100원", "야잘알김동구", "도루묵", "클로저스파크", "9회말2아웃", 
                            "대타전문가", "KBO정신병자", "용규놀이터", "월급루팡", "류뿡"]
                        chat_pool = [
                            "아니 감독 돌았냐 ㅋㅋㅋ 진짜 뇌 빼고 경기하네", "지금 스퀴즈 각인데?? 왜 안 번트??", "투수 제발 좀 바꿔라!! 어깨 갈린다 ㅠㅠ", 
                            "이 타이밍에 도루 안 하면 언제 하냐고!!! 🏃‍♂️💨", "이게 진짜 KBO 클래식이지 ㅋㅋㅋㅋ 고증 보소", "NC식 현질 유도 없어서 갓겜 인정합니다", 
                            "데드볼 던질 때 흠칫했다 ㅋㅋㅋ 리얼리티 굿", "야수 마운드 기어 올라오는 거 실화냐?? 막장 야구 ㅋㅋㅋ", "혈압 올라 죽겠네 ㅋㅋㅋ 혈압약 시켰다", 
                            "2스트라이크 이후에 파울 커트 미쳤다 ㅋㅋㅋ 끈질기네", "용규놀이 지독하다 지독해 ㅋㅋㅋ 투수 눈물 흘리는 중 😭", "오늘 경기 9회말 끝내기 각이다 가슴이 웅장해진다"
                        ]
                        game.chzzk_chats.append(f"💬 **{random.choice(users)}**: {random.choice(chat_pool)}")
                        if len(game.chzzk_chats) > 10: game.chzzk_chats.pop(0)

                    chat_box = st.container(height=350)
                    with chat_box:
                        for chat in reversed(game.chzzk_chats):
                            st.markdown(f"<div style='font-size: 14px; margin-bottom: 5px;'>{chat}</div>", unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # 🕹️ [모드 2] 🔥 미니게임 메뉴 분기 처리 영역 🔥
    # -----------------------------------------------------------------
    elif mode_choice == "🕹️ 미니게임 3종":
        st.title("🕹️ 미니게임 천국 (다이아 수급 & 탕진 모드)")
        st.caption("다이아를 모아 144경기 페넌트레이스 팀 운영에 보탬이 되거나, 화끈한 손맛을 즐겨보세요!")
        
        selected_mini_game = st.selectbox(
            "🎮 플레이할 미니게임을 선택하세요",
            ["🚀 챌린지 홈런 더비 (입장료 50💎)", 
             "⚡ 9회말 2아웃 만루 클러치 히터 (입장료 50💎)", 
             "🎯 오늘은 삼진왕 (입장료 30💎)"],
            key="select_mini_game_type"
        )
        st.markdown("---")

        if "🚀 챌린지 홈런 더비" in selected_mini_game:
            render_homerun_derby_ui()
        elif "⚡ 9회말 2아웃 만루 클러치 히터" in selected_mini_game:
            render_homerun_game_ui()
        elif "🎯 오늘은 삼진왕" in selected_mini_game:
            render_king_of_strikeout_ui()


if __name__ == "__main__":
    main()
