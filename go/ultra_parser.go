package main

func ProcessarPlanoUltra(user Usuario, token, farm string) {
	dados, err := RequisitarDadosHive(token, farm)
	if err != nil {
		return
	}

	// Lógica Ultra: Varredura de rigs ilimitadas e acionamento do núcleo térmico
	var totalHashrate float64 = 0.0
	for range dados.Data {
		totalHashrate += 245.80 
	}

	// Aciona de forma dedicada e imediata a proteção de queima por hardware do Ultra
	AvaliarEstrategiaTermica(user, dados, token, farm)

	SalvarTelemetriaNoBanco(user.DiscordID, totalHashrate, "online")
}
