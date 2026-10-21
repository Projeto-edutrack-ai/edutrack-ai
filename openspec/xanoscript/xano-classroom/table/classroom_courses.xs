// Cursos do Google Classroom (dados controlados pelo Classroom).
// Origem do futuro subjects no FastAPI. workload_hours e demais campos
// editáveis continuam apenas no FastAPI/SQLite.
table classroom_courses {
  schema {
    int id
    timestamp created_at?=now
    timestamp updated_at?=now
  
    // Dono (local_users.id, PK interna do Xano)
    int owner_id {
      table = "local_users"
    }
  
    // courses.id do Classroom; chave de upsert junto com owner_id
    text google_course_id filters=trim
  
    // Campos controlados pelo Classroom
    text name
    text? section?
    text? description_heading?
    text? description?
    text? room?
    text? alternate_link?
  
    // courses.courseState (ACTIVE, ARCHIVED, ...). Guardado como texto para não
    // quebrar o upsert se o Google adicionar novos valores.
    text? course_state?
    timestamp? google_created_at?
    timestamp? google_updated_at?
  
    // Escolha do usuário sobre quais cursos importar (configuração da integração)
    bool selected?=false
  
    // false quando o curso deixou de aparecer na última sincronização
    bool is_active?=true
    timestamp? synced_at?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {
      type : "btree|unique"
      field: [{name: "owner_id", op: "asc"}, {name: "google_course_id", op: "asc"}]
    }
    {type: "btree", field: [{name: "updated_at", op: "desc"}]}
  ]

  tags = ["classroom"]
}
