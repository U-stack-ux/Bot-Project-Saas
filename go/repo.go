package main

import (
	"context"
	"time"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo/options"
)

func FormatarTempoAgora() string {
	return time.Now().Format("02/01/2006 15:04:05")
}

func SalvarTelemetriaNoBanco(discordID string, hashrate float64, status string) {
	db := ObterBanco()
	coll := db.Collection("rigs")

	filtro := bson.M{"discord_id": discordID}
	update := bson.M{
		"$set": bson.M{
			"hashrate":      hashrate,
			"status":        status,
			"atualizado_em": FormatarTempoAgora(),
		},
	}
	opts := options.Update().SetUpsert(true)
	_, _ = coll.UpdateOne(context.Background(), filtro, update, opts)
}
