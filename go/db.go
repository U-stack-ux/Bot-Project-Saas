package main

import (
	"context"
	"time"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

var mongoClient *mongo.Client

func ObterBanco() *mongo.Database {
	if mongoClient == nil {
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		
		client, err := mongo.Connect(ctx, options.Client().ApplyURI(ObterMongoURI()))
		if err != nil {
			panic(err)
		}
		mongoClient = client
	}
	return mongoClient.Database("bot_mineracao")
}
