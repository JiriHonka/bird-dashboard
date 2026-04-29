#Plán implementace správy ptačího datasetu
Přehled

Cílem je vytvořit webovou aplikaci, která umožní přihlášeným uživatelům spravovat záznamy o ptácích (CRUD operace – Create, Read, Update, Delete). Nepřihlášení uživatelé nebudou mít přístup ke správě databáze.

#Fáze 1: Autentizace uživatele (Login systém)
Funkcionalita
Přihlášení uživatele
Ochrana rout (přístup pouze pro přihlášené)
Workflow
Uživatel otevře aplikaci.
Je přesměrován na přihlašovací stránku.
Zadá uživatelské jméno a heslo.
Po úspěšném přihlášení je přesměrován na hlavní dashboard.
Pokud přihlášení selže, zobrazí se chybová hláška.
Uživatelské rozhraní
Stránka: /login
Formulář obsahuje:
input: uživatelské jméno
input: heslo
tlačítko: „Přihlásit se“
Chybová zpráva pod formulářem
Technické poznámky
Použití session nebo JWT tokenů
Middleware pro ochranu rout
#Fáze 2: Zobrazení seznamu ptáků (Read)
Funkcionalita
Výpis všech záznamů v databázi
Workflow
Uživatel se přihlásí.
Je přesměrován na stránku se seznamem ptáků.
Vidí tabulku se záznamy.
Uživatelské rozhraní
Stránka: /birds
Tabulka obsahuje sloupce:
Název
Latinský název
Popis
Akce (Upravit, Smazat)
Tlačítko: „Přidat nového ptáka“
#Fáze 3: Přidání nového záznamu (Create)
Funkcionalita
Vytvoření nového záznamu o ptákovi
Workflow
Uživatel klikne na „Přidat nového ptáka“.
Je přesměrován na formulář.
Vyplní údaje.
Odešle formulář.
Po úspěchu je přesměrován zpět na seznam.
Uživatelské rozhraní
Stránka: /birds/new
Formulář obsahuje:
Název
Latinský název
Popis
(volitelně) obrázek
Tlačítka:
„Uložit“
„Zrušit“
#Fáze 4: Úprava záznamu (Update)
Funkcionalita
Editace existujícího záznamu
Workflow
Uživatel klikne na „Upravit“ u konkrétního záznamu.
Otevře se formulář s předvyplněnými daty.
Uživatel provede změny.
Uloží změny.
Vrátí se zpět na seznam.
Uživatelské rozhraní
Stránka: /birds/:id/edit
Formulář stejný jako při vytváření
Předvyplněná data
#Fáze 5: Smazání záznamu (Delete)
Funkcionalita
Odstranění záznamu z databáze
Workflow
Uživatel klikne na „Smazat“.
Zobrazí se potvrzovací dialog.
Po potvrzení je záznam odstraněn.
Seznam se aktualizuje.
Uživatelské rozhraní
Tlačítko „Smazat“ v tabulce
Modal/dialog s potvrzením:
„Opravdu chcete smazat tento záznam?“
Tlačítka: „Ano“ / „Ne“
#Fáze 6: Ochrana aplikace (Authorization)
Funkcionalita
Zajištění, že CRUD operace jsou dostupné pouze přihlášeným
Workflow
Nepřihlášený uživatel se pokusí vstoupit na /birds.
Je automaticky přesměrován na /login.
Přihlášený uživatel má plný přístup.
Technické řešení
Middleware kontrolující autentizaci
Token uložený v cookies/localStorage
#Fáze 7: Struktura databáze
Tabulka: birds
id (PK)
name (string)
latin_name (string)
description (text)
image_url (string, volitelné)
created_at
updated_at
#Fáze 8: API návrh
Endpointy
POST /api/login
GET /api/birds
POST /api/birds
PUT /api/birds/:id
DELETE /api/birds/:id
#Fáze 9: Verzování a commit
Postup
Vytvořit soubor: PLAN.md
Vložit tento plán
Commit zpráva:
docs: přidán plán implementace správy ptačího datasetu
Shrnutí

Aplikace bude mít jasný tok:

Login stránka
Dashboard se seznamem ptáků
Možnost přidávat, upravovat a mazat záznamy
Vše dostupné pouze po přihlášení