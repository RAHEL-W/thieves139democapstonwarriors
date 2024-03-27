from flask import render_template, redirect, url_for, flash,request, jsonify
import requests
from . import main
from app.models import User,db,SaveGame, UserInvitation, Message, EventPost
from flask_login import login_required, current_user
from datetime import datetime
from .forms import InviteForm, PostsavegameForm

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
  

@main.route('/save_game/<date>')

@login_required
def save_game(date):
    response = requests.get("https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/9/schedule")
    if response.status_code == 200:
        data = response.json()
        events = data['events']
        
        running_wins = 0
        running_losses = 0
        selected_event = None
        for event in events:
            date_obj = datetime.strptime(event['date'], '%Y-%m-%dT%H:%M%SZ')
            formatted_date = date_obj.strftime('%d %b %Y')
            if formatted_date == date:
                selected_event = event
                break




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

    if selected_event:
     print(selected_event)
     game = SaveGame.query.filter_by(date=date).first()
    if not game:
        new_Savegame = SaveGame(
    date=date,
    opponent=selected_event['competitions'][0]['competitors'][0]['team']['shortDisplayName'],
    opponent2=selected_event['competitions'][0]['competitors'][1]['team']['shortDisplayName'],
    opponent_img=selected_event['competitions'][0]['competitors'][0]['team']['logos'][0]['href'],
    opponent_img2=selected_event['competitions'][0]['competitors'][1]['team']['logos'][0]['href'],
    user_id=current_user.id
        )
        flash('Successful! game save.', 'success')
        db.session.add(new_Savegame)
        db.session.commit()
    return redirect(url_for('main.schedule'))








@main.route('/invite/<save_game_date>', methods=["GET", "POST"])
@login_required
def invite(save_game_date):
    form = InviteForm()

    if request.method == "POST" and form.validate_on_submit():
        # Find the specific SaveGame instance
        save_game = SaveGame.query.filter_by(date=save_game_date).first_or_404()


       
        email = form.email.data
        caption = form.caption.data
        invited_by_user_id = current_user.id
            
            # Create a new UserInvitation with the SaveGame's date
        new_user_invitation = UserInvitation(
                email=email,
                invited_by_user_id=invited_by_user_id,
                caption=caption,
                date=save_game.date, # Use the date from the specific SaveGame
                opponent = save_game.opponent,
                opponent2 = save_game.opponent2,
                opponent_img = save_game.opponent_img,
                opponent_img2 = save_game.opponent_img2
            )
        new_user_invitation.save()

        flash('Successful! Invite sent.', 'success')

    

        return redirect(url_for('main.save'))
    else:
        return render_template('invite.html', form=form, save_game_date=save_game_date)


 
@main.route('/save') 
@login_required  
def save():
    SaveGames = SaveGame.query.filter_by(user_id = current_user.id).all()
    UserInvitations = UserInvitation.query.filter_by(email=current_user.email).all()
    # invitegame= SaveGame.query.filter_by(date=date).all()
    return render_template('savegame.html', SaveGames=SaveGames ,  UserInvitations=UserInvitations)



@main.route('/delete_savegame/<save_game_date>')  
@login_required
def delete_savegame(save_game_date):
    savegame = SaveGame.query.filter_by(date=save_game_date).first()
    if savegame and savegame.user_id == current_user.id:
        db.session.delete(savegame)
        db.session.commit()
        flash(' SAVEGAME is deleted', 'danger')
        return redirect(url_for('main.save'))
    else:
        flash('this SAVEGAME it doesn\'t belong to you','danger')
        return redirect(url_for('main.save',save_game_date=save_game_date)) 
    

@main.route('/delete_invitation/<invitation_date>')  
@login_required
def delete_invitation(invitation_date):
    invitation = UserInvitation.query.filter_by(date=invitation_date).first()
    if invitation and invitation.email == current_user.email:
        db.session.delete(invitation)
        db.session.commit()
        flash(' Invitation is succefully deleted', 'danger')
        return redirect(url_for('main.save'))
    else:
        flash('this INVITATION it doesn\'t belong to you','danger')
        return redirect(url_for('main.save',invitation_date=invitation_date)) 


