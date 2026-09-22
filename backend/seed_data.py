from datetime import datetime, timezone, timedelta
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.subject import Subject
from app.models.task import AcademicTask

def seed_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        demo_email = "aluno@edutrack.edu.br"
        user = db.query(User).filter(User.email == demo_email).first()
        
        if user:
            print(f"[Seed] Usuário {demo_email} já existe. Limpando dados antigos para recriação limpa...")
            db.query(AcademicTask).filter(AcademicTask.user_id == user.id).delete()
            db.query(Subject).filter(Subject.user_id == user.id).delete()
            db.delete(user)
            db.commit()

        print(f"[Seed] Criando usuário demo com dados acadêmicos: {demo_email}...")
        user = User(
            name="Lucas Ferreira",
            email=demo_email,
            password_hash=get_password_hash("senha123"),
            course="Ciência da Computação",
            college_year="3º Ano / 6º Semestre",
            institution="Instituto de Tecnologia & Computação",
            bio="Foco em Inteligência Artificial, Estruturas de Dados e Arquitetura de Sistemas.",
            avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        now = datetime.now(timezone.utc)
        
        # 1. Criar Disciplinas
        print("[Seed] Criando disciplinas...")
        subjects_data = [
            {
                "name": "Programação em Python & IA",
                "professor": "Prof. Dr. Ricardo Ramos",
                "workload_hours": 80.0,
                "description": "Desenvolvimento com Python, algoritmos de IA, OpenSpec e APIs modernas.",
                "start_date": now - timedelta(days=40),
                "end_date": now + timedelta(days=50)
            },
            {
                "name": "Estrutura de Dados e Algoritmos",
                "professor": "Profa. Dra. Mariana Lima",
                "workload_hours": 80.0,
                "description": "Filas, pilhas, árvores binárias, grafos e complexidade assintótica.",
                "start_date": now - timedelta(days=40),
                "end_date": now + timedelta(days=50)
            },
            {
                "name": "Modelagem de Banco de Dados & Xano",
                "professor": "Prof. Carlos Eduardo",
                "workload_hours": 60.0,
                "description": "Modelagem relacional, schemas NoSQL, XanoScript e otimização de queries.",
                "start_date": now - timedelta(days=40),
                "end_date": now + timedelta(days=50)
            },
            {
                "name": "Engenharia de Software & OpenSpec",
                "professor": "Profa. Beatriz Souza",
                "workload_hours": 40.0,
                "description": "Spec-Driven Development, arquitetura de microsserviços e documentação viva.",
                "start_date": now - timedelta(days=40),
                "end_date": now + timedelta(days=50)
            }
        ]

        created_subjects = {}
        for s_data in subjects_data:
            s = Subject(user_id=user.id, **s_data)
            db.add(s)
            db.commit()
            db.refresh(s)
            created_subjects[s.name] = s

        # 2. Criar Tarefas Acadêmicas
        print("[Seed] Criando tarefas acadêmicas...")
        tasks_data = [
            {
                "subject": "Programação em Python & IA",
                "title": "Lab 1: Configuração do ambiente e scripts básicos",
                "description": "Instalação do Python, poetry/pip e primeiros scripts de automação.",
                "due_date": now - timedelta(days=20),
                "status": "completed",
                "estimated_time_minutes": 120.0,
                "actual_time_minutes": 180.0,
                "completed_at": now - timedelta(days=21)
            },
            {
                "subject": "Programação em Python & IA",
                "title": "Lab 2: Implementar algoritmo de métricas com OpenSpec",
                "description": "Cálculo de média ponderada e projeção de velocity.",
                "due_date": now - timedelta(days=5),
                "status": "completed",
                "estimated_time_minutes": 180.0,
                "actual_time_minutes": 260.0,
                "completed_at": now - timedelta(days=6)
            },
            {
                "subject": "Programação em Python & IA",
                "title": "Projeto Prático: Integração com API Gemini",
                "description": "Conectar gerador de recomendações com a biblioteca google-genai.",
                "due_date": now + timedelta(days=2),
                "status": "in_progress",
                "estimated_time_minutes": 150.0,
                "actual_time_minutes": 60.0,
                "completed_at": None
            },
            {
                "subject": "Estrutura de Dados e Algoritmos",
                "title": "Lista de Exercícios 1: Pilhas e Filas",
                "description": "Resolução de 10 problemas práticos no LeetCode.",
                "due_date": now - timedelta(days=15),
                "status": "completed",
                "estimated_time_minutes": 120.0,
                "actual_time_minutes": 90.0,
                "completed_at": now - timedelta(days=16)
            },
            {
                "subject": "Estrutura de Dados e Algoritmos",
                "title": "Trabalho 1: Implementação de Árvore AVL",
                "description": "Balanceamento e rotações em C++/Python.",
                "due_date": now + timedelta(days=1),
                "status": "in_progress",
                "estimated_time_minutes": 180.0,
                "actual_time_minutes": 75.0,
                "completed_at": None
            },
            {
                "subject": "Estrutura de Dados e Algoritmos",
                "title": "Seminário: Algoritmos de Caminhamento em Grafos (Dijkstra)",
                "description": "Preparação dos slides e benchmark de complexidade.",
                "due_date": now + timedelta(days=12),
                "status": "pending",
                "estimated_time_minutes": 120.0,
                "actual_time_minutes": 0.0,
                "completed_at": None
            },
            {
                "subject": "Modelagem de Banco de Dados & Xano",
                "title": "DER: Modelagem Conceitual do EduTrack",
                "description": "Criação do diagrama entidade-relacionamento.",
                "due_date": now - timedelta(days=10),
                "status": "completed",
                "estimated_time_minutes": 90.0,
                "actual_time_minutes": 80.0,
                "completed_at": now - timedelta(days=11)
            },
            {
                "subject": "Modelagem de Banco de Dados & Xano",
                "title": "XanoScript: Configuração de Schemas e Endpoints",
                "description": "Implementação das tabelas subjects e academic_tasks.",
                "due_date": now + timedelta(days=7),
                "status": "pending",
                "estimated_time_minutes": 120.0,
                "actual_time_minutes": 0.0,
                "completed_at": None
            },
            {
                "subject": "Engenharia de Software & OpenSpec",
                "title": "OpenSpec Proposal 001: Especificação de MVP",
                "description": "Documentação formal dos requisitos e user stories.",
                "due_date": now - timedelta(days=18),
                "status": "completed",
                "estimated_time_minutes": 60.0,
                "actual_time_minutes": 45.0,
                "completed_at": now - timedelta(days=19)
            },
            {
                "subject": "Engenharia de Software & OpenSpec",
                "title": "Matriz de Rastreabilidade e tasks.md",
                "description": "Mapeamento de critérios de aceitação e conformidade.",
                "due_date": now + timedelta(days=15),
                "status": "pending",
                "estimated_time_minutes": 60.0,
                "actual_time_minutes": 0.0,
                "completed_at": None
            }
        ]

        for t_data in tasks_data:
            subj_name = t_data.pop("subject")
            subj = created_subjects[subj_name]
            task = AcademicTask(user_id=user.id, subject_id=subj.id, **t_data)
            db.add(task)

        db.commit()
        print("[Seed] Banco de dados populado com sucesso com perfil completo do aluno!")
        
    except Exception as e:
        db.rollback()
        print(f"[Seed] Erro: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
