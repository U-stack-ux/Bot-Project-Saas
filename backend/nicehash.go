package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// Estruturas para mapear a resposta real da API da NiceHash
type NiceHashResponse struct {
	MiningRigs []struct {
		Name        string  `json:"name"`
		StatusDescription string `json:"statusDescription"`
		RigDeviceWithStatuses []struct {
			Temperature int `json:"temperature"`
		} `json:"rigDeviceWithStatuses"`
	} `json:"miningRigs"`
}

// BuscarDadosNiceHash conecta direto nos servidores da NiceHash com as credenciais do cliente
func BuscarDadosNiceHash(apiKey, apiSecret, organizationId string) ([]RigData, error) {
	url := "https://api2.nicehash.com/main/api/v2/mining/rigs2"
	
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}

	// 💡 A NiceHash exige Headers específicos para validação da API Key
	req.Header.Set("X-Time", fmt.Sprintf("%d", time.Now().UnixNano()/int64(time.Millisecond)))
	req.Header.Set("X-ApiKey", apiKey)
	req.Header.Set("X-Organization-Id", organizationId)
	// Nota: Em produção, a NiceHash também exige uma assinatura HMAC no Header 'X-Auth', 
	// que geraremos com o 'apiSecret' assim que você rodar as chaves de teste.

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("erro na API da NiceHash: status %d", resp.StatusCode)
	}

	var nhResp NiceHashResponse
	if err := json.NewDecoder(resp.Body).Decode(&nhResp); err != nil {
		return nil, err
	}

	var rigs []RigData
	for _, rig := range nhResp.MiningRigs {
		temp := 0
		if len(rig.RigDeviceWithStatuses) > 0 {
			temp = rig.RigDeviceWithStatuses[0].Temperature // Pega a temperatura do primeiro dispositivo/GPU
		}

		rigs = append(rigs, RigData{
			Nome:        rig.Name,
			Status:      rig.StatusDescription,
			Temperatura: temp,
			HashRate:    "Ver no Painel", // A NiceHash calcula o Hashrate por algoritmo ativo
		})
	}

	return rigs, nil
}
