from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SelectField, BooleanField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from wtforms.widgets import TextArea


class UserForm(FlaskForm):
    """Form for creating and editing users"""
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=50, message='Username must be between 3 and 50 characters')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    
    first_name = StringField('First Name', validators=[
        DataRequired(message='First name is required'),
        Length(max=50, message='First name must be less than 50 characters')
    ])
    
    last_name = StringField('Last Name', validators=[
        DataRequired(message='Last name is required'),
        Length(max=50, message='Last name must be less than 50 characters')
    ])
    
    role = SelectField('Role', choices=[
        ('', 'Select Role'),
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin')
    ], validators=[DataRequired(message='Please select a role')])
    
    password = PasswordField('Password', validators=[
        Optional(),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        Optional(),
        EqualTo('password', message='Passwords must match')
    ])
    
    is_active = BooleanField('Active Status', default=True)


class EventForm(FlaskForm):
    """Form for creating and editing events"""
    title = StringField('Event Title', validators=[
        DataRequired(message='Title is required'),
        Length(max=200, message='Title must be less than 200 characters')
    ])
    
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=1000, message='Description must be less than 1000 characters')
    ])
    
    event_date = StringField('Event Date', validators=[
        DataRequired(message='Event date is required')
    ])
    
    event_time = StringField('Event Time', validators=[
        Optional()
    ])
    
    location = StringField('Location', validators=[
        Optional(),
        Length(max=200, message='Location must be less than 200 characters')
    ])
    
    is_active = BooleanField('Active Status', default=True)


class NoteForm(FlaskForm):
    """Form for uploading notes"""
    title = StringField('Note Title', validators=[
        DataRequired(message='Title is required'),
        Length(max=200, message='Title must be less than 200 characters')
    ])
    
    course_id = SelectField('Course', validators=[
        DataRequired(message='Course is required')
    ], coerce=int)
    
    content = TextAreaField('Content/Description', validators=[
        Optional(),
        Length(max=1000, message='Content must be less than 1000 characters')
    ])
    
    topic = StringField('Topic', validators=[
        Optional(),
        Length(max=100, message='Topic must be less than 100 characters')
    ])
    
    chapter = StringField('Chapter', validators=[
        Optional(),
        Length(max=100, message='Chapter must be less than 100 characters')
    ])
    
    uploaded_file = FileField('Upload File', validators=[
        FileRequired(message='Please select a file to upload'),
        FileAllowed(['pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx'], 
                   message='Only PDF, DOC, DOCX, TXT, PPT, and PPTX files are allowed')
    ])
    
    is_active = BooleanField('Active Status', default=True)
