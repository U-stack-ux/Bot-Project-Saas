package main

// Usuario representa o documento do MongoDB preenchido pelo Python
type Usuario struct {
	DiscordID            string `bson:"discord_id"`
	Plano                string `bson:"plano"`
	TermosAceitos        bool   `bson:"termos_aceitos"`
	Configurado          bool   `bson:"configurado"`
	TokenSeguro          string `bson:"token_seguro"`
	FarmSegura           string `bson:"farm_segura"`
	LimiteTemperatura    int    `bson:"limite_temperatura"`
	ProtecaoTermicaAtiva bool   `bson:"protecao_termica_ativa"`
}

// HiveResponse mapeia a estrutura de telemetria real devolvida pelo HiveOS
type HiveResponse struct {
	Data []struct {
		ID    int    `json:"id"`
		Name  string `json:"name"`
		Stats struct {
			Temps []int `json:"temps"`
		} `json:"stats"`
	} `json:"data"`
}
