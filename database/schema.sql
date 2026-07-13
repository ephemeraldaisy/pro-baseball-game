-- 구단 기본 마스터 정보
CREATE TABLE teams (
    team_id VARCHAR(50) PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    homerun INT NOT NULL DEFAULT 0,
    hit INT NOT NULL DEFAULT 0,
    defense INT NOT NULL DEFAULT 0,
    stamina INT NOT NULL DEFAULT 0,
    steal_b INT NOT NULL DEFAULT 0
);

-- 게임 메인 세션 정보
CREATE TABLE game_sessions (
    game_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    away_team_id VARCHAR(50) NOT NULL,
    home_team_id VARCHAR(50) NOT NULL,
    away_score INT DEFAULT 0,
    home_score INT DEFAULT 0,
    current_inning INT DEFAULT 1,
    current_phase VARCHAR(10) DEFAULT '초',
    game_status VARCHAR(20) DEFAULT 'PROGRESS', -- PROGRESS, FINISHED, DRAW
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (away_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (home_team_id) REFERENCES teams(team_id)
);

-- 이닝별 누적 스코어 장부 정보 (KBO 12회차 고증)
CREATE TABLE scoreboard_records (
    record_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    game_id BIGINT NOT NULL,
    inning_num INT NOT NULL,
    away_run INT DEFAULT 0,
    home_run INT DEFAULT 0,
    FOREIGN KEY (game_id) REFERENCES game_sessions(game_id),
    UNIQUE KEY uq_game_inning (game_id, inning_num)
);
