package main

import (
    "net/http"
    "os"
    "log"
)

func StartServer() {
    http.HandleFunc("/api/cmd", func(w http.ResponseWriter, r *http.Request) {
        // Validação de segurança aqui (Auth token + Plan check)
        w.Header().Set("Content-Type", "application/json")
        w.Write([]byte(`{"status":"ok"}`))
    })

    port := os.Getenv("PORT")
    if port == "" { port = "8080" }
    
    log.Fatal(http.ListenAndServe(":"+port, nil))
}
