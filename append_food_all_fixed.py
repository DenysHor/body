# -*- coding: utf-8 -*-
import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

SHEET_ID = "1iWi6m3o2qatEyDTNXKqkqq_xQ3DacE_E7_NR162GNeI"
FOOD_SHEET_TITLE = "Харчування"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def get_gspread_client():
    """
    Авторизація через:
    1. GCP_SERVICE_ACCOUNT_JSON (секрет GitHub)
    2. GOOGLE_APPLICATION_CREDENTIALS (локальний файл)
    """
    json_secret = os.environ.get("GCP_SERVICE_ACCOUNT_JSON")
    if json_secret:
        info = json.loads(json_secret)
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    else:
        cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "gpt-body-parameters-ee1a7fa0b8b5.json")
        if not os.path.exists(cred_path):
            raise FileNotFoundError("Не знайдено JSON ключ. Додай секрет GCP_SERVICE_ACCOUNT_JSON або локальний файл.")
        creds = Credentials.from_service_account_file(cred_path, scopes=SCOPES)
    return gspread.authorize(creds)

HEADERS = [
    "Дата","Час","Прийом","Страва / Продукт","Кількість","Ккал",
    "Білки (г)","Жири (г)","Вуглеводи (г)","Клітковина (г)","Позначка","Нотатка"
]

def ensure_food_sheet(sh):
    try:
        ws = sh.worksheet(FOOD_SHEET_TITLE)
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=FOOD_SHEET_TITLE, rows=400, cols=len(HEADERS))
        ws.update([HEADERS], value_input_option="USER_ENTERED")
        return ws
    if not ws.row_values(1):
        ws.update([HEADERS], value_input_option="USER_ENTERED")
    return ws

def load_existing_keys(ws):
    """Зчитує унікальні ключі (Дата, Прийом, Страва / Продукт) щоб уникати дублікатів"""
    records = ws.get_all_records(numeric_value_handling='RAW')
    keys = {(r["Дата"], r["Прийом"], r["Страва / Продукт"]) for r in records if r.get("Дата")}
    return keys

def append_food_rows(rows):
    gc = get_gspread_client()
    sh = gc.open_by_key(SHEET_ID)
    ws = ensure_food_sheet(sh)
    existing = load_existing_keys(ws)
    new_rows = [r for r in rows if (r[0], r[2], r[3]) not in existing]
    if new_rows:
        ws.append_rows(new_rows, value_input_option="USER_ENTERED")
        print(f"✅ Додано рядків: {len(new_rows)}")
    else:
        print("ℹ️ Нових записів немає.")

if __name__ == "__main__":
    # Приклад автоматичного додавання нового прийому їжі
    today = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M")

    rows = [[
        today, now_time, "Сніданок",
        "Яєчня з перцем, сиром і лавашем", "≈350 г",
        420, 27, 25, 20, 1.5,
        "оцінка", "Перед сніданком — вода з лимоном"
    ]]

    append_food_rows(rows)
