
from django.db import connection
from django.utils import timezone
from datetime import datetime


def update_stadium_name(old_name, new_name):
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM MatchSession WHERE stadium_name = %s AND stadium_name != %s", [new_name, old_name])
        if cursor.fetchone()[0] > 0:
            return False, "The new stadium name already exists. Please choose a different name."
        cursor.execute("UPDATE MatchSession SET stadium_name = %s WHERE stadium_name = %s", [new_name, old_name])
        cursor.connection.commit()
        return True, "Stadium name updated successfully."
    
    
def get_user_type(username, password):
    with connection.cursor() as cursor:
        for table in ['DBManager', 'Player', 'Jury', 'Coach']:
            cursor.execute(f"SELECT * FROM {table} WHERE username = %s AND password = %s", [username, password])
            if cursor.fetchone():
                return table
    return None


def get_next_id(table_name):
    
    if table_name == "PlayerTeams":
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT MAX(player_teams_id) FROM {table_name}")
            max_id = cursor.fetchone()[0]
            return max_id + 1 if max_id is not None else 1
    
    if table_name == "PlayerPositions":
         with connection.cursor() as cursor:
            cursor.execute(f"SELECT MAX(player_positions_id) FROM {table_name}")
            max_id = cursor.fetchone()[0]
            return max_id + 1 if max_id is not None else 1
        

def save_user(data, user_type):
    try:
        with connection.cursor() as cursor:
            if user_type == 'Player':
                cursor.execute("""
                    INSERT INTO Player (username, password, name, surname, date_of_birth, height, weight)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (data['username'], data['password'], data['name'], data['surname'],
                      data['date_of_birth'], data['height'], data['weight']))
                
                query = "SELECT team_ID FROM team WHERE team_name = %s"

                cursor.execute(query, [data['team']])
                result = cursor.fetchone()
                if result:
                    team_id = result[0]
                    print("Found team_id:", team_id)
                else:
                    print("No results found. Check if the team name exists in the database.")
               
                cursor.execute("SELECT team_ID FROM team WHERE team_name = %s", [data['team']])
                print("asfsdfsdasa", cursor.fetchone()[0])
                team_ID = cursor.fetchone()[0] 

                cursor.execute("SELECT position_ID FROM position WHERE position_name = %s", [data['position']])
                position_ID = cursor.fetchone()[0]
                
            
                player_teams_id = get_next_id("PlayerTeams") 
                player_positions_id = get_next_id("PlayerPositions") 
                
                
                cursor.execute("""
                    INSERT INTO PlayerTeams (player_teams_id, username, team)
                    VALUES (%s, %s, %s)
                """, (player_teams_id, data['username'], team_ID))

                cursor.execute("""
                    INSERT INTO PlayerPositions (player_positions_id, username, position)
                    VALUES (%s, %s, %s)
                """, (player_positions_id, data['username'], position_ID))
            
            cursor.connection.commit()
            print("Player and associations added successfully.")
            if user_type == 'Coach':
                sql = """INSERT INTO Coach (username, password, name, surname, nationality)
                         VALUES (%s, %s, %s, %s, %s)"""
                params = (data['username'], data['password'], data['name'], data['surname'], data['nationality'])
            if user_type == 'Jury':
                sql = """INSERT INTO Jury (username, password, name, surname, nationality)
                         VALUES (%s, %s, %s, %s, %s)"""
                params = (data['username'], data['password'], data['name'], data['surname'], data['nationality'])
            
            if user_type in ['Coach', 'Jury']:
                cursor.execute(sql, params)

            cursor.connection.commit()
            print("Data added successfully.")
            print("Insert successful")
    except Exception as e:
        print(f"An error occurred during SQL execution: {e}")
        

def delete_match(session_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM matchsession WHERE session_ID = %s", [session_id])
            cursor.execute("DELETE FROM sessionsquads WHERE session_ID = %s", [session_id])
            connection.commit()
            if cursor.rowcount > 0:
                return True, "Match session deleted successfully."
            else:
                return False, "No match session found with the provided ID."
    except Exception as e:
        return False, f"An error occurred: {str(e)}"
 
 
def validate_stadium(stadium_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM Stadium WHERE stadium_id = %s", [stadium_id])
        return cursor.fetchone()[0] > 0

def validate_jury(jury_username):
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM Jury WHERE username = %s", [jury_username])
        return cursor.fetchone()[0] > 0
    
def validate_team(logged_coach_username,team_id):
    with connection.cursor() as cursor:
        cursor.execute("""
                SELECT COUNT(*)
                FROM Team
                WHERE coach_username = %s AND team_id = %s
            """, [logged_coach_username, team_id])
        result = cursor.fetchone()

    return result[0] > 0   
    
   
    
def save_match_session(data):
    try:
        with connection.cursor() as cursor:
            # Fetch the stadium details using the provided stadium_id
            cursor.execute("SELECT stadium_name, stadium_country FROM Stadium WHERE stadium_id = %s", [data['stadium_id']])
            stadium_details = cursor.fetchone()
            
            if not stadium_details:
                return False, "Stadium not found."

            # Fetch the current maximum session_ID
            cursor.execute("SELECT MAX(session_ID) FROM MatchSession")
            max_id_result = cursor.fetchone()
            if max_id_result and max_id_result[0] is not None:
                next_session_id = max_id_result[0] + 1
            else:
                next_session_id = 1  # If table is empty, start with ID 1
            
            # Insert the new match session using the fetched stadium details and calculated next_session_id
            cursor.execute("""
                INSERT INTO MatchSession (session_ID, team_id, stadium_id, stadium_name, stadium_country, date, time_slot, assigned_jury_username)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                next_session_id,
                data['team_id'], data['stadium_id'],
                stadium_details[0], stadium_details[1],
                data['date'], data['time_slot'], data['jury_username']
            ))
            connection.commit()
        return True, "Session added successfully."
    except Exception as e:
        return False, str(e)


