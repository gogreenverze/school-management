# Flask-Admin Initialization Fix

If you encounter the following error when running the application:

```
Traceback (most recent call last):
  File "/workspaces/school-management/run.py", line 3, in <module>
    app = create_app()
          ^^^^^^^^^^^^
  File "/workspaces/school-management/app/__init__.py", line 62, in create_app
    admin.init_app(app)
  File "/home/codespace/.local/lib/python3.12/site-packages/flask_admin/base.py", line 724, in init_app
    app.register_blueprint(view.create_blueprint(self))
  File "/home/codespace/.local/lib/python3.12/site-packages/flask/scaffold.py", line 50, in wrapper_func
    return f(self, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/codespace/.local/lib/python3.12/site-packages/flask/app.py", line 997, in register_blueprint
    blueprint.register(self, options)
  File "/home/codespace/.local/lib/python3.12/site-packages/flask/blueprints.py", line 310, in register
    raise ValueError(
```

You need to fix the Flask-Admin initialization in the application. The issue is that the Flask-Admin instance is being initialized at the module level with a specific template_mode and URL, but then we're trying to modify its index_view in the `init_admin_views` function after it's already been initialized.

## Fix 1: Update app/__init__.py

1. Open `app/__init__.py`
2. Find the line where `admin` is initialized (around line 19)
3. Change it from:
   ```python
   admin = Admin(name='School Management System', template_mode='bootstrap4', url='/admin_panel', endpoint='admin_panel')
   ```
   to:
   ```python
   admin = None  # Will be initialized in create_app
   ```

4. Find the section where admin is initialized in the `create_app` function (around line 90-93)
5. Change it from:
   ```python
   # Initialize admin views
   from app.routes.admin_views import init_admin_views
   init_admin_views(admin, db)
   admin.init_app(app)
   ```
   to:
   ```python
   # Initialize admin
   global admin
   from app.routes.admin_views import SecureAdminIndexView
   admin = Admin(
       app,
       name='School Management System',
       template_mode='bootstrap4',
       url='/admin_panel',
       endpoint='admin_panel',
       index_view=SecureAdminIndexView()
   )
   
   # Initialize admin views
   from app.routes.admin_views import init_admin_views
   init_admin_views(admin, db)
   ```

## Fix 2: Update app/routes/admin_views.py

1. Open `app/routes/admin_views.py`
2. Find the `init_admin_views` function (around line 126)
3. Remove the line that sets the index_view:
   ```python
   # Override default index view
   admin.index_view = SecureAdminIndexView()
   ```
   So the function should start with:
   ```python
   def init_admin_views(admin, db):
       # Add model views
       admin.add_view(UserModelView(User, db.session, category='Users'))
       ...
   ```

After making these changes, the application should start without errors.

## Why This Fix Works

The issue was that we were trying to modify the Flask-Admin instance after it had already been initialized. By initializing the admin instance with the correct index_view from the start, we avoid this problem.

In the original code:
1. `admin` was created at the module level
2. `admin.init_app(app)` was called to register it with the Flask app
3. We tried to change `admin.index_view` after it was already registered

In the fixed code:
1. `admin` is initialized as `None` at the module level
2. In `create_app`, we create the admin instance with the correct index_view
3. We then add the model views
4. The admin instance is properly registered with the Flask app

This ensures that the admin instance is fully configured before it's registered with the Flask app.
