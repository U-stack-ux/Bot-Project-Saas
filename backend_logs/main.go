package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"github.com/joho/godotenv"
)

func main() {
	godotenv.Load()
	InitDB()
	fmt.Println("🛡️  UpScore Engine: Sistema de Monitoramento Real Ativo")

	// Rota que o Python chama para atualizar o Dashboard
	http.HandleFunc("/monitorar", func(w http.ResponseWriter, r *http.Request) {
		discordID := r.URL.Query().Get("id")
		
		// 1. Busca usuário e token criptografado
		user, err := GetUserFromDB(discordID)
		if err != nil { w.WriteHeader(404); return }

		// 2. Busca dados REAIS na HiveOS
		stats, err := GetHiveStats(user.HiveToken)
		if err != nil { w.WriteHeader(500); return }

		// 3. Devolve JSON limpo para o Python
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(stats)
	})

	http.ListenAndServe(":8080", nil)
}
// Adicione esta rota dentro da função main() do seu main.go

http.HandleFunc("/logs", func(w http.ResponseWriter, r *http.Request) {
id := r.URL.Query().Get("id")
logs, _ := GetLogs(id)
w.Header().Set("Content-Type", "application/json")
json.NewEncoder(w).Encode(logs)
})
// Adicione esta rota dentro da função main() do seu main.go

	http.HandleFunc("/logs", func(w http.ResponseWriter, r *http.Request) {
		id := r.URL.Query().Get("id")
		logs, _ := GetLogs(id)
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(logs)
	})
