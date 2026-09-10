import os
import sqlite3

DB_NAME = os.path.join(os.path.dirname(__file__), 'baseball_league.db')

def get_db_connection():
    """建立資料庫連線並回傳 connection 物件"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def _team_display_label(team_id, team_name):
    """整理球隊在下拉選單中的顯示文字，避免空隊名顯示成 None"""
    if team_name:
        return f"{team_id} - {team_name}"
    return team_id


def team_exists(team_id):
    """確認 TEAM 表中是否存在指定球隊"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT 1 FROM TEAM WHERE team_id = ? LIMIT 1', (team_id,))
    exists = cursor.fetchone() is not None
    conn.close()

    return exists


def get_year_options():
    """取得資料庫中可查詢的年份選項"""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
    SELECT DISTINCT year FROM TEAM WHERE year IS NOT NULL
    UNION
    SELECT DISTINCT year FROM PLAYER WHERE year IS NOT NULL
    UNION
    SELECT DISTINCT year FROM LEAGUE_GAME WHERE year IS NOT NULL
    UNION
    SELECT DISTINCT year FROM PARENT_OUT_ROLE WHERE year IS NOT NULL
    ORDER BY year DESC
    '''

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    return [row['year'] for row in rows]


def get_level_options():
    """取得球隊層級選項"""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
    SELECT DISTINCT level
    FROM TEAM
    WHERE level IS NOT NULL AND level != ''
    ORDER BY level
    '''

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    return [row['level'] for row in rows]


def get_team_options():
    """取得球隊下拉選單選項"""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
    SELECT team_id, team_name, year, level
    FROM TEAM
    WHERE team_id IS NOT NULL AND team_id != ''
    ORDER BY year DESC, level, team_name
    '''

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            'team_id': row['team_id'],
            'team_name': row['team_name'],
            'display_label': _team_display_label(row['team_id'], row['team_name']),
            'year': row['year'],
            'level': row['level']
        }
        for row in rows
    ]


def get_player_name_options():
    """取得球員姓名選項"""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
    SELECT DISTINCT chinese_name
    FROM PLAYER
    WHERE chinese_name IS NOT NULL
      AND chinese_name != ''
      AND team_id IS NOT NULL
      AND team_id != ''
    ORDER BY chinese_name
    '''

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    return [row['chinese_name'] for row in rows]


def get_season_options():
    """取得賽季選項"""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
    SELECT DISTINCT season
    FROM LEAGUE_GAME
    WHERE season IS NOT NULL AND season != ''
    ORDER BY season
    '''

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    return [row['season'] for row in rows]


def get_serno_options():
    """取得比賽場序選項"""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
    SELECT DISTINCT serNo
    FROM LEAGUE_GAME
    WHERE serNo IS NOT NULL AND serNo != ''
    ORDER BY serNo
    '''

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    return [row['serNo'] for row in rows]


