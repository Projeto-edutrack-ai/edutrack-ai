# Atualização da busca

Com o servidor parado, deixe correcao_busca.zip em D:\Downloads e execute:

```powershell
Expand-Archive -LiteralPath "D:\Downloads\correcao_busca.zip" -DestinationPath "D:\Downloads\edutrack1_corrigido\edutrack1_corrigido" -Force
.\.venv\Scripts\python.exe run_server.py
```

Atualize com Ctrl+Shift+R e pesquise Integração e Integracao. Nenhuma migração ou alteração de registros; não contém .env ou banco. A função de normalização é registrada no SQLite na abertura da conexão, então o processo precisa ser reiniciado. Visual do dropdown deve ser conferido no navegador.
