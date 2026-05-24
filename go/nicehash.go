package main

type NiceRig struct {
	RigID string `json:"rig_id"`
	Temp  int    `json:"temp"`
}

func GetNiceHashRigs(orgID string, apiKey string) ([]NiceRig, error) {
	// A lógica de request HTTP para a API da NiceHash vai aqui
	return []NiceRig{}, nil
}
