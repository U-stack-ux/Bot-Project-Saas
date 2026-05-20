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
	"sync"
	"time"

	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

var mongoClient *mongo.Client
var usersCollection *mongo.Collection

type SetPlanRequest struct {
	DiscordID      string `json:"discord_id"`
	PlanoEscolhido string `json:"plano_escolhido"`
	Plataforma     string `json:"plataforma"` 
	ApiToken       string `json:"api_token"`  
}

type RigData struct {
	Nome     string  `json:"nome"`
	Status   string  `json:"status"`
	Temp     int     `json:"temperatura"`
	HashRate string  `json:"hashrate"`
}

type MemoryCache struct {
	sync.RWMutex
	DadosPorCliente map[string][]RigData
	UltimaBusca     time.Time
}

type PlanSettings struct {
	CheckInterval  time.Duration
	HasSmartAlerts bool
}

type User struct {
	DiscordID          string    `bson:"discord_id"`
	ClienteID          string    `bson:"cliente_id"`
	Plano              string    `bson:"plano"`
	ApiToken           string    `bson:"api_token"` 
	Plataforma         string    `bson:"plataforma"`
	DataCriacao        time.Time `bson:"data_creation"`
	DataExpiracao      time.Time `bson:"data_expiration"`
	DisclaimerAccepted bool      `bson:"disclaimer_accepted"`
	AcceptedAt         time.Time `bson:"accepted_at"`
}

var cacheGlobal = MemoryCache{DadosPorCliente: make(map[string][]RigData)}

func GetPlanSettings(plano string) PlanSettings {
	switch plano {
	case "ULTRA":
		return PlanSettings{CheckInterval: 10 * time.Second, HasSmartAlerts: true}
	case "PRO":
		return PlanSettings{CheckInterval: 30 * time.Second, HasSmartAlerts: true}
	default:
		return PlanSettings{CheckInterval: 1 * time.Minute, HasSmartAlerts: false}
	}
}

func DecryptToken(cryptoText string) (string, error) {
	keyHex := os.Getenv("ENCRYPTION_KEY")
	if keyHex == "" {
		keyHex = "0123456789abcdef0123456789abcdef"
	}
	key, _ := hex.DecodeString(keyHex)
	ciphertext, _ := hex.DecodeString(cryptoText)

	block, err := aes.NewCipher(key)
	if err != nil {
		return "", err
	}
	if len(ciphertext) < aes.BlockSize {
		return "", fmt.Errorf("ciphertext curto demais")
	}
	iv := ciphertext[:aes.BlockSize]
	ciphertext = ciphertext[aes.BlockSize:]

	stream := cipher.NewCFBEncrypter(block, iv)
	stream.XORKeyStream(ciphertext, ciphertext)
	return string(ciphertext), nil
}

func EncryptToken(plainText string) (string, error) {
	keyHex := os.Getenv("ENCRYPTION_KEY")
	if keyHex == "" {
		keyHex = "0123456789abcdef0123456789abcdef"
	}
	key, _ := hex.DecodeString(keyHex)
	block, err := aes.NewCipher(key)
	if err != nil {
		return "", err
	}
	ciphertext := make([]byte, aes.BlockSize+len(plainText))
	iv := ciphertext[:aes.BlockSize]
	if _, err := io.ReadFull(rand.Reader, iv); err != nil {
		return "", err
	}
	stream := cipher.NewCFBEncrypter(block, iv)
	stream.XORKeyStream(ciphertext[aes.BlockSize:], []byte(plainText))
	return hex.EncodeToString(ciphertext), nil
}

