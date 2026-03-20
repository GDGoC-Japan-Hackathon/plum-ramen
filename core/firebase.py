import firebase_admin

if not firebase_admin._apps:
    firebase_admin.initialize_app()
