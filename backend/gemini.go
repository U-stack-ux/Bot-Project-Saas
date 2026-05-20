package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
)

// Estruturas de dados para conversar com a API do Gemini
type GeminiRequest struct {
	Contents []GeminiContent `json:"contents"`
}

type GeminiContent struct {
	Parts []GeminiPart `json:"parts"`
}

type GeminiPart struct {
	Text string `json:"text"`
}

type GeminiResponse struct {
	Candidates []struct {
		Content struct {
			Parts []struct {
				Text string `json:"text"`
			} `json:"parts"`
		} `json:"content"`
	} `json:"candidates"`
}

// AnalisarErroComIA envia os dados da Rig com defeito para o Gemini diagnosticar
func AnalisarErroComIA(dadosRig string, idioma string) (string, error) {
	apiKey := os.Getenv("GEMINI_API_KEY")
	if apiKey == "" {
		return "Erro interno: Inteligência Artificial temporariamente indisponível.", fmt.Errorf("GEMINI_API_KEY faltando")
	}

	url := "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + apiKey

	// Prompt de Engenharia de Contexto para blindar a IA e fazê-la agir como especialista
	prompt := fmt.Sprintf(
		"Você é a inteligência artificial integrada do Upscore SaaS, um engenheiro especialista em mineração de criptomoedas de nível mundial. "+
			"Analise o seguinte relatório de telemetria e erro da Rig do cliente: '%s'. "+
			"Gere um diagnóstico direto, curto, objetivo e dê a solução exata (ajuste de overclock, troca de cabos, refrigeração). "+
			"Regra crucial: Responda estritamente no idioma '%s' de forma natural.", dadosRig, idioma,
	)

	reqBody := GeminiRequest{
		Contents: []GeminiContent{
			{
				Parts: []GeminiPart{
					{Text: prompt},
				},
			},
		},
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return "", err
	}

	resp, err := http.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	var geminiResp GeminiResponse
	if err := json.Unmarshal(body, &geminiResp); err != nil {
		return "", err
	}

	if len(geminiResp.Candidates) > 0 && len(geminiResp.Candidates[0].Content.Parts) > 0 {
		return geminiResp.Candidates[0].Content.Parts[0].Text, nil
	}

	return "A IA analisou os dados, mas não conseguiu gerar um diagnóstico preciso no momento.", nil
}
