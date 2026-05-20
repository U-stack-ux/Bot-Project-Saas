package main

import (
	"time"
)

// PlanTier define os limites rígidos e os tempos de alerta de cada plano
type PlanTier struct {
	Name            string        `json:"name"`
	MaxRigs         int           `json:"max_rigs"`
	AlertInterval   time.Duration `json:"alert_interval"` // Intervalo de avisos periódicos
	NotifyEndOfPlan bool          `json:"notify_end_of_plan"`
}

// GetPlanSettings centraliza a lógica dos 3 planos (FREE, PRO, ULTRA)
func GetPlanSettings(tier string) PlanTier {
	switch tier {
	case "ULTRA":
		return PlanTier{
			Name:            "ULTRA",
			MaxRigs:         9999,                 // Ilimitado de verdade
			AlertInterval:   30 * 24 * time.Hour,  // Alertas automáticos a cada 30 dias
			NotifyEndOfPlan: true,
		}
	case "PRO":
		return PlanTier{
			Name:            "PRO",
			MaxRigs:         10,                   // Limite de produção plano médio
			AlertInterval:   30 * 24 * time.Hour,  // Alertas automáticos a cada 30 dias
			NotifyEndOfPlan: true,
		}
	case "FREE":
	default:
		return PlanTier{
			Name:            "FREE (TESTE 3 DIAS)",
			MaxRigs:         2,                    // Limite severo para forçar upgrade
			AlertInterval:   0,                    // ZERO avisos a cada 30 dias
			NotifyEndOfPlan: true,                 // Apenas aviso de fim de plano!
		}
	}
}
