import json
import os

def load_notes():
    if os.path.exists("notes.json"):
        with open("notes.json", "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_notes():
    with open("notes.json", "w", encoding="utf-8") as file:
        json.dump(notes_db, file, ensure_ascii=False, indent=4)

notes_db = load_notes()

def add_note(title, text):
    new_id = len(notes_db) + 1
    new_note = {
        "id": new_id,
        "title": title,
        "text": text
    }
    notes_db.append(new_note)
    save_notes()
    return f"Нотатку '{title}' успішно додано та збережено у файл!"

def show_notes():
    if not notes_db:
        print("\nСписок нотаток порожній.")
        return
    
    print("\n--- ТВОЇ ЗБЕРЕЖЕНІ НОТАТКИ ---")
    for note in notes_db:
        print(f"[{note['id']}] {note['title']}: {note['text']}")
    print("------------------------------")

def remove_last_note():
    if notes_db:
        removed = notes_db.pop()
        save_notes()
        return f"Видалено нотатку: '{removed['title']}'"
    else:
        return "Немає нотаток для видалення."

while True:
    print("\n=== МЕНЮ (JSON SAVED) ===")
    print("1. Переглянути всі нотатки")
    print("2. Додати нову нотатку")
    print("3. Видалити останню нотатку")
    print("0. Вийти з програми")
    
    choice = input("\nОбери дію (0-3): ")
    
    if choice == "1":
        show_notes()
    elif choice == "2":
        t = input("Введіть заголовок: ")
        txt = input("Введіть текст нотатки: ")
        result = add_note(t, txt)
        print(result)
    elif choice == "3":
        result = remove_last_note()
        print(result)
    elif choice == "0":
        print("Програму завершено. Усі дані збережені!")
        break
    else:
        print("Невірний вибір, спробуй ще раз.")