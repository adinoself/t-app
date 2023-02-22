import requests
import streamlit as st
import transcribe
import time
import sys
from zipfile import ZipFile
from time import sleep
import os
import pickle
from pathlib import Path
import streamlit_authenticator as stauth

auth_key = st.secrets['auth_key']

st.header("Transcription Service")

# --- USER AUTHENTICATION ---
names = ["Joseph Modi", "Emmah Wavinya", "Raissa A", "Abdul M"]
usernames = ["adinoself", "missdivine", "raissanbg", "abdulnbg"]
credentials = {"usernames":{}}

# LOAD HASHED PASSWORDS
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, usernames, hashed_passwords, "transcription", "abcdef", cookie_expiry_days=0)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:

    # ----SIDEBAR ---
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome, {name}")


    # 1
    # THIS IS THE AUTHORIZATION HEADER
    def get_url(auth_key, data):
        '''
          Parameter:
            token: The API key
            data : The File Object to upload
          Return Value:
            url  : Url to uploaded file
        '''
        headers = {'authorization': auth_key}
        response = requests.post('https://api.assemblyai.com/v2/upload',
                                 headers=headers,
                                 data=data)
        url = response.json()["upload_url"]
        print("Uploaded File and got temporary URL to file")
        return url


    # 2 GET THE TRANSCRIBE ID
    def get_transcribe_id(auth_key, url):
        '''
          Parameter:
            token: The API key
            url  : Url to uploaded file
          Return Value:
            id   : The transcription id of the file
        '''
        endpoint = "https://api.assemblyai.com/v2/transcript"
        json = {
            "audio_url": url,
            "speaker_labels": True

        }
        headers = {
            "authorization": auth_key,
            "content-type": "application/json"
        }
        response = requests.post(endpoint, json=json, headers=headers)
        id = response.json()['id']
        print("Made request and file is currently queued")
        print(response.json())
        return id


    # 3 UPLOADED FILE
    def upload_file(fileObj):
        '''
          Parameter:
            fileObj: The File Object to transcribe
          Return Value:
            token  : The API key
            transcribe_id: The ID of the file which is being transcribed
        '''
        auth_key = st.secrets['auth_key']
        url = get_url(auth_key, fileObj)
        t_id = get_transcribe_id(auth_key, url)
        print("transcribe_id")
        return auth_key, t_id


    # 4 GET THE TRANSCRIPTION RESULT
    def get_text(auth_key, transcribe_id):
        '''
          Parameter:
            token: The API key
            transcribe_id: The ID of the file which is being
          Return Value:
            result : The response object
        '''
        endpoint = f"https://api.assemblyai.com/v2/transcript/{transcribe_id}"
        headers = {
            "authorization": auth_key,
        }
        result = requests.get(endpoint, headers=headers).json()
        # print(result.text)
        return result

    # ---- THE APP ---- FILE UPLOADER UI ----
    fileObject = st.file_uploader(label = "Please upload your file")
    if fileObject:
        auth_key, transcribe_id = upload_file(fileObject)
        result = {}
        #polling
        sleep_duration = 1
        percent_complete = 0
        progress_bar = st.progress(percent_complete)
        st.text("Currently in queue")
        while result.get("status") != "processing":
            percent_complete += sleep_duration
            time.sleep(sleep_duration)
            progress_bar.progress(percent_complete/10)
            result = get_text(auth_key, transcribe_id)

        sleep_duration = 0.01
        
        # CHECK IF TRANSCRIPTION IS COMPLETE
        
        for percent in range(percent_complete,101):
            time.sleep(sleep_duration)
            progress_bar.progress(percent)

        with st.spinner("Processing....."):
            while result.get("status") != 'completed':
            #while result.json()['status'] != 'completed':
                #sleep(5)
                #st.warning('Transcription is processing...')
                result = get_text(auth_key, transcribe_id)
                #result = requests.get(endpoint, headers=headers)

    
     # PRINT TRANSCRIBED TEXT
        st.success('Transcription Successful!')
        st.subheader("Transcribed Text")
        st.success(result['text'])

     # SAVE TRANSCRIBED TEXT TO A FILE

     # SAVE AS A TXT FILE
        yt_txt = open('plain text transcript.txt', 'w')
        yt_txt.write(result["text"])
        yt_txt.close()

     # SAVE AS SRT FILE
        endpoint = f"https://api.assemblyai.com/v2/transcript/{transcribe_id}"
        headers = {
            "authorization": auth_key,
        }
        result = requests.get(endpoint, headers=headers).json()
        srt_endpoint = endpoint + "/srt"
        srt_response = requests.get(srt_endpoint, headers=headers)
        with open("transcript with time stamps.txt", "w") as _file:
            _file.write(srt_response.text)
            print(srt_response)

        zip_file = ZipFile('transcription.zip', 'w')
        zip_file.write('plain text transcript.txt')
        zip_file.write('transcript with time stamps.txt')
        zip_file.close()

        with open("transcription.zip", "rb") as zip_download:
         btn = st.download_button(
             label="Download Transcript",
             data=zip_download,
             file_name="transcription.zip",
             mime="zip"
         )
