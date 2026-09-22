// XanoScript API Logic Definition: Endpoints e Regras de Negócio
// EduTrack AI - Spec-Driven Development

endpoint "POST /subjects" {
  auth: "user"
  input {
    name: text
    professor: text?
    workload_hours: decimal = 60.0
    description: text?
    start_date: timestamp?
    end_date: timestamp?
  }
  action {
    db.insert("subjects", {
      user_id: auth.user.id,
      name: input.name,
      professor: input.professor,
      workload_hours: input.workload_hours,
      description: input.description,
      start_date: input.start_date,
      end_date: input.end_date,
      created_at: now()
    })
  }
}

endpoint "POST /academic_tasks/{id}/study-time" {
  auth: "user"
  input {
    id: integer
    additional_minutes: decimal
    new_status: text?
  }
  action {
    var task = db.get("academic_tasks", { id: input.id, user_id: auth.user.id })
    if (!task) {
      error(404, "Tarefa não encontrada")
    }

    var updated_time = task.actual_time_minutes + input.additional_minutes
    var update_payload = { actual_time_minutes: updated_time }

    if (input.new_status != null) {
      update_payload.status = input.new_status
      if (input.new_status == "completed") {
        update_payload.completed_at = now()
      }
    }

    db.update("academic_tasks", task.id, update_payload)
  }
}

endpoint "GET /analytics/progress" {
  auth: "user"
  action {
    // Chama microserviço Python para cálculos de precisão
    return run_python_service("calculate_weighted_progress", { user_id: auth.user.id })
  }
}
