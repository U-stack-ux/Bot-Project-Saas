package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"go.mongodb.org/mongo-driver/mongo"
)

// IniciarServidorWeb roda o site e o recebimento de dados em segundo plano
func IniciarServidorWeb(mongoClient *mongo.Client) {
	
	// Rota para servir o arquivo index.html (o seu site)
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		http.ServeFile(w, r, "index.html")
	})

	// Rota para receber os dados do formulário e salvar no MongoDB
	http.HandleFunc("/enviar-dados", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Método não permitido", http.StatusMethodNotAllowed)
			return
		}

		// Pega os dados digitados no site pelo cliente
		nome := r.FormValue("nome")
		usuario := r.FormValue("usuario")
		idade := r.FormValue("idade")

		// Cria o documento ultra-compacto (Economiza seus 512MB do Mongo!)
		provaJuridica := map[string]interface{}{
			"n": nome,    // Nome completo
			"u": usuario, // Usuário do Discord
			"i": idade,   // Idade
			"t": 1,       // Termos aceitos (1 = Sim)
			"p": 0,       // Plano (0 = Free, 1 = Pro, 2 = Ultra)
			"d": time.Now().Format("02/01/2006 15:04"), // Data e hora do aceite
		}

		// Salva na coleção "clientes" do seu MongoDB
		colecao := mongoClient.Database("bot_saas").Collection("clientes")
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()

		_, err := colecao.InsertOne(ctx, provaJuridica)
		if err != nil {
			http.Error(w, "Erro ao salvar os dados no banco", http.StatusInternalServerError)
			return
		}

		// Alerta bonito na tela e joga o cliente de volta para o Discord
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		w.Write([]byte(`
			<script>
				alert("Termos aceitos com sucesso! Volte para o Discord e verifique sua DM.");
				window.location.href = "https://discord.com/app";
			</script>
		`))
	})

	// Inicia o servidor na porta que o Render exige
	go func() {
		port := os.Getenv("PORT")
		if port == "" {
			port = "8080" // Porta padrão local caso não ache a do Render
		}
		fmt.Println("🌐 Servidor Web do Site ativo na porta:", port)
		if err := http.ListenAndServe(":"+port, nil); err != nil {
			log.Printf("Erro no servidor web: %v", err)
		}
	}()
}
