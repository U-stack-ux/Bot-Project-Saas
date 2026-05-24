package main

import (
	"context"
	"fmt"
	"os"
	"go.mongodb.org/mongo-driver/bson"
)

func VerificarTermosContratuais(discordID string) Usuario {
	db := ObterBanco()
	var user Usuario
	
	err := db.Collection("usuarios").FindOne(context.Background(), bson.M{"discord_id": discordID}).Decode(&user)
	if err != nil {
		fmt.Printf("[GO AVISO] Usuário %s não localizado na base.\n", discordID)
		os.Exit(0)
	}

	// Trava de segurança absoluta solicitada
	if !user.TermosAceitos {
		fmt.Printf("[💥 ACESSO NEGADO] Usuário %s tentou rodar sem assinar os termos jurídicos!\n", discordID)
		os.Exit(0)
	}
	
	return user
}
