import os
from main import BASE_DIR
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

spreadsheet_id = '13kWLMsatq8brJWiQRAaYKzxMgB4Ohh874ebtJOABvZo'
sheet_name = 'data'

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
sacc_json_path = os.path.join(BASE_DIR, 'mobile_scraper', 'GoogleSheets', 'creds', 'sacc1.json')

credentials = ServiceAccountCredentials.from_json_keyfile_name(sacc_json_path, scope)
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()


def read_column(column_name):
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=sheet_name+'!'+column_name+'2:'+column_name).execute()

    values = []
    for value in result.get('values'):
        values.append(value[0])

    return values


def write_column(data, wr_range):
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=wr_range,
        valueInputOption="RAW",
        body={'values': data}
    ).execute()


def get_last_row():
    rows = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_name + "!" + "A:Z").execute().\
        get('values', [])
    last_row_id = len(rows)
    return last_row_id
