package main

import (
	"net/http"
	"os"
)

func download(w http.ResponseWriter, r *http.Request) {
	path := r.URL.Query().Get("path")
	// Intentional fixture: request path controls file read.
	data, err := os.ReadFile("/srv/app/uploads/" + path)
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	w.Write(data)
}

func main() {
	http.HandleFunc("/download", download)
	http.ListenAndServe(":8080", nil)
}
