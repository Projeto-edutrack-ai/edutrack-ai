const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm');
const fs=require('node:fs'),path=require('node:path');

test('App boots while logged out and binds subject submit on login without native navigation',async()=>{
 const listeners=new Map(),formHandlers=new Map(),calls=[];
 const classList={add(){},remove(){},toggle(){return false},contains(){return false}};
 const button={disabled:false,textContent:'Salvar'};
 const form={addEventListener(type,fn){formHandlers.set(type,fn)},querySelector(){return button}};
 const nodes={
  'form-subject-modal':form,
  'subject-modal-name':{value:'Teste de integração'},
  'subject-modal-professor':{value:'Teste'},
  'subject-modal-workload':{value:'40'},
  'subject-modal-description':{value:'Descrição'},
  'modal-subject-overlay':{classList},
 };
 let token=null;
 const API={getToken:()=>token,getCurrentUser:()=>({id:1,name:'Teste'}),
  createSubject:async payload=>{calls.push(payload);return {id:7}},
  getProgressAnalytics:async()=>({}),getTimeDistribution:async()=>({distribution:[]}),getTasks:async()=>[],getAIInsights:async()=>({recommendations:[],alerts:[]})};
 const context={API,console,URLSearchParams,
  Toast:{show(){}},setTimeout(){},setInterval(){},clearInterval(){},
  localStorage:{getItem(){return null}},
  document:{documentElement:{classList},getElementById:id=>nodes[id]||null,querySelectorAll:()=>[],addEventListener(){}},
  window:{location:{search:''},addEventListener:(type,fn)=>listeners.set(type,fn)},
 };
 vm.createContext(context);
 for(const file of ['auth.js','dashboard.js','subjects.js','tasks.js','insights.js','app.js'])
  vm.runInContext(fs.readFileSync(path.join(__dirname,'../frontend/js',file),'utf8'),context,{filename:file});
 const App=vm.runInContext('App',context);
 assert.doesNotThrow(()=>App.init());
 assert.equal(typeof listeners.get('auth-success'),'function');
 token='test-jwt';
 await listeners.get('auth-success')();
 await new Promise(resolve=>setImmediate(resolve));
 assert.equal(typeof formHandlers.get('submit'),'function');
 let prevented=false;
 await formHandlers.get('submit')({preventDefault(){prevented=true}});
 assert.equal(prevented,true);
 assert.equal(calls.length,1);
 assert.equal(calls[0].name,'Teste de integração');
 assert.equal(calls[0].workload_hours,40);
 assert.equal(button.disabled,false);
});

test('repeat login refreshes views without rebinding form and timer handlers',async()=>{
 const context={document:{addEventListener(){}},window:{},console};
 const counts={};
 for(const name of ['Dashboard','Subjects','Tasks','Insights']) {
  counts[name]=0;
  context[name]={init:async()=>counts[name]++};
 }
 let refreshes=0;
 context.Dashboard.loadAllDashboardData=async()=>refreshes++;
 context.Subjects.loadSubjects=async()=>refreshes++;
 context.Tasks.loadTasks=async()=>refreshes++;
 context.Insights.loadInsights=async()=>refreshes++;
 vm.createContext(context);
 vm.runInContext(fs.readFileSync(path.join(__dirname,'../frontend/js/app.js'),'utf8'),context);
 const app=vm.runInContext('App',context);
 await app.loadAllViews();await app.loadAllViews();
 assert.deepEqual(Object.values(counts),[1,1,1,1]);
 assert.equal(refreshes,4);
});

test('failed refresh preserves existing subject cards and reports stale view',async()=>{
 let warning=null,requests=0,finish;
 const grid={innerHTML:'saved-card',querySelector(selector){return selector==='.subject-card'?{}:warning},prepend(node){warning=node}};
 const context={console:{error(){}},document:{getElementById:id=>id==='subjects-grid'?grid:null,createElement:()=>({setAttribute(){}})},
  API:{getSubjects:()=>{requests++;return new Promise((resolve,reject)=>{finish=reject})}}};
 vm.createContext(context);
 vm.runInContext(fs.readFileSync(path.join(__dirname,'../frontend/js/subjects.js'),'utf8'),context);
 const subjects=vm.runInContext('Subjects',context);
 const a=subjects.loadSubjects(),b=subjects.loadSubjects();
 finish(new Error('Limite Xano 429'));
 await Promise.all([a,b]);
 assert.equal(requests,1);
 assert.equal(grid.innerHTML,'saved-card');
 assert.match(warning.textContent,/última lista carregada/);
 assert.match(warning.textContent,/429/);
});

test('returning to an earlier pending search keeps the most recently requested filter',async()=>{
 const pending=new Map(),rendered=[];
 const grid={querySelector(){return null}};
 const context={console,document:{getElementById:id=>id==='subjects-grid'?grid:null},API:{getSubjects:q=>new Promise(resolve=>pending.set(q,resolve))}};
 vm.createContext(context);
 vm.runInContext(fs.readFileSync(path.join(__dirname,'../frontend/js/subjects.js'),'utf8'),context);
 const s=vm.runInContext('Subjects',context);
 s.renderSubjectCards=rows=>rendered.push(rows[0]);s.updateSubjectSelects=()=>{};
 const a=s.loadSubjects('a'),b=s.loadSubjects('b'),again=s.loadSubjects('a');
 pending.get('b')(['result-b']);pending.get('a')(['result-a']);
 await Promise.all([a,b,again]);assert.deepEqual(rendered,['result-a']);
});
