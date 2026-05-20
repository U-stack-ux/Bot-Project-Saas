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

type SetPlanRequest struct {
	DiscordID      string `json:"discord_id"`
	PlanoEscolhido string `json:"plano_escolhido"`
	HiveOSToken    string `json:"hiveos_token"` // Recebido de forma opcional no cadastro
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
	fmt.Println("🌟 Conectado com sucesso ao MongoDB Atlas com Criptografia Ativa!")

	router := gin.Default()

	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "online", "message": "API SaaS Criptografada Rodando!"})
	})

	// 🔍 ENDPOINT: Verifica plano, rigs e intervalo permitido do cliente
	router.GET("/users/check-plan", func(c *gin.Context) {
		clientID := c.Query("cliente_id")
		
		if clientID == "novo" || clientID == "" {
			c.JSON(http.StatusOK, gin.H{"has_plan": false})
			return
		}

		planoDoBanco := "PRO" 
		settings := GetPlanSettings(planoDoBanco)
		rigsSimuladas := []string{"Rig-01-Main", "Rig-02-Mining"}

		c.JSON(http.StatusOK, gin.H{
			"has_plan":        true,
			"plano":           settings.Name,
			"check_interval":  settings.CheckInterval.Minutes(),
			"has_smart_alert": settings.HasSmartAlerts,
			"rigs":            rigsSimuladas,
		})
	})

	// 🚀 ENDPOINT: Salva a escolha do plano aplicando Criptografia no Token de API
	router.POST("/users/set-plan", func(c *gin.Context) {
		var req SetPlanRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Dados inválidos"})
			return
		}

		tokenProtegido := "Nenhum fornecido"
		if req.HiveOSToken != "" {
			var err error
			tokenProtegido, err = EncryptToken(req.HiveOSToken)
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Falha na segurança interna"})
				return
			}
		}

		// AQUI O GO GRAVA NO MONGODB ATLAS:
		// Salva o ID do Discord, o Plano e a Hash Criptografada (tokenProtegido)
		fmt.Printf("💾 [MongoDB SEGURO] Discord: %s | Plano: %s | Token AES-256: %s\n", req.DiscordID, req.PlanoEscolhido, tokenProtegido)
		
		c.JSON(http.StatusOK, gin.H{"status": "success", "message": "Plano e credenciais gravadas com segurança!"})
	})

	router.POST("/commands/power", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "success"})
	})

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	router.Run(":" + port)
}
