package main

import "fmt"

func ExecutarFluxoMotor(discordID string) {
	// Fase 1: Validação Jurídica Obrigatória
	user := VerificarTermosContratuais(discordID)

	if !user.Configurado {
		fmt.Println("[GO INFO] Credenciais pendentes de configuração.")
		return
	}

	// Descriptografa os acessos apenas na memória RAM
	tokenReal := DescriptografarToken(user.TokenSeguro)
	farmReal := DescriptografarToken(user.FarmSegura)

	fmt.Printf("[GO] Processando requisição do Plano: %s\n", user.Plano)

	// Fase 2: Redirecionamento por tipo de plano contratado
	switch user.Plano {
	case "Free":
		ProcessarPlanoFree(user.DiscordID, tokenReal, farmReal)
	case "Pro":
		ProcessarPlanoPro(user.DiscordID, tokenReal, farmReal)
	case "Ultra":
		ProcessarPlanoUltra(user, tokenReal, farmReal)
	default:
		ProcessarPlanoFree(user.DiscordID, tokenReal, farmReal)
	}
}
