# Lądowy Dron Komunikacyjny 5G
## Instrukcja Obsługi
### Przygotowanie środowiska
Przed pierwszym uruchomieniem aplikacji należy uruchomić skrypt setup.sh, który przygotuje dla niej środowisko pracy.
Skrypt ten wystarczy uruchomić raz.
Po zmodyfikowaniu plików konfiguracyjnych systemu należy uruchomić setup.sh ponownie, w celu zastosowania wprowadzonych zmian (poprzednie środowisko zostanie automatycznie usunięte)
Aby uruchomienie skryptu stało się możliwe, może być konieczne użycie komendy "chmod +x setup.sh". 
Uwaga: Skrypt pobiera niezbędne biblioteki z siciowych repozytoriów - niezbędna jest łączność z internetem.

W folderze 'config-files' znajdują się pliki konfiguracyjne, pozwalające zmodyufikować działanie aplikacji.
Obecnie dostępny jest jeden plik: 'zigbee2mqtt_configuration.yaml', który pozwala skonfigurować komponent zigbee2mqtt.

### Uruchomienie
Do uruchamiania systemu służy skrypt "start.sh".
System będzie działał, dopóki skrypt pozostanie uruchomiony.

### Usunięcie środowiska
Skryptu "teardown.sh" można użyć, aby skasować środowisko, w którym pracowała aplikacja.
Uwaga: poskutkuje to skasowaniem zawartości bazy danych.
Aby zarchiwizować zawartość bazy danych, można skopiować plik drone.json do innej lokalizacji.

### Uwaga
Aby zapewnić poprawne działanie systemu, nie należy przenosić plików między katalogami - w przeciwnym wypadku ścieżki z których korzystają programy i skrypty mogą okazać się niepoprawne, co poskutkuje niepoprawnym działaniem aplikacji.

