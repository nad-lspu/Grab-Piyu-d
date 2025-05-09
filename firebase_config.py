import pyrebase

firebase_config = {
    "apiKey": "AIzaSyC6WJzNijzPO8Bmg4mWEb_MIoJioj7xtJc",
    "authDomain": "grab-piyu-d.firebaseapp.com",
    "databaseURL": "https://grab-piyu-d-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "grab-piyu-d",
    "storageBucket": "grab-piyu-d.firebasestorage.app",
    "messagingSenderId": "77622540773",
    "appId": "1:77622540773:web:63f8e07a3c71b4ee61170c",
    "measurementId": "G-HG2SF55TBS"
}

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()
auth = firebase.auth()