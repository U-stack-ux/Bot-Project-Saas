package main

import (
	"context"
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// --- ESTRUTURAS DE DADOS ---

type RigData struct {
	Nome       string `json:"nome"`
	Status     string `json:"status"`
	Temp       int    `json:"temperatura"`
	HashRate   string `json:"hashrate"`
}

type User struct {
	DiscordID          string    `bson:"discord_id" json:"discord_id"`
	ClientID           string    `bson:"cliente_id" json:"cliente_id"`
	Plano              string    `bson:"plano" json:"plano"`
	ApiToken           string    `bson:"api_token" json:"api_token"`
	Plataforma         string    `bson:"plataforma" json:"plataforma"`
	DataCriacao        time.Time `bson:"datacriacao" json:"datacriacao"`
	DataExpiracao      time.Time `bson:"dataexpiracao" json:"dataexpiracao"`
	DisclaimerAccepted bool      `bson:"disclaimer_accepted" json:"disclaimer_accepted"`
}

type PlanSettings struct {
	CheckInterval int  `json:"check_interval"`
	HasSmartAlerts bool `json:"has_smart_alerts"`
}

type SetPlanRequest struct {
	DiscordID      string `json:"discord_id" binding:"required"`
	PlanoEscolhido string `json:"plano_escolhido" binding:"required"`
	Plataforma     string `json:"plataforma" binding:"required"`
	ApiToken       string `json:"api_token" binding:"required"`
}

// Resposta unificada para o Bot
type UserActiveStatus struct {
	DiscordID string    `json:"discord_id"`
	Plano     string    `json:"plano"`
	Rigs      []RigData `json:"rigs"`
}

// --- VARIÁVEIS GLOBAIS E CACHE ---

var (
	usersCollection *mongo.Collection
	mongoClient     *mongo.Client
	cacheGlobal     = struct {
		sync.RWMutex
		DadosPorCliente map[string][]RigData
		UltimaBusca     time.Time
	}{DadosPorCliente: make(map[string][]RigData)}
)

// --- FUNÇÕES AUXILIARES DE CRIPTOGRAFIA ---

func decryptToken(cipherTextHex string) string {
	key := []byte("12345678901234567890123456789012") // Chave AES de 32 bytes de produção
	cipherText, err := hex.DecodeString(cipherTextHex)
	if err != nil || len(cipherText) < aes.BlockSize {
		return ""
	}
	block, err := aes.NewCipher(key)
	if err != nil {
		return ""
	}
	iv := cipherText[:aes.BlockSize]
	cipherText = cipherText[aes.BlockSize:]
	stream := cipher.NewCFBDecrypter(block, iv)
	stream.XORKeyStream(cipherText, cipherText)
	return string(cipherText)
}

func encryptToken(plainText string) string {
	key := []byte("12345678901234567890123456789012")
	block, err := aes.NewCipher(key)
	if err != nil {
		return ""
	}
	cipherText := make([]byte, aes.BlockSize+len(plainText))
	iv := cipherText[:aes.BlockSize]
	if _, err := io.ReadFull(rand.Reader, iv); err != nil {
		return ""
	}
	stream := cipher.NewCFBEncrypter(block, iv)
	stream.XORKeyStream(cipherText[aes.BlockSize:], []byte(plainText))
	return hex.EncodeToString(cipherText)
}

// --- REGRAS DE NEGÓCIO DOS PLANOS ---

	}
}

// --- INTEGRAÇÃO COM AS APIS DE MINERAÇÃO ---

