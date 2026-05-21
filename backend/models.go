package main

import "time"

// RigData unifica os dados reais vindos da HiveOS, NiceHash ou RaveOS
type RigData struct {
	Nome        string `json:"nome"`
	Status      string `json:"status"`
	Temperatura int    `json:"temperatura"`
	HashRate    string `json:"hashrate"`
}

// User representa a estrutura real do cliente salva no MongoDB Atlas
type User struct {
	DiscordID     string    `bson:"discord_id" json:"discord_id"`
	ClientID      string    `bson:"cliente_id" json:"cliente_id"`
	ApiToken      string    `bson:"api_token" json:"api_token"`
        DisclaimerAccepted bool `bson:"disclaimer_accepted" json:"disclaimer_accepted"`
        Plano         string    `bson:"plano" json:"plano"`
	HiveOSToken   string    `bson:"hiveos_token" json:"hiveos_token"`
	Plataforma    string    `bson:"plataforma" json:"plataforma"`
	DataCriacao   time.Time `bson:"data_criacao" json:"data_criacao"`
	DataExpiracao time.Time `bson:"data_expiracao" json:"data_expiracao"`
}