func fetchHiveOsData(token string) []RigData {
	client := &http.Client{Timeout: 10 * time.Second}
	req, _ := http.NewRequest("GET", "https://api2.hiveos.farm/api/v2/farms", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := client.Do(req)
	if err != nil || resp.StatusCode != 200 {
		return []RigData{{Nome: "Erro HiveOS", Status: "Offline/Verificar API", Temp: 0, HashRate: "0 MH/s"}}
	}
	defer resp.Body.Close()

	var result struct {
		Data []struct {
			Name string `json:"name"`
			Stats struct {
				WorkersTotal int `json:"workers_total"`
				RigsOnline   int `json:"rigs_online"`
			} `json:"stats"`
		} `json:"data"`
	}
	_ = json.NewDecoder(resp.Body).Decode(&result)

	var rigs []RigData
	for _, farm := range result.Data {
		status := "Estável"
		if farm.Stats.RigsOnline < farm.Stats.WorkersTotal {
			status = "Aviso: Rig Offline"
		}
		rigs = append(rigs, RigData{
			Nome:     farm.Name,
			Status:   status,
			Temp:     60, 
			HashRate: fmt.Sprintf("%d/%d Online", farm.Stats.RigsOnline, farm.Stats.WorkersTotal),
		})
	}
	if len(rigs) == 0 {
		return []RigData{{Nome: "Farm Principal", Status: "Sem Rigs Ativas", Temp: 0, HashRate: "0 MH/s"}}
	}
	return rigs
}

func fetchNiceHashData(apiKey string) []RigData {
	client := &http.Client{Timeout: 10 * time.Second}
	req, _ := http.NewRequest("GET", "https://api2.nicehash.com/main/api/v2/mining/rigs2", nil)
	req.Header.Set("X-Auth", apiKey)

	resp, err := client.Do(req)
	if err != nil || resp.StatusCode != 200 {
		return []RigData{{Nome: "Erro NiceHash", Status: "Offline/Verificar API", Temp: 0, HashRate: "0 MH/s"}}
	}
	defer resp.Body.Close()

	var result struct {
		MiningRigs []struct {
			Name        string `json:"name"`
			MinerStatus string `json:"minerStatus"`
		} `json:"miningRigs"`
	}
	_ = json.NewDecoder(resp.Body).Decode(&result)

	var rigs []RigData
	for _, r := range result.MiningRigs {
		rigs = append(rigs, RigData{
			Nome:     r.Name,
			Status:   r.MinerStatus,
			Temp:     55,
			HashRate: "Ativa",
		})
	}
	if len(rigs) == 0 {
		return []RigData{{Nome: "NiceHash Worker", Status: "Nenhuma Rig Encontrada", Temp: 0, HashRate: "0 MH/s"}}
	}
	return rigs
}

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
	usersCollection = client.Database("upscore_saas").Collection("users")

	router := gin.Default()

	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "online"})
	})

	router.GET("/internal/check-plan", func(c *gin.Context) {
		clientID := c.Query("cliente_id")
		discordID := c.Query("discord_id")

		var user User
		ctxTimeout, cancelTimeout := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancelTimeout()

		err := usersCollection.FindOne(ctxTimeout, bson.M{
			"$or": []bson.M{
				{"discord_id": discordID},
				{"cliente_id": clientID},
			},
		}).Decode(&user)

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
		rigs, emCache := cacheGlobal.DadosPorCliente[user.ClienteID]

		if !emCache || time.Since(cacheGlobal.UltimaBusca) > 1*time.Minute {
			tokenDecriptografado, _ := DecryptToken(user.ApiToken)
			if user.Plataforma == "nicehash" {
				rigs = fetchNiceHashData(tokenDecriptografado)
			} else {
				rigs = fetchHiveOsData(tokenDecriptografado)
			}
			cacheGlobal.DadosPorCliente[user.ClienteID] = rigs
			cacheGlobal.UltimaBusca = time.Now()
		}
		cacheGlobal.Unlock()

		c.JSON(http.StatusOK, gin.H{
			"has_plan":        true,
			"plano":           user.Plano,
			"plataforma":      user.Plataforma,
			"check_interval":  settings.CheckInterval.Seconds(),
			"has_smart_alert": settings.HasSmartAlerts,
			"disclaimer":      user.DisclaimerAccepted,
			"rigs":            rigs,
		})
	})

	router.POST("/users/set-plan", func(c *gin.Context) {
		var req SetPlanRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Dados inválidos"})
			return
		}

		tokenCriptografado, err := EncryptToken(req.ApiToken)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Erro de segurança"})
			return
		}

		duracao := 30 * 24 * time.Hour
		if req.PlanoEscolhido == "FREE" {
			duracao = 3 * 24 * time.Hour
		}

		ctxTimeout, cancelTimeout := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancelTimeout()

		prefixo := "API-"
		if req.Plataforma != "" {
			prefixo = fmt.Sprintf("%s-", hex.EncodeToString([]byte(req.Plataforma))[:3])
		}

		novoUsuario := User{
			DiscordID:          req.DiscordID,
			ClienteID:          prefixo + req.DiscordID[:5],
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

		_, err = usersCollection.UpdateOne(ctxTimeout, filter, update, opts)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Erro ao salvar"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"status": "success"})
	})

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
		update := bson.M{"$set": bson.M{
			"disclaimer_accepted": true,
			"accepted_at":         time.Now(),
		}}

		_, err := usersCollection.UpdateOne(ctxTimeout, filter, update)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Erro ao atualizar termos"})
			return
		}

		c.JSON(http.StatusOK, gin.H{"status": "success"})
	})

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	router.Run(":" + port)
}
