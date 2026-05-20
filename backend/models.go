package main

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

// User representa a conta do cliente no MongoDB Atlas
type User struct {
	ID             primitive.ObjectID `bson:"_id,omitempty" json:"id"`
	DiscordID      string             `bson:"discord_id" json:"discord_id"`
	ClienteID      string             `bson:"cliente_id" json:"cliente_id"` // ID da HiveOS/NiceHash
	Plano          string             `bson:"plano" json:"plano"`           // FREE, PRO, ULTRA
	HiveOSToken    string             `bson:"hiveos_token" json:"hiveos_token"` // Guardado em AES-256
	Plataforma     string             `bson:"plataforma" json:"plataforma"`   // "hiveos", "nicehash", etc.
	DataCriacao    time.Time          `bson:"data_criacao" json:"data_criacao"`
	DataExpiracao  time.Time          `bson:"data_expiracao" json:"data_expiracao"`
}

// RigData representa a estrutura real de cada placa que vai para o Cache RAM e Discord
type RigData struct {
	Nome        string `bson:"nome" json:"nome"`
	Status      string `bson:"status" json:"status"`
	Temperatura int    `bson:"temperatura" json:"temperatura"`
	HashRate    string `bson:"hash_rate" json:"hash_rate"`
}
