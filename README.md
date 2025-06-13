# 📁 FileShare - Simple File Sharing App

Upload files, get shareable links, and manage everything in one place! 🚀

## ⚡ Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python app.py

# 3. Open browser
# Go to http://localhost:5000
```

That's it! Your file sharing app is running! 🎉

## 🎮 How to Use

1. **Sign Up** → Create your account
2. **Upload** → Drag & drop any file  
3. **Share** → Get a magic link to send anyone
4. **Manage** → Download, delete, or unshare files

## 🛠️ What's Inside

```
📁 Project Structure
├── app.py              # Main Flask app
├── requirements.txt    # Python packages
├── templates/          # HTML pages
│   ├── landingpage.html   # Welcome page
│   ├── dashboard.html     # File management
│   ├── login.html         # Login page
│   └── register.html      # Sign up page
├── static/dashboard.css   # Styling
└── uploads/            # Your files live here
```



## 🔧 Tech Stack

- **Python Flask** - Web framework
- **PostgreSQL** - Database  
- **Bootstrap** - Pretty UI
- **Flask-Login** - User sessions
- **UUID** - Secure file sharing

## 🚀 Features

- ✅ Secure user accounts
- ✅ File upload/download
- ✅ Shareable links (no account needed)
- ✅ File management dashboard
- ✅ Mobile-friendly design
- ✅ Docker support

## 🎓 For Developers

**Key Files:**
- `app.py` - All the Flask routes and logic
- `templates/dashboard.html` - Main user interface


**Database:**
- Users table (login info)
- Files table (file metadata + share tokens)

**Security:**
- Password hashing with Werkzeug
- UUID-based file IDs and share tokens
- Login required decorators

---

