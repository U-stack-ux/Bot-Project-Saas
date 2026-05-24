package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

func RequisitarDadosHive(token, farmID string) (HiveResponse, error) {
	url := fmt.Sprintf("https://hiveos.farm", farmID)
	req, _ := http.NewRequest("GET", url, nil)
	req.Header.Set("Authorization", "Bearer "+token)

	client := &http.Client{Timeout: 7 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return HiveResponse{}, err
	}
	defer resp.Body.Close()

	var resultado HiveResponse
	if resp.StatusCode == http.StatusOK {
		json.NewDecoder(resp.Body).Decode(&resultado)
		return resultado, nil
	}
	
	return HiveResponse{}, fmt.Errorf("Erro HTTP: %d", resp.StatusCode)
}
