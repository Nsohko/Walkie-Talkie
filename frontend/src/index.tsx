import App from "./App"
import React from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import "bootstrap/dist/css/bootstrap.min.css";


document.title = "Healthhack 2025";

const root = createRoot(document.getElementById("root") as HTMLElement);

root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
);
