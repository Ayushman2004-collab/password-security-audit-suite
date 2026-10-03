# Password Security Auditing & Controlled Attack Simulation Suite

A Flask-based cybersecurity lab toolkit for password-policy testing, password-strength assessment, controlled dictionary/brute-force simulations, offline hash-format identification, and security reporting.

## What this project implements

### 1. Password Strength Analyzer
- Complexity checks for lowercase, uppercase, digits, and symbols
- Entropy/search-space estimate
- Common-password detection
- Predictable sequence detection
- Repeated-character detection
- Severity classification and mitigation recommendations

### 2. Dictionary Generator
- User-supplied seed generation
- Case variations
- Leetspeak transformations
- Appended years, numbers, and symbols
- Small common-password candidate set
- Deliberately bounded educational output

### 3. Hash Testing Simulator
- SHA-256 test hashing
- Dictionary candidate comparison against a supplied SHA-256 hash
- Attempt counting
- Safe local demonstration using user-provided lab values

### 4. Offline Hash Extraction / Format Inspector
- Parses **user-supplied lab text exports** rather than accessing the host's credential stores
- Accepts shadow-style `username:hash` records and standalone hash lists
- Identifies common formats such as Linux shadow SHA-256/SHA-512, bcrypt, yescrypt, MD5, SHA-1, SHA-256, SHA-512, and NTLM/MD5-length hashes
- Explicitly reports the MD5/NTLM ambiguity of a bare 32-character hexadecimal digest

> The project does **not** read `/etc/shadow`, SAM, or SYSTEM hives automatically. For safety and portability, the Hash Format Inspector operates only on lab data that the tester explicitly supplies or uploads.

### 5. Brute-Force Simulator
- Incremental candidate enumeration
- Lowercase, uppercase, letters, digits, alphanumeric, and symbol character sets
- Maximum length limited to four characters for the classroom simulation
- SHA-256 comparison of each candidate
- Attempts and measured attempts/second
- Search-space calculation
- Estimated worst-case time based on the measured local rate

### 6. Security Reporting
- JSON report
- CSV report
- Password strength/severity summary
- Dictionary and brute-force match counts
- Attempts, rate, search space, and estimated worst-case time where available

## Architecture

```text
                    +----------------------+
                    |    Flask Dashboard   |
                    +----------+-----------+
                               |
        +----------------------+----------------------+
        |          |             |          |          |
   Analyzer   Dictionary    Hash Test   Brute Force  Reports
        |          |             |          |          |
        +----------+-------------+----------+----------+
                               |
                    +----------v-----------+
                    |   Security Results   |
                    +----------------------+
                               |
                    +----------v-----------+
                    | JSON / CSV Reporting |
                    +----------------------+

   Separate lab-data workflow:
   supplied text/export -> Hash Format Inspector -> format identification
```

## Red-team techniques demonstrated

- Password dictionary generation and mutation
- Dictionary-based password testing
- Hash comparison
- Controlled brute-force enumeration
- Search-space and cracking-time estimation

## Blue-team techniques demonstrated

- Password-strength assessment
- Entropy and search-space analysis
- Detection of common/predictable passwords
- Risk/severity classification
- Authentication-security recommendations
- Audit reporting

## Ethical scope

Use only passwords, hashes, and lab exports that you own or are explicitly authorized to test. The application is intentionally local and bounded. It does not connect to login services, perform network authentication attacks, harvest credentials, or automatically access Windows SAM/SYSTEM or Linux `/etc/shadow` databases.

## Project structure

```text
password_security_dashboard/
├── app.py
├── modules/
│   ├── analyzer.py
│   ├── brute_force.py
│   ├── dictionary_generator.py
│   ├── hash_formats.py
│   ├── hash_simulator.py
│   └── report.py
├── templates/
├── static/
├── data/
├── reports/
├── lab_samples/
├── tests/
└── requirements.txt
```

## Windows setup

```text
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Linux/macOS

```text
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

## Recommended demo sequence

1. Open **Password Analyzer** and test `password123`.
2. Open **Dictionary Generator** and generate a small lab wordlist.
3. Open **Hash Simulator** and use the displayed SHA-256 demo hash.
4. Open **Brute-Force Simulator**, select lowercase, and test `abc` with maximum length 3.
5. Open **Hash Format Inspector** and load `lab_samples/sample_hash_export.txt`.
6. Generate the JSON + CSV security report.

## Limitations and future extensions

The project deliberately does not perform live credential extraction. A production-grade authorized auditing platform could add a separately isolated import pipeline for organization-approved exports, additional password-hash verification libraries, authenticated access controls, persistent storage, CSRF protection, and role-based reporting.
