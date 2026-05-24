package main

type HiveRig struct {
	ID     int    `json:"id"`
	Temp   int    `json:"temp"`
	Status string `json:"status"`
}

// GetHiveRigs busca os dados na API da HiveOS
func GetHiveRigs(apiKey string, farmID string) ([]HiveRig, error) {
	// A lógica de request HTTP para a API da HiveOS vai aqui
	return []HiveRig{}, nil
}

// SendHiveCommand envia o comando de PowerOn/PowerOff
func SendHiveCommand(apiKey string, rigID int, command string) error {
	return nil
}
