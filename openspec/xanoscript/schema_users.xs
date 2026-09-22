// XanoScript Schema Definition: users
// EduTrack AI - Spec-Driven Development (v1.1)

table users {
  id: integer {
    primary_key: true,
    auto_increment: true
  }
  name: text {
    required: true,
    description: "Nome completo do estudante"
  }
  email: email {
    required: true,
    unique: true,
    description: "Email institucional ou pessoal para login"
  }
  password: password {
    required: true,
    description: "Hash de senha criptografado"
  }
  avatar_url: text {
    nullable: true,
    description: "URL da foto de perfil ou Data URI em Base64"
  }
  course: text {
    nullable: true,
    default: "Ciência da Computação",
    description: "Curso de graduação do estudante"
  }
  college_year: text {
    nullable: true,
    default: "3º Ano / 6º Semestre",
    description: "Ano letivo ou semestre atual"
  }
  institution: text {
    nullable: true,
    description: "Nome da faculdade ou universidade"
  }
  bio: text {
    nullable: true,
    description: "Biografia ou metas acadêmicas do estudante"
  }
  created_at: timestamp {
    default: now()
  }
}
