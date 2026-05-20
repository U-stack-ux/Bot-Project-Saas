package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

type Worker struct {
	ID     string `json:"id"`
	Name   string `json:"name"`
	Status string `json:"status"`
	Temps  []int  `json:"temps"`
}

func GetStats(token string) ([]Worker, error) {
	t, _ := Decrypt(token)
	req, _ := http.NewRequest("GET", "https://api2.hiveos.farm/api/v2/farms/0/workers", nil)
	req.Header.Set("Authorization", "Bearer "+t)
	
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil { return nil, err }
	defer resp.Body.Close()

	var res struct { Data []Worker `json:"data"` }
	json.NewDecoder(resp.Body).Decode(&res)
	return res.Data, nil
}

func SendCommand(token, workerID, cmd string) error {
	t, _ := Decrypt(token)
	url := fmt.Sprintf("https://api2.hiveos.farm/api/v2/farms/0/workers/%s/command", workerID)
	body, _ := json.Marshal(map[string]string{"command": cmd})
	
	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(body))
	req.Header.Set("Authorization", "Bearer "+t)
	req.Header.Set("Content-Type", "application/json")
	
	client := &http.Client{}
	_, err := client.Do(req)
	return err
}
