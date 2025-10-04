# -*- coding: utf-8 -*-
"""
append_food_all_fixed.py

Оновлює лист "Харчування" у заданій Google-таблиці.
Авторизація:
- у CI (GitHub Actions) через секрет GCP_SERVICE_ACCOUNT_JSON
  або через створений воркфлоу тимчасовий файл GOOGLE_APPLICATION_CREDENTIALS;
- локально можна або експортувати GOOGLE_APPLICATION_CREDENTIALS, або теж
  передати JSON у GCP_SERVICE_ACCOUNT_JSON.

Що саме додається:
- Скрипт намагається імпортувати функцію build_rows() з append_entries.py
  (якщо вона є у вашому проєкті) — і використати її для формування рядків.
- Якщо імпорту немає або сталася помилка, скрипт нічого не додає і просто
  завершується повідомленням (без помилки), аби CI не падав.
"""

from __future__ import annotations

import os
import json
from typing import List, Sequence

import gspread
from google.oauth2.service_account import Credentials


# ---- Налаштування доступів до Google APIs ----
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Ідентифікатор таблиці. Зручніше тримати у секреті/змінній середовища.
SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "").strip()

# Назва робочого аркуша, куди пишемо дані
SHEET_TITLE = "Харчування"

# Заголовки (якщо аркуш порожній — створимо/поставимо їх)
HEADERS = [
    "Дата", "Час", "Прийом", "Страва / Продукт", "Кількість", "Ккал",
    "Білки (г)", "Жири (г)", "Вуглеводи (г)", "Клітковина (г)", "Позначка", "Нотатка",
]


# ---- Авторизація через secrets/env ----
def get_gspread_client() -> gspread.Client:
    """
    Пробуємо 2 варіанти:
    1) GCP_SERVICE_ACCOUNT_JSON (рядок із JSON — найзручніше для GitHub Actions)
    2) GOOGLE_APPLICATION_CREDENTIALS (шлях до .json файлу)
    """
    json_secret = os.environ.get("GCP_SERVICE_ACCOUNT_JSON")
    if json_secret:
        info = json.loads(json_secret)
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    else:
        cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not cred_path or not os.path.exists(cred_path):
            raise FileNotFoundError(
                "Немає облікових даних: "
                "ані GCP_SERVICE_ACCOUNT_JSON, ані валідного GOOGLE_APPLICATION_CREDENTIALS."
            )
        creds = Credentials.from_service_account_file(cred_path, scopes=SCOPES)

    return gspread.authorize(creds)


# ---- Робота з таблицею ----
def open_sheet(client: gspread.Client, sheet_id: str):
    if not sheet_id:
        raise RuntimeError(
            "Не задано GOOGLE_SHEET_ID (ідентифікатор таблиці). "
            "Додайте його в Secrets/Environment або встановіть локально."
        )
    return client.open_by_key(sheet_id)


def ensure_worksheet(sh, title: str, headers: Sequence[str]):
    """Повертає аркуш `title`; якщо його немає — створює. Якщо порожній — ставить заголовки."""
    try:
        ws = sh.worksheet(title)
        # Якщо заголовки відсутні (порожній аркуш) — додамо їх
        first_row = ws.row_values(1)
        if not first_row:
            ws.update([list(headers)], value_input_option="USER_ENTERED")
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=title, rows=500, cols=len(headers))
        ws.update([list(headers)], value_input_option="USER_ENTERED")
    return ws


def append_rows(ws, rows: List[Sequence]):
    """Додає рядки у кінець аркуша, якщо вони є."""
    if not rows:
        print("ℹ️ Немає нових рядків для додавання — пропускаю.")
        return
    ws.append_rows(rows, value_input_option="USER_ENTERED")
    print(f"✅ Додано рядків: {len(rows)}")


# ---- Джерело даних ----
def build_rows_from_project() -> List[Sequence]:
    """
    Спроба імпортувати генератор рядків з вашого проєкту.
    Якщо у вас є файл append_entries.py з функцією build_rows() — вона буде викликана.
    Інакше повертаємо порожній список, щоб CI не падав.
    """
    try:
        from append_entries import build_rows  # ваша функція, якщо існує
        rows = build_rows()
        if not isinstance(rows, list):
            raise TypeError("append_entries.build_rows() має повертати list[Sequence].")
        return rows
    except Exception as e:
        print(f"⚠️ Не вдалось отримати рядки з append_entries.build_rows(): {e}")
        return []


def main():
    client = get_gspread_client()
    sh = open_sheet(client, SHEET_ID)
    ws = ensure_worksheet(sh, SHEET_TITLE, HEADERS)

    # 1) Основний шлях: беремо всі рядки з вашого генератора
    rows = build_rows_from_project()

    # 2) (Опціонально) якщо хочете — тут можна додати якісь фолбек-рядки
    #    або залишити як є (нічого не додавати, якщо генератора немає).

    append_rows(ws, rows)


if __name__ == "__main__":
    main()
