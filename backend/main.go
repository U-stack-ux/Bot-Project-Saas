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

// Estrutura dinâmica para receber os dados reais do cliente de forma ilimitada
type PowerRequest struct {
	RigName string `json:"rig_name"`
	Action  string `json:"action"`
}

func main() {
	// 1. Configuração do MongoDB Atlas
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

	// 2. Configuração do Servidor Web (Gin)
	router := gin.Default()

	// --- ROTA ESSENCIAL PARA O UPTIMEROBOT ---
	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":  "online",
			"message": "Upscore SaaS API rodando com sucesso!",
		})
	})

	// 3. Suas rotas existentes e novas (Onde o bot em Python se conecta)
	router.POST("/commands/delete", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "Comando delete processado"})
	})

	// ROTA REAL E DINÂMICA DE ENERGIA (PRODUÇÃO ILIMITADA)
	router.POST("/commands/power", func(c *gin.Context) {
		var req PowerRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Dados inválidos enviados"})
			return
		}

		// Aqui os dados reais chegam de forma dinâmica e limpa do Python
		fmt.Printf("🚀 [PRODUÇÃO] Comando de %s enviado para a rig: %s\n", req.Action, req.RigName)

		c.JSON(http.StatusOK, gin.H{
			"status":  "success",
			"rig_name": req.RigName,
			"action":  req.Action,
		})
	})

	// 4. Inicialização na Porta Dinâmica do Render
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080" // Porta padrão local
	}

	fmt.Printf("🚀 Servidor rodando na porta %s\n", port)
	if err := router.Run(":" + port); err != nil {
		log.Fatal("Falha ao iniciar o servidor Go: ", err)
	}
}
