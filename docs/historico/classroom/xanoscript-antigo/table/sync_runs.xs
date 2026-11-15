// Log de execuções de sincronização com o Classroom (auditoria e diagnóstico).
table sync_runs {
  schema {
    int id
    timestamp created_at?=now
  
    // Dono (local_users.id, PK interna do Xano)
    int owner_id {
      table = "local_users"
    }
  
    enum trigger_type?=manual {
      values = ["manual", "scheduled"]
    }
  
    enum status?=running {
      values = ["running", "success", "partial", "error"]
    }
  
    timestamp started_at?=now
    timestamp? finished_at?
  
    int courses_upserted?=0
    int coursework_upserted?=0
    int submissions_upserted?=0
  
    text? error_message?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {
      type : "btree"
      field: [{name: "owner_id", op: "asc"}, {name: "started_at", op: "desc"}]
    }
    {type: "btree", field: [{name: "status", op: "asc"}]}
  ]

  tags = ["classroom"]
}
