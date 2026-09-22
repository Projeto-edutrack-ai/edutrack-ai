// XanoScript Schema Definition: academic_tasks
// EduTrack AI - Spec-Driven Development

table academic_tasks {
  id: integer {
    primary_key: true,
    auto_increment: true
  }
  user_id: integer {
    required: true,
    reference: users.id,
    on_delete: cascade
  }
  subject_id: integer {
    required: true,
    reference: subjects.id,
    on_delete: cascade
  }
  title: text {
    required: true,
    description: "Título da tarefa ou trabalho"
  }
  description: text {
    required: false
  }
  due_date: timestamp {
    required: false,
    description: "Data e hora de entrega prevista"
  }
  status: enum {
    values: ["pending", "in_progress", "completed"],
    default: "pending"
  }
  estimated_time_minutes: decimal {
    required: true,
    default: 60.0,
    description: "Tempo estimado planejado para a tarefa em minutos"
  }
  actual_time_minutes: decimal {
    required: true,
    default: 0.0,
    description: "Tempo real acumulado de estudo/execução em minutos"
  }
  completed_at: timestamp {
    required: false
  }
  created_at: timestamp {
    default: now()
  }
}
