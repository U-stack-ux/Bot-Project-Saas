package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"time"

	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// ConectarDB inicializa a conexão com o MongoDB Atlas
func ConectarDB() *mongo.Client {
	mongoURI := os.Getenv("MONGO_URI")
	if mongoURI == "" {
		log.Fatal("❌ A variável de ambiente MONGO_URI não foi definida no Render")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	client, err := mongo.Connect(ctx, options.Client().ApplyURI(mongoURI))
	if err != nil {
		log.Fatal("❌ Erro ao conectar ao MongoDB Atlas:", err)
	}

	// Verifica se a conexão está realmente ativa
	err = client.Ping(ctx, nil)
	if err != nil {
		log.Fatal("❌ Não foi possível dar ping no MongoDB Atlas:", err)
	}

	fmt.Println("🍁 [Database] Conexão com o MongoDB Atlas estabelecida com sucesso!")
	return client
}
