const express = require("express");
const fs = require("fs");
const path = require("path");
// Server configuration via Model Context Protocol (MCP)

const app = express();
app.use(express.json());

// Ferramentas do sistema local expostas via MCP
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

// Rota Padrão na raiz para facilitar a visualização no navegador
app.get("/", (req, res) => {
    res.send("<h1>Servidor MCP do RAG Assistant 🚀</h1><p>Status: Ativo!</p><p>As ferramentas expostas estão acessíveis via <b>GET /mcp/tools</b>.</p>");
});

// Rota de Início Padrão do MCP (Discovery das ferramentas)
app.get("/mcp/tools", (req, res) => {
    res.json({
        server_name: "Assistente_RAG_MCP",
        version: "1.0.0",
        tools: mcpTools
    });
});

// Endpoint para Execução das ferramentas solicitadas pela IA
app.post("/mcp/execute", (req, res) => {
    const { tool_name, parameters } = req.body;

    if (tool_name === "read_local_file") {
        try {
            const fullPath = path.resolve(__dirname, parameters.file_path);

            // Validação básica de segurança (evitar que a IA leia arquivos sensíveis do sistema)
            if (fullPath.includes("C:\\Windows") || fullPath.includes("/etc/")) {
                return res.status(403).json({ error: "Acesso negado pela segurança do MCP." });
            }

            const content = fs.readFileSync(fullPath, "utf-8");
            return res.json({ result: content });
        } catch (error) {
            return res.status(500).json({ error: "Erro ao ler o arquivo: " + error.message });
        }
    }

    return res.status(404).json({ error: "Ferramenta não encontrada." });
});

const PORT = 8001; // MCP rodando em porta diferente do FastAPI
app.listen(PORT, () => {
    console.log(`[MCP SERVER] Servidor Model Context Protocol rodando em http://localhost:${PORT}`);
    console.log(`[MCP SERVER] Endpoint de Descoberta: http://localhost:${PORT}/mcp/tools`);
});
