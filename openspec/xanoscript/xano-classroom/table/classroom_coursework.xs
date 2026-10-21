// Atividades (courseWork) do Google Classroom, controladas pelo Classroom.
// Origem do futuro academic_tasks no FastAPI. actual_time_minutes, status manual
// e estimated_time_minutes continuam apenas no FastAPI/SQLite.
table classroom_coursework {
  schema {
    int id
    timestamp created_at?=now
    timestamp updated_at?=now
  
    // Dono (local_users.id, PK interna do Xano)
    int owner_id {
      table = "local_users"
    }
  
    // Curso ao qual a atividade pertence (classroom_courses.id)
    int classroom_courses_id {
      table = "classroom_courses"
    }
  
    // courseWork.id: único apenas dentro de um curso; chave de upsert junto com
    // owner_id e classroom_courses_id
    text google_coursework_id filters=trim
  
    // Campos controlados pelo Classroom
    text title
    text? description?
    text? alternate_link?
    decimal? max_points?
    timestamp? due_at?
    timestamp? google_created_at?
    timestamp? google_updated_at?
  
    // courseWork.state (PUBLISHED, DRAFT, DELETED) e workType, como texto
    text? state?
    text? work_type?
  
    // false quando a atividade deixou de aparecer na última sincronização
    bool is_active?=true
    timestamp? synced_at?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {
      type : "btree|unique"
      field: [
        {name: "owner_id", op: "asc"}
        {name: "classroom_courses_id", op: "asc"}
        {name: "google_coursework_id", op: "asc"}
      ]
    }
    {type: "btree", field: [{name: "classroom_courses_id", op: "asc"}]}
    {type: "btree", field: [{name: "due_at", op: "asc"}]}
    {type: "btree", field: [{name: "updated_at", op: "desc"}]}
  ]

  tags = ["classroom"]
}
