# -*- coding: utf-8 -*-
import gspread
from oauth2client.service_account import ServiceAccountCredentials

SERVICE_ACCOUNT_FILE = "gpt-body-parameters-ee1a7fa0b8b5.json"
SHEET_ID = "1iWi6m3o2qatEyDTNXKqkqq_xQ3DacE_E7_NR162GNeI"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPES)
gc = gspread.authorize(creds)
sh = gc.open_by_key(SHEET_ID)

# гарантуємо аркуш
HEADERS = ["Дата","Час","Прийом","Страва / Продукт","Кількість","Ккал",
           "Білки (г)","Жири (г)","Вуглеводи (г)","Клітковина (г)","Позначка","Нотатка"]
try:
    ws = sh.worksheet("Харчування")
except gspread.exceptions.WorksheetNotFound:
    ws = sh.add_worksheet(title="Харчування", rows=400, cols=len(HEADERS))
    ws.update([HEADERS], value_input_option="USER_ENTERED")

# тестове оновлення + один рядок
ws.update("A1", "Дата")
ws.append_row(["TEST-ROW","", "Тест", "Перевірка доступу", "", "", "", "", "", "", "", ""],
              value_input_option="USER_ENTERED")
print("✅ Smoke-тест пройшов. Перевір аркуш «Харчування».")
