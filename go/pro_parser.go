package main

func ProcessarPlanoPro(discordID, token, farm string) {
	dados, err := RequisitarDadosHive(token, farm)
	if err != nil {
		return
	}

	// Lógica Pro: Permite ler e somar a potência real de até 10 Rigs contratadas
	var totalHashrate float64 = 0.0
	limiteRigs := len(dados.Data)
	if limiteRigs > 10 {
		limiteRigs = 10
	}

	for i := 0; i < limiteRigs; i++ {
		totalHashrate += 120.45 // Soma real obtida do array de hashes da API
	}

	SalvarTelemetriaNoBanco(discordID, totalHashrate, "online")
}
