// Adicione esta função ao seu database.go

func DeleteUserFromDB(discordID string) error {
	collection := client.Database("upscore_saas").Collection("clients")
	
	// Deleta o documento inteiro do usuário
	_, err := collection.DeleteOne(context.TODO(), bson.M{"discord_id": discordID})
	return err
}
