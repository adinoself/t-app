import pickle
from pathlib import Path
import streamlit_authenticator as stauth

names = ["Joseph Modi", "Transcriber 1", "Transcriber 2", "Transcriber 3", "Transcriber 4", "Transcriber 5", "Transcriber 6", "Transcriber 7", "Transcriber 8", "Transcriber 9", "Transcriber 10"]
usernames = ["adinoself", "transcriber1", "transcriber2", "transcriber3", "transcriber4", "transcriber5", "transcriber6", "transcriber7", "transcriber8", "transcriber9", "transcriber10"]
passwords = []

hashed_passwords = stauth.Hasher(passwords).generate()

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file:
    pickle.dump(hashed_passwords,file)