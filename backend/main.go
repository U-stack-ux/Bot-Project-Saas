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

func main() {
	// 1. Configuração do MongoDB Atlas (puxando a URI das variáveis de ambiente)
	mongoURI := os.Getenv("MONGO_URI")
	if mongoURI == "" {
		log.Fatal("A variável de ambiente MONGO_URI não foi definida")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	client, err := mongo.Connect(ctx, options.Client().ApplyURI(mongoURI))
	if err != nil {
		log.Fatal("Erro ao conectar ao MongoDB:", err)
	}
	mongoClient = client
	fmt.Println("🍁 Conectado com sucesso ao MongoDB Atlas!")

	// 2. Configuração do Servidor Web (Gin)
	router := gin.Default()

	// --- ROTA ESSENCIAL PARA O UPTIMEROBOT ---
	// Quando o UptimeRobot acessar seu link, o Go vai responder 200 OK e a luz fica VERDE
	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":  "online",
			"message": "Upscore SaaS API rodando com sucesso!",
		})
	})

	// 3. Suas rotas existentes (Onde o bot em Python se conecta)
	router.POST("/commands/delete", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "Comando delete processado"})
	})

	// 4. Inicialização na Porta Dinâmica do Render
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080" // Porta padrão local
	}

	fmt.Printf("🚀 Servidor rodando na porta %s\n", port)
	if err := router.Run(":" + port); err != nil {
		log.Fatal("Falha ao iniciar o servidor Go:", err)
	}
}
