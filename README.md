# Elektrischer Schwingkreis und mechanisches Federpendel

Interaktive, synchrone Matplotlib-Animation zum Vergleich eines idealen LC-Schwingkreises mit einem ungedaempften Federpendel.

## Start

Python 3 mit NumPy und Matplotlib benoetigt:

```bash
python -m pip install numpy matplotlib
python schwingkreis_vergleich.py
```

## Bedienung

- Start/Pause: Animation anhalten oder fortsetzen
- < und >: Um eine Viertelperiode vor oder zurueck
- Phase: Zeitpunkt innerhalb einer Periode einstellen
- Tempo: Animationsgeschwindigkeit von 0.1 bis 3

## Physikalischer Zusammenhang

Die Kondensatorladung q und die mechanische Auslenkung s sind proportional zu cos(omega t). Der elektrische Strom und die mechanische Geschwindigkeit sind proportional zu sin(omega t), jeweils mit entsprechender Vorzeichenkonvention.

Elektrische Energie und magnetische Energie wechseln zwischen 0 und der konstanten Gesamtenergie:

```text
E_el / E_ges = cos(omega*t)^2
E_mag / E_ges = sin(omega*t)^2
```

Das Modell ist idealisiert: Kein elektrischer Widerstand, keine mechanische Reibung. Die gezeigte Zeitachse ist eine illustrative Skala (T = 8 s), kein realer Frequenzvergleich.

Die Schaltung und mechanische Analogie sind bewusst schematisch gezeichnet.