def get_league_role_options():
    """取得聯盟職務選項"""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
    SELECT DISTINCT out_role
    FROM PARENT_OUT_ROLE
    WHERE out_role IS NOT NULL AND out_role != ''
    ORDER BY out_role
    '''

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    return [row['out_role'] for row in rows]

# ====================================================
# 功能一. 查詢某一年份，某一球隊的"隊教練"、"打擊教練"與 "助理教練"
# ====================================================
def query_team_coaches(team_id):
    """
    查詢特定球隊的指定職務教練 (隊教練, 打擊教練, 助理教練)。
    
    Args:
        team_id (str): 球隊ID (例如: '2025MajorB')
        
    Returns:
        dict: {
            'team_name': 球隊名稱,
            'coaches': [ {'name': 教練姓名, 'role': 職務}, ... ]
        }
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
    SELECT 
        T.team_name,
        P.parent_name,
        TP.in_role
    FROM TEAM T
    JOIN TEAM_PARENT TP ON T.team_id = TP.team_id
    JOIN PARENT P ON TP.family_id = P.family_id AND TP.code = P.code
    WHERE T.team_id = ?
      AND TP.in_role IN ('隊教練', '打擊教練', '助理教練')
    '''
    
    cursor.execute(query, (team_id,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return None

    result = {
        'team_name': rows[0]['team_name'] or team_id,
        'coaches': []
    }
    
    for row in rows:
        result['coaches'].append({
            'name': row['parent_name'],
            'role': row['in_role']
        })
        
    return result


# ====================================================
# 功能二. 查詢某一球隊所有家長職務
# ====================================================
def query_team_all_roles(team_id):
    """
    查詢特定球隊所有家長職務。

    Args:
        team_id (str): 球隊ID

    Returns:
        dict: {
            'team_name': 球隊名稱,
            'roles': [ {'parent_name': ..., 'in_role': ...}, ... ]
        }
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
    SELECT
        T.team_name,
        P.parent_name,
        TP.in_role
    FROM TEAM T
    JOIN TEAM_PARENT TP ON T.team_id = TP.team_id
    JOIN PARENT P ON TP.family_id = P.family_id AND TP.code = P.code
    WHERE T.team_id = ?
    ORDER BY TP.in_role, P.parent_name
    '''

    cursor.execute(query, (team_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return None

    return {
        'team_name': rows[0]['team_name'] or team_id,
        'roles': [
            {
                'parent_name': row['parent_name'],
                'in_role': row['in_role']
            }
            for row in rows
        ]
    }


# ====================================================
# 功能三. 查詢某一年份(，某一球隊層級的)所有球隊
# ====================================================
def query_teams_by_year_level(year, level=None):
    """
    查詢年度球隊列表。
    
    Args:
        year (int): 年份 (必填)
        level (str, optional): 球隊層級 (選填，例如 'Major', 'U8')
        
    Returns:
        list: [ {'team_id': ID, 'team_name': 名稱}, ... ]
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if level:
        query = '''
        SELECT team_id, team_name 
        FROM TEAM 
        WHERE year = ? AND level = ?
        '''
        params = (year, level)
    else:
        query = '''
        SELECT team_id, team_name 
        FROM TEAM 
        WHERE year = ?
        '''
        params = (year,)
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            'team_id': row['team_id'],
            'team_name': row['team_name'] or row['team_id']
        }
        for row in rows
    ]



# ====================================================
# 功能四. 查詢某一年份，某一球隊所有球員的中文姓名、英文姓名和年級
# ====================================================
def query_team_players(team_id):
    """
    查詢特定球隊的所有球員詳細資訊。
    
    Args:
        team_id (str): 球隊ID
        
    Returns:
        dict: {
            'team_name': 球隊名稱,
            'players': [ {'chinese_name': ..., 'english_name': ..., 'grade': ...}, ... ]
        }
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
    SELECT 
        T.team_name,
        PL.chinese_name,
        PL.english_name,
        PL.grade
    FROM TEAM T
    JOIN PLAYER PL ON T.team_id = PL.team_id
    WHERE T.team_id = ?
    '''
    
    cursor.execute(query, (team_id,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return None
        
    result = {
        'team_name': rows[0]['team_name'] or team_id,
        'players': []
    }
    
    for row in rows:
        result['players'].append({
            'chinese_name': row['chinese_name'],
            'english_name': row['english_name'],
            'grade': row['grade']
        })
        
    return result


# ====================================================
# 功能五. 查詢某一球員 a.在某一年份 b.歷年的球隊
# ====================================================
def query_player_history(chinese_name, year=None):
    """
    查詢球員的球隊經歷。
    
    Args:
        chinese_name (str): 球員中文姓名 (必填)
        year (int, optional): 年份 (選填)
        
    Returns:
        list: [ {'team_id': ID, 'team_name': 名稱, 'year': 年份}, ... ]
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    base_query = '''
    SELECT 
        T.team_id,
        T.team_name,
        T.year
    FROM PLAYER PL
    JOIN TEAM T ON PL.team_id = T.team_id
    WHERE PL.chinese_name = ?
    '''
    
    if year:
        query = base_query + ' AND PL.year = ?'
        params = (chinese_name, year)
    else:
        query = base_query + ' ORDER BY PL.year DESC'
        params = (chinese_name,)
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            'team_id': row['team_id'], 
            'team_name': row['team_name'],
            'year': row['year']
        } 
        for row in rows
    ]