def calculate_average_rating(jury_username):
    
    with connection.cursor() as cursor:
            cursor.execute("""
                SELECT AVG(rating) AS average_rating, COUNT(*) AS total_sessions
                FROM MatchSession
                WHERE assigned_jury_username = %s AND rating IS NOT NULL
            """, [jury_username])
            result = cursor.fetchone()
            average_rating = result[0] if result[0] else 0
            total_sessions = result[1]

    return average_rating, total_sessions


def validate_rating(session_id, username, rating):
    """ Validate if the session can be rated by the jury """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT date FROM MatchSession
            WHERE session_ID = %s AND assigned_jury_username = %s AND rating IS NULL
        """, [session_id, username])
        session = cursor.fetchone()
        if session:
            session_date = datetime.strptime(session[0], '%Y-%m-%d').date()
            print(session_date)
            if session_date < datetime.now().date():
                return True
    return False


def submit_rating(session_id, rating):
    """ Update the session with the given rating """
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE MatchSession SET rating = %s WHERE session_ID = %s
        """, [rating, session_id])
        connection.commit()
        
def update_jury_statistics(username):
    """ Recalculate the average rating and total count """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT AVG(rating), COUNT(*)
            FROM MatchSession
            WHERE assigned_jury_username = %s AND rating IS NOT NULL
        """, [username])
        result = cursor.fetchone()
        return result if result else (0, 0)
    
from django.db import connection
from datetime import datetime

def player_query(player_username):
    with connection.cursor() as cursor:
        # Get all unique players this player has played with
        cursor.execute("""
            SELECT DISTINCT p.username, p.name, p.surname
            FROM Player p
            JOIN SessionSquads ss ON p.id = ss.player_id
            JOIN SessionSquads ss2 ON ss.session_id = ss2.session_id
            WHERE ss2.player_id = (SELECT id FROM Player WHERE username = %s) AND p.username != %s
        """, [player_username, player_username])
        played_with = cursor.fetchall()

        # Get the session IDs where this player played
        cursor.execute("""
            SELECT session_id
            FROM SessionSquads
            WHERE player_id = (SELECT id FROM Player WHERE username = %s)
        """, [player_username])
        session_ids = [item[0] for item in cursor.fetchall()]

        # Get the player(s) played with the most and their counts
        cursor.execute("""
            SELECT p.username, COUNT(*) as count
            FROM Player p
            JOIN SessionSquads ss ON p.id = ss.player_id
            WHERE ss.session_id IN %s AND p.username != %s
            GROUP BY p.username
            ORDER BY count DESC
        """, [tuple(session_ids), player_username])
        most_played_with = cursor.fetchall()

        max_sessions = most_played_with[0][1] if most_played_with else 0
        players_most_played = [player[0] for player in most_played_with if player[1] == max_sessions]

        # Calculate average height if more than one
        if len(players_most_played) > 1:
            cursor.execute("""
                SELECT AVG(height)
                FROM Player
                WHERE username IN %s
            """, [tuple(players_most_played)])
            avg_height = cursor.fetchone()[0]
        elif players_most_played:
            cursor.execute("""
                SELECT height
                FROM Player
                WHERE username = %s
            """, [players_most_played[0]])
            avg_height = cursor.fetchone()[0]
        else:
            avg_height = None

        # Transform played_with to a list of dicts for better handling in templates
        played_with = [{'username': player[0], 'name': player[1], 'surname': player[2]} for player in played_with]

        return played_with, avg_height
