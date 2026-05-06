Fáze 1: Veřejný dashboard (Read-only)
Funkcionalita
Zobrazení seznamu ptáků bez možnosti úprav
Workflow
Uživatel otevře aplikaci
Vidí dashboard
Uživatelské rozhraní

Stránka: /dashboard

Tabulka obsahuje:

Název
Latinský název
Popis

Prvky:

tlačítko „Přihlásit se“

 Bez:
Upravit
Smazat
Přidat

Fáze 2: Autentizace uživatele (Login systém)
Funkcionalita
Přihlášení uživatele
Klikne na „Přihlásit se“
Je přesměrován na /login
Zadá přihlašovací údaje
Po úspěšném přihlášení je přesměrován na /birds
Při chybě se zobrazí hláška

Fáze 3: CRUD rozhraní (správa ptáků)
Funkcionalita
Plná správa dat (Create, Update, Delete)
Workflow
Uživatel je přihlášen
Je na /birds
Vidí tabulku s akcemi
Může upravovat data
Uživatelské rozhraní

Stránka: /birds

Tabulka obsahuje:

Název
Latinský název
Popis
Akce (Upravit, Smazat)

Tlačítko:

„Přidat nového ptáka“

Fáze 4: Přidání nového záznamu (Create)
Funkcionalita
Přidání záznamu (pouze přihlášený)
Workflow
Klik na „Přidat nového ptáka“
Formulář
Odeslání
Návrat na /birds
Uživatelské rozhraní

Stránka: /birds_form

Formulář:

Název
Latinský název
Popis
Tlačítka:

Uložit
Zrušit

Fáze 5: Úprava záznamu (Update)
Funkcionalita
Editace záznamu
Workflow
Klik na „Upravit“
Úprava
Uložení
Návrat na /birds
předvyplněný formulář

Fáze 6: Smazání záznamu (Delete)
Funkcionalita
Smazání záznamu
Workflow
Klik na „Smazat“
Potvrzení
Smazání
Aktualizace seznamu
Uživatelské rozhraní
tlačítko „Smazat“
potvrzovací dialog

Fáze 7: Ochrana aplikace (Authorization)
Funkcionalita
Oddělení veřejné a neveřejné části
Pravidla
/dashboard veřejné
/birds pouze přihlášený
Workflow
Nepřihlášený uživatel jde na /dashboard
 přesměrování na /login
Přihlášený uživatel na /birds