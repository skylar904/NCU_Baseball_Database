from flask import Flask, render_template, request
import db_util  # 匯入你的標準版 db_util.py

app = Flask(__name__)

# ==========================================
# 首頁
# ==========================================
@app.route('/')
def index():
    return render_template('index.html')

# ==========================================
# 1. 查教練
# ==========================================
@app.route('/coaches', methods=['GET'])
def search_coaches():
    team_id = request.args.get('team_id')
    result = None
    error = None
    team_options = db_util.get_team_options()

    if team_id:
        team_id = team_id.strip() # 去除前後空白
        result = db_util.query_team_coaches(team_id)
        if not result:
            if db_util.team_exists(team_id):
                error = "資料庫中有這支球隊，但目前沒有隊教練、打擊教練或助理教練資料。"
            else:
                error = "查無這支球隊。"

    return render_template('coaches.html', result=result, search_id=team_id, error=error, team_options=team_options)

# ==========================================
# 2. 查球隊職務 (功能 A)
# ==========================================
@app.route('/team_all_roles', methods=['GET'])
def search_team_all_roles():
    team_id = request.args.get('team_id')
    result = None
    error = None
    team_options = db_util.get_team_options()

    if team_id:
        team_id = team_id.strip()
        result = db_util.query_team_all_roles(team_id)
        if not result:
            if db_util.team_exists(team_id):
                error = "資料庫中有這支球隊，但目前沒有隊內職務資料。"
            else:
                error = "查無這支球隊。"

    return render_template('team_all_roles.html', result=result, search_id=team_id, error=error, team_options=team_options)

# ==========================================
# 3. 查球隊球員名單
# ==========================================
@app.route('/team_players', methods=['GET'])
def search_team_players():
    team_id = request.args.get('team_id')
    result = None
    error = None
    team_options = db_util.get_team_options()

    if team_id:
        team_id = team_id.strip()
        result = db_util.query_team_players(team_id)
        if not result:
            if db_util.team_exists(team_id):
                error = "資料庫中有這支球隊，但目前沒有球員名單資料。"
            else:
                error = "查無這支球隊。"

    return render_template('team_players.html', result=result, search_id=team_id, error=error, team_options=team_options)

# ==========================================
# 4. 查球員經歷
# ==========================================
@app.route('/player', methods=['GET'])
def search_player_history():
    name = request.args.get('name')
    year = request.args.get('year')
    history = []
    error = None
    player_options = db_util.get_player_name_options()
    year_options = db_util.get_year_options()

    if name:
        name = name.strip()
        try:
            year_int = int(year) if year else None
            history = db_util.query_player_history(name, year_int)
            if not history:
                if year:
                    error = "資料庫中有這位球員，但該年度目前沒有球隊經歷資料。"
                else:
                    error = "目前沒有這位球員的球隊經歷資料。"
        except ValueError:
            history = []
            error = "年份資料有誤。"

    return render_template(
        'player.html',
        history=history,
        search_name=name,
        search_year=year,
        error=error,
        player_options=player_options,
        year_options=year_options
    )

# ==========================================
# 5. 查聯盟職務 (功能 B)
# ==========================================
@app.route('/league_roles', methods=['GET'])
def search_league_roles():
    year = request.args.get('year')
    out_role = request.args.get('out_role')
    parents = []
    error = None
    year_options = db_util.get_year_options()
    role_options = db_util.get_league_role_options()

    if year and out_role:
        try:
            year_int = int(year)
            role_clean = out_role.strip()
            
            parents = db_util.query_league_role_parents(year_int, role_clean)
            if not parents:
                error = "該年度目前沒有這個聯盟職務的人員資料。"
        except ValueError:
            error = "年份格式錯誤，請輸入西元年份。"

    return render_template(
        'league_roles.html',
        parents=parents,
        s_year=year,
        s_role=out_role,
        error=error,
        year_options=year_options,
        role_options=role_options
    )

# ==========================================
# 6. 查球隊列表
# ==========================================
@app.route('/teams', methods=['GET'])
def search_teams():
    year = request.args.get('year')
    level = request.args.get('level')
    teams = []
    error = None
    year_options = db_util.get_year_options()
    level_options = db_util.get_level_options()

    if year:
        try:
            year_int = int(year)
            level_clean = level.strip() if level else None
            teams = db_util.query_teams_by_year_level(year_int, level_clean)
            if not teams:
                if level_clean:
                    error = "該年度目前沒有這個層級的球隊資料。"
                else:
                    error = "該年度目前沒有球隊資料。"
        except ValueError:
            error = "年份資料有誤。"

    return render_template(
        'teams.html',
        teams=teams,
        search_year=year,
        search_level=level,
        error=error,
        year_options=year_options,
        level_options=level_options
    )

# ==========================================
# 7. 查比賽資訊
# ==========================================
@app.route('/game', methods=['GET'])
def search_game():
    year = request.args.get('year')
    season = request.args.get('season')
    serNo = request.args.get('serNo')
    info = None
    error = None
    year_options = db_util.get_year_options()
    season_options = db_util.get_season_options()
    serno_options = db_util.get_serno_options()

    if year and season and serNo:
        try:
            info = db_util.query_game_info(int(year), season.strip(), serNo.strip())
            if not info:
                error = "這組年份、賽季與場序目前沒有對應的比賽資料。"
        except ValueError:
            info = None
            error = "年份資料有誤。"

    return render_template(
        'game.html',
        info=info,
        s_year=year,
        s_season=season,
        s_serNo=serNo,
        error=error,
        year_options=year_options,
        season_options=season_options,
        serno_options=serno_options
    )

# ==========================================
# 8. 查球隊賽程
# ==========================================
@app.route('/team_games', methods=['GET'])
def search_team_games():
    year = request.args.get('year')
    season = request.args.get('season')
    team_id = request.args.get('team_id')
    games = []
    error = None
    year_options = db_util.get_year_options()
    season_options = db_util.get_season_options()
    team_options = db_util.get_team_options()

    if year and season and team_id:
        try:
            games = db_util.query_team_games(int(year), season.strip(), team_id.strip())
            if not games:
                if db_util.team_exists(team_id.strip()):
                    error = "資料庫中有這支球隊，但該年度與賽季目前沒有賽程資料。"
                else:
                    error = "查無這支球隊。"
        except ValueError:
            games = []
            error = "年份資料有誤。"

    return render_template(
        'team_games.html',
        games=games,
        s_year=year,
        s_season=season,
        s_id=team_id,
        error=error,
        year_options=year_options,
        season_options=season_options,
        team_options=team_options
    )

# ==========================================
# 球隊詳情
# ==========================================
@app.route('/team/<team_id>', methods=['GET'])
def team_detail(team_id):
    team_id = team_id.strip()
    coaches_result = db_util.query_team_coaches(team_id)
    players_result = db_util.query_team_players(team_id)

    team_name = team_id
    if coaches_result:
        team_name = coaches_result['team_name']
    elif players_result:
        team_name = players_result['team_name']

    return render_template(
        'team_detail.html',
        team_name=team_name,
        coaches=coaches_result['coaches'] if coaches_result else [],
        players=players_result['players'] if players_result else []
    )

if __name__ == '__main__':
    app.run(debug=True, port=8001)
