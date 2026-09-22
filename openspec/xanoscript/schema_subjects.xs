// XanoScript Schema Definition: subjects
// EduTrack AI - Spec-Driven Development

table subjects {
  id: integer {
    primary_key: true,
    auto_increment: true
  }
  user_id: integer {
    required: true,
    reference: users.id,
    on_delete: cascade,
    description: "Vínculo de propriedade com o usuário autenticado"
  }
  name: text {
    required: true,
    description: "Nome da disciplina (ex: Estrutura de Dados)"
  }
  professor: text {
    required: false,
    description: "Nome do professor responsável"
  }
  workload_hours: decimal {
    required: true,
    default: 60.0,
    description: "Carga horária total da disciplina em horas"
  }
  description: text {
    required: false,
    description: "Ementa ou descrição resumida"
  }
  start_date: timestamp {
    required: false,
    description: "Data de início das aulas"
  }
  end_date: timestamp {
    required: false,
    description: "Data de término do semestre"
  }
  created_at: timestamp {
    default: now()
  }
}
