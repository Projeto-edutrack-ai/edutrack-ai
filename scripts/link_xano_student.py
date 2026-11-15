"""Administrative linking for existing Xano students. Dry-run unless --apply is supplied.

Run locally on a trusted server, never expose this as a public endpoint.
"""
import argparse
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'backend'))
from dotenv import load_dotenv
load_dotenv(root/'.env')
from app.core.database import SessionLocal,init_db
from app.models.user import User
from app.services.xano_crud import XanoCrudClient,XanoCrudError


def main():
    parser=argparse.ArgumentParser(description='Vincular conta local a um aluno Xano já verificado pela equipe.')
    parser.add_argument('--local-user-id',type=int,required=True)
    parser.add_argument('--xano-aluno-id',type=int,required=True)
    parser.add_argument('--apply',action='store_true',help='Grava o vínculo após a verificação administrativa')
    args=parser.parse_args()
    if args.local_user_id<=0 or args.xano_aluno_id<=0:parser.error('Use IDs positivos')
    init_db()
    api=XanoCrudClient()
    if not api.is_configured():parser.error('Configure a URL CRUD no .env')
    try:
        students=api.list_all('/alunos')
    except XanoCrudError as exc:
        parser.error(str(exc))
    remote=next((a for a in students if a['id']==args.xano_aluno_id),None)
    if remote is None:parser.error('Aluno remoto não encontrado')
    with SessionLocal() as db:
        user=db.get(User,args.local_user_id)
        if user is None:parser.error('Usuário local não encontrado')
        conflict=db.query(User).filter(User.xano_aluno_id==args.xano_aluno_id,User.id!=user.id).first()
        if conflict:parser.error('Aluno remoto já está vinculado a outra conta local')
        if user.xano_aluno_id is not None and (user.xano_aluno_id!=args.xano_aluno_id or user.xano_binding_base!=api._base):
            parser.error('Já existe outro vínculo; revise a migração administrativamente em vez de sobrescrever')
        if str(remote.get('email') or '').lower().strip()!=user.email.lower().strip():
            parser.error('E-mails diferentes; não vinculado. Revise a identidade administrativamente')
        print(f'Vínculo proposto: usuário local {user.id} -> aluno Xano {args.xano_aluno_id}.')
        print('A igualdade de e-mail não comprova identidade. Execute --apply somente após verificação pela equipe.')
        if args.apply:
            user.xano_aluno_id=args.xano_aluno_id;user.xano_binding_base=api._base
            db.commit();print('Vínculo salvo.')
        else:print('Simulação: nenhum vínculo alterado.')
    return 0


if __name__=='__main__':raise SystemExit(main())
