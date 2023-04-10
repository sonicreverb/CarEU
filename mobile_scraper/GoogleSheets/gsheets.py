import os
from main import BASE_DIR
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials

spreadsheet_id = '13kWLMsatq8brJWiQRAaYKzxMgB4Ohh874ebtJOABvZo'

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
sacc_json_path = os.path.join(BASE_DIR, 'mobile_scraper', 'GoogleSheets', 'creds', 'sacc1.json')

credentials = ServiceAccountCredentials.from_json_keyfile_name(sacc_json_path, scope)
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()


def read_column(column_name, sheet_name):
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


# удаление строки
def delete_row(row_index, sheet_name):
    # указываем sheet_name
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheet_id = None
    for some_sheet in sheet_metadata.get('sheets', []):
        if some_sheet.get('properties', {}).get('title', '') == sheet_name:
            sheet_id = some_sheet.get('properties', {}).get('sheetId')
            break

    if not sheet_id:
        print(f"Лист '{sheet_name}' не найден в таблице.")
    else:
        # создание запроса на удаление строк в указанном листе
        delete_request = {
            'deleteDimension': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'ROWS',
                    'startIndex': row_index - 1,
                    'endIndex': row_index
                }
            }
        }

        # отправка запроса на удаление строк
        try:
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': [delete_request]}
            ).execute()
        except HttpError as error:
            print(f"Ошибка: {error}")


def get_last_row(sheet_name):
    rows = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_name + "!" + "A:Z").execute().\
        get('values', [])
    last_row_id = len(rows)
    return last_row_id
