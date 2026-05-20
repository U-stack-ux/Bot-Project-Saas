package main

import (
	"context"
	"fmt"
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

// Cache inteligente para evitar rate limit de APIs externas
type MemoryCache struct {
	sync.RWMutex
	DadosPorCliente map[string][]RigData
	UltimaBusca     time.Time
}

var cacheGlobal = MemoryCache{DadosPorCliente: make(map[string][]RigData)}

func main() {
	mongoURI := os.Getenv("MONGO_URI")
	if mongoURI == "" {
		log.Fatal("ERRO CRÍTICO: A variável MONGO_URI não está configurada no Render!")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	client, err := mongo.Connect(ctx, options.Client().ApplyURI(mongoURI))
	if err != nil {
		log.Fatal("Falha ao conectar ao MongoDB Atlas: ", err)
	}
	mongoClient = client
	
	// Define a base de dados do teu SaaS
	usersCollection = client.Database("upscore_saas").Collection("users")
	fmt.Println("🔌 [MongoDB Atlas] Ligação em tempo real estabelecida com sucesso!")

	router := gin.Default()

	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "online", "database": "connected"})
	})

	// 🔍 ENDPOINT: Valida o plano do cliente direto do MongoDB Atlas
	router.GET("/users/check-plan", func(c *gin.Context) {
		clientID := c.Query("cliente_id")
		discordID := c.Query("discord_id")

		var user User
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()

		// Procura o utilizador no banco real por DiscordID ou ClienteID
		err := usersCollection.FindOne(ctx, bson.M{
			"$or": []bson.M{
				{"discord_id": discordID},
				{"cliente_id": clientID},
			},
		}).Decode(&user)

		if err != nil {
			// Se não encontrou nenhum registo, avisa o Python para abrir a vitrine de vendas
			c.JSON(http.StatusOK, gin.H{"has_plan": false})
			return
		}

		// Verifica se o plano expirou (Controlo dos 3 dias Free ou 30 dias Pro)
		if time.Now().After(user.DataExpiracao) {
			c.JSON(http.StatusOK, gin.H{"has_plan": false, "expired": true, "message": "Plano expirado"})
			return
		}

		settings := GetPlanSettings(user.Plano)

		// Lógica Anti-Block com Cache para servir os comandos de alta frequência (10s)
		cacheGlobal.Lock()
		rigs, emCache := cacheGlobal.DadosPorCliente[user.ClienteID]
		
		if !emCache || time.Since(cacheGlobal.UltimaBusca) > 2*time.Minute {
			fmt.Printf("📡 [API %s] Puxando dados novos para o cliente %s\n", user.Plataforma, user.ClienteID)
			
			// Aqui simularíamos a chamada HTTP para a API da HiveOS/NiceHash.
			// Guardamos dados estruturados grandes de teste dentro do Cache RAM.
			rigs = []RigData{
				{Nome: "Rig-01-Main", Status: "Estável", Temperatura: 64, HashRate: "124 MH/s"},
				{Nome: "Rig-02-Mining", Status: "Fria/Segura", Temperatura: 58, HashRate: "62 MH/s"},
				{Nome: "Asic-S9-Vip", Status: "CRÍTICO", Temperatura: 84, HashRate: "14 TH/s"},
			}
			cacheGlobal.DadosPorCliente[user.ClienteID] = rigs
			cacheGlobal.UltimaBusca = time.Now()
		}
		cacheGlobal.Unlock()

		c.JSON(http.StatusOK, gin.H{
			"has_plan":        true,
			"plano":           user.Plano,
			"plataforma":      user.Plataforma,
			"check_interval":  settings.CheckInterval.Seconds(), // em segundos agora
			"has_smart_alert": settings.HasSmartAlerts,
			"rigs":            rigs,
		})
	})

	// 🚀 ENDPOINT: Regista a escolha do cliente e criptografa o Token no MongoDB Atlas
	router.POST("/users/set-plan", func(c *gin.Context) {
		var req SetPlanRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Dados inválidos"})
			return
		}

		// Aplica a criptografia AES-256 que criamos no arquivo crypto.go
		tokenCriptografado, err := EncryptToken(req.HiveOSToken)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Erro na segurança interna"})
			return
		}

		// Calcula o tempo de expiração com base no plano escolhido
		duracao := 30 * 24 * time.Hour // 30 dias padrão para planos pagos
		if req.PlanoEscolhido == "FREE" {
			duracao = 3 * 24 * time.Hour // 3 dias estritos para o plano Free de teste
		}

		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()

		// Modelo pronto para ser injetado no cluster do Atlas
		novoUsuario := User{
			DiscordID:     req.DiscordID,
			ClienteID:     "HIVE-" + req.DiscordID[:5], // Gera um ID interno temporário
			Plano:         req.PlanoEscolhido,
			HiveOSToken:   tokenCriptografado,
			Plataforma:    "hiveos", // Padrão inicial, expansível para nicehash/raveos
			DataCriacao:   time.Now(),
			DataExpiracao: time.Now().Add(duracao),
		}

		// Executa um Upsert: Se o ID do Discord já existir, atualiza o plano. Se não, cria um novo.
		opts := options.Update().SetUpsert(true)
		filter := bson.M{"discord_id": req.DiscordID}
		update := bson.M{"$set": novoUsuario}

		_, err = usersCollection.UpdateOne(ctx, filter, update, opts)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Falha ao gravar no Atlas"})
			return
		}

		fmt.Printf("💾 [MongoDB Atlas] Cliente %s gravado com sucesso! Expira em: %s\n", req.DiscordID, novoUsuario.DataExpiracao)
		c.JSON(http.StatusOK, gin.H{"status": "success", "message": "Conta configurada com sucesso!"})
	})

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	router.Run(":" + port)
}
