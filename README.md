# MacOS File Size Chart (GUI)

Aplikacja okienkowa w języku Python, która skanuje wybrany katalog, znajduje w nim największe pliki i generuje wbudowane, estetyczne wykresy (kołowy oraz słupkowy) przedstawiające zużycie przestrzeni dyskowej.

## Wymagania

- Python 3.7 lub nowszy
- Wbudowana w Pythona biblioteka `tkinter` 
- **Brak zewnętrznych zależności!** Aplikacja opiera się wyłącznie na standardowych bibliotekach Pythona, dzięki czemu jest bardzo lekka i błyskawicznie się uruchamia.

## Uruchomienie ze źródeł

Aby uruchomić aplikację wprost z kodu źródłowego, otwórz terminal (lub wiersz poleceń), przejdź do katalogu z projektem i wykonaj polecenie:

```bash
python3 macos_filesize_chart.py
```

---

## Kompilacja (Standalone App)

Aplikację można łatwo skompilować do postaci jednego pliku wykonywalnego (`.exe` na Windows lub paczki `.app` na macOS). Skompilowana aplikacja nie wymaga zainstalowanego Pythona na komputerze docelowym.

### Przygotowanie do kompilacji
Musisz zainstalować narzędzie `pyinstaller` za pomocą menedżera pakietów pip:
```bash
pip install pyinstaller
```

### Kompilacja na systemie Windows (.exe)
Będąc w folderze projektu, uruchom polecenie:
```bash
pyinstaller --noconsole --onefile --name "MacOS_FileSizeChart" --icon=icon.ico --add-data "icon.png;." macos_filesize_chart.py
```
Gotowy plik `MacOS_FileSizeChart.exe` pojawi się w folderze `dist\`.

### Kompilacja na systemie macOS (.app)
Będąc w folderze projektu na komputerze z systemem Mac, uruchom polecenie:
```bash
pyinstaller --noconsole --windowed --name "MacOS_FileSizeChart" --icon=icon.icns --add-data "icon.png:." macos_filesize_chart.py
```
Gotowa aplikacja `MacOS_FileSizeChart.app` pojawi się w folderze `dist/`.

---

## Automatyczna kompilacja (GitHub Actions)

Projekt ma już skonfigurowany mechanizm **GitHub Actions**. Oznacza to, że paczki dla obu systemów mogą być budowane automatycznie, bezpośrednio na serwerach GitHuba (co pozwala na zbudowanie aplikacji dla MacOS bez posiadania komputera Apple!).

**Jak pobrać skompilowane wersje z GitHuba?**
1. Przejdź do zakładki **Actions** na stronie głównej swojego repozytorium GitHub.
2. Wybierz workflow o nazwie **Build Executables** (po lewej stronie).
3. Kliknij przycisk **Run workflow** -> **Run workflow** (po prawej stronie).
4. Po około minucie proces się zakończy. Kliknij na dany przebieg (Run), a na samym dole w sekcji **Artifacts** znajdziesz gotowe paczki do pobrania:
   - `MacOS_FileSizeChart_Windows` (zawiera plik `.exe`)
   - `MacOS_FileSizeChart_macOS` (zawiera plik `MacOS_FileSizeChart.app.zip`)

*Uwaga: Paczki generują się automatycznie również wtedy, gdy utworzysz w repozytorium nowy Tag (np. `v1.2.0`).*

---

## Funkcje Aplikacji
- **Skanowanie dysku:** Możliwość wyboru dowolnego katalogu i wyszukania w nim `N` największych plików.
- **Tabela wyników:** Lista z numerem porządkowym, rozmiarem, nazwą i dokładną ścieżką do pliku na dysku.
- **Dwa tryby wykresu:** Płynne przełączanie między wykresem kołowym (z legendą) a wykresem słupkowym za pomocą radio-przycisków.
- **Autorski renderer:** Rysowanie wykresów zrealizowano przy pomocy wbudowanego płótna `tk.Canvas`, eliminując wady renderowania znane z innych zewnętrznych bibliotek.
- **Natywny wygląd:** Kod automatycznie wykrywa środowisko macOS i dostosowuje interfejs okna tak, aby idealnie pasował do stylistyki systemu (motyw Aqua).
