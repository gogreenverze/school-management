# Git Setup and Deployment Instructions

This document provides detailed instructions for setting up the School Management System using Git, as well as deploying it to a new environment.

## Setting Up a GitHub Repository

1. **Create a GitHub account** (if you don't already have one):
   - Go to [GitHub](https://github.com/) and sign up for an account.

2. **Create a new repository**:
   - Click on the "+" icon in the top right corner of GitHub and select "New repository".
   - Name your repository (e.g., "school-management").
   - Add a description (optional).
   - Choose whether the repository should be public or private.
   - Do NOT initialize the repository with a README, .gitignore, or license (since we already have these files).
   - Click "Create repository".

3. **Push your local repository to GitHub**:
   - After creating the repository, GitHub will show instructions for pushing an existing repository.
   - Run the following commands in your terminal (replace `yourusername` with your GitHub username):

   ```bash
   git remote add origin https://github.com/yourusername/school-management.git
   git branch -M main
   git push -u origin main
   ```

## Cloning and Running the Application

### Prerequisites

- Python 3.8 or higher
- Git
- pip (Python package installer)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/school-management.git
cd school-management
```

### Step 2: Set Up the Environment

You can either use the setup script or follow the manual setup process:

#### Option 1: Using the Setup Script

```bash
python setup.py
```

This script will:
- Create a virtual environment
- Create a .env file with default settings
- Create the instance directory
- Install dependencies
- Initialize the database

After running the script, activate the virtual environment:
- On Windows: `venv\Scripts\activate`
- On macOS/Linux: `source venv/bin/activate`

#### Option 2: Manual Setup

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a .env file** with the following content:
   ```
   SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///instance/school.db
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=true
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-email-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   ```

5. **Create the instance directory**:
   ```bash
   mkdir -p instance
   ```

6. **Initialize the database**:
   ```bash
   python create_db.py
   ```

### Step 3: Run the Application

```bash
python run.py
```

The application will be available at http://127.0.0.1:5007

### Default Login Credentials

- **Admin**: Username: `admin`, Password: `admin123`
- **Teacher**: Username: `teacher1`, Password: `teacher123`
- **Student**: Username: `student1`, Password: `student123`

## Updating the Application

To update your local copy of the application with the latest changes from GitHub:

```bash
git pull origin main
```

If there are database schema changes, you may need to run migrations:

```bash
flask db upgrade
```

## Troubleshooting

### Database Issues

If you encounter database issues, you can reset the database:

```bash
python reset_db.py
```

### Dependency Issues

If you encounter issues with dependencies, try updating them:

```bash
pip install --upgrade -r requirements.txt
```

### Environment Issues

Make sure your .env file contains all the necessary environment variables and that they are correctly set.

## Contributing to the Project

1. **Fork the repository** on GitHub.
2. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/school-management.git
   ```
3. **Create a new branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes** and commit them:
   ```bash
   git add .
   git commit -m "Add your feature description"
   ```
5. **Push to your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Create a Pull Request** on GitHub.

## Deployment to Production

For production deployment, consider the following:

1. Use a production-ready database like PostgreSQL instead of SQLite.
2. Set up a proper web server like Nginx or Apache with a WSGI server like Gunicorn.
3. Use environment variables for sensitive information.
4. Set `debug=False` in the Flask application.
5. Consider using a service like Docker for containerization.

A basic production setup might look like:

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn --bind 0.0.0.0:8000 "app:create_app()"
```

Then configure Nginx to proxy requests to Gunicorn.
