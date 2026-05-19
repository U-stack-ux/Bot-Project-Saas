package main

import (
	"context"
	"time"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

var client *mongo.Client

func InitDB() {
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	client, _ = mongo.Connect(ctx, options.Client().ApplyURI("mongodb://localhost:27017"))
}

func LogActivity(discordID, rigName, action, details string) {
	col := client.Database("upscore").Collection("logs")
	col.InsertOne(context.TODO(), bson.M{
		"discord_id": discordID,
		"rig_name":   rigName,
		"action":     action,
		"details":    details,
		"timestamp":  time.Now(),
	})
}

func DeleteUser(discordID string) error {
	col := client.Database("upscore").Collection("users")
	_, err := col.DeleteOne(context.TODO(), bson.M{"discord_id": discordID})
	return err
}
