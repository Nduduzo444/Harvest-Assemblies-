from flask import Flask, render_template, redirect, url_for, request, session, flash
from models import db, Admin, Event, Leader, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from flask_mail import Mail, Message as MailMessage

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///church.db'
app.config['UPLOAD_SERMONS'] = 'static/uploads/sermons'
app.config['UPLOAD_POSTERS'] = 'static/uploads/posters'

db.init_app(app)

# Create tables and seed admin
with app.app_context():
    db.create_all()
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin')
        admin.set_password('church123')
        db.session.add(admin)
        db.session.commit()
        
# Mail config
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_password'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)        

# Public Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/sermons')
def sermons():
    path = app.config['UPLOAD_SERMONS']
    os.makedirs(path, exist_ok=True)
    sermon_files = os.listdir(path)
    return render_template('sermons.html', sermons=sermon_files)

@app.route('/events')
def events():
    today = datetime.today().date()
    current_events = Event.query.filter(Event.end_date >= today).all()
    archived_events = Event.query.filter(Event.end_date < today).all()
    return render_template('events.html', current_events=current_events, archived_events=archived_events)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        content = request.form['message']
        urgency = request.form['urgency']

        msg = Message(name=name, email=email, subject=subject, content=content, urgency=urgency)
        db.session.add(msg)
        db.session.commit()

        # Auto-reply
        reply = MailMessage(
            subject="Thank you for contacting Harvest Church",
            sender=app.config['MAIL_USERNAME'],
            recipients=[email],
            body=f"Dear {name},\n\nThank you for reaching out. We’ve received your message and will respond soon.\n\nBlessings,\nHarvest Assemblies of Christ Global Church"
        )
        mail.send(reply)

        flash("Your message has been sent!")
        return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/people')
def people():
    leaders = Leader.query.all()
    return render_template('people.html', leaders=leaders)

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Admin.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    sermon_files = os.listdir(app.config['UPLOAD_SERMONS'])
    poster_files = os.listdir(app.config['UPLOAD_POSTERS'])
    leaders = Leader.query.all()
    messages = Message.query.order_by(Message.timestamp.desc()).all()

    return render_template('admin_dashboard.html', sermons=sermon_files, posters=poster_files, leaders=leaders, messages=messages)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/reset', methods=['GET', 'POST'])
def admin_reset():
    if request.method == 'POST':
        new_password = request.form['new_password']
        user = Admin.query.filter_by(username='admin').first()
        if user:
            user.set_password(new_password)
            db.session.commit()
            flash("Password updated successfully!")
        return redirect(url_for('admin_login'))
    return render_template('admin_reset.html')

# Upload Routes
@app.route('/upload_sermon', methods=['POST'])
def upload_sermon():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    file = request.files['sermon_file']
    title = request.form['title']
    filename = secure_filename(file.filename)
    path = app.config['UPLOAD_SERMONS']
    os.makedirs(path, exist_ok=True)
    file.save(os.path.join(path, filename))
    flash(f"Sermon '{title}' uploaded successfully!")
    return redirect(url_for('admin_dashboard'))

@app.route('/upload_event', methods=['POST'])
def upload_event():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    title = request.form['event_title']
    description = request.form['description']
    category = request.form['category']
    start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
    end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
    poster = request.files['poster']
    filename = secure_filename(poster.filename)

    path = app.config['UPLOAD_POSTERS']
    os.makedirs(path, exist_ok=True)
    poster.save(os.path.join(path, filename))

    event = Event(title=title, description=description, category=category,
                  poster_filename=filename, start_date=start_date, end_date=end_date)
    db.session.add(event)
    db.session.commit()

    flash(f"Event '{title}' uploaded successfully!")
    return redirect(url_for('admin_dashboard'))

@app.route('/upload_leader', methods=['POST'])
def upload_leader():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    name = request.form['name']
    position = request.form['position']
    motto = request.form['motto']
    phone = request.form['phone']
    email = request.form['email']
    image = request.files['image']
    filename = secure_filename(image.filename)

    path = 'static/images/people'
    os.makedirs(path, exist_ok=True)
    image.save(os.path.join(path, filename))

    leader = Leader(name=name, position=position, motto=motto,
                    phone=phone, email=email, image_filename=filename)
    db.session.add(leader)
    db.session.commit()

    flash(f"Leader '{name}' uploaded successfully!")
    return redirect(url_for('admin_dashboard'))

# Delete Routes
@app.route('/delete_sermon/<filename>', methods=['POST'])
def delete_sermon(filename):
    path = os.path.join(app.config['UPLOAD_SERMONS'], filename)
    if os.path.exists(path):
        os.remove(path)
        flash(f"Sermon '{filename}' deleted.")
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_poster/<filename>', methods=['POST'])
def delete_poster(filename):
    path = os.path.join(app.config['UPLOAD_POSTERS'], filename)
    if os.path.exists(path):
        os.remove(path)
        flash(f"Poster '{filename}' deleted.")
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_leader/<int:leader_id>', methods=['POST'])
def delete_leader(leader_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    leader = Leader.query.get_or_404(leader_id)
    image_path = os.path.join('static/images/people', leader.image_filename)
    if os.path.exists(image_path):
        os.remove(image_path)

    db.session.delete(leader)
    db.session.commit()
    flash(f"Leader '{leader.name}' removed.")
    return redirect(url_for('admin_dashboard'))
    
    
@app.route('/delete_message/<int:message_id>', methods=['POST'])
def delete_message(message_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    msg = Message.query.get_or_404(message_id)
    db.session.delete(msg)
    db.session.commit()
    flash("Message deleted.")
    return redirect(url_for('admin_dashboard'))

@app.route('/archive_message/<int:message_id>', methods=['POST'])
def archive_message(message_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    msg = Message.query.get_or_404(message_id)
    msg.is_archived = True
    db.session.commit()
    flash("Message archived.")
    return redirect(url_for('admin_dashboard'))
    
# Run the app
if __name__ == '__main__':
    app.run(debug=True)