const fs = require('fs');
const path = require('path');
const pdf = require('pdf-parse');
const axios = require('axios');

const PDF_DIR = path.join(__dirname, 'arquivos_pdf');
const API_URL = 'http://127.0.0.1:8000/documents/';

// Processamento em lote de PDFs e TXTs para vetorização
async function processAllPdfs() {
    if (!fs.existsSync(PDF_DIR)) {
        fs.mkdirSync(PDF_DIR, { recursive: true });
        console.log(`[INFO] Diretório '${PDF_DIR}' criado. Insira os arquivos na pasta antes de executar.`);
        return;
    }

    const files = fs.readdirSync(PDF_DIR).filter(f => f.toLowerCase().endsWith('.pdf') || f.toLowerCase().endsWith('.txt'));

    if (files.length === 0) {
        console.log(`[INFO] Nenhum PDF ou TXT encontrado na pasta '${PDF_DIR}'.`);
        return;
    }

    console.log(`[INÍCIO] Encontrados ${files.length} arquivos. Iniciando processamento...`);

    for (const file of files) {
        const filePath = path.join(PDF_DIR, file);
        try {
            let content = "";
            const title = file.replace(/\.(pdf|txt)$/i, '');

            if (file.toLowerCase().endsWith('.pdf')) {
                const dataBuffer = fs.readFileSync(filePath);
                const data = await pdf(dataBuffer);
                content = data.text.trim();
            } else {
                content = fs.readFileSync(filePath, 'utf-8').trim();
            }

            console.log(`\n⏳ Extraindo e enviando: ${title} (${content.substring(0, 50).replace(/\n/g, ' ')}...)`);

            // Enviando para nossa API Python
            const response = await axios.post(API_URL, {
                title: title,
                content: content
            });

            console.log(`✅ Sucesso! Resposta da API:`, response.data.message);
        } catch (error) {
            console.error(`❌ Erro ao processar o arquivo ${file}:`, error.message);
        }
    }

    console.log(`\n[FIM] Processamento em lote concluído!`);
}

processAllPdfs();
