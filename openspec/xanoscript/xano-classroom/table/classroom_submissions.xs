// Entrega (studentSubmission) do aluno para cada atividade, controlada pelo Classroom.
// O estado da entrega é informativo: o status manual do aluno fica no FastAPI.
table classroom_submissions {
  schema {
    int id
    timestamp created_at?=now
    timestamp updated_at?=now
  
    // Dono (local_users.id, PK interna do Xano)
    int owner_id {
      table = "local_users"
    }
  
    // Atividade à qual a entrega pertence (classroom_coursework.id)
    int classroom_coursework_id {
      table = "classroom_coursework"
    }
  
    // studentSubmission.id; chave de upsert junto com owner_id e classroom_coursework_id
    text google_submission_id filters=trim
  
    // studentSubmission.state (NEW, CREATED, TURNED_IN, RETURNED, RECLAIMED_BY_STUDENT),
    // como texto para tolerar novos valores
    text? state?
    bool? late?
    decimal? assigned_grade?
    text? alternate_link?
    timestamp? google_created_at?
    timestamp? google_updated_at?
  
    timestamp? synced_at?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {
      type : "btree|unique"
      field: [
        {name: "owner_id", op: "asc"}
        {name: "classroom_coursework_id", op: "asc"}
        {name: "google_submission_id", op: "asc"}
      ]
    }
    {type: "btree", field: [{name: "classroom_coursework_id", op: "asc"}]}
    {type: "btree", field: [{name: "state", op: "asc"}]}
  ]

  tags = ["classroom"]
}
