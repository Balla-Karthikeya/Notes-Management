from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import random
from flask import make_response
from reportlab.pdfgen import canvas
from io import BytesIO
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk
from config import Config
import uuid

nltk.download('punkt')
nltk.download('punkt_tab')

app = Flask(__name__)

app.config.from_object(Config)

mysql = MySQL(app)

app.config['MAIL_USE_TLS'] = True

mail = Mail(app)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(
            request.form['password']
        )

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM users WHERE email=%s",
            [email]
        )

        existing_user = cur.fetchone()

        if existing_user:
            flash("Email already registered", "danger")
            return redirect(url_for('register'))

        otp = random.randint(100000, 999999)

        session['otp'] = str(otp)
        session['username'] = username
        session['email'] = email
        session['password'] = password

        msg = Message(
            "OTP Verification",
            sender=app.config['MAIL_USERNAME'],
            recipients=[email]
        )

        msg.body = f"""
Hello {username},

Your OTP for Notes Management System is:

{otp}

Thank You.
        """

        mail.send(msg)

        flash("OTP Sent Successfully", "success")

        return redirect(url_for('verify_otp'))

    return render_template('register.html')


@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():

    if request.method == 'POST':

        entered_otp = request.form['otp']

        if entered_otp == session.get('otp'):

            cur = mysql.connection.cursor()

            cur.execute(
                """
                INSERT INTO users(username,email,password)
                VALUES(%s,%s,%s)
                """,
                (
                    session['username'],
                    session['email'],
                    session['password']
                )
            )

            mysql.connection.commit()
            cur.close()

            session.pop('otp', None)

            flash(
                "Registration Successful. Please Login.",
                "success"
            )

            return redirect(url_for('login'))

        flash("Invalid OTP", "danger")

    return render_template('verify_otp.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM users WHERE email=%s",
            [email]
        )

        user = cur.fetchone()

        cur.close()

        if user:

            if check_password_hash(
                user[3],
                password
            ):

                session['user_id'] = user[0]
                session['username'] = user[1]

                flash(
                    "Login Successful",
                    "success"
                )

                return redirect(
                    url_for('dashboard')
                )

        flash(
            "Invalid Email or Password",
            "danger"
        )

    return render_template('login.html')


@app.route('/logout')
def logout():

    session.clear()

    flash(
        "Logged Out Successfully",
        "info"
    )

    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT *
        FROM notes
        WHERE user_id=%s
        AND is_deleted=0
        ORDER BY
            is_pinned DESC,
            is_favorite DESC,
            created_at DESC
        """,
        [session['user_id']]
    )

    notes = cur.fetchall()

    total_notes = len(notes)

    cur.execute(
        """
        SELECT *
        FROM activity_log
        WHERE user_id=%s
        ORDER BY created_at DESC
        LIMIT 3
        """,
        [session['user_id']]
    )

    activities = cur.fetchall()

    cur.close()

    return render_template(
        'dashboard.html',
        notes=notes,
        total_notes=total_notes,
        activities=activities
    )

@app.route('/addnote', methods=['GET', 'POST'])
def addnote():


 if request.method == 'POST':

    title = request.form['title']
    category = request.form['category']
    content = request.form['content']

    cur = mysql.connection.cursor()

    cur.execute(
        """
        INSERT INTO notes
        (
            title,
            content,
            category,
            user_id
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s
        )
        """,
        (
            title,
            content,
            category,
            session['user_id']
        )
    )

    mysql.connection.commit()

    cur.execute(
        """
        INSERT INTO activity_log
        (
            user_id,
            activity
        )
        VALUES
        (
            %s,
            %s
        )
        """,
        (
            session['user_id'],
            f"Added {title}"
        )
    )

    mysql.connection.commit()

    cur.close()

    flash(
        "Note Added Successfully",
        "success"
    )

    return redirect(
        url_for('dashboard')
    )

 return render_template(
    'add_note.html'
)

@app.route('/viewnote/<int:id>')
def viewnote(id):

    if 'user_id' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT *
        FROM notes
        WHERE id=%s
        AND user_id=%s
        """,
        (
            id,
            session['user_id']
        )
    )

    note = cur.fetchone()

    cur.close()

    return render_template(
        'view_note.html',
        note=note
    )

