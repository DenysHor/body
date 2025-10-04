# -*- coding: utf-8 -*-
import json, sys
import gspread
from oauth2client.service_account import ServiceAccountCredentials

JSON_PATH = "gpt-body-parameters-ee1a7fa0b8b5.json"
SHEET_ID = "1iWi6m3o2qatEyDTNXKqkqq_xQ3DacE_E7_NR162GNeI"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HEADERS = ["Дата","Час","Прийом","Страва / Продукт","Кількість","Ккал",
           "Білки (г)","Жири (г)","Вуглеводи (г)","Клітковина (г)","Позначка","Нотатка"]

def read_service_email(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("client_email")

def main():
    print("▶ Читаю JSON…")
    try:
        svc_email = read_service_email(JSON_PATH)
        print("   service account email:", svc_email)
        if not svc_email:
            print("❌ У JSON немає client_email. Завантаж правильний ключ.")
            sys.exit(1)
    except FileNotFoundError:
        print(f"❌ Не знайдено файл ключа: {JSON_PATH}")
        print("   Переконайся, що файл лежить у цій самій папці й названий саме так.")
        sys.exit(1)

    print("▶ Авторизація…")
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_PATH, SCOPES)
        gc = gspread.authorize(creds)
        print("   ✅ Авторизовано")
    except Exception as e:
        print("❌ Авторизація не вдалася:", e)
        sys.exit(1)

    print("▶ Відкриваю таблицю…")
    try:
        sh = gc.open_by_key(SHEET_ID)
        print("   ✅ Таблицю відкрито.")
    except Exception as e:
        print("❌ Не вдалось відкрити таблицю за цим ID.")
        print("   Можливі причини: нема доступу для", svc_email, "або ID помилковий.")
        print("   Деталі:", e)
        sys.exit(1)

    try:
        titles = [w.title for w in sh.worksheets()]
        print("📄 Існуючі аркуші:", titles)
    except Exception as e:
        print("❌ Не вдалось прочитати аркуші:", e)
        sys.exit(1)

    print("▶ Гарантую аркуш «Харчування»…")
    try:
        try:
            ws = sh.worksheet("Харчування")
        except gspread.exceptions.WorksheetNotFound:
            ws = sh.add_worksheet(title="Харчування", rows=400, cols=len(HEADERS))
        # Заголовки (на всякий)
        ws.update([HEADERS], value_input_option="USER_ENTERED")
        print("   ✅ Аркуш готовий.")
    except Exception as e:
        print("❌ Не вдалось створити/оновити аркуш «Харчування». Можливі права:", e)
        sys.exit(1)

    print("▶ Пишу TEST-ROW…")
    try:
        ws.append_row(["TEST-ROW","","Тест","Перевірка доступу","","","","","","","",""],
                      value_input_option="USER_ENTERED")
        print("🎉 Готово! Перевір у таблиці аркуш «Харчування» — має бути рядок TEST-ROW у колонці A.")
    except Exception as e:
        print("❌ Не вдалось додати рядок. Ймовірно, проблема з правами або скоупами:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
