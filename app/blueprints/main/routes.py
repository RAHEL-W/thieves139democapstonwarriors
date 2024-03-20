from flask import render_template, redirect, url_for, flash
import requests
from . import main
from app.models import User,db
from flask_login import login_required, current_user
from datetime import datetime


@main.route('/')
def home():
   return render_template('home.html')

@main.route('/players')
def players():
   return render_template('players.html')

@main.route('/connect')
@login_required
def connect():
   users = User.query.filter(User.id != current_user.id)
   return render_template('connect.html', users=users)


@main.route('/follow/<user_id>')
@login_required
def follow(user_id):
   user = User.query.get(user_id)
   current_user.following.append(user)
   db.session.commit()
   flash(f'successfully followed {user.username}', 'info')
   return redirect(url_for('main.connect'))



@main.route('/unfollow/<user_id>')
@login_required
def unfollow(user_id):
   user = User.query.get(user_id)
   current_user.following.remove(user)
   db.session.commit()
   flash(f'successfully unfollowed {user.username}', 'warning')
   return redirect(url_for('main.connect'))

   
@main.route('/roster')
def roster():
   url=f'http://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/GS/roster'
   
   response = requests.get(url)
   data = response.json()
   players = data['athletes']
   for player in players:
      name = player['fullName']  # Removed the comma to fix the tuple issue
      num = player['jersey'] 
      pos=player.get('position', {}).get('abbreviation', '--')  # Safely access nested college name
      age = player.get('age', 'Unknown')  # Using .get() for safer access
      height = player.get('displayHeight', '--')
      weight = player.get('weight', '--')
      college = player.get('college', {}).get('name', '--')  # Safely access nested college name
      salary = player.get('contract', {}).get('salary', '--')  # Safely access nested college name
      imag_url=player.get('headshot', {}).get('href', 'No Image URL')  # example key for image URL
      print(name, num,pos,age, height, weight, college,salary)
   return render_template('roster.html', players=players)




def get_score_as_int(score_value):
    if score_value is not None and score_value != 'N/A':
        try:
            return int(float(score_value))
        except ValueError:
            return 0
    else:
        return 






    
@main.route('/schedule')
def schedule():
    response = requests.get("https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/9/schedule")
    if response.status_code == 200:
        data = response.json()
        events = data['events']

        running_wins = 0
        running_losses = 0

        for event in events:
            date_obj = datetime.strptime(event['date'], '%Y-%m-%dT%H:%M%SZ')
            event['formatted_date'] = date_obj.strftime('%d %b %Y')



            game_played = False  # Flag to check if the game has been played
            for competition in event['competitions']:
                for competitor in competition['competitors']:
                    if competitor['team']['abbreviation'] == 'GS':
                        if 'winner' in competitor:
                            game_played = True
                            if competitor['winner']:
                                running_wins += 1
                            else:
                                running_losses += 1

            if game_played:
                event['cumulative_wins'] = running_wins
                event['cumulative_losses'] = running_losses
            else:
                event['cumulative_wins'] = ''
                event['cumulative_losses'] = ''

            
            
            competitions = event['competitions']
            if competitions and len(competitions) > 0:
                competitors = competitions[0]['competitors']

                if 'score' in competitors[0] and 'score' in competitors[1]:
                    event['homescore'] = get_score_as_int(competitors[0]['score']['value'])
                    event['awayscore'] = get_score_as_int(competitors[1]['score']['value'])
                else:
                    # Assign empty string for upcoming games
                    event['homescore'] = ''
                    event['awayscore'] = ''
                event['opponent'] = competitors[0]['team']['shortDisplayName'] if len(competitors) > 1 else ' '
                event['opponent2'] = competitors[1]['team']['shortDisplayName'] if len(competitors) > 1 else ' '
                event['opponent_img'] = competitors[0]['team']['logos'][0]['href'] if len(competitors) > 1 and len(competitors[0]['team']['logos']) > 0 else  ' '
                event['opponent_img2'] = competitors[1]['team']['logos'][0]['href'] if len(competitors) > 1 and len(competitors[1]['team']['logos']) > 0 else ' '

                event['high_points'] = event['high_points_name'] = event['high_assistance'] = event['high_assistance_name'] = event['high_rounds'] = event['high_rounds_name'] = ' '

            
                for competitor in competitors:
                    leaders = competitor.get('leaders', [])
                    for leader in leaders:
                        if leader['name'] == 'points':
                            event['high_points'] = get_score_as_int(leader['leaders'][0]['value']) if leader['leaders'] else ' '
                            event['high_points_name'] = leader['leaders'][0]['athlete']['lastName'] if leader['leaders'] else ' '
                        elif leader['name'] == 'assists':
                            event['high_assistance'] = get_score_as_int(leader['leaders'][0]['value']) if leader['leaders'] else ' '
                            event['high_assistance_name'] = leader['leaders'][0]['athlete']['lastName'] if leader['leaders'] else ' '
                        elif leader['name'] == 'rebounds':
                            event['high_rounds'] = get_score_as_int(leader['leaders'][0]['value']) if leader['leaders'] else ' '
                            event['high_rounds_name'] = leader['leaders'][0]['athlete']['lastName'] if leader['leaders'] else ' '

    else:
        
        events = []

    return render_template('schedule.html', events=events)
  
