package main

import (
	"fmt"
	"os"
)

func main() {
	// Verifica se o Python passou o ID por argumento
	if len(os.Args) < 2 {
		fmt.Println("[GO CRÍTICO] Nenhum Discord ID foi fornecido pelo Python.")
		os.Exit(1)
	}
	discordID := os.Args[1]

	// Inicializa e executa o roteamento inteligente
	ExecutarFluxoMotor(discordID)
}
