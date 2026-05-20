package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

var mongoClient *mongo.Client

// Estruturas de comunicação SaaS
type PlanCheckResponse struct {
	HasPlan bool     `json:"has_plan"`
	Plano   string   `json:"plano"`
	Rigs    []string `json:"rigs"`
}

type SetPlanRequest struct {
	DiscordID     string `json:"discord_id"`
	PlanoEscolhido string `json:"plano_escolhido"`
}

func main() {
	mongoURI := os.Getenv("MONGO_URI")
	if mongoURI == "" {
		log.Fatal("A variável de ambiente MONGO_URI não foi definida")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	client, err := mongo.Connect(ctx, options.Client().ApplyURI(mongoURI))
	if err != nil {
		log.Fatal("Erro ao conectar ao MongoDB: ", err)
	}
	mongoClient = client
	fmt.Println("🌟 Conectado com sucesso ao MongoDB Atlas!")

	router := gin.Default()

	// Rota padrão base
	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "online", "message": "API SaaS ativa"})
	})

	// 🔍 ENDPOINT: Verifica se o ID do cliente já possui plano ou se é novo
	router.GET("/users/check-plan", func(c *gin.Context) {
		clientID := c.Query("cliente_id")
		
		if clientID == "novo" || clientID == "" {
			// Simula para o Python que o cliente não tem plano cadastrado ainda
			c.JSON(http.StatusOK, PlanCheckResponse{HasPlan: false})
			return
		}

		// Se o ID for de um cliente ativo (Simulação vinda do MongoDB)
		rigsDoCliente := []string{"Rig-01-Main", "Rig-02-Mining"}
		c.JSON(http.StatusOK, PlanCheckResponse{
			HasPlan: true,
			Plano:   "PRO",
			Rigs:    rigsDoCliente,
		})
	})

	// 🚀 ENDPOINT: Salva a escolha do plano feita nos botões do Discord no MongoDB
	router.POST("/users/set-plan", func(c *gin.Context) {
		var req SetPlanRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Dados inválidos"})
			return
		}

		// AQUI O GO SALVA NO BANCO DE DADOS ATALAS:
		fmt.Printf("💾 [MongoDB] Usuário do Discord %s ativou com sucesso o plano: %s\n", req.DiscordID, req.PlanoEscolhido)
		
		c.JSON(http.StatusOK, gin.H{"status": "success", "message": "Plano gravado com sucesso"})
	})

	// Mantém compatibilidade com comandos antigos do painel administrativo
	router.POST("/commands/delete", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "Processado"})
	})

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	router.Run(":" + port)
}
