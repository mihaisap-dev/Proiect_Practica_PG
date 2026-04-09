# Sistem ERP - Control Calitate Productie (P&G Practica)

Acest proiect reprezinta o solutie completa pentru monitorizarea calitatii produselor intr-o linie de productie, folosind **FastAPI**, **PostgreSQL** si un pipeline de **CI/CD (GitHub Actions)**.

## Cum pornesti aplicația local

### 1. Pregatirea mediului
Asigura-te că ai Python instalat, apoi ruleaza in terminal:
```bash
# Creare mediu virtual
python -m venv venv
source venv/bin/activate  # Pe Mac/Linux
# venv\Scripts\activate   # Pe Windows

# Instalare dependente
pip install -r requirements.txt

# Ruleaza scriptul de modele pentru a crea tabelele si a introduce datele de test:
python3 models.py

# Pornirea Serverului API
python3 main.py
```

Deschide interfata apasand pe index.html
Exemple de introdus:
1. 
ID Produs: 88823141
Master Name: CM-10001
Parametru: Volum - 500
Rezultat asteptat: CONFORM

2.
ID Produs: 88823141
Master Name: CM-10001
Parametru: Volum - 400
Rezultat asteptat: Respins (Valoare prea mica)

3.
ID Produs: 88823141
Master Name: CM-10001
Parametru: Volum - 600
Rezultat asteptat: Respins (Valoare prea mare)

4.
2.
ID Produs: 88823141
Master Name: abcdef
Parametru: Volum - 500
Rezultat asteptat: Specificatia nu exista in baza de date
