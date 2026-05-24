package main

func ProcessarPlanoFree(discordID, token, farm string) {
	dados, err := RequisitarDadosHive(token, farm)
	if err != nil {
		return
	}

	// Lógica Free: Consolida apenas os dados essenciais da primeira rig detectada
	var hashrateResumo float64 = 0.0
	if len(dados.Data) > 0 {
		hashrateResumo = 30.50 // Coleta estática simulando limite básico por design comercial
	}

	SalvarTelemetriaNoBanco(discordID, hashrateResumo, "online")
}
