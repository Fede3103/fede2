# Fedekeanu Tracker

Piccola demo didattica per un test di privacy. La raccolta dell'IP e dello user-agent avviene **solo dopo** che il visitatore ha letto l'informativa e selezionato la casella di consenso.

## Dati raccolti
- IP pubblico (non GPS e non indirizzo civico)
- User-agent (informazioni dichiarate dal browser su browser/dispositivo)
- Data e ora UTC dell'invio del consenso

Non integra geolocalizzazione IP, fingerprinting, pixel nascosti o tracciamento automatico. L'hosting potrebbe conservare propri log tecnici: verifica le condizioni del provider.

## Avvio locale
Richiede Python 3.10+.

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

Imposta le variabili d'ambiente prima di avviare:

Windows PowerShell:
```powershell
$env:SECRET_KEY="inserisci-una-stringa-lunga-casuale"
$env:ADMIN_PASSWORD="scegli-una-password-lunga"
python app.py
```

macOS/Linux:
```bash
export SECRET_KEY="inserisci-una-stringa-lunga-casuale"
export ADMIN_PASSWORD="scegli-una-password-lunga"
python app.py
```

Apri `http://127.0.0.1:5000`. Dashboard: `http://127.0.0.1:5000/admin`.

## Pubblicazione
Puoi pubblicarlo su un hosting Python che supporti Flask e Gunicorn (ad esempio Render). Carica questa cartella su un repository Git e crea un Web Service usando `requirements.txt` e `gunicorn app:app`. Imposta obbligatoriamente:
- `SECRET_KEY`: stringa casuale lunga e segreta
- `ADMIN_PASSWORD`: password lunga e unica

Il file `render.yaml` è un punto di partenza. Il database SQLite su filesystem effimero può essere azzerato al riavvio o al redeploy; per conservazione persistente configura un disco persistente o un database gestito. Non usare `/tmp` per dati che vuoi conservare.

## Prima di usarlo con partecipanti
- Condividi il link solo con persone che sanno che si tratta di un test.
- Mantieni visibile e comprensibile l'informativa prima del consenso.
- Definisci finalità, base giuridica, periodo di conservazione e modalità per esercitare i diritti applicabili; per una tesi, confrontati con relatore/ateneo e, se necessario, DPO.
- Non tentare di ricavare indirizzi civici da IP. La geolocalizzazione IP è imprecisa e non equivale a una posizione GPS.
- Cancella i dati appena non sono più necessari.

Questa demo non costituisce consulenza legale o una valutazione GDPR.


## Campi tecnici aggiuntivi
Dopo il consenso esplicito vengono inviati: tipo dispositivo stimato, sistema operativo e browser stimati, lingua e lingue dichiarate, risoluzione schermo, dimensioni finestra, fuso orario, protocollo, user-agent e infine IP pubblico. Le stime basate sullo user-agent possono essere inesatte. Non viene raccolto il referrer, GPS o posizione precisa.
