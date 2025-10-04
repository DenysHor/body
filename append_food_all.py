# -*- coding: utf-8 -*-
import gspread
from oauth2client.service_account import ServiceAccountCredentials

SERVICE_ACCOUNT_FILE = "gpt-body-parameters-ee1a7fa0b8b5.json"
SHEET_ID = "1iWi6m3o2qatEyDTNXKqkqq_xQ3DacE_E7_NR162GNeI"

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
gc = gspread.authorize(creds)
sh = gc.open_by_key(SHEET_ID)

F_HEADERS = ["Дата","Час","Прийом","Страва / Продукт","Кількість","Ккал",
             "Білки (г)","Жири (г)","Вуглеводи (г)","Клітковина (г)","Позначка","Нотатка"]

def ensure_food_sheet():
    try:
        ws = sh.worksheet("Харчування")
        if ws.row_count == 1 and not any(ws.row_values(1)):
            ws.update([F_HEADERS], value_input_option="USER_ENTERED")
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title="Харчування", rows=400, cols=len(F_HEADERS))
        ws.update([F_HEADERS], value_input_option="USER_ENTERED")
    return ws

def append_food_rows(rows):
    ws = ensure_food_sheet()
    ws.append_rows(rows, value_input_option="USER_ENTERED")

# ---- Дані 21.09.2025
rows = [
    # сніданок — немає деталізації, ставимо позначку
    ["2025-09-21","ранок","Сніданок","Сніданок (деталі не вказані)","-", "", "", "", "", "", "потребує уточнення","Перед сніданком — вода з лимоном"],
    # перекус банан (~120 г)
    ["2025-09-21","після тренування","Перекус","Банан","≈120 г", 105, 1.3, 0.3, 27, 3.1, "оцінка",""],
    # вечеря: індичка + овочі + олія + кунжут
    ["2025-09-21","вечір","Вечеря","Індичка (філе)","≈200 г", 220, 46, 2, 0, 0, "оцінка","Теплий салат з індички"],
    ["2025-09-21","вечір","Вечеря","Овочі мікс (перець, помідор, салат)","≈200 г", 60, 2, 0.5, 12, 3, "оцінка",""],
    ["2025-09-21","вечір","Вечеря","Оливкова олія","1 ст. л. (15 мл)", 120, 0, 14, 0, 0, "оцінка","у соусі"],
    ["2025-09-21","вечір","Вечеря","Кунжут","1 ч. л. (5 г)", 29, 1, 2.6, 1.3, 1.1, "оцінка",""],

    # ---- Дані 04.10.2025 (сьогодні)
    ["2025-10-04","обід","Обід","Гречка варена","≈250 г (1 чашка)", 155, 5.7, 1.4, 33, 4.5, "оцінка","з цибулею, часником, овочами"],
    ["2025-10-04","обід","Обід","Овочі (цибуля, перець, морква)","≈150 г", 45, 1.5, 0.2, 10, 2.0, "оцінка",""],
    ["2025-10-04","обід","Обід","Олія для обсмаження","1 ч. л. (5 мл)", 45, 0, 5, 0, 0, "оцінка",""],
    ["2025-10-04","обід","Обід","Яловичина пісна 5%","≈150 г", 250, 26, 15, 0, 0, "оцінка","уточнено"],
    ["2025-10-04","обід","Обід","Томатний сік","≈250 мл", 45, 2, 0, 10, 1, "оцінка",""],
]

if __name__ == "__main__":
    append_food_rows(rows)
    print("✅ Харчування: усі відомі записи додано.")
