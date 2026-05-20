# MacOS File Size Analyzer (GUI)

Aplikacja okienkowa w języku Python, która skanuje wybrany katalog na systemie MacOS, znajduje największe pliki i generuje wbudowany interaktywny wykres kołowy (pie chart) przedstawiający procentowe i ilościowe użycie dysku przez te pliki.

## Wymagania

- Python 3.7 lub nowszy
- Wbudowana w Pythona biblioteka `tkinter`
- Biblioteka `matplotlib`

## Instalacja i Uruchomienie

1. Upewnij się, że masz zainstalowanego Pythona.
2. **Nie musisz ręcznie instalować żadnych bibliotek!** Skrypt przy pierwszym uruchomieniu sam sprawdzi, czy posiada wymagane pakiety (np. `matplotlib`) i w razie potrzeby pobierze je automatycznie.

Uruchom poniższe polecenie w terminalu:

```bash
python3 macos_filesize_chart.py
```

### Jak uruchamiać aplikację dwuklikiem (jak normalny program na MacOS)?

System MacOS domyślnie otwiera pliki `.py` w edytorze tekstu (np. TextEdit). Aby uruchamiać go jak zwykłą aplikację po dwukrotnym kliknięciu, wykonaj jedną z poniższych metod:

**Metoda 1: Przypisanie do Python Launcher (Zalecane dla plików .py)**
1. Kliknij plik `macos_filesize_chart.py` **prawym przyciskiem myszy** (lub Control+Klik).
2. Wybierz **Informacje (Get Info)**.
3. Znajdź sekcję **Otwórz w programie: (Open with:)**.
4. Z rozwijanej listy wybierz **Python Launcher** (znajduje się w Aplikacje -> Python 3.x).
5. Kliknij przycisk **Zmień wszystko... (Change All...)**.
Od teraz podwójne kliknięcie na plik automatycznie uruchomi aplikację!

**Metoda 2: Zmiana rozszerzenia na .command**
1. Zmień nazwę pliku z `macos_filesize_chart.py` na `macos_filesize_chart.command`.
2. Otwórz terminal i nadaj mu prawa do wykonywania poleceniem: 
   `chmod +x /ścieżka/do/macos_filesize_chart.command`
Teraz dwuklik na plik `.command` otworzy aplikację.

---

Otworzy się okno aplikacji, w którym możesz:
1. **Wybrać katalog** za pomocą przycisku "Przeglądaj...".
2. **Wybrać liczbę plików** do przeanalizowania.
3. Kliknąć **"Rozpocznij Skanowanie"**.

Proces działa w tle (nie zawiesza aplikacji), a po zakończeniu po lewej stronie pojawi się tabela ze szczegółami plików, a po prawej stronie interaktywny wykres kołowy.
