import firebase_admin
from firebase_admin import firestore, credentials

db = None

try:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print("Firebase disabled : ",e)