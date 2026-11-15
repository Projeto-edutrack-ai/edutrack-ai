const test=require('node:test'), assert=require('node:assert/strict'), vm=require('node:vm');
const fs=require('node:fs'), path=require('node:path');
function makeClient(fetch, config){
 const store=new Map([['edutrack_token','jwt-test'],['edutrack_user','{"id":1,"name":"Ana"}'],['edutrack_xano_aluno','{"id":1}']]);
 const context={window:{location:{origin:'https://edu.example'},EDUTRACK_CONFIG:config,dispatchEvent(){}},
 localStorage:{getItem:k=>store.get(k)||null,setItem:(k,v)=>store.set(k,v),removeItem:k=>store.delete(k)},
 fetch, URLSearchParams,console:{error(){},warn(){}},CustomEvent:class{}};
 vm.createContext(context);
 vm.runInContext(fs.readFileSync(path.join(__dirname,'../frontend/js/api.js'),'utf8'),context);
 return {api:vm.runInContext('API',context),store};
}
function json(body,status=200){return new Response(JSON.stringify(body),{status,headers:{'Content-Type':'application/json'}});}

test('browser CRUD uses same-origin authenticated backend and exact status field',async()=>{
 const calls=[];
 const {api}=makeClient(async(url,options)=>{
  calls.push({url,options});
  if(url.includes('/xano/materias'))return json([{id:2,alunos_id:1,nome:'Python',carga_horaria:80}]);
  return json([{id:9,materias_id:2,titulo_:'Lista',status:'concluida',actual_time_minutes:12,estimated_time_minutes:90}]);
 });
 const subjects=await api.getSubjects();
 assert.equal(subjects[0].progress_percentage,100);
 assert.equal(subjects[0].total_time_spent_minutes,12);
 const tasks=await api.getTasks();
 assert.equal(tasks[0].status,'completed');assert.equal(tasks[0].actual_time_minutes,12);
 for(const call of calls){
  assert.ok(call.url.startsWith('https://edu.example/api/xano/'));
  assert.equal(call.options.headers.Authorization,'Bearer jwt-test');
 }
});

test('task PATCH preserves the literal Xano enum and real time metadata',async()=>{
 let sent;
 const row={id:9,materias_id:2,titulo_:'Lista',descricao:'',prazo:null,status:'pendente',estimated_time_minutes:90,actual_time_minutes:12};
 const {api}=makeClient(async(url,options)=>{
  if(options.method==='PATCH'){sent=JSON.parse(options.body);return json({...row,...sent});}
  return json(row);
 },{apiBase:'https://backend.example/api/'});
 const result=await api.updateTask(9,{status:'in_progress'});
 assert.equal(sent.status,'em_andamento ');assert.equal(result.status,'in_progress');
 assert.equal(result.estimated_time_minutes,90);assert.equal(result.actual_time_minutes,12);
});

test('mentor and token password recovery are retained',async()=>{
 const calls=[];
 const {api}=makeClient(async(url,options)=>{calls.push({url,options});return json({answer:'Teste'});});
 await api.askAI('Como estudar?');
 assert.equal(calls[0].url,'https://edu.example/api/ai/ask');
 assert.equal(JSON.parse(calls[0].options.body).question,'Como estudar?');
 assert.equal(typeof api.resetPassword,'function');
});

test('gateway error is not replaced by invented zero progress',async()=>{
 const {api}=makeClient(async()=>json({detail:'Dados indisponíveis'},502));
 await assert.rejects(api.getProgressAnalytics(),/Dados indisponíveis/);
});

test('failed identity sync removes old account binding',async()=>{
 const {api,store}=makeClient(async()=>json({status:'link_required',aluno:null}));
 await api.syncXanoAluno({id:2});assert.equal(store.has('edutrack_xano_aluno'),false);
});

test('no Classroom integration and all API methods used by UI exist',()=>{
 const {api}=makeClient(async()=>json({}));
 const dir=path.join(__dirname,'../frontend/js');
 for(const f of fs.readdirSync(dir).filter(f=>f.endsWith('.js'))){
  const source=fs.readFileSync(path.join(dir,f),'utf8');
  assert.ok(!/Classroom\.|\/classroom\//.test(source),f);
  for(const match of source.matchAll(/\bAPI\.([A-Za-z_][A-Za-z_0-9]*)\s*\(/g))
   assert.equal(typeof api[match[1]],'function',`${f}: API.${match[1]} unavailable`);
 }
});

test('overdue search uses backend with explicit flag and blank text allowed',async()=>{
 let called;
 const {api}=makeClient(async(url)=>{called=new URL(url);return json({});});
 await api.search('',null,true);
 assert.equal(called.searchParams.get('overdue'),'true');assert.equal(called.searchParams.get('q'),'');
});
