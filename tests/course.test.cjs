const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const course=JSON.parse(read('course.json')),html=read('index.html'),manifest=JSON.parse(read('source-manifest.json'));
assert.deepEqual(JSON.parse(html.match(/<script id="lms-course-data"[^>]*>(.*?)<\/script>/s)[1]),course);
const context={};vm.createContext(context);vm.runInContext(read('lms-runtime.js')+';globalThis.api=LMS;',context);
const model=context.api.validate(course);assert.equal(context.api.ready(model).length,0);
const items=context.api.flatten(model.sections),decks=items.filter(n=>n.type==='slides');
assert.equal(decks.length,20);assert.equal(manifest.sources.length,14);
for(const s of manifest.sources){for(const id of s.lessonIds||[s.lessonId])assert.ok(decks.some(d=>d.id===id));if(s.sourcePath)assert.equal(crypto.createHash('sha256').update(read(s.sourcePath)).digest('hex'),s.sha256);}
for(const d of decks)for(const s of d.slides){
  assert.ok(s.body.length<20000,'No runtime truncation: '+s.id);
  assert.equal((s.body.match(/^```/gm)||[]).length%2,0,'Balanced fences: '+s.id);
  assert.ok(!/\{\{\s*\w+\(/.test(s.body),'Unresolved MDN macro: '+s.id);
  for(const m of s.body.matchAll(/```json\n([\s\S]*?)\n```/g))assert.doesNotThrow(()=>JSON.parse(m[1]),'JSON example: '+s.id);
}
for(const qz of [...items.filter(n=>n.type==='quiz'),model.finalQuiz])for(const q of qz.questions){assert.ok(q.answer>=0&&q.answer<q.options.length);assert.ok(q.explanation);assert.equal(new Set(q.options).size,q.options.length);}
assert.equal(model.finalQuiz.questions.length,18);
const modulePrompts=new Set(items.filter(n=>n.type==='quiz').flatMap(n=>n.questions.map(q=>q.prompt)));
for(const q of model.finalQuiz.questions)assert.ok(!modulePrompts.has(q.prompt),'Independent final prompt');
// Check the runtime behaviors the authored clinic teaches, including failure cases.
assert.equal(JSON.stringify({a:undefined,b:null}),'\u007b"b":null}');
assert.equal(JSON.stringify([undefined,null]),'[null,null]');
assert.equal(JSON.stringify(undefined),undefined);
assert.equal(JSON.stringify({x:NaN,y:Infinity,when:new Date('2026-01-01T00:00:00Z')}),'{"x":null,"y":null,"when":"2026-01-01T00:00:00.000Z"}');
assert.throws(()=>JSON.parse('{"x":01,}'),SyntaxError);
assert.throws(()=>JSON.stringify({id:9007199254740993n}),TypeError);
const cyclic={};cyclic.self=cyclic;assert.throws(()=>JSON.stringify(cyclic),TypeError);
const shared={};assert.equal(JSON.stringify([shared,shared]),'[{},{}]');
const id=9007199254740993n;assert.equal(BigInt(JSON.parse(JSON.stringify({id:id.toString()})).id),id);
console.log('PASS: source hashes, embedded parity, runtime readiness, '+decks.length+' decks, JSON examples, grammar fences and assessment integrity');