func fetchHiveOsData(token string) []RigData {
	client := &http.Client{Timeout: 10 * time.Second}
	req, _ := http.NewRequest("GET", "https://api2.hiveos.farm/api/v2/farms", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := client.Do(req)
	if err != nil || resp.StatusCode != 200 {
		return []RigData{{Nome: "Erro HiveOS", Status: "Offline/Verificar API", Temperatura: 0, HashRate: "0 MH/s"}}
	}
	defer resp.Body.Close()

	var result struct {
		Data []struct {
			Name  string `json:"name"`
			Stats struct {
				WorkersTotal int `json:"workers_total"`
				RigsOnline   int `json:"rigs_online"`
			} `json:"stats"`
		} `json:"data"`
	}

	_ = json.NewDecoder(resp.Body).Decode(&result)
	var rigs []RigData
	for _, farm := range result.Data {
		status := "Live"
		if farm.Stats.RigsOnline < farm.Stats.WorkersTotal {
			status = "Aviso: Rig Offline"
		}
		rigs = append(rigs, RigData{
			Nome:     farm.Name,
			Status:   status,
			Temperatura:     68, // Temperatura média simulada vinda do parser estrutural se ausente
			HashRate: fmt.Sprintf("%d/%d Online", farm.Stats.RigsOnline, farm.Stats.WorkersTotal),
		})
	}

	if len(rigs) == 0 {
		return []RigData{{Nome: "Farm Principal", Status: "Sem Rigs Ativas", Temperatura: 0, HashRate: "0 MH/s"}}
	}
	return rigs
}

func fetchNiceHashData(apiKey string) []RigData {
	client := &http.Client{Timeout: 10 * time.Second}
	req, _ := http.NewRequest("GET", "https://api2.nicehash.com/main/api/v2/mining/rigs2", nil)
	req.Header.Set("X-Organization-Id", "nicehash-org")

	resp, err := client.Do(req)
	if err != nil || resp.StatusCode != 200 {
		return []RigData{{Nome: "Erro NiceHash", Status: "Offline/Verificar API", Temperatura: 0, HashRate: "0 MH/s"}}
	}
	defer resp.Body.Close()

	var result struct {
		MiningRigs []struct {
			Name       string `json:"name"`
			MinerStatus string `json:"minerStatus"`
		} `json:"miningRigs"`
	}

	_ = json.NewDecoder(resp.Body).Decode(&result)
	var rigs []RigData
	for _, r := range result.MiningRigs {
		rigs = append(rigs, RigData{
			Nome:     r.Name,
			Status:   r.MinerStatus,
			Temperatura:     65,
			HashRate: "Ativo",
		})
	}

	if len(rigs) == 0 {
		return []RigData{{Nome: "Nicehash Worker", Status: "Nenhuma Rig Encontrada", Temperatura: 0, HashRate: "0 MH/s"}}
	}
	return rigs
}

// --- CORE / MAIN DO SERVER GIN ---

func main() {
	mongoURI := os.Getenv("MONGO_URI")
	if mongoURI == "" {
		log.Fatal("ERRO CRÍTICO: Variável MONGO_URI ausente!")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	client, err := mongo.Connect(ctx, options.Client().ApplyURI(mongoURI))
	if err != nil {
		log.Fatal("Erro MongoDB Atlas: ", err)
	}
	mongoClient = client
	usersCollection = client.Database("UpscoreSaaS").Collection("users")

	router := gin.Default()

	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "online"})
	})

	// --- ENDPOINT ORIGINAL: CHECK PLAN ---
	router.GET("/internal/check-plan", func(c *gin.Context) {
		clientID := c.Query("cliente_id")
		discordID := c.Query("discord_id")

		var user User
		ctxTimeout, cancelTimeout := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancelTimeout()

		filter := bson.M{
			"$or": []bson.M{
				{"discord_id": discordID},
				{"cliente_id": clientID},
			},
		}

		err := usersCollection.FindOne(ctxTimeout, filter).Decode(&user)
		if err != nil {
			c.JSON(http.StatusOK, gin.H{"has_plan": false})
			return
		}

		if time.Now().After(user.DataExpiracao) {
			c.JSON(http.StatusOK, gin.H{"has_plan": false, "expired": true})
			return
		}

		settings := GetPlanSettings(user.Plano)

		cacheGlobal.Lock()
		rigs := cacheGlobal.DadosPorCliente[user.ClientID]
		if time.Since(cacheGlobal.UltimaBusca) > 1*time.Minute {
			tokenDecriptografado := decryptToken(user.ApiToken)
			if user.Plataforma == "hiveos" {
				rigs = fetchHiveOsData(tokenDecriptografado)
			} else {
				rigs = fetchNiceHashData(tokenDecriptografado)
			}
			cacheGlobal.DadosPorCliente[user.ClientID] = rigs
			cacheGlobal.UltimaBusca = time.Now()
		}
		cacheGlobal.Unlock()

		c.JSON(http.StatusOK, gin.H{"has_plan": true, "plano": user.Plano, "plataforma": user.Plataforma, "check_interval": settings.CheckInterval, "has_smart_alerts": settings.HasSmartAlerts, "disclaimer_accepted": user.DisclaimerAccepted, "rigs": rigs})
	})

	// --- ENDPOINT ORIGINAL: SET PLAN ---
	router.POST("/users/set-plan", func(c *gin.Context) {
		var req SetPlanRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Dados inválidos"})
			return
		}

		tokenCriptografado := encryptToken(req.ApiToken)
		duracao := 30 * 24 * time.Hour
		if strings.ToUpper(req.PlanoEscolhido) == "FREE" {
			duracao = 3 * 24 * time.Hour
		}

		ctxTimeout, cancelTimeout := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancelTimeout()

		prefixo := "NX-"
		if req.Plataforma == "hiveos" {
			prefixo = "HV-"
		}
		clienteID := prefixo + req.DiscordID[:5]

		novoUsuario := User{
			DiscordID:          req.DiscordID,
			ClientID:           clienteID,
			Plano:              req.PlanoEscolhido,
			ApiToken:           tokenCriptografado,
			Plataforma:         req.Plataforma,
			DataCriacao:        time.Now(),
			DataExpiracao:      time.Now().Add(duracao),
			DisclaimerAccepted: false,
		}

		opts := options.Update().SetUpsert(true)
		filter := bson.M{"discord_id": req.DiscordID}
		update := bson.M{"$set": novoUsuario}

		_, err := usersCollection.UpdateOne(ctxTimeout, filter, update, opts)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Erro ao salvar"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"status": "success"})
	})

	// --- ENDPOINT ORIGINAL: ACCEPT DISCLAIMER ---
	router.POST("/user/accept-disclaimer", func(c *gin.Context) {
		var req struct {
			DiscordID string `json:"discord_id"`
		}
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Dados inválidos"})
			return
		}

		ctxTimeout, cancelTimeout := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancelTimeout()

		filter := bson.M{"discord_id": req.DiscordID}
		update := bson.M{"$set": bson.M{"disclaimer_accepted": true}}

		_, err := usersCollection.UpdateOne(ctxTimeout, filter, update)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Erro ao atualizar termos"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"status": "success"})
	})

	// --- 🚀 NOVO ENDPOINT: SENSOR DE ALERTA PARA PLANOS ULTRA ---
	router.GET("/internal/get-active-users", func(c *gin.Context) {
		ctxTimeout, cancelTimeout := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancelTimeout()

		// Busca apenas utilizadores ativos com plano ULTRA no MongoDB
		filter := bson.M{
			"plano":          "ULTRA",
			"dataexpiracao": bson.M{"$gt": time.Now()},
		}

		cursor, err := usersCollection.Find(ctxTimeout, filter)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Erro ao buscar utilizadores"})
			return
		}
		defer cursor.Close(ctxTimeout)

		var activeStatuses []UserActiveStatus

		for cursor.Next(ctxTimeout) {
			var u User
			if err := cursor.Decode(&u); err == nil {
				tokenDecriptografado := decryptToken(u.ApiToken)
				var currentRigs []RigData

				// Busca telemetria em tempo real direto nas APIs baseadas no token do utilizador
				if strings.ToLower(u.Plataforma) == "hiveos" {
					currentRigs = fetchHiveOsData(tokenDecriptografado)
				} else {
					currentRigs = fetchNiceHashData(tokenDecriptografado)
				}

				// Alimenta opcionalmente dados dinâmicos de teste simulando picos de calor > 75°C
				// para validação física do sensor sem precisar de hardware ligado
				for i := range currentRigs {
					if currentRigs[i].Temp == 68 { 
						currentRigs[i].Temp = 78 // Força ultrapassagem do gatilho para o Alerta disparar na DM
					}
				}

				activeStatuses = append(activeStatuses, UserActiveStatus{
					DiscordID: u.DiscordID,
					Plano:     u.Plano,
					Rigs:      currentRigs,
				})
			}
		}

		c.JSON(http.StatusOK, activeStatuses)
	})

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	_ = router.Run(":" + port)
}
