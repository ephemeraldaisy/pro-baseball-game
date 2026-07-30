import os
import json
import base64
import random
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 💡 분리된 모듈에서 필요한 데이터 및 엔진 Import
from data import (
    TEAMS, MATCHUP_MATRIX, TEAM_ROSTERS, MATRIX_COLUMNS, 
    color_matchup_cells, render_roster_viewer, get_default_lineup
)
from engine import PureKboEngine, PitcherDomain, HyperClovaX_AI

def main() -> None:
    st.set_page_config(layout="wide")
    st.markdown("<style>.stButton>button { width: 100%; font-size: 14px !important; font-weight: bold; }</style>", unsafe_allow_html=True)
    
    st.title("⚾ 순수한 야구 시뮬레이터")

    if "full_kbo_engine" not in st.session_state: st.session_state.full_kbo_engine = None
    if "nc_diamonds" not in st.session_state: st.session_state.nc_diamonds = 1000
    if "my_team" not in st.session_state: st.session_state.my_team = "💖 핑크 돌핀스"

    df_matchup = pd.DataFrame.from_dict(MATCHUP_MATRIX, orient='index', columns=list(MATCHUP_MATRIX.keys()))

    with st.sidebar:
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
                        else:
                            st.error("다이아 부족!")

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
                        else:
                            st.error("다이아 부족!")

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
                        else:
                            st.error("다이아 부족!")

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
                        else:
                            st.error("다이아 부족!")

        st.markdown("---")
        st.markdown("### 💾 세이브 / 로드")
        
        with st.expander("🔑 세이브 코드 발급"):
            if st.session_state.full_kbo_engine is None:
                st.caption("경기가 시작된 후에 중간 저장이 가능합니다. ")
            else:
                st.write("현재 경기 상황과 투수 체력까지 모두 저장됩니다. 코드를 복사해 보관하세요.")
                game = st.session_state.full_kbo_engine

                my_pitchers_data = [
                    {"name": p.name, "role": p.role, "max_stamina": p.max_stamina, "stamina": p.stamina, "pitches_thrown": p.pitches_thrown}
                    for p in game.my_pitchers
                ]
                enemy_pitchers_data = [
                    {"name": p.name, "role": p.role, "max_stamina": p.max_stamina, "stamina": p.stamina, "pitches_thrown": p.pitches_thrown}
                    for p in game.enemy_pitchers
                ]
                save_data = {
                    "diamonds": st.session_state.nc_diamonds,
                    "my_team": st.session_state.my_team,
                    "enemy_team": game.enemy_team,
                    "is_home_team": game.is_home_team,
                    "our_score": game.our_score,
                    "enemy_score": game.enemy_score,
                    "away_stats": game.away_stats,
                    "home_stats": game.home_stats,
                    "inning": game.inning,
                    "phase": game.phase,
                    "my_batter_number": game.my_batter_number,
                    "enemy_batter_number": game.enemy_batter_number,
                    "our_total_pitches": game.our_total_pitches,
                    "enemy_total_pitches": game.enemy_total_pitches,
                    "strike": game.strike,
                    "ball": game.ball,
                    "out_count": game.out_count,
                    "base1": game.base1,
                    "base2": game.base2,
                    "base3": game.base3,
                    "away_inning_scores": game.away_inning_scores,
                    "home_inning_scores": game.home_inning_scores,
                    "game_log": game.game_log,
                    "pitch_history": game.pitch_history,
                    "chzzk_chats": game.chzzk_chats,
                    "hit_buff": game.hit_buff,
                    "manager_ejected": game.manager_ejected,
                    "my_pitcher_idx": game.my_pitcher_idx,
                    "my_used_pitchers": list(game.my_used_pitchers),
                    "my_pitchers": my_pitchers_data,
                    "enemy_pitcher_idx": game.enemy_pitcher_idx,
                    "enemy_used_pitchers": list(game.enemy_used_pitchers),
                    "enemy_pitchers": enemy_pitchers_data
                }
                json_str = json.dumps(save_data, ensure_ascii=False)
                encoded_code = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
                st.code(encoded_code, language="text")
                st.caption("위 코드를 더블클릭해 복사하세요!")

        with st.expander("🔓 코드 불러오기"):
            input_code = st.text_input("코드 입력", key="save_code_input", placeholder="세이브 코드를 붙여넣으세요")
            if st.button("📂 데이터 로드 실행"):
                if input_code.strip():
                    try:
                        decoded_bytes = base64.b64decode(input_code.encode('utf-8'))
                        decoded_str = decoded_bytes.decode('utf-8')
                        data = json.loads(decoded_str)
                        
                        st.session_state.nc_diamonds = data.get("diamonds", 1000)
                        st.session_state.my_team = data.get("my_team", "💖 핑크 돌핀스")

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
                        loaded_game.my_pitchers = []
                        for p_dict in data["my_pitchers"]:
                            p_obj = PitcherDomain(p_dict["name"], p_dict["role"], p_dict["max_stamina"])
                            p_obj.stamina = p_dict["stamina"]
                            p_obj.pitches_thrown = p_dict["pitches_thrown"]
                            loaded_game.my_pitchers.append(p_obj)
                            
                        loaded_game.enemy_pitcher_idx = data["enemy_pitcher_idx"]
                        loaded_game.enemy_used_pitchers = set(data["enemy_used_pitchers"])
                        loaded_game.enemy_pitchers = []
                        for p_dict in data["enemy_pitchers"]:
                            p_obj = PitcherDomain(p_dict["name"], p_dict["role"], p_dict["max_stamina"])
                            p_obj.stamina = p_dict["stamina"]
                            p_obj.pitches_thrown = p_dict["pitches_thrown"]
                            loaded_game.enemy_pitchers.append(p_obj)
                        
                        st.session_state.full_kbo_engine = loaded_game
                        st.toast("🎉 데이터 복구 성공! 로드가 완료되었습니다핑!", icon="💾")
                        st.rerun()
                    except Exception:
                        st.error("❌ 유효하지 않은 암호 코드입니다.")
                else:
                    st.warning("코드를 입력해 주세요!")

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
            else:
                st.error("⚠️ assets/team_stories.txt 파일 누락.")

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
            else:
                st.error("⚠️ assets/team-roster.txt 파일 누락.")

        st.divider()
        st.header("팀별 디폴트 타순")
        if st.button("기본 선발 라인업과 선발투수"):
            if os.path.exists("assets/default-lineup.txt"):
                with open("assets/default-lineup.txt", "r", encoding="utf-8") as f:
                    st.text_area("팀별 주전", value=f.read(), height=200, disabled=True)
            else:
                st.error("⚠️ assets/default-lineup.txt 파일 누락.")

    # 1. 경기 개시 전 팀 선택 및 라인업 커스텀 설정 영역
    if st.session_state.full_kbo_engine is None:
        st.session_state.my_team = st.selectbox("우리 팀 선택:", list(TEAMS.keys()), index=list(TEAMS.keys()).index(st.session_state.my_team))

        sp_list = TEAM_ROSTERS[st.session_state.my_team]["pitchers"]["선발(5)"]
        selected_sp_idx = st.selectbox("⚾ **오늘의 선발 투수 지명**",
            options=list(range(len(sp_list))),
            format_func=lambda x: f"{x+1}선발: {sp_list[x]} (체력: {TEAMS[st.session_state.my_team]['stamina']})",
            key=f"select_sp_{st.session_state.my_team}"
        )
        
        st.markdown(f"#### 📊 {st.session_state.my_team}의 구단별 상성표 요약")
        if st.session_state.my_team in df_matchup.index:
            my_status = df_matchup.loc[[st.session_state.my_team]]
            try:
                styled_status = my_status.style.map(color_matchup_cells)
            except AttributeError:
                styled_status = my_status.style.applymap(color_matchup_cells)
                
            st.dataframe(styled_status, width="stretch")

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
                    default_player = default_lineup[idx] if idx < len(default_lineup) else all_batters[idx % len(all_batters)]
                    d_idx = all_batters.index(default_player) if default_player in all_batters else 0
                    
                    sel = st.selectbox(
                        f"**{idx+1}번 타자**",
                        options=all_batters,
                        index=d_idx,
                        key=f"start_lineup_select_{idx}"
                    )
                    custom_lineup.append(sel)

            st.markdown("---")
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                if st.button("💾 현재 타순을 이 팀의 기본 오더로 저장", key=f"btn_save_lineup_{st.session_state.my_team}"):
                    st.session_state[saved_key] = custom_lineup
                    st.toast(f"✅ {st.session_state.my_team}의 선발 타순이 저장되었습니다!", icon="💾")
            with b_col2:
                if st.button("🔄 기본 추천 타순으로 초기화", key="btn_reset_lineup"):
                    if saved_key in st.session_state:
                        del st.session_state[saved_key]
                    st.toast("🔄 추천 타순으로 초기화되었습니다.", icon="🧹")
                    st.rerun()
        
        has_duplicates = len(set(custom_lineup)) != len(custom_lineup)
        if has_duplicates:
            seen = set()
            duplicates = set(p for p in custom_lineup if p in seen or seen.add(p))
            dup_names = ", ".join(duplicates)
            st.warning(f"⚠️ **라인업 중복 경고**: [{dup_names}] 선수가 중복 선택되었습니다! 서로 다른 9명의 타자로 라인업을 완성해 주세요.")
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

    # 2. 경기 진행 중 메인 화면
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
            try:
                styled_status = my_status.style.map(color_matchup_cells)
            except AttributeError:
                styled_status = my_status.style.applymap(color_matchup_cells)
                
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

                    else:
                        st.caption("🚨 더 이상 교체 가능한 대기 투수가 없습니다!")
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

        display_away = []
        display_home = []

        final_inning = game.inning
        if game.game_over and game.phase == "초" and game.home_inning_scores[game.inning - 1] == "":
            final_inning = max(1, game.inning - 1)

        for i in range(12):
            if game.game_over:
                if i == 8 and game.home_inning_scores[i] == "X":
                    display_away.append(game.away_inning_scores[i])
                    display_home.append("X")
                elif i >= game.inning:
                    display_away.append("")
                    display_home.append("")
                else:
                    display_away.append(game.away_inning_scores[i])
                    display_home.append(game.home_inning_scores[i])
            else:
                display_away.append("" if i >= game.inning else game.away_inning_scores[i])
                display_home.append("" if i >= game.inning else game.home_inning_scores[i])
        
        sb = {
            "BOARD": [f"🚌 {away_name}", f"🏟️ {home_name}"],
            "1": [display_away[0], display_home[0]], "2": [display_away[1], display_home[1]], "3": [display_away[2], display_home[2]],
            "4": [display_away[3], display_home[3]], "5": [display_away[4], display_home[4]], "6": [display_away[5], display_home[5]],
            "7": [display_away[6], display_home[6]], "8": [display_away[7], display_home[7]], "9": [display_away[8], display_home[8]],
            "10": [display_away[9], display_home[9]], "11": [display_away[10], display_home[10]],
            "R": [game.away_stats["R"], game.home_stats["R"]],
            "H": [game.away_stats["H"], game.home_stats["H"]],
            "E": [game.away_stats["E"], game.home_stats["E"]],
            "B": [game.away_stats["B"], game.home_stats["B"]]
        }
        st.table(pd.DataFrame(sb).set_index("BOARD"))

        if game.game_over:
            st.success(game.game_result_msg)
            if st.button("새 경기 시작", type="primary"): st.session_state.full_kbo_engine = None; st.rerun()
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
                    ax.set_xlim(-1.5, 1.5)
                    ax.set_ylim(-0.5, 2.8)
                    ax.axis('off')

                    inning_text = f"TOP {game.inning}" if game.phase == "초" else f"BOT {game.inning}"
                    ax.text(0, 2.7, inning_text, color='#ff922b', fontsize=12, ha='center', va='center', 
                            weight='bold', bbox=dict(facecolor='#2b2b2b', edgecolor='#ff922b', boxstyle='round,pad=0.4', lw=1.5))

                    base_coords = {
                        "home": (0, 0),
                        "base1": (1, 1),
                        "base2": (0, 2),
                        "base3": (-1, 1)
                    }

                    base_states = {
                        "base1": game.base1,
                        "base2": game.base2,
                        "base3": game.base3
                    }

                    for b_name, (x, y) in base_coords.items():
                        if b_name == "home":
                            rect = patches.Rectangle((x-0.1, y-0.1), 0.2, 0.2, angle=45, edgecolor='#aaaaaa', facecolor='#ffffff', lw=1.5)
                            ax.add_patch(rect)
                            continue

                        is_runner = base_states[b_name]
                        bg_color = '#ff6b6b' if is_runner else '#3d3d3d'
                        edge_color = '#ffcbd1' if is_runner else '#777777'
                        line_width = 2.0 if is_runner else 1.0

                        rect = patches.Rectangle((x-0.18, y-0.18), 0.36, 0.36, angle=45, rotation_point='center',
                                                 edgecolor=edge_color, facecolor=bg_color, lw=line_width)
                        ax.add_patch(rect)
                        
                        label_map = {"base1": "1B", "base2": "2B", "base3": "3B"}
                        text_color = '#ffffff' if is_runner else '#aaaaaa'
                        ax.text(x, y, label_map[b_name], color=text_color, fontsize=9, ha='center', va='center', weight='bold')

                    line_style = dict(color='#555555', linestyle='--', linewidth=1, zorder=0)
                    ax.plot([0, 1, 0, -1, 0], [0, 1, 2, 1, 0], **line_style)

                    current_is_our_turn = (not game.is_home_team and game.phase == "초") or (game.is_home_team and game.phase == "말")
                    if current_is_our_turn:
                        active_batter = f"OUR BATTER: {game.my_batter_number}"
                    else:
                        active_batter = f"ENEMY BATTER: {game.enemy_batter_number}"

                    ax.text(0, -0.4, active_batter, color='#51cf66', fontsize=11, ha='center', va='center', 
                            weight='bold', bbox=dict(facecolor='#2b2b2b', edgecolor='#51cf66', boxstyle='round,pad=0.3', lw=1))

                    st.pyplot(fig, width="stretch")
                    plt.close(fig)
                st.info(HyperClovaX_AI.get_recommendation(game.pitch_history, game.base3, game.inning, current_is_our_turn))

                if game.manager_ejected:
                    st.error("🟥 감독 퇴장 상태입니다! 수석코치 AI가 전술을 위임받아 진행합니다.")
                    if st.button("🤖 [수석코치 AI] 다음 구 진행", type="primary", key="btn_coach_ai", width="stretch"):
                        my_p = game.get_current_my_pitcher()
                        has_timeout = game.my_timeouts_left > 0
                        
                        should_use_timeout = False
                        if has_timeout:
                            if not current_is_our_turn and my_p.stamina <= (my_p.max_stamina * 0.3):
                                should_use_timeout = True
                            elif current_is_our_turn and (game.base2 or game.base3) and random.random() < 0.20:
                                should_use_timeout = True
                
                        if should_use_timeout:
                            game.use_my_timeout()
                        else:
                            if current_is_our_turn:
                                valid_choices = [1, 2, 3]
                                has_runner = game.base1 or game.base2 or game.base3
                                if has_runner: valid_choices.append(5)
                                if game.base3: valid_choices.append(4)
                                
                                ai_choice = random.choice(valid_choices)
                                if has_runner and random.random() < 0.10:
                                    game.trigger_steal()
                                else:
                                    game.play_turn(ai_choice)
                            else:
                                choice = random.choice([1, 2, 3, 4])
                                if choice == 4:
                                    game.play_intentional_walk()
                                else:
                                    game.play_defense_one_pitch(choice)
                                    
                        st.rerun()

                elif current_is_our_turn:
                    st.caption(f"🔍 구질 히스토리: {', '.join(game.pitch_history)}")
                    st.markdown("### 📢 공격 작전")
                    b1, b2, b3, b4 = st.columns(4)
                    
                    with b1:
                        if st.button("💥 강공 (풀스윙)", key="btn_swing_1"):
                            game.play_turn(1)    
                            st.rerun()
                        if st.button("🏃‍♂️ 스퀴즈 번트", key="btn_bunt_4"):
                            game.play_turn(4)
                            st.rerun()
                    with b2:
                        if st.button("🌟 밀어치기", key="btn_push_2"):
                            game.play_turn(2)
                            st.rerun()
                        if st.button("🔥 런앤히트", key="btn_runhit_5"):
                            game.play_turn(5)
                            st.rerun()
                    with b3:
                        if st.button("👀 웨이팅", key="btn_wait_3"): 
                            game.play_turn(3)
                            st.rerun()
                        if st.button("🏃 도루", key="btn_steal"): 
                            game.trigger_steal()
                            st.rerun()

                    with b4:
                        if st.button(f"⏱️ 타임 (잔여 {game.my_timeouts_left}회)", width="stretch"):
                            game.use_my_timeout()
                            st.rerun()
                            
                else:
                    st.markdown("### 🛡️ 수비 볼배합")
                    d1, d2, d3, d4, d5 = st.columns(5)
                    with d1:
                        if st.button("⚾ 정면 승부"): game.play_defense_one_pitch(1); st.rerun()
                    with d2:
                        if st.button("🥎 유인구"): game.play_defense_one_pitch(2); st.rerun()
                    with d3:
                        if st.button("🔮 제구 위주"): game.play_defense_one_pitch(3); st.rerun()
                    with d4:
                        if st.button("🛑 고의사구"): game.play_intentional_walk(); st.rerun()
                    with d5: 
                        if st.button(f"⏱️ 타임 (잔여 {game.my_timeouts_left}회)", width="stretch"):
                            game.use_my_timeout()
                            st.rerun()

                st.divider()
                st.markdown("### 📜 게임 로그")
                for log in reversed(game.game_log[-5:]): st.write(log)

            with col_chat:
                st.markdown("#### 📺 실시간 채팅")
                
                if not game.game_over:
                    users = ["야구천재", "방구석펩", "침착한스트리머", "로켓단", "다이아수저", "삼진에진심인편", "치지직조율사", "치킨치킨",
                        "물개아님돌고래임", "돔구장건설요청", "내주머니속100원", "야잘알김동구",
                        "도루묵", "클로저스파크", "9회말2아웃", "대타전문가", "KBO정신병자", "용규놀이터", 
                            "찜질방수건도둑", "월급루팡", "카미야최고야", "메카미야", "츄츄트레인", "자라나라머리머리", "류뿡"]
                    chat_pool = [
                        "아니 감독 돌았냐 ㅋㅋㅋ 진짜 뇌 빼고 경기하네", 
                        "지금 스퀴즈 각인데?? 왜 안 번트??", 
                        "투수 제발 좀 바꿔라!! 어깨 갈린다 ㅠㅠ", 
                        "감독 혹사 수준 보소 ㅋㅋㅋ 노동청 신고함",
                        "대타 누구 올릴 거냐?? 벤치 멤버 믿을 놈이 없다",
                        "이 타이밍에 도루 안 하면 언제 하냐고!!! 🏃‍♂️💨",
                        "대기업 급 핑돌이 물리 연산력 ㄷㄷ", 
                        "이게 진짜 KBO 클래식이지 ㅋㅋㅋㅋ 고증 보소", 
                        "방구석 과몰입 꿀잼이네 ㅋㅋㅋ 중계 맛집", 
                        "오늘 밸런스 패치 황밸이네 ㅋㅋ 쫄깃하다",
                        "NC식 현질 유도 없어서 갓겜 인정합니다", 
                        "데드볼 던질 때 흠칫했다 ㅋㅋㅋ 리얼리티 굿",
                        "야수 마운드 기어 올라오는 거 실화냐?? 막장 야구 ㅋㅋㅋ",
                        "일본의 카미야가 생각난다",
                        "혈압 올라 죽겠네 ㅋㅋㅋ 혈압약 시켰다",
                        "네이버 톡방 폼 미쳤다 ㅋㅋㅋ",
                        "오늘 주침 스트존 왜 저럼?? 눈을 장식으로 달았나",
                        "아웃 아웃 아웃!! 맨날 플라이 아웃만 치냐!! 수비 보소",
                        "볼넷 밀어내기로 점수 내는 거 개꿀잼이네 ㅋㅋㅋ",
                        "2스트라이크 이후에 파울 커트 미쳤다 ㅋㅋㅋ 끈질기네",
                        "용규놀이 지독하다 지독해 ㅋㅋㅋ 투수 눈물 흘리는 중 😭",
                        "이게 야구냐?? 예능이지 ㅋㅋㅋㅋ",
                        "킹갓 제네럴 에이스 마운드 등장 ㄷㄷㄷ 지렸다",
                        "야수 등판하면 배팅볼 꿀맛인데 ㅋㅋㅋ 홈런 가자!!!",
                        "오늘 경기 9회말 끝내기 각이다 가슴이 웅장해진다",
                        "야구는 뒷전이냐",
                        "왜 이렇게 못 치냐", 
                        "답답해서 내가 친다"
                    ]
                    new_chat = f"💬 **{random.choice(users)}**: {random.choice(chat_pool)}"
                    game.chzzk_chats.append(new_chat)
                    
                    if len(game.chzzk_chats) > 10:
                        game.chzzk_chats.pop(0)

                chat_box = st.container(height=350)
                with chat_box:
                    for chat in reversed(game.chzzk_chats):
                        st.markdown(f"<div style='font-size: 14px; margin-bottom: 5px;'>{chat}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