messages = []

@main.route('/send', methods=['POST'])
@login_required
def send():
    recipient_id = request.form.get('recipient_id')
    message_text = request.form.get('message')

    if recipient_id and message_text:
        message = Message(
            sender_id=current_user.id,
            recipient_id=recipient_id,
            text=message_text
        )
        db.session.add(message)
        db.session.commit()
        return jsonify({'status': 'success', 'message': message_text})
    return jsonify({'status': 'error', 'message': 'Missing recipient or message'})


@main.route('/receive')
@login_required
def receive():
    messages = Message.query.filter(
        (Message.sender_id == current_user.id) | 
        (Message.recipient_id == current_user.id)
    ).join(User, User.id == Message.sender_id).add_columns(User.username).all()

    messages_data = [{
        'id': msg.Message.id,
        'sender_id': msg.Message.sender_id, 
        'sender_username': msg.username,
        'recipient_id': msg.Message.recipient_id,
        'text': msg.Message.text, 
        'timestamp': msg.Message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        'is_sender': msg.Message.sender_id == current_user.id
    } for msg in messages]

    return jsonify(messages_data)

@main.route('/chat')
@login_required
def chat():
    users = User.query.filter(User.id != current_user.id).all()

    return render_template('message.html', users=users)






@main.route('/edit_message/<int:message_id>', methods=['POST'])
@login_required
def edit_message(message_id):
    new_text = request.form.get('new_text')
    message = Message.query.get_or_404(message_id)

    if message.sender_id != current_user.id:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403

    if new_text:
        message.text = new_text
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Message updated'})

    return jsonify({'status': 'error', 'message': 'No new text provided'})



@main.route('/delete_message/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)

    if message.sender_id != current_user.id:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403

    db.session.delete(message)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Message deleted'})





@main.route('/post_savegame/<save_game_date>', methods=["GET", "POST"])
@login_required
def post_savegame(save_game_date):
    form = PostsavegameForm()

    save_game = SaveGame.query.filter_by(date=save_game_date).first_or_404()

    if form.validate_on_submit():
        new_event_post = EventPost(
            place=form.place.data,
            caption=form.caption.data,
            user_id=current_user.id,
            date=save_game.date, 
            opponent=save_game.opponent,
            opponent2=save_game.opponent2,
            opponent_img=save_game.opponent_img,
            opponent_img2=save_game.opponent_img2
        )
        db.session.add(new_event_post)
        db.session.commit()

        flash('Successful! Event Post.', 'success')
        return redirect(url_for('post.feed'))  # Adjust the redirect as needed

    return render_template('eventpost.html', form=form, save_game=save_game)




@main.route('/edit_event/<event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = EventPost.query.get(event_id)
    if not event:
        flash("Event not found!", "danger")
        return redirect(url_for('main.feed'))

    if event.user_id != current_user.id:
        flash("You do not have permission to edit this event.", "danger")
        return redirect(url_for('main.feed'))

    form = PostsavegameForm(obj=event)
    if form.validate_on_submit():
        event.caption = form.caption.data
        event.place = form.place.data
        # ... any other fields to update ...
        db.session.commit()
        flash('Event successfully updated!', 'info')
        return redirect(url_for('post.feed'))

    return render_template('editeventpost.html', form=form, event=event)
 
    




@main.route('/delete_event/<event_id>')  
@login_required
def delete_event(event_id):
    event = EventPost.query.get(event_id) 
    if event and event.user_id == current_user.id:
        db.session.delete(event)
        db.session.commit()
        flash(' event is succefully deleted', 'danger')
        return redirect(url_for('post.feed'))
    else:
        flash('this event it doesn\'t belong to you','danger')
        return redirect(url_for('post.feed')) 