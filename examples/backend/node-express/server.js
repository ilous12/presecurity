import express from "express";
import { exec } from "node:child_process";

const app = express();

app.get("/lookup", (req, res) => {
  const host = req.query.host;

  // Intentional fixture: user input reaches a shell command.
  exec(`nslookup ${host}`, (error, stdout) => {
    if (error) {
      res.status(500).send(error.message);
      return;
    }
    res.type("text/plain").send(stdout);
  });
});

app.listen(3000);