@app.route('/editnote/<int:id>', methods=['GET', 'POST'])
def editnote(id):

    if 'user_id' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    if request.method == 'POST':

        title = request.form['title']
        category = request.form['category']
        content = request.form['content']

        cur.execute(
            """
            UPDATE notes
            SET title=%s,
                category=%s,
                content=%s
            WHERE id=%s
            AND user_id=%s
            """,
            (
                title,
                category,
                content,
                id,
                session['user_id']
            )
        )

        mysql.connection.commit()

        cur.execute(
            """
            INSERT INTO activity_log
            (
                user_id,
                activity
            )
            VALUES
            (
                %s,
                %s
            )
            """,
            (
                session['user_id'],
                f"Edited {title}"
            )
        )

        mysql.connection.commit()

        flash(
            "Note Updated Successfully",
            "success"
        )

        cur.close()

        return redirect(
            url_for('dashboard')
        )

    cur.execute(
        """
        SELECT *
        FROM notes
        WHERE id=%s
        AND user_id=%s
        """,
        (
            id,
            session['user_id']
        )
    )

    note = cur.fetchone()

    cur.close()

    return render_template(
        'edit_note.html',
        note=note
    )



@app.route('/deletenote/<int:id>')
def deletenote(id):

    if 'user_id' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute(
        """
        UPDATE notes
        SET is_deleted=1
        WHERE id=%s
        AND user_id=%s
        """,
        (
            id,
            session['user_id']
        )
    )

    mysql.connection.commit()

    cur.close()

    flash(
        "Note moved to Trash",
        "warning"
    )

    return redirect('/dashboard')


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():

    if request.method == 'POST':

        email = request.form['email']

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM users WHERE email=%s",
            [email]
        )

        user = cur.fetchone()

        cur.close()

        if not user:
            flash("Email not found", "danger")
            return redirect(url_for('forgot_password'))

        otp = random.randint(100000, 999999)

        session['reset_email'] = email
        session['reset_otp'] = str(otp)

        msg = Message(
            "Password Reset OTP",
            sender=app.config['MAIL_USERNAME'],
            recipients=[email]
        )

        msg.body = f"""
Your Password Reset OTP is:

{otp}

Do not share this OTP.
        """

        mail.send(msg)

        flash("OTP sent successfully", "success")

        return redirect(url_for('verify_reset_otp'))

    return render_template('forgot_password.html')

@app.route('/verify-reset-otp', methods=['GET', 'POST'])
def verify_reset_otp():

    if request.method == 'POST':

        otp = request.form['otp']

        if otp == session.get('reset_otp'):

            return redirect(url_for('reset_password'))

        flash("Invalid OTP", "danger")

    return render_template('verify_reset_otp.html')


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():

    if request.method == 'POST':

        password = generate_password_hash(
            request.form['password']
        )

        cur = mysql.connection.cursor()

        cur.execute(
            """
            UPDATE users
            SET password=%s
            WHERE email=%s
            """,
            (
                password,
                session['reset_email']
            )
        )

        mysql.connection.commit()
        cur.close()

        session.pop('reset_email', None)
        session.pop('reset_otp', None)

        flash(
            "Password Updated Successfully",
            "success"
        )

        return redirect(url_for('login'))

    return render_template('reset_password.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/profile')
def profile():

    if 'user_id' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT username, email FROM users WHERE id=%s",
        [session['user_id']]
    )

    user = cur.fetchone()

    cur.execute(
        "SELECT COUNT(*) FROM notes WHERE user_id=%s",
        [session['user_id']]
    )

    total_notes = cur.fetchone()[0]

    cur.close()

    return render_template(
        'profile.html',
        user=user,
        total_notes=total_notes
    )

@app.route('/change-password', methods=['GET', 'POST'])
def change_password():

    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':

        current_password = request.form['current_password']
        new_password = request.form['new_password']

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT password FROM users WHERE id=%s",
            [session['user_id']]
        )

        user = cur.fetchone()

        if check_password_hash(user[0], current_password):

            hashed_password = generate_password_hash(new_password)

            cur.execute(
                "UPDATE users SET password=%s WHERE id=%s",
                (hashed_password, session['user_id'])
            )

            mysql.connection.commit()

            flash(
                'Password updated successfully',
                'success'
            )

            return redirect('/profile')

        else:

            flash(
                'Current password is incorrect',
                'danger'
            )

        cur.close()

    return render_template('change_password.html')


@app.route('/toggle-pin/<int:id>')
def toggle_pin(id):

    if 'user_id' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute(
        """
        UPDATE notes
        SET is_pinned =
        CASE
            WHEN is_pinned = 1 THEN 0
            ELSE 1
        END
        WHERE id=%s
        AND user_id=%s
        """,
        (id, session['user_id'])
    )

    mysql.connection.commit()

    cur.close()

    return redirect('/dashboard')

