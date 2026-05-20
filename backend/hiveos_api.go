package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

type WorkerStats struct {
	ID       string  `json:"id"`
	Name     string  `json:"name"`
	Status   string  `json:"status"`
	Hashrate float64 `json:"hashrate"`
	Temps    []int   `json:"temps"`
}

func GetHiveStats(encryptedToken string) ([]WorkerStats, error) {
	token, err := Decrypt(encryptedToken)
	if err != nil { return nil, err }
	client := &http.Client{Timeout: 10 * time.Second}
	req, _ := http.NewRequest("GET", "https://api2.hiveos.farm/api/v2/farms/0/workers", nil)
	req.Header.Set("Authorization", "Bearer "+token)
	resp, err := client.Do(req)
	if err != nil { return nil, err }
	defer resp.Body.Close()
	var result struct { Data []WorkerStats `json:"data"` }
	json.NewDecoder(resp.Body).Decode(&result)
	return result.Data, nil
}

func ControlWorker(encryptedToken, workerID, action string) error {
	token, err := Decrypt(encryptedToken)
	if err != nil { return err }
	client := &http.Client{Timeout: 10 * time.Second}
	url := fmt.Sprintf("https://api2.hiveos.farm/api/v2/farms/0/workers/%s/command", workerID)
	payload, _ := json.Marshal(map[string]string{"command": action})
	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(payload))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")
	resp, err := client.Do(req)
	if err != nil { return err }
	defer resp.Body.Close()
	return nil
}
