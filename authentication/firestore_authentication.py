from firebase_admin import credentials, firestore, initialize_app, storage
from decouple import config
import pyrebase
import os

# configuration for authentication via firestore
config_auth = {
    'apiKey': config('API_KEY'),
    'authDomain': "bachelorproef-2223.firebaseapp.com",
    'projectId': "bachelorproef-2223",
    'storageBucket': "bachelorproef-2223.appspot.com",
    'messagingSenderId': config('MESSAGING_SENDER_ID'),
    'appId': config('APP_ID'),
    'measurementId': config('MEASUREMENT_ID'),
    'databaseURL': ''
}

pb = pyrebase.initialize_app(config_auth)
auth = pb.auth()

### INITIALISATION
cred = credentials.Certificate({
  "type": "service_account",
  "project_id": "bachelorproef-2223",
  "private_key_id": config('PRIVATE_KEY_ID'),
  "private_key": config('PRIVATE_KEY').replace(r'\n', '\n'),
  "client_email": config('CLIENT_EMAIL'),
  "client_id": config('CLIENT_ID'),
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-vsza3%40bachelorproef-2223.iam.gserviceaccount.com"
})

default_app = initialize_app(cred, {
    'storageBucket': 'bachelorproef-2223.appspot.com'})
db = firestore.client()
bucket = storage.bucket()

