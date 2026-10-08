export const CATEGORIES=['창업·사업화','R&D·기술','경진대회','교육·멘토링','금융','판로·수출','인력','기타'];
export const STATUSES=['관심','지원 준비','제출 완료','심사 중','선정','탈락'];
export const STORAGE_KEY='moa.startup-desk.v1';
export const dateKey=d=>`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
export const koreaToday=()=>new Intl.DateTimeFormat('sv-SE',{timeZone:'Asia/Seoul',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
export const parseDate=s=>new Date(s+'T12:00:00');
export const addDays=(s,n)=>{let d=parseDate(s);d.setDate(d.getDate()+n);return dateKey(d)};
export function validDate(s){return typeof s==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(s)&&!isNaN(parseDate(s))&&dateKey(parseDate(s))===s}
export function daysLeft(s,today=koreaToday()){return s?Math.round((Date.parse(s+'T00:00:00Z')-Date.parse(today+'T00:00:00Z'))/86400000):null}
export function safeURL(s){try{const u=new URL(s);return ['https:','http:'].includes(u.protocol)&&!u.username&&!u.password?u.href:''}catch{return ''}}
export function cleanRecord(r){
 if(!r||typeof r!=='object'||typeof r.id!=='string'||!/^(manual|sample|bizinfo):[a-zA-Z0-9_.:-]{1,180}$/.test(r.id)||typeof r.title!=='string'||!r.title.trim()||r.title.length>200)throw Error('공고 형식이 올바르지 않습니다.');
 const text=(key,max=10000)=>typeof r[key]==='string'?r[key].slice(0,max):'';
 for(const key of ['deadline','start'])if(r[key]&&!validDate(r[key]))throw Error('날짜 형식이 올바르지 않습니다.');
 if(r.start&&r.deadline&&r.start>r.deadline)throw Error('마감일은 시작일 이후여야 합니다.');
 if(r.url&&!safeURL(r.url))throw Error('링크는 http 또는 https 주소여야 합니다.');
 const source=r.id.split(':')[0];
 return {id:r.id,title:r.title.trim(),organization:text('organization',200),category:CATEGORIES.includes(r.category)?r.category:'기타',eligibility:Array.isArray(r.eligibility)?r.eligibility.filter(x=>typeof x==='string').slice(0,20).map(x=>x.slice(0,100)):['확인 필요'],start:r.start||'',deadline:r.deadline||'',url:safeURL(r.url),description:text('description'),source,periodText:text('periodText',200),publishedAt:text('publishedAt',50),tags:text('tags',500)};
}
export function emptyState(){return {version:1,manual:[],tracking:{},snapshots:{},demo:false}}
export function validateState(raw){
 if(!raw||raw.version!==1||!Array.isArray(raw.manual)||!raw.tracking||typeof raw.tracking!=='object'||Array.isArray(raw.tracking)||!raw.snapshots||typeof raw.snapshots!=='object'||Array.isArray(raw.snapshots))throw Error('모아 v1 백업 파일이 아닙니다.');
 if(raw.manual.length>5000||Object.keys(raw.tracking).length>10000||Object.keys(raw.snapshots).length>10000)throw Error('백업 항목이 너무 많습니다.');
 const state=emptyState();state.demo=raw.demo===true;
 state.manual=raw.manual.map(cleanRecord);if(state.manual.some(r=>r.source!=='manual')||new Set(state.manual.map(r=>r.id)).size!==state.manual.length)throw Error('수동 공고 데이터가 올바르지 않습니다.');
 for(const [id,r]of Object.entries(raw.snapshots)){const clean=cleanRecord(r);if(clean.id!==id)throw Error('공고 식별자가 일치하지 않습니다.');state.snapshots[id]=clean;}
 for(const [id,t]of Object.entries(raw.tracking)){if(!/^(manual|sample|bizinfo):[a-zA-Z0-9_.:-]{1,180}$/.test(id)||!t||!STATUSES.includes(t.status)||typeof t.favorite!=='boolean'||typeof t.note!=='string'||t.note.length>10000)throw Error('지원 기록 형식이 올바르지 않습니다.');state.tracking[id]={favorite:t.favorite,status:t.status,note:t.note};}
 return state;
}
export function mergeStates(current,incoming){return validateState({version:1,demo:current.demo,manual:[...new Map([...current.manual,...incoming.manual].map(r=>[r.id,r])).values()],tracking:{...current.tracking,...incoming.tracking},snapshots:{...current.snapshots,...incoming.snapshots}})}
export function mergedRecords(official,state,samples){const map=new Map(Object.values(state.snapshots).filter(r=>r.source!=='sample'||state.demo).map(r=>[r.id,{...r,archived:r.source==='bizinfo'}]));for(const r of [...official,...state.manual,...(state.demo?samples:[])])map.set(r.id,r);return [...map.values()]}
export function filterRecords(records,{query='',category='',eligibility='',status='',hideClosed=false,page='calendar',today=koreaToday()},tracking){const q=query.trim().toLocaleLowerCase();return records.filter(r=>(!q||[r.title,r.organization,r.description,r.tags,...r.eligibility].join(' ').toLocaleLowerCase().includes(q))&&(!category||r.category===category)&&(!eligibility||r.eligibility.includes(eligibility))&&(!status||tracking[r.id]?.status===status)&&(!hideClosed||!r.deadline||r.deadline>=today)&&(page!=='favorites'||tracking[r.id]?.favorite)&&(page!=='pipeline'||tracking[r.id])).sort((a,b)=>(a.deadline||'9999').localeCompare(b.deadline||'9999')||a.title.localeCompare(b.title));}
export function makeSamples(today=koreaToday()){const titles=['AI 헬스케어 아이디어 사업화 지원','예비창업자를 위한 첫걸음 프로그램','여성 창업가 성장 지원','디지털 헬스 창업 경진대회','초기기업 R&D 실증 지원','사업계획서 집중 멘토링','로컬 브랜드 창업 지원','바이오 스타트업 투자 준비','신사업 아이디어 발굴 프로그램'];return titles.map((title,i)=>cleanRecord({id:'sample:'+i,title:'[샘플] '+title,organization:'체험용 가상 지원기관',category:CATEGORIES[[0,0,0,2,1,3,0,3,0][i]],eligibility:[["예비창업자"],["예비창업자"],["여성창업자"],["예비창업자","초기창업자"],["초기창업자"],["예비창업자"],["초기창업자"],["초기창업자"],["확인 필요"]][i],deadline:i===8?'':addDays(today,[-2,2,4,7,10,14,19,23][i]),start:addDays(today,-15),description:'화면과 저장 기능을 체험하기 위한 가상 공고입니다. 실제 모집사업이 아니며 신청할 수 없습니다. 샘플 일정은 오늘을 기준으로 만들어집니다.',url:'',tags:'샘플'}))}
