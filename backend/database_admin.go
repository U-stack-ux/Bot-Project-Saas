package main

import (
	"context"
	"time"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
)

// IsAdmin verifica no MongoDB se o discord_id possui a role de 'admin'
func IsAdmin(client *mongo.Client, discordID string) (bool, error) {
	// Acessa a database 'upscore_saas' e a coleção 'Administradores'
	collection := client.Database("upscore_saas").Collection("Administradores")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	var resultado bson.M
	// Procura por um documento onde o discord_id seja igual ao enviado e o papel seja admin
	filtro := bson.M{
		"discord_id": discordID,
		"papel":      "admin",
	}

	err := collection.FindOne(ctx, filtro).Decode(&resultado)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			return false, nil // Não encontrou nenhum admin com esse ID
		}
		return false, err // Outro erro qualquer de banco
	}

	return true, nil // Encontrou e é admin!
}
