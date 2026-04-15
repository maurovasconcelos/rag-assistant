const express = require("express");
const fs = require("fs");
const path = require("path");

const app = express();
app.use(express.json());
const mcpTools = [
    {
        name: "read_local_file",
        description: "Lê o conteúdo de um arquivo de texto ou log no sistema para a IA analisar.",
        parameters: {
            type: "object",
            properties: {
                file_path: {
                    type: "string",
                    description: "O caminho relativo ou absoluto do arquivo a ser lido."
                }
            },
            required: ["file_path"]
        }
    }
];
app.get("/", (req, res) => {
    res.send("<h1>Servidor MCP do RAG Assistant 🚀</h1><p>Status: Ativo!</p><p>As ferramentas expostas estão acessíveis via <b>GET /mcp/tools</b>.</p>");
});

app.get("/mcp/tools", (req, res) => {
    res.json({
        server_name: "Assistente_RAG_MCP",
        version: "1.0.0",
        tools: mcpTools
    });
});

app.post("/mcp/execute", (req, res) => {
    const { tool_name, parameters } = req.body;

    if (tool_name === "read_local_file") {
        try {
            const projectRoot = path.resolve(__dirname, "..");
            const fullPath = path.resolve(projectRoot, parameters.file_path);

            if (!fullPath.startsWith(projectRoot)) {
                return res.status(403).json({ error: "Access Denied: Path Traversal attempt intercepted." });
            }

            const content = fs.readFileSync(fullPath, "utf-8");
            return res.json({ result: content });
        } catch (error) {
            return res.status(500).json({ error: "Erro ao ler o arquivo: " + error.message });
        }
    }

    return res.status(404).json({ error: "Ferramenta não encontrada." });
});
const PORT = 8001;
app.listen(PORT, () => {
    console.log(`[MCP SERVER] Servidor Model Context Protocol rodando em http://localhost:${PORT}`);
    console.log(`[MCP SERVER] Endpoint de Descoberta: http://localhost:${PORT}/mcp/tools`);
});
