from flask import redirect,render_template,url_for, request, flash 
from . import post
from .forms import  CreatePost
from flask_login import login_required, current_user
from app.models import  db, Post,EventPost









@post.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = CreatePost()

    if request.method == 'POST' and form.validate_on_submit:
        img_url = form.img_url.data
        caption = form.caption.data
        location = form.location.data
        user_id = current_user.id
        
        new_post = Post(img_url=img_url, caption=caption, location=location, user_id=user_id)
        new_post.save()
        flash('Successfully created new post ', 'success')
        return redirect(url_for('main.home'))

    else:
        return render_template('create_post.html', form=form)
    



@post.route('/feed')   
def feed():
    posts = Post.query.all()
    Events= EventPost.query.all()
    return render_template('feed.html', posts=posts, Events=Events)






@post.route('/edit_post/<post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get(post_id) 
    form = CreatePost(obj=post)  # Instantiate the form with eventpost data
    if post and post.user_id == current_user.id:
        if request.method == 'POST' and form.validate_on_submit():
            post.img_url = form.img_url.data
            post.caption = form.caption.data
            post.location = form.location.data

            post.save()
            flash('successfully updataed post', 'info')
            return redirect(url_for('post.feed'))  
        else:

         return render_template('edit_post.html', form=form, post=post)
        
    else:
        flash('this post it doesn\'t belong to you','danger')
        return redirect(url_for('post.feed'))    
    




@post.route('/delete_post/<post_id>')  
@login_required
def delete_post(post_id):
    post = Post.query.get(post_id) 
    if post and post.user_id == current_user.id:
        db.session.delete(post)
        db.session.commit()
        flash(' post is succefully deleted', 'danger')
        return redirect(url_for('post.feed'))
    else:
        flash('this post it doesn\'t belong to you','danger')
        return redirect(url_for('post.feed')) 
    