# ====================================================
# 功能六. 查詢某一年份，某一聯盟職務的家長
# ====================================================
def query_league_role_parents(year, out_role):
    """
    查詢特定年份擔任指定聯盟職務的家長。

    Args:
        year (int): 年份
        out_role (str): 聯盟職務

    Returns:
        list: [家長姓名, ...]
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
    SELECT DISTINCT
        P.parent_name
    FROM PARENT_OUT_ROLE POR
    JOIN PARENT P ON POR.family_id = P.family_id AND POR.code = P.code
    WHERE POR.year = ?
      AND POR.out_role = ?
    ORDER BY P.parent_name
    '''

    cursor.execute(query, (year, out_role))
    rows = cursor.fetchall()
    conn.close()

    return [row['parent_name'] for row in rows]


# ====================================================
# 功能七. 查詢特定場序的比賽詳細資訊
# ====================================================
def query_game_info(year, season, serNo):
    """
    查詢特定比賽的詳細資訊。

    Args:
        year (int): 年份
        season (str): 賽季
        serNo (str): 場序

    Returns:
        dict: 比賽詳細資訊
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
    SELECT
        LG.place,
        LG.date,
        LG.from_ AS start_time,
        LG.to_ AS end_time,
        H_TEAM.team_name AS h_team_name,
        G_TEAM.team_name AS g_team_name
    FROM LEAGUE_GAME LG
    JOIN TEAM H_TEAM ON LG.hTeam_id = H_TEAM.team_id
    JOIN TEAM G_TEAM ON LG.gTeam_id = G_TEAM.team_id
    WHERE LG.year = ?
      AND LG.season = ?
      AND LG.serNo = ?
    '''

    cursor.execute(query, (year, season, serNo))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        'place': row['place'],
        'date': row['date'],
        'from': row['start_time'],
        'to': row['end_time'],
        'home_team': row['h_team_name'],
        'guest_team': row['g_team_name']
    }


# ====================================================
# 功能八. 查詢某球隊在某年度賽季的賽程
# ====================================================
def query_team_games(year, season, team_id):
    """
    查詢特定球隊在指定年度與賽季的所有比賽。

    Args:
        year (int): 年份
        season (str): 賽季
        team_id (str): 球隊ID

    Returns:
        list: [比賽資訊, ...]
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
    SELECT
        LG.serNo,
        LG.place,
        LG.date,
        LG.from_ AS start_time,
        LG.to_ AS end_time,
        H_TEAM.team_name AS h_team_name,
        G_TEAM.team_name AS g_team_name
    FROM LEAGUE_GAME LG
    JOIN TEAM H_TEAM ON LG.hTeam_id = H_TEAM.team_id
    JOIN TEAM G_TEAM ON LG.gTeam_id = G_TEAM.team_id
    WHERE LG.year = ?
      AND LG.season = ?
      AND (LG.hTeam_id = ? OR LG.gTeam_id = ?)
    ORDER BY LG.date, LG.from_, LG.serNo
    '''

    cursor.execute(query, (year, season, team_id, team_id))
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            'serNo': row['serNo'],
            'place': row['place'],
            'date': row['date'],
            'from': row['start_time'],
            'to': row['end_time'],
            'home_team': row['h_team_name'],
            'guest_team': row['g_team_name']
        }
        for row in rows
    ]
