from flask import Flask,request,render_template,redirect, send_file,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import uuid
import dotenv

dotenv.load_dotenv()

app=Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

login_manager=LoginManager(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    password=db.Column(db.String(255),nullable=False)  # Increased from 60 to 255
    files=db.relationship('File',backref='User',lazy=True)


class File(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    file_id=db.Column(db.String(40),nullable=False,unique=True)
    file_name=db.Column(db.String(100),nullable=False)
    filepath=db.Column(db.String(200),nullable=False)
    share_token=db.Column(db.String(40),nullable=True,unique=True)  # For sharing files

with app.app_context():
    # Only drop tables if you need to reset the database schema
    # Uncomment the next line ONLY if you need to reset the database for new fields:
    # db.drop_all()  # Database now has share_token field - don't delete data!
    db.create_all()

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('landingpage.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        user=User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password,password):
            login_user(user)
            flash('Login successful! Welcome back.', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid email or password. Please try again.', 'error')
    return render_template('login.html')

@app.route('/register',methods=['POST','GET'])
def register():
    if request.method=='POST':
        try:
            name=request.form['Name']
            email=request.form['email']
            password=request.form['password']
              # Check if email already exists
            if User.query.filter_by(email=email).first():
                flash('Email already exists! Please use a different email.', 'error')
                return redirect(url_for('register'))
            
            # Generate password hash
            rpassword=generate_password_hash(password)
            
            # Create new user
            user=User(username=name,email=email,password=rpassword)
            db.session.add(user)
            db.session.commit()
            
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'error')
            return redirect(url_for('register'))
            
    return render_template('register.html')

@app.route('/dashboard',methods=['POST','GET'])
@login_required
def dashboard():
    files=File.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html',files=files)

@app.route('/upload',methods=['POST','GET'])
@login_required
def upload():
    if request.method=='POST':
        try:
            if 'file' not in request.files:
                flash('No file selected for upload.', 'warning')
                return redirect(url_for('dashboard'))
            
            file=request.files['file']
            if file.filename == '':
                flash('Please select a file to upload.', 'warning')
                return redirect(url_for('dashboard'))

            filename=secure_filename(file.filename)
            if not filename:
                flash('Invalid filename. Please use a valid file name.', 'error')
                return redirect(url_for('dashboard'))
                
            file_id=str(uuid.uuid4())
            filepath=f"{file_id}_{filename}"
            
            # Save file
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filepath))
            
            # Save to database
            new_file=File(user_id=current_user.id, file_id=file_id, file_name=filename, filepath=filepath)
            db.session.add(new_file)
            db.session.commit()
            
            flash('File uploaded successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Upload failed: {str(e)}', 'error')
            return redirect(url_for('dashboard'))
            
    # This should never be reached since upload form is only on dashboard
    return redirect(url_for('dashboard'))
@app.route('/download/<file_id>', methods=['GET'])
@login_required
def download(file_id):
    try:
        file=File.query.filter_by(file_id=file_id,user_id=current_user.id).first()
        if not file:
            flash('File not found!', 'error')
            return redirect(url_for('dashboard'))
            
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filepath)
        if not os.path.exists(file_path):
            flash('File not found on disk!', 'error')
            return redirect(url_for('dashboard'))
            
        return send_file(file_path, as_attachment=True, download_name=file.file_name)
        
    except Exception as e:
        flash(f'Download failed: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/delete/<file_id>', methods=['POST'])
@login_required
def delete(file_id):
    try:
        file = File.query.filter_by(file_id=file_id, user_id=current_user.id).first()
        if not file:
            flash('File not found!', 'error')
            return redirect(url_for('dashboard'))
            
        # Delete physical file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filepath)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete from database
        db.session.delete(file)
        db.session.commit()
        
        flash('File deleted successfully!', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Delete failed: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/share/<file_id>', methods=['POST'])
@login_required
def share_file(file_id):
    try:
        file = File.query.filter_by(file_id=file_id, user_id=current_user.id).first()
        if not file:
            flash('File not found!', 'error')
            return redirect(url_for('dashboard'))
        
        # Generate share token if not exists
        if not file.share_token:
            file.share_token = str(uuid.uuid4())
            db.session.commit()
        
        # Create share URL
        share_url = url_for('shared_file', share_token=file.share_token, _external=True)
        flash(f'Share link created: {share_url}', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Share failed: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/shared/<share_token>')
def shared_file(share_token):
    try:
        file = File.query.filter_by(share_token=share_token).first()
        if not file:
            flash('Shared file not found or link expired!', 'error')
            return redirect(url_for('home'))
            
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filepath)
        if not os.path.exists(file_path):
            flash('File not found on disk!', 'error')
            return redirect(url_for('home'))
            
        return send_file(file_path, as_attachment=True, download_name=file.file_name)
        
    except Exception as e:
        flash(f'Download failed: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/unshare/<file_id>', methods=['POST'])
@login_required
def unshare_file(file_id):
    try:
        file = File.query.filter_by(file_id=file_id, user_id=current_user.id).first()
        if not file:
            flash('File not found!', 'error')
            return redirect(url_for('dashboard'))
        
        # Remove share token
        file.share_token = None
        db.session.commit()
        
        flash('File unshared successfully!', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Unshare failed: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully!', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Use environment variable for debug mode (False in production)
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    app.run(host=host, port=port, debug=debug_mode)