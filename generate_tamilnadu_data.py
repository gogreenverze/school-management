"""
Script to generate Tamil Nadu specific data for the School Management System.
This includes Tamil names, schools, and all education boards in India.
"""
import os
import random
from datetime import datetime, timedelta, date
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models.user import User, AdminProfile, TeacherProfile, ParentProfile, StudentProfile
from app.models.academic_structure import Board, Standard, Section
from app.models.attendance import Class, Sport

# Tamil Nadu standard names
tn_standards = [
    {'name': 'LKG', 'description': 'Lower Kindergarten'},
    {'name': 'UKG', 'description': 'Upper Kindergarten'},
    {'name': 'Standard 1', 'description': 'First Standard'},
    {'name': 'Standard 2', 'description': 'Second Standard'},
    {'name': 'Standard 3', 'description': 'Third Standard'},
    {'name': 'Standard 4', 'description': 'Fourth Standard'},
    {'name': 'Standard 5', 'description': 'Fifth Standard'},
    {'name': 'Standard 6', 'description': 'Sixth Standard'},
    {'name': 'Standard 7', 'description': 'Seventh Standard'},
    {'name': 'Standard 8', 'description': 'Eighth Standard'},
    {'name': 'Standard 9', 'description': 'Ninth Standard'},
    {'name': 'Standard 10', 'description': 'Tenth Standard (SSLC)'},
    {'name': 'Standard 11', 'description': 'Eleventh Standard (Higher Secondary First Year)'},
    {'name': 'Standard 12', 'description': 'Twelfth Standard (Higher Secondary Second Year)'}
]

# Section names
section_names = ['A', 'B', 'C', 'D', 'E', 'F']

# Subjects for different standards
primary_subjects = ['Tamil', 'English', 'Mathematics', 'Environmental Science', 'General Knowledge']
middle_subjects = ['Tamil', 'English', 'Mathematics', 'Science', 'Social Science', 'Hindi/Sanskrit/French']
high_subjects = ['Tamil', 'English', 'Mathematics', 'Science', 'Social Science', 'Hindi/Sanskrit/French', 'Computer Science']
higher_secondary_groups = [
    'Pure Science (Physics, Chemistry, Mathematics, Biology)',
    'Computer Science (Physics, Chemistry, Mathematics, Computer Science)',
    'Commerce (Accountancy, Commerce, Economics, Computer Applications)',
    'Arts (History, Geography, Political Science, Economics)',
    'Vocational (Automobile, Electronics, IT, Agriculture)'
]

# Sports offered in Tamil Nadu schools
sports_list = [
    {'name': 'Cricket', 'category': 'Team Sport'},
    {'name': 'Football', 'category': 'Team Sport'},
    {'name': 'Volleyball', 'category': 'Team Sport'},
    {'name': 'Basketball', 'category': 'Team Sport'},
    {'name': 'Kabaddi', 'category': 'Team Sport'},
    {'name': 'Kho Kho', 'category': 'Team Sport'},
    {'name': 'Badminton', 'category': 'Racquet Sport'},
    {'name': 'Table Tennis', 'category': 'Racquet Sport'},
    {'name': 'Tennis', 'category': 'Racquet Sport'},
    {'name': 'Athletics', 'category': 'Track and Field'},
    {'name': 'Swimming', 'category': 'Aquatics'},
    {'name': 'Karate', 'category': 'Martial Arts'},
    {'name': 'Silambam', 'category': 'Martial Arts'},
    {'name': 'Chess', 'category': 'Board Game'},
    {'name': 'Carrom', 'category': 'Board Game'},
    {'name': 'Yoga', 'category': 'Fitness'}
]

# Teacher qualifications
teacher_qualifications = [
    'B.Ed., M.A. Tamil',
    'B.Ed., M.Sc. Mathematics',
    'B.Ed., M.Sc. Physics',
    'B.Ed., M.Sc. Chemistry',
    'B.Ed., M.Sc. Biology',
    'B.Ed., M.A. English',
    'B.Ed., M.A. History',
    'B.Ed., M.A. Geography',
    'B.Ed., M.Com.',
    'B.Ed., M.C.A.',
    'B.P.Ed., M.P.Ed.',
    'B.Ed., M.A. Economics',
    'B.Ed., M.A. Political Science',
    'B.Ed., M.Sc. Computer Science',
    'B.Ed., M.A. Hindi',
    'B.Ed., M.A. Sanskrit',
    'B.Ed., M.A. French',
    'B.F.A., M.F.A.',
    'B.Mus., M.Mus.',
    'D.T.Ed., B.Ed.'
]

# Blood groups
blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

# Tamil Nadu specific data
tn_districts = [
    'Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem', 'Tirunelveli',
    'Tiruppur', 'Erode', 'Vellore', 'Thoothukkudi', 'Dindigul', 'Thanjavur',
    'Ranipet', 'Sivakasi', 'Karur', 'Udhagamandalam', 'Hosur', 'Nagercoil',
    'Kanchipuram', 'Kumarapalayam', 'Karaikkudi', 'Neyveli', 'Cuddalore',
    'Kumbakonam', 'Tiruvannamalai', 'Pollachi', 'Rajapalayam', 'Gudiyatham',
    'Pudukkottai', 'Vaniyambadi', 'Ambur', 'Nagapattinam'
]

# Common Tamil surnames
tamil_surnames = [
    'Murugan', 'Rajan', 'Kumar', 'Krishnan', 'Sundaram', 'Pillai', 'Nadar',
    'Gounder', 'Naidu', 'Chettiar', 'Thevar', 'Iyer', 'Iyengar', 'Sharma',
    'Pandian', 'Subramanian', 'Venkatesh', 'Natarajan', 'Annamalai', 'Palaniswamy',
    'Shanmugam', 'Kannan', 'Chandran', 'Selvaraj', 'Venkatesan', 'Ramachandran',
    'Durairaj', 'Saravanan', 'Balasubramanian', 'Ganesan', 'Muthusamy', 'Arumugam'
]

# Common Tamil first names
tamil_male_first_names = [
    'Arun', 'Bala', 'Chandru', 'Dinesh', 'Ezhil', 'Ganesh', 'Hari', 'Inba',
    'Jagan', 'Karthik', 'Lokesh', 'Madhan', 'Naveen', 'Prabhu', 'Rajesh',
    'Senthil', 'Tamil', 'Udhay', 'Vijay', 'Yuvan', 'Anand', 'Bharath',
    'Deepak', 'Gopal', 'Harish', 'Karthikeyan', 'Manoj', 'Nandha', 'Prasad',
    'Ramesh', 'Sathish', 'Surya', 'Vignesh', 'Ashwin', 'Balaji', 'Charan'
]

tamil_female_first_names = [
    'Anitha', 'Bhavani', 'Chitra', 'Divya', 'Eswari', 'Geetha', 'Hema',
    'Indhu', 'Janani', 'Kala', 'Lakshmi', 'Meena', 'Nithya', 'Priya',
    'Radha', 'Saranya', 'Tamilselvi', 'Uma', 'Vani', 'Yamuna', 'Abinaya',
    'Brindha', 'Deepika', 'Gayathri', 'Hari Priya', 'Kalpana', 'Malathi',
    'Nirmala', 'Pavithra', 'Ramya', 'Sangeetha', 'Thenmozhi', 'Vanitha'
]

# All education boards in India
indian_boards = [
    {
        'name': 'Tamil Nadu State Board of School Examination',
        'code': 'TNSBSE',
        'description': 'The official board of education for the state of Tamil Nadu',
        'state': 'Tamil Nadu'
    },
    {
        'name': 'Central Board of Secondary Education',
        'code': 'CBSE',
        'description': 'National level board of education in India for public and private schools',
        'state': 'All India'
    },
    {
        'name': 'Indian Certificate of Secondary Education',
        'code': 'ICSE',
        'description': 'Private board of secondary education in India',
        'state': 'All India'
    },
    {
        'name': 'International Baccalaureate',
        'code': 'IB',
        'description': 'International education foundation with programs for students aged 3 to 19',
        'state': 'International'
    },
    {
        'name': 'National Institute of Open Schooling',
        'code': 'NIOS',
        'description': 'Board for distance education at school level in India',
        'state': 'All India'
    },
    {
        'name': 'Andhra Pradesh Board of Secondary Education',
        'code': 'APBSE',
        'description': 'State board of education for Andhra Pradesh',
        'state': 'Andhra Pradesh'
    },
    {
        'name': 'Assam Board of Secondary Education',
        'code': 'SEBA',
        'description': 'State board of education for Assam',
        'state': 'Assam'
    },
    {
        'name': 'Bihar School Examination Board',
        'code': 'BSEB',
        'description': 'State board of education for Bihar',
        'state': 'Bihar'
    },
    {
        'name': 'Chhattisgarh Board of Secondary Education',
        'code': 'CGBSE',
        'description': 'State board of education for Chhattisgarh',
        'state': 'Chhattisgarh'
    },
    {
        'name': 'Goa Board of Secondary & Higher Secondary Education',
        'code': 'GBSHSE',
        'description': 'State board of education for Goa',
        'state': 'Goa'
    },
    {
        'name': 'Gujarat Secondary and Higher Secondary Education Board',
        'code': 'GSEB',
        'description': 'State board of education for Gujarat',
        'state': 'Gujarat'
    },
    {
        'name': 'Haryana Board of School Education',
        'code': 'HBSE',
        'description': 'State board of education for Haryana',
        'state': 'Haryana'
    },
    {
        'name': 'Himachal Pradesh Board of School Education',
        'code': 'HPBOSE',
        'description': 'State board of education for Himachal Pradesh',
        'state': 'Himachal Pradesh'
    },
    {
        'name': 'Jammu and Kashmir State Board of School Education',
        'code': 'JKBOSE',
        'description': 'State board of education for Jammu and Kashmir',
        'state': 'Jammu and Kashmir'
    },
    {
        'name': 'Jharkhand Academic Council',
        'code': 'JAC',
        'description': 'State board of education for Jharkhand',
        'state': 'Jharkhand'
    },
    {
        'name': 'Karnataka Secondary Education Examination Board',
        'code': 'KSEEB',
        'description': 'State board of education for Karnataka',
        'state': 'Karnataka'
    },
    {
        'name': 'Kerala Board of Public Examinations',
        'code': 'KBPE',
        'description': 'State board of education for Kerala',
        'state': 'Kerala'
    },
    {
        'name': 'Maharashtra State Board of Secondary and Higher Secondary Education',
        'code': 'MSBSHSE',
        'description': 'State board of education for Maharashtra',
        'state': 'Maharashtra'
    },
    {
        'name': 'Manipur Board of Secondary Education',
        'code': 'BOSEM',
        'description': 'State board of education for Manipur',
        'state': 'Manipur'
    },
    {
        'name': 'Meghalaya Board of School Education',
        'code': 'MBOSE',
        'description': 'State board of education for Meghalaya',
        'state': 'Meghalaya'
    },
    {
        'name': 'Mizoram Board of School Education',
        'code': 'MBSE',
        'description': 'State board of education for Mizoram',
        'state': 'Mizoram'
    },
    {
        'name': 'Nagaland Board of School Education',
        'code': 'NBSE',
        'description': 'State board of education for Nagaland',
        'state': 'Nagaland'
    },
    {
        'name': 'Odisha Board of Secondary Education',
        'code': 'BSE',
        'description': 'State board of education for Odisha',
        'state': 'Odisha'
    },
    {
        'name': 'Punjab School Education Board',
        'code': 'PSEB',
        'description': 'State board of education for Punjab',
        'state': 'Punjab'
    },
    {
        'name': 'Rajasthan Board of Secondary Education',
        'code': 'RBSE',
        'description': 'State board of education for Rajasthan',
        'state': 'Rajasthan'
    },
    {
        'name': 'Sikkim State Human Resource Development Department',
        'code': 'HRDD',
        'description': 'State board of education for Sikkim',
        'state': 'Sikkim'
    },
    {
        'name': 'Telangana Board of Secondary Education',
        'code': 'TBSE',
        'description': 'State board of education for Telangana',
        'state': 'Telangana'
    },
    {
        'name': 'Tripura Board of Secondary Education',
        'code': 'TBSE',
        'description': 'State board of education for Tripura',
        'state': 'Tripura'
    },
    {
        'name': 'Uttar Pradesh Board of High School and Intermediate Education',
        'code': 'UPMSP',
        'description': 'State board of education for Uttar Pradesh',
        'state': 'Uttar Pradesh'
    },
    {
        'name': 'Uttarakhand Board of School Education',
        'code': 'UBSE',
        'description': 'State board of education for Uttarakhand',
        'state': 'Uttarakhand'
    },
    {
        'name': 'West Bengal Board of Secondary Education',
        'code': 'WBBSE',
        'description': 'State board of education for West Bengal',
        'state': 'West Bengal'
    }
]