@app.route('/toggle-favorite/<int:id>')
def toggle_favorite(id):

    if 'user_id' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute(
        """
        UPDATE notes
        SET is_favorite =
        CASE
            WHEN is_favorite = 1 THEN 0
            ELSE 1
        END
        WHERE id=%s
        AND user_id=%s
        """,
        (id, session['user_id'])
    )

    mysql.connection.commit()

    cur.close()

    return redirect('/dashboard')

@app.route('/trash')
def trash():

    if 'user_id' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT *
        FROM notes
        WHERE user_id=%s
        AND is_deleted=1
        ORDER BY created_at DESC
        """,
        [session['user_id']]
    )

    notes = cur.fetchall()

    cur.close()

    return render_template(
        'trash.html',
        notes=notes
    )

@app.route('/restore-note/<int:id>')
def restore_note(id):

    if 'user_id' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute(
        """
        UPDATE notes
        SET is_deleted=0
        WHERE id=%s
        AND user_id=%s
        """,
        (
            id,
            session['user_id']
        )
    )

    mysql.connection.commit()

    cur.close()

    flash(
        "Note restored successfully",
        "success"
    )

    return redirect('/trash')

@app.route('/delete-permanently/<int:id>')
def delete_permanently(id):

    if 'user_id' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT title
        FROM notes
        WHERE id=%s
        AND user_id=%s
        """,
        (
            id,
            session['user_id']
        )
    )

    note = cur.fetchone()

    if note:

        note_title = note[0]

        cur.execute(
            """
            DELETE FROM notes
            WHERE id=%s
            AND user_id=%s
            """,
            (
                id,
                session['user_id']
            )
        )

        mysql.connection.commit()

        cur.execute(
            """
            INSERT INTO activity_log
            (
                user_id,
                activity
            )
            VALUES
            (
                %s,
                %s
            )
            """,
            (
                session['user_id'],
                f"Deleted {note_title}"
            )
        )

        mysql.connection.commit()

    cur.close()

    flash(
        "Note deleted permanently",
        "danger"
    )

    return redirect(
        url_for('trash')
    )

@app.route('/export-pdf/<int:id>')
def export_pdf(id):

    if 'user_id' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT title, content, category
        FROM notes
        WHERE id=%s
        AND user_id=%s
        """,
        (id, session['user_id'])
    )

    note = cur.fetchone()

    cur.close()

    if not note:
        return "Note not found"

    from io import BytesIO
    from flask import make_response
    from reportlab.pdfgen import canvas

    buffer = BytesIO()

    pdf = canvas.Canvas(buffer)

    pdf.setTitle(note[0])

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, 800, note[0])

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 770, f"Category: {note[2]}")

    y = 730

    for line in note[1].split('\n'):

        pdf.drawString(50, y, line)

        y -= 20

    pdf.save()

    buffer.seek(0)

    response = make_response(buffer.getvalue())

    response.headers['Content-Type'] = 'application/pdf'

    response.headers[
        'Content-Disposition'
    ] = f'attachment; filename={note[0]}.pdf'

    return response


@app.route('/summarize/<int:id>')
def summarize_note(id):

    if 'user_id' not in session:
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT *
        FROM notes
        WHERE id=%s
        AND user_id=%s
        """,
        (id, session['user_id'])
    )

    note = cur.fetchone()

    cur.close()

    parser = PlaintextParser.from_string(
        note[2],
        Tokenizer("english")
    )

    summarizer = LsaSummarizer()

    summary = ""

    for sentence in summarizer(parser.document, 5):
        summary += str(sentence) + " "

    return render_template(
        'summary.html',
        note=note,
        summary=summary
    )

@app.route('/share-note/<int:id>')
def share_note(id):

    if 'user_id' not in session:
        return redirect('/login')

    token = str(uuid.uuid4())

    cur = mysql.connection.cursor()

    cur.execute(
        """
        UPDATE notes
        SET share_token=%s
        WHERE id=%s
        AND user_id=%s
        """,
        (
            token,
            id,
            session['user_id']
        )
    )

    mysql.connection.commit()

    cur.close()

    share_link = request.host_url + "shared/" + token

    return render_template(
      'share_note.html',
       share_link=share_link
)

@app.route('/shared/<token>')
def shared_note(token):

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT *
        FROM notes
        WHERE share_token=%s
        """,
        [token]
    )

    note = cur.fetchone()

    cur.close()

    if not note:
        return "Invalid Share Link"

    return render_template(
        'shared_note.html',
        note=note
    )




if __name__ == '__main__':
    app.run(debug=True)