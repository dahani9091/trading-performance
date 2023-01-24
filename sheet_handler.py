import io
import pyrebase
import config
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json



class FirebaseStorage:
    def __init__(self):
        self.firebase = pyrebase.initialize_app(config.firebaseConfig)
        self.storage = self.firebase.storage()

    def upload_pdf(self, pdf_data:io.BytesIO, storage_path:str):
        storage_path = storage_path.strip("/")
        # with open(pdf_path, "rb") as pdf_file:
        self.storage.child(storage_path).put(pdf_data.read())
        return self.storage.child(storage_path).get_url(None)

    def download_pdf(self, storage_path:str):
        storage_path = storage_path.strip("/")
        pdf_url = self.storage.child(storage_path).get_url(None)
        pdf_data = io.BytesIO(requests.get(pdf_url).content)
        return pdf_data



class GoogleSheet:
    def __init__(self, creds_file_path:str="google_sheet.json"):
        self.creds_file_path = creds_file_path
        self.creds = self.get_creds_dict()
        self.scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
        self.credentials = ServiceAccountCredentials.from_json_keyfile_dict(self.creds, self.scope)
        self.client = gspread.authorize(self.credentials)
        
    def get_creds_dict(self):
        with open(self.creds_file_path, "r") as f:
            creds = json.load(f)
        return creds

    def open_sheet(self, sheet_name:str):
        self.sheet_name = sheet_name
        self.sheet = self.client.open(sheet_name).get_worksheet(0)

    def add_row(self, values:list):
        '''
        values: list of values to add to the sheet, in these order: 
        [Pos ,Side ,Symbol ,Price, TimeStamp, BoughtPrice]

        '''
        self.sheet.append_row(values)
    
    def download_sheet_as_pdf(self):
        scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
        ]
        creds=ServiceAccountCredentials.from_json_keyfile_name(self.creds_file_path,scope)
        client=gspread.authorize(creds)

        spreadsheet_name = self.sheet_name
        spreadsheet = client.open(spreadsheet_name)
        url = 'https://docs.google.com/spreadsheets/export?format=pdf&id=' + spreadsheet.id
        headers = {'Authorization': 'Bearer ' + creds.create_delegated("").get_access_token().access_token}
        res = requests.get(url, headers=headers)
        return io.BytesIO(res.content)

def update_sheet(values):
    # create a firebase storage object
    firebase_storage = FirebaseStorage()

    # create a google sheet object
    google_sheet = GoogleSheet()

    # open the sheet
    google_sheet.open_sheet("test2")

    # add a row to the sheet
    google_sheet.add_row(values)

    # download the sheet as pdf
    sheet_pdf_data = google_sheet.download_sheet_as_pdf()

    # upload the sheet pdf to firebase storage
    sheet_pdf_url = firebase_storage.upload_pdf(sheet_pdf_data, "trading-performance.pdf")

    print("Sheet URL: ",sheet_pdf_url)

    # download the sheet pdf from firebase storage
    sheet_pdf_data = firebase_storage.download_pdf("trading-performance.pdf")

    # save the sheet pdf to a file
    with open("trading-performance.pdf", "wb") as f:
        f.write(sheet_pdf_data.read())