package main

import (
	"crypto/aes"
	"crypto/cipher"
	"encoding/base64"
)

func DescriptografarToken(textoCripto string) string {
	if textoCripto == "" {
		return ""
	}
	dados, _ := base64.StdEncoding.DecodeString(textoCripto)
	if len(dados) < 16 {
		return ""
	}
	
	chave := ObterChaveCripto()
	block, _ := aes.NewCipher(chave[:32]) // AES-256 usando os 32 bytes da sua chave
	decrypted := make([]byte, len(dados))
	
	iv := dados[:16]
	stream := cipher.NewCFBDecrypter(block, iv)
	stream.XORKeyStream(decrypted, dados[16:])
	return string(decrypted)
}
