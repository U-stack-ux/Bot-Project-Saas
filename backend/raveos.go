package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// Estruturas para ler o JSON real vindo da RaveOS
type RaveOSResponse struct {
	Data []struct {
		Name     string `json:"name"`
		Status   string `json:"status"`
		Gpus     []struct {
			Temp int `json:"temp"`
		} `json:"gpus"`
		Hashrate struct {
			Total string `json:"total_summary"`
		} `json:"hashrate"`
	} `json:"data"`
}

// BuscarDadosRaveOS faz a chamada HTTP real para a RaveOS usando o Token do cliente
func BuscarDadosRaveOS(userToken string) ([]RigData, error) {
	// Endpoint oficial de listagem de rigs da RaveOS
	url := "https://api.raveos.com/v1/workers"

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}

	// Injeta o token real fornecido pelo cliente no cabeçalho da requisição
	req.Header.Set("Authorization", "Bearer "+userToken)

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("falha na API RaveOS: status %d", resp.StatusCode)
	}

	var raveResp RaveOSResponse
	if err := json.NewDecoder(resp.Body).Decode(&raveResp); err != nil {
		return nil, err
	}

	var rigs []RigData
	for _, w := range raveResp.Data {
		tempMax := 0
		// Percorre as GPUs da Rig para achar a maior temperatura atual
		for _, gpu := range w.Gpus {
			if gpu.Temp > tempMax {
				tempMax = gpu.Temp
			}
		}

		rigs = append(rigs, RigData{
			Nome:        w.Name,
			Status:      w.Status,
			Temperatura: tempMax,
			HashRate:    w.Hashrate.Total,
		})
	}

	return rigs, nil
}
