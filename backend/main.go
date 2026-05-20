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
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

var mongoClient *mongo.Client

// 🧠 ESTRUTURA DE CACHE EM MEMÓRIA (Proteção contra Bloqueios)
type TelemetriaCache struct {
	sync.RWMutex
	DadosRigs    []string
	UltimaBusca  time.Time
}

// Inicializa o cache global na memória RAM do Go
var cacheGlobal = TelemetriaCache{}

type SetPlanRequest struct {
	DiscordID      string `json:"discord_id"`
	PlanoEscolhido string `json:"plano_escolhido"`
	HiveOSToken    string `json:"hiveos_token"`
}

func main() {
	mongoURI := os.Getenv("MONGO_URI")
	if mongoURI == "" {
		log.Fatal("A variável de ambiente MONGO_URI não foi definida")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	client, err := mongo.Connect(ctx, options.Client().ApplyURI(mongoURI))
	if err != nil {
		log.Fatal("Erro ao conectar ao MongoDB: ", err)
	}
	mongoClient = client
	fmt.Println("🌟 Conectado ao MongoDB com Sistema de Proteção Anti-Block!")

	router := gin.Default()

	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "online", "message": "API Anti-Block Ativa!"})
	})

	// 🔍 ENDPOINT SEGURO: Serve o Python a cada 10s sem tocar na HiveOS toda hora
	router.GET("/users/check-plan", func(c *gin.Context) {
		clientID := c.Query("cliente_id")
		
		if clientID == "novo" || clientID == "" {
			c.JSON(http.StatusOK, gin.H{"has_plan": false})
			return
		}

		planoDoBanco := "ULTRA" 
		settings := GetPlanSettings(planoDoBanco)

		// LÓGICA DO CACHE ANTIBLOQUEIO:
		cacheGlobal.Lock()
		// Se o cache estiver vazio ou tiver mais de 2 minutos, o Go busca na HiveOS de verdade
		if len(cacheGlobal.DadosRigs) == 0 || time.Since(cacheGlobal.UltimaBusca) > 2*time.Minute {
			fmt.Println("📡 [HiveOS API] Buscando novos dados direto da API externa...")
			// Simula a resposta da HiveOS salva no cache
			cacheGlobal.DadosRigs = []string{"Rig-01-Main", "Rig-02-Mining", "Asic-S9-Vip"}
			cacheGlobal.UltimaBusca = time.Now()
		} else {
			// Se o Python pediu antes de 2 minutos (ex: no ciclo de 10 segundos), o Go nem gasta internet
			fmt.Println("🧠 [Cache RAM] Servindo dados em alta velocidade sem gastar cota da HiveOS!")
		}
		rigsProntas := cacheGlobal.DadosRigs
		cacheGlobal.Unlock()

		c.JSON(http.StatusOK, gin.H{
			"has_plan":        true,
			"plano":           settings.Name,
			"check_interval":  settings.CheckInterval.Minutes(),
			"has_smart_alert": settings.HasSmartAlerts,
			"rigs":            rigsProntas,
		})
	})

	router.POST("/users/set-plan", func(c *gin.Context) {
		var req SetPlanRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Dados inválidos"})
			return
		}
		c.JSON(http.StatusOK, gin.H{"status": "success", "message": "Plano gravado"})
	})

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	router.Run(":" + port)
}
