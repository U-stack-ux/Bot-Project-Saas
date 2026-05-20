package main

import (
	"time"
)

type PlanTier struct {
	Name            string        `json:"name"`
	MaxRigs         int           `json:"max_rigs"`
	CheckInterval   time.Duration `json:"check_interval"`   // Tempo de loop de cada plano
	AlertInterval   time.Duration `json:"alert_interval"`   // Lembrete de 30 dias
	NotifyEndOfPlan bool          `json:"notify_end_of_plan"`
	HasSmartAlerts  bool          `json:"has_smart_alerts"` // Avisos imediatos na DM por temperatura
}

func GetPlanSettings(tier string) PlanTier {
	switch tier {
	case "ULTRA":
		return PlanTier{
			Name:            "ULTRA",
			MaxRigs:         9999,
			CheckInterval:   1 * time.Minute,       // 🔥 ATUALIZA A CADA 1 MINUTO
			AlertInterval:   30 * 24 * time.Hour,   // Relatório a cada 30 dias
			NotifyEndOfPlan: true,
			HasSmartAlerts:  true,                  // Termômetro Inteligente Ativo
		}
	case "PRO":
		return PlanTier{
			Name:            "PRO",
			MaxRigs:         10,
			CheckInterval:   5 * time.Minute,       // 💎 ATUALIZA A CADA 5 MINUTOS
			AlertInterval:   30 * 24 * time.Hour,   // Relatório a cada 30 dias
			NotifyEndOfPlan: true,
			HasSmartAlerts:  true,                  // Termômetro Inteligente Ativo
		}
	case "FREE":
	default:
		return PlanTier{
			Name:            "FREE (TESTE 3 DIAS)",
			MaxRigs:         2,
			CheckInterval:   15 * time.Minute,      // 🥑 ATUALIZA A CADA 15 MINUTOS
			AlertInterval:   0,                     // Sem avisos mensais
			NotifyEndOfPlan: true,                  // Apenas aviso de fim de plano!
			HasSmartAlerts:  false,                 // Sem alertas térmicos imediatos
		}
	}
}
