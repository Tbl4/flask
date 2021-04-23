from flask import Flask, render_template, redirect, request, abort, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from werkzeug.urls import url_parse

from forms.user import RegisterForm, LoginForm
from data.things import Thing
from data import db_session
from data.users import User
from flask_mail import Mail

import os
from forms.reset_password import ResetPasswordRequestForm, ResetPasswordForm
import random

from threading import Thread
from flask import render_template
from flask_mail import Message

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'sc*FzSPF72itHTt&Cj3bPMAe&4bRxGoH'

mail = Mail(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'ivantishkov2@gmail.com'
app.config['MAIL_PASSWORD'] = 'vi2307ir2604Z_'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
print(app.config)
mail.init_app(app)

login_manager.login_view = 'login'


def send_async_email(app, msg):
    print(3)
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    print(2)
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()


def send_password_reset_email(user):
    print(1)
    token = user.get_reset_password_token()
    send_email('Reset Your Password',
               sender='ivantishkov2@gmail.com',
               recipients=[user.email],
               text_body=render_template('reset_password.txt',
                                         username=user.name, token=token),
               html_body=render_template('reset_password_temp.html',
                                         username=user.name, token=token))


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/things.db")
    app.run()


'''
@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости', form=form)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html', title='Редактирование новости', form=form)
'''


@app.route("/")
def index():
    db_sess = db_session.create_session()
    all_things = db_sess.query(Thing).all()
    selected_things = random.sample(all_things, 2)
    return render_template("index.html", things=selected_things)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print(form.email.data)
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        print(user)
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            # Пока не придумал
            # if user.is_admin:
            #     print(1)
            #     return redirect("/admin/")
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Проверьте свою электронную почту, туда было отправлена ссылка для сброса пароля.')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Восстановление пароля', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == user).first()
        user.set_password(form.password.data)
        db_sess.commit()
        flash('Ваш пароль изменен.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

# Пока не придумал
# @app.route('/admin/', methods=['GET'])
# @login_required
# def admin():
#     print(2)
#     db_sess = db_session.create_session()
#     user = db_sess.query(User).all()[0]
#     print(user.is_admin)
#     if user.is_admin:
#         return render_template('admin.html')
#     else:
#         return redirect('/logout')


if __name__ == '__main__':
    main()
