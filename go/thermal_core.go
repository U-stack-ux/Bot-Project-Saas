package main

import "fmt"

func AvaliarEstrategiaTermica(user Usuario, telemetria HiveResponse, token, farm string) {
	if !user.ProtecaoTermicaAtiva {
		return
	}

	for _, worker := range telemetria.Data {
		superaquecido := false
		for _, t := range worker.Stats.Temps {
			if t >= user.LimiteTemperatura {
				superaquecido = true
				break
			}
		}

		// Dispara ações reais de contenção baseadas no estresse de temperatura das GPUs
		if superaquecido {
			fmt.Printf("[⚠️ CORTE TÉRMICO ULTRA] Desligando minerador do Worker: %s\n", worker.Name)
			ExecutarComandoHardware(farm, worker.ID, token, "miner stop")
		} else {
			// Função opcional de rearme automático se as condições nominais voltarem
			// ExecutarComandoHardware(farm, worker.ID, token, "miner start")
		}
	}
}
