  - task: "Creazione capo promoter con organizzazione opzionale"
    implemented: true
    working: true
    file: "server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "Test completato con successo. Verificato che si può creare un capo promoter senza specificare un'organizzazione (campo opzionale). L'API funziona correttamente sia con organizzazione specificata che senza. Il campo organizzazione viene impostato come 'Da assegnare' quando non specificato."