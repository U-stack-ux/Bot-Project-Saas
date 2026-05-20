package main

import (
	"time"
)

type PlanTier struct {
	Name            string        `json:"name"`
	MaxRigs         int           `json:"max_rigs"`
	CheckInterval   time.Duration `json:"check_interval"`   
	AlertInterval   time.Duration `json:"alert_interval"`   
	NotifyEndOfPlan bool          `json:"notify_end_of_plan"`
	HasSmartAlerts  bool          `json:"has_smart_alerts"` 
}

func GetPlanSettings(tier string) PlanTier {
	switch tier {
	case "ULTRA":
		return PlanTier{
			Name:            "ULTRA",
			MaxRigs:         9999,
			CheckInterval:   10 * time.Second,      
			AlertInterval:   30 * 24 * time.Hour,   
			NotifyEndOfPlan: true,
			HasSmartAlerts:  true,                  
		}
	case "PRO":
		return PlanTier{
			Name:            "PRO",
			MaxRigs:         10,
			CheckInterval:   5 * time.Minute,       
			AlertInterval:   30 * 24 * time.Hour,   
			NotifyEndOfPlan: true,
			HasSmartAlerts:  true,                  
		}
	case "FREE":
		return PlanTier{
			Name:            "FREE (TESTE 3 DIAS)",
			MaxRigs:         2,
			CheckInterval:   15 * time.Minute,      
			AlertInterval:   0,                     
			NotifyEndOfPlan: true,                  
			HasSmartAlerts:  false,                 
		}
	default:
		return PlanTier{
			Name:            "FREE (TESTE 3 DIAS)",
			MaxRigs:         2,
			CheckInterval:   15 * time.Minute,      
			AlertInterval:   0,                     
			NotifyEndOfPlan: true,                  
			HasSmartAlerts:  false,                 
		}
	}
}
