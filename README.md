# 📝 Notes Management System

A full-stack **Notes Management System** built using **Flask**, **Python**, **MySQL**, **HTML**, **CSS**, **Bootstrap**, and **Jinja2**. The application enables users to securely create, organize, edit, share, and manage personal notes through a modern, responsive, and user-friendly interface.

---

## 🚀 Features

* 👤 User Registration & Login
* 🔒 Secure Password Authentication
* 📧 Email OTP Verification
* 🔑 Forgot Password & Reset Password
* 👤 User Profile Management
* 🔐 Change Password
* 📝 Create, Edit, View & Delete Notes
* 🗑️ Trash Bin with Restore & Permanent Delete
* 📂 Note Categorization
* 🔍 Search & Filter Notes
* 📌 Pin Important Notes
* ⭐ Mark Notes as Favorites
* 📄 Export Individual Notes as PDF
* ✍️ Rich Text Editor (CKEditor)
* 🤖 AI-Based Note Summarization
* 🤝 Share Notes via Shareable Link
* 🌙 Dark Mode
* 📊 Dashboard with Recent Activity
* 📖 Word Count, Character Count & Reading Time
* 📱 Fully Responsive User Interface

---

## 🛠️ Tech Stack

### Backend

* Python
* Flask

### Frontend

* HTML5
* CSS3
* Bootstrap 5
* Jinja2
* JavaScript

### Database

* MySQL

### Libraries

* Flask-Mail
* ReportLab
* CKEditor
* Sumy
* NLTK

### Tools

* Git
* GitHub
* VS Code

---

## 📂 Project Structure

```text
Notes_Management/
│
├── static/
│   ├── css/
│   ├── images/
│   └── uploads/
│
├── templates/
│   ├── about.html
│   ├── add_note.html
│   ├── base.html
│   ├── change_password.html
│   ├── dashboard.html
│   ├── edit_note.html
│   ├── forgot_password.html
│   ├── index.html
│   ├── login.html
│   ├── profile.html
│   ├── register.html
│   ├── reset_password.html
│   ├── share_note.html
│   ├── shared_note.html
│   ├── summary.html
│   ├── trash.html
│   ├── verify_otp.html
│   ├── verify_reset_otp.html
│   └── view_note.html
│
├── app.py
├── config.py
├── database.sql
├── requirements.txt
├── README.md
├── .env.example
└── .gitignore
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/Balla-Karthikeya/Notes-Management.git
cd Notes-Management
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file and add:

```env
SECRET_KEY=your_secret_key
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

### Configure Database

* Create a MySQL database.
* Import `database.sql`.
* Update database credentials in `config.py`.

### Run Application

```bash
python app.py
```

Visit:

```text
http://127.0.0.1:5000
```

---

## 📸 Screenshots

* Home Page
* Login Page
* Dashboard
* Add Note
* View Note
* Profile
* Trash
* AI Summary
* Share Note

(Add screenshots here)

---

## 🚀 Future Improvements

* ☁️ Cloud Deployment
* 📎 File Attachments
* 🏷️ Custom Tags
* 🔔 Push Notifications
* 📱 Mobile Application
* 🔄 Real-time Collaboration

---

## 👨‍💻 Author

**Karthikeya Balla**

GitHub: https://github.com/Balla-Karthikeya

---

## ⭐ Support

If you found this project useful, consider giving it a **⭐ Star** on GitHub.

---

## 📜 License

This project is intended for educational and learning purposes.
