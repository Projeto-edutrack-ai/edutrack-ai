import os
import sys
import webbrowser
import uvicorn
from pathlib import Path

# Garante suporte a UTF-8 no console do Windows (evita UnicodeEncodeError com emojis)
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Adiciona o diretório backend ao PYTHONPATH
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir / "backend"
sys.path.insert(0, str(backend_dir))

# Carrega o arquivo .env (se existir) antes de iniciar o app: SMTP, Xano, Gemini etc.
try:
    from dotenv import load_dotenv
    load_dotenv(current_dir / ".env")
except ImportError:
    pass

def main():
    print("=" * 70)
    print("🎓 EduTrack AI — Assistente Educacional Personalizado")
    print("   Metodologia Spec-Driven Development (OpenSpec v1.0)")
    print("=" * 70)
    
    # 1. Garantir que o banco de dados está populado para o aluno
    db_file = current_dir / "edutrack.db"
    if not db_file.exists():
        print("[Início] Inicializando e populando banco de dados com dados demo...")
        try:
            from seed_data import seed_database
            seed_database()
        except Exception as e:
            print(f"[Aviso] Falha ao executar seed automático: {e}")

    host = "127.0.0.1"
    port = 8000
    url = f"http://{host}:{port}"

    print(f"\n🚀 Servidor iniciando em: {url}")
    print(f"📖 Documentação Swagger API: {url}/docs")
    print(f"🖥️ Interface do Estudante: {url}")
    print(f"\n🔑 Credenciais da Conta Demo:")
    print(f"   Email: aluno@edutrack.edu.br")
    print(f"   Senha:  senha123\n")
    print("Pressione Ctrl+C para encerrar o servidor.\n" + "-" * 70)

    # Iniciar servidor Uvicorn
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=False,
        app_dir=str(backend_dir)
    )

if __name__ == "__main__":
    main()
