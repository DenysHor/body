# -*- coding: utf-8 -*-
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ==== НАЛАШТУВАННЯ ====
SERVICE_ACCOUNT_FILE = "gpt-body-parameters-ee1a7fa0b8b5.json"
SHEET_ID = "1iWi6m3o2qatEyDTNXKqkqq_xQ3DacE_E7_NR162GNeI"
# ======================

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
gc = gspread.authorize(creds)
sh = gc.open_by_key(SHEET_ID)

def ensure_sheet(title: str, headers: list[str]):
    """Створює аркуш і заголовки, якщо їх немає, і повертає worksheet."""
    try:
        ws = sh.worksheet(title)
        # якщо порожній — ставимо заголовки
        if ws.row_count == 1 and not any(ws.row_values(1)):
            ws.update([headers], value_input_option="USER_ENTERED")
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=title, rows=200, cols=max(10, len(headers)))
        ws.update([headers], value_input_option="USER_ENTERED")
    return ws

# ---- Заголовки ----
J_HEADERS = ["Дата","Вага (кг)","ІМТ","Тілесний жир (%)","Скелетні м’язи (%)","Вода (%)",
             "Білок (%)","Вісцеральний жир (рівень)","Кісткова маса (%)","BMR (ккал)",
             "Фітнес-вік","Вага жиру (кг)","BFMI","FFM (кг)","Примітки"]

F_HEADERS = ["Дата","Час","Прийом","Страва / Продукт","Кількість","Ккал",
             "Білки (г)","Жири (г)","Вуглеводи (г)","Клітковина (г)","Позначка","Нотатка"]

P_HEADERS = ["Дата","Діапазон (мін–макс, уд/хв)","Останнє вимірювання",
             "Приклад низького","Приклад високого","Середній у спокої","Примітки"]

def append_row(title: str, headers: list[str], row: list):
    ws = ensure_sheet(title, headers)
    # якщо перший рядок — заголовки, вставляємо з другого
    ws.append_row(row, value_input_option="USER_ENTERED")

# ====== ПРИКЛАДИ ВИКЛИКІВ ======
def append_journal_entry(
    date_str, weight, bmi, fat_pct, muscle_pct, water_pct,
    protein_pct, visceral, bone_pct, bmr, fitness_age, fat_mass, bfmi, ffm, note=""
):
    append_row("Журнал", J_HEADERS, [
        date_str, weight, bmi, fat_pct, muscle_pct, water_pct,
        protein_pct, visceral, bone_pct, bmr, fitness_age, fat_mass, bfmi, ffm, note
    ])

def append_food_entry(
    date_str, time_str, meal, item, qty, kcal, protein, fat, carbs, fiber=0, tag="оцінка", note=""
):
    append_row("Харчування", F_HEADERS, [
        date_str, time_str, meal, item, qty, kcal, protein, fat, carbs, fiber, tag, note
    ])

def append_pulse_entry(
    date_str, range_str, last_hr, low_sample, high_sample, resting_avg, note=""
):
    append_row("Пульс", P_HEADERS, [
        date_str, range_str, last_hr, low_sample, high_sample, resting_avg, note
    ])

if __name__ == "__main__":
    print("Готово. Імпортуй функції з цього файлу та викликай append_* для дописування нових рядків.")
