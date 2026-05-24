package main

import "os"

func ObterMongoURI() string {
	uri := os.Getenv("MONGO_URI")
	if uri == "" {
		panic("MONGO_URI não configurado no ambiente do Go.")
	}
	return uri
}

func ObterChaveCripto() []byte {
	key := os.Getenv("ENCRYPTION_KEY")
	if key == "" {
		panic("ENCRYPTION_KEY não configurada no ambiente do Go.")
	}
	return []byte(key)
}
