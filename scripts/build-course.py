"""Build a static JSON course from the checked-in, licensed MDN snapshot."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MDN = 'https://developer.mozilla.org/en-US/docs/'
COMMIT = 'bf7ff749b987d530e9a6c07f23ac66f94d968e57'
sources = []

def deck(id, title, pairs):
    return dict(id=id, type='slides', title=title, slides=[dict(id=f'{id}-s{i+1}', title=t, body=b) for i,(t,b) in enumerate(pairs)])

def module(id, title, children, questions=None, skill=None):
    if questions:
        children.append(dict(id=id+'-check', type='quiz', title='Skill check: '+skill, skill=skill, questions=[dict(id=f'{id}-q{i+1}', prompt=p, options=o, answer=a, explanation=e) for i,(p,o,a,e) in enumerate(questions)]))
    return dict(id=id, type='section', title=title, children=children)

def macro(match):
    name, args = match.group(1).lower(), re.findall(r'"([^"]*)"', match.group(2) or '')
    if name in ['compat','specifications','interactiveexample','previousmenunext','apiref','availableinworkers','embedlivesample']:
        return ''
    if name == 'optional_inline': return '(optional)'
    if not args: return ''
    key = args[0]; label = args[1] if len(args)>1 else key
    if name == 'glossary': slug = 'Glossary/'+key
    elif name == 'httpheader': slug = 'Web/HTTP/Reference/Headers/'+key
    elif name == 'htmlelement': slug = 'Web/HTML/Reference/Elements/'+key
    elif name == 'domxref':
        slug = 'Web/API/'+key.replace('.', '/')
    elif name == 'jsxref':
        key = key.removesuffix('()')
        slug = 'Web/JavaScript/Reference/'+key if key.startswith(('Operators/','Statements/')) else 'Web/JavaScript/Reference/Global_Objects/'+key.replace('.', '/')
    else: return label
    return f'[`{label}`]({MDN+slug.replace(chr(32), chr(95))})'

def clean(text, url):
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    # MDN's prerequisites table is UI scaffolding; preserve its learning information as prose.
    text = re.sub(r'<table>.*?</table>', '**Prerequisites:** basic HTML, CSS and JavaScript. **Outcomes:** recognize JSON, read nested values, retrieve JSON, parse and stringify.', text, flags=re.S)
    text = re.sub(r'<sup>.*?</sup>', '', text, flags=re.S)
    text = re.sub(r'\{\{\s*(\w+)(?:\((.*?)\))?\s*\}\}', macro, text)
    text = re.sub(r'^</?details>\s*$', '', text, flags=re.M)
    text = re.sub(r'<summary>(.*?)</summary>', r'**\1**', text)
    text = text.replace('> [!NOTE]', '> **Note:**')
    text = text.replace('](/en-US/docs/', ']('+MDN)
    text = re.sub(r'\]\(#([^)]*)\)', lambda m: ']('+url+'#'+m[1]+')', text)
    # External reference image stays a link; no third-party image request during study.
    text = re.sub(r'!\[([^\]]*)\]\(([^)]*)\)', lambda m: '[Diagram: '+m[1]+']('+ (url.rstrip('/')+'/'+m[2] if not m[2].startswith('http') else m[2]) +')', text)
    text = re.sub(r'^(\s*```)(js|html|json|plain)(?:[^\n]*)$', r'\1\2', text, flags=re.M)
    return text.strip()

def source(key, objective, practice, check):
    raw = (ROOT/'docs/mdn'/f'{key}.md').read_text()
    front, text = raw.split('---', 2)[1:]
    title = re.search(r'^title: (.+)$', front, re.M)[1].strip('"')
    slug = re.search(r'^slug: (.+)$', front, re.M)[1]
    url = MDN+slug; id = 'mdn-'+key
    title = {'json':'The JSON namespace and complete grammar', 'guide':'Working with JSON: a browser example', 'skills':'MDN practice tasks'}.get(key,title)
    pairs = [('Learning objective', objective+'\n\nSource: ['+title+']('+url+'). Adapted from MDN contributors under [CC BY-SA 2.5](https://creativecommons.org/licenses/by-sa/2.5/). Sections and code examples are retained; navigation widgets are removed. Run code examples in a browser console or local project, not inside this slide reader.')]
    chunks=[]; heading=title; lines=[]; fence=False
    for line in text.splitlines():
        if line.lstrip().startswith('```'): fence=not fence
        if not fence and re.match(r'^#{2,4} ', line):
            if '\n'.join(lines).strip(): chunks.append((heading,'\n'.join(lines)))
            heading=re.sub(r'^#+ ', '', line);lines=[]
        else: lines.append(line)
    if '\n'.join(lines).strip(): chunks.append((heading,'\n'.join(lines)))
    for heading, body in chunks:
        if heading in ('Specifications','Browser compatibility'):
            body = f'Check the live [MDN {heading.lower()} section]({url}#{heading.lower().replace(" ","_")}) for specification links and current engine support. Compatibility tables are generated upstream and are not frozen into this text snapshot.'
        else: body=clean(body,url)
        if body: pairs.append((heading,body))
    pairs += [('Practice — try before continuing',practice),('Worked self-check',check)]
    sources.append(dict(id=key,title=title,url=url,lessonId=id,upstreamCommit=COMMIT,sourcePath='docs/mdn/'+key+'.md',sha256=hashlib.sha256(raw.encode()).hexdigest(),upstreamHeadings=re.findall(r'^#{2,4} (.+)$',text,re.M),adaptation='Preserve source sections/examples; resolve MDN macros and links; replace generated compatibility/specification widgets with live references; append original objective/practice.'))
    return deck(id,title,pairs)

orientation=deck('start','Start here',[
 ('A small, focused course','Learn JSON as a data format, then use it from JavaScript. You do not need to complete an API or HTTP course first. Basic JavaScript helps with the parsing and serialization modules. Study one lesson per session; the reference sections include advanced examples you can revisit.'),
 ('Read, practice, explain','Read each slide, predict an example’s result, run it in your browser console, then explain the result in your own words. Exercises are self-assessed. Module quizzes give feedback and skill reports. Reading all slides enables Mark lesson complete. Retakes are enabled; passing is 80%.'),
 ('What the sources cover','JSON.org: its introductory format description and complete grammar concepts. MDN: glossary, Working with JSON, test-your-skills tasks, the JSON namespace, all four static methods, three error references, and Request/Response body JSON methods. Third-party libraries linked by JSON.org, historical essays, all HTTP documentation and JSON Schema specifications are outside this course.'),
 ('Your progress and exports','Your progress, notes and settings stay in this browser. Reports are personal study feedback. Use Copy entire course below the final assessment to make one plain-text study article, including code, source links, quizzes and answers. All lessons are open by default; Settings can enable completion gates. There is no account server or verified certificate.'),
 ('Source credits','MDN contributors’ documentation is adapted under [CC BY-SA 2.5](https://creativecommons.org/licenses/by-sa/2.5/). The course content uses the same license. Source files and the full upstream license are included in docs/mdn. JSON.org is linked and summarized; its language implementation directory is not copied. Documentation snapshot: 2026-10-07. New JavaScript features require runtime support checks.')])

grammar=deck('jsonorg-format','JSON.org: format and containers',[
 ('The format','JSON is language-independent text for exchanging data. It represents records with objects and sequences with arrays. Source: [Introducing JSON](https://www.json.org/json-en.html).'),
 ('Objects','An object uses braces. Names are double-quoted strings; a colon joins each name to its value. Commas separate members. Object member order should not carry business meaning.\n\n```json\n{"course":"JSON","published":true,"rating":null}\n```'),
 ('Arrays and nesting','An array uses brackets and has meaningful element order. Containers may nest; an empty object or array is valid.\n\n```json\n{"lessons":[{"title":"Syntax","tags":["data","text"]}]}\n```'),
 ('The six value categories','A value may be an object, array, string, number, boolean or null. A complete JSON document may also be a single primitive.\n\n```json\n["JSON",12,true,false,null,{},[]]\n```'),
 ('Practice','Write a course record with title, published flag, nullable description and an ordered lessons array. Include two lessons, each with a duration number. Use no comments or trailing commas.'),
 ('Worked self-check','```json\n{"title":"JSON","published":false,"description":null,"lessons":[{"title":"Syntax","minutes":10},{"title":"Parsing","minutes":15}]}\n```\n\nThe list preserves lesson order; names describe the meaning of values. Source diagrams and the language implementation directory remain available on JSON.org.')])
tokens=deck('jsonorg-tokens','JSON.org: strings, numbers and whitespace',[
 ('Strings and escapes','Strings use double quotes and Unicode characters. Backslash escapes include quote, backslash, slash, b, f, n, r, t and u followed by four hexadecimal digits. Raw control characters are forbidden.'),
 ('Two levels of escaping',r'''This JSON contains an escaped newline and a Windows-style path:

```json
{"message":"Line one\nLine two","path":"C:\\notes"}
```

In a JavaScript string literal, preserve those backslashes:

```js
const text = '{"message":"Line one\\nLine two"}';
console.log(JSON.parse(text).message);
// Line one
// Line two
```'''),
 ('Numbers','Use decimal numbers with optional minus, fraction and exponent. Leading zeros, hexadecimal, NaN and Infinity are excluded.\n\nValid: `0`, `-4`, `0.25`, `2e3`, `-1.2E-3`.\nInvalid: `01`, `+4`, `.25`, `4.`, `0x10`, `2e`.'),
 ('Whitespace','Between tokens, JSON permits space, tab, line feed and carriage return. Whitespace inside a string is data; it cannot split a number or keyword. Source: [JSON.org grammar](https://www.json.org/json-en.html).'),
 ('Practice and check','Repair `{name: \'Sam\', amount: 01, done: True,}`.\n\n```json\n{"name":"Sam","amount":1,"done":true}\n```\n\nExplain each change: quoted name, double-quoted string, decimal spelling, lowercase keyword, removed trailing comma. The JSON namespace reference later includes the complete formal grammar.')])
sources.append(dict(id='jsonorg',title='Introducing JSON',url='https://www.json.org/json-en.html',lessonIds=['jsonorg-format','jsonorg-tokens'],adaptation='Original concise summary of format and grammar; original practice examples. Library directory and historical articles linked, not reproduced.'))

boundaries=deck('data-boundaries','Syntax is only the first check',[
 ('Three questions','1. Is the text legal JSON?\n2. Is the parsed value the expected shape and type?\n3. Does it satisfy the application’s rules?\n\n`{"minutes":"ten"}` is valid JSON but is unsuitable when minutes must be a finite, nonnegative number.'),
 ('Check values explicitly','```js\nfunction isLesson(v) {\n  return v !== null && typeof v === "object" && !Array.isArray(v)\n    && typeof v.title === "string"\n    && typeof v.minutes === "number"\n    && Number.isFinite(v.minutes) && v.minutes >= 0;\n}\nconsole.log(isLesson({ title: "Syntax", minutes: 10 })); // true\nconsole.log(isLesson({ title: "Syntax", minutes: "10" })); // false\n```\n\nThis authored check validates two fields. It is not a complete JSON Schema validator.'),
 ('Do not execute data','Use JSON.parse rather than eval. Display untrusted strings with textContent. JSON parsing does not make HTML safe or authorize a user. A parsed __proto__ property is data; merging attacker-controlled names into other objects needs separate care. See [MDN parsing](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON/parse).'),
 ('Practice and check','Classify `null`, `{}`, `{"title":"Syntax","minutes":-2}` and `{"title":"Syntax","minutes":10}`. All four are valid JSON. Only the last passes isLesson. An application might add maximum duration, allowed fields and length constraints.')])

roundtrip=deck('roundtrip-clinic','Predict what survives a round trip',[
 ('Conversion is not universal cloning','JSON encodes data, not JavaScript behavior or identity. Parsing a serialized class instance does not restore its prototype or methods. Dates serialize as strings. Maps and Sets need a chosen representation. structuredClone is a separate API with different supported types.'),
 ('Undefined changes by position','```js\nconsole.log(JSON.stringify({ a: undefined, b: null })); // {"b":null}\nconsole.log(JSON.stringify([undefined, null])); // [null,null]\nconsole.log(JSON.stringify(undefined)); // undefined (not JSON text)\n```\n\nDistinguish an omitted field, explicit null and false. They often mean different things in a data contract.'),
 ('Hooks and explicit representations','```js\nconst progress = {\n  completed: new Set(["syntax", "parse"]),\n  toJSON() { return { completed: [...this.completed] }; }\n};\nconsole.log(JSON.stringify(progress));\n// {"completed":["syntax","parse"]}\n```\n\nA toJSON method chooses data to serialize. It does not install a corresponding parser.'),
 ('Practice and check','Predict JSON.stringify({ x: NaN, y: Infinity, when: new Date("2026-01-01T00:00:00Z") }).\n\nResult: `{"x":null,"y":null,"when":"2026-01-01T00:00:00.000Z"}`. On parse, when is still a string. Use a documented representation and deliberate reconstruction if a Date is required.')])

precision=deck('precision-clinic','Choose an exact-number contract',[
 ('The format and the runtime differ','A syntactically valid JSON number can exceed JavaScript Number precision or range. JSON has no BigInt suffix. Identifiers do not need arithmetic: represent long IDs as strings. Never convert a large ID to Number merely to satisfy a serializer.'),
 ('Portable string representation','```js\nconst id = 9007199254740993n;\nconst text = JSON.stringify({ id: id.toString() });\nconsole.log(text); // {"id":"9007199254740993"}\nconsole.log(BigInt(JSON.parse(text).id) === id); // true\n```\n\nThe receiver must agree that this field is a decimal integer string.'),
 ('Source text access','```js\nconst supportsSource = (() => {\n  let found = false;\n  JSON.parse("1", (key, value, context) => {\n    found = context?.source === "1";\n    return value;\n  });\n  return found;\n})();\nif (supportsSource) {\n  const data = JSON.parse(\n    \'{"id":9007199254740993}\',\n    (key, value, context) => key === "id" ? BigInt(context.source) : value\n  );\n  console.log(data.id === 9007199254740993n); // true\n}\n```\n\nThe primitive source spelling can recover a value after Number conversion. Feature detection is required in older runtimes.'),
 ('Raw JSON does not fix the receiver','```js\nif (typeof JSON.rawJSON === "function") {\n  const text = JSON.stringify({ id: JSON.rawJSON("9007199254740993") });\n  console.log(text); // {"id":9007199254740993}\n}\n```\n\nThe emitted digits are exact. Ordinary JSON.parse can still round them. Choose the representation for the capabilities of both sender and receiver.'),
 ('Practice and check','A mobile client and server exchange 20-digit IDs. Prefer a decimal string unless both sides explicitly support exact numeric decoding. Test the exact digits, not only whether the payload parses. For money, agree on units and rounding; JSON itself defines neither.')])

capstone=deck('capstone','Project: a JSON lesson catalog',[
 ('Deliverables','Create catalog.json, catalog.js and a short README. Use a browser console or a local Node environment. Build a two-course catalog with ordered lessons, published flags, nullable descriptions and long string IDs. This LMS does not execute or grade the project.'),
 ('Acceptance checks','Parse the catalog and validate its shape. Extract the second lesson title. Produce a pretty-printed export with only approved fields. Persist and reload a copy. Include one invalid-syntax fixture and one valid-JSON wrong-shape fixture. Ensure an HTML-looking title stays plain text if displayed.'),
 ('Serialization decisions','Document how dates, omitted fields and null are represented. Demonstrate that a BigInt fails without an explicit conversion. Choose either a string-ID contract or a feature-detected exact-number approach. Explain why JSON.parse(JSON.stringify(value)) is not your general cloning tool.'),
 ('Worked reference shape','```json\n{"courses":[{"id":"9007199254740993","title":"JSON","published":true,"description":null,"lessons":[{"title":"Syntax","minutes":10},{"title":"Parsing","minutes":15}]},{"id":"9007199254740995","title":"Data formats","published":false,"description":"Practice","lessons":[]}]}\n```\n\nAfter parsing, `catalog.courses[0].lessons[1].title` is `Parsing`. Store IDs as strings end to end.'),
 ('Self-review rubric','Score 0–2 for each: valid syntax; nested reads; shape checks; parse-error handling; deliberate stringify behavior; lossless IDs; storage round trip; clear documentation. Aim for 13/16. Explain one tradeoff aloud. This manual rubric is separate from the final quiz.')])

sections=[module('m1','01 Start here',[orientation]),module('m2','02 Format and grammar',[
 grammar,tokens,source('glossary','Explain why JSON is text and language independent.','Compare a JSON document with the JavaScript value obtained by parsing it.','The document is a textual representation. Parsing creates a runtime value; the format is not limited to JavaScript.')],[
 ('Which document is valid JSON?',["{'name':'Jo'}",'{"name":"Jo"}', '{name:"Jo"}'],1,'Names and string values require double quotes.'),
 ('Which can be a complete JSON document?',['Only an object','Only an array','A single false value'],2,'Any JSON value may be at the root.'),
 ('Which numeric spelling is legal?',['01','1e2','0x10'],1,'An exponent is allowed; leading zeros and hexadecimal are not.'),
 ('What carries order in a JSON data model?',['Array positions','Object member meaning inferred from position','Whitespace indentation'],0,'Arrays represent ordered sequences.')],'JSON syntax'),
 module('m3','03 Read JSON in JavaScript',[
 source('guide','Load JSON, read nested values, and distinguish JSON text from parsed data.','Using the superhero example, obtain the second hero’s third power. Then replace the remote fetch with a JSON string and parse it locally.','Read superHeroes.members[1].powers[2]. In this dataset that is Superhuman reflexes. response.json() already parses the body; JSON.parse is used only when you have text.'),
 source('json','Navigate the namespace, formal grammar and numeric interoperability choices.','Identify every JSON static method. Explain why new JSON() is invalid and why a long integer can lose precision.','The namespace provides parse, stringify, rawJSON and isRawJSON. It is not a constructor. JavaScript Number cannot represent every syntactically valid JSON number exactly.')],[
 ('After await response.json(), what do you usually hold?',['A JSON file path','A parsed JavaScript value','An automatically validated domain object'],1,'The body is decoded and parsed, but business validation is separate.'),
 ('How do you access the second lesson title in parsed catalog.lessons?',['catalog.lessons[1].title','catalog.lessons[2].title','JSON.title(catalog)'],0,'JavaScript array indexing starts at zero.'),
 ('What is JSON in JavaScript?',['A constructor for all records','A browser-only storage engine','A namespace with static methods'],2,'Use JSON.parse(text), not new JSON().')],'Reading JSON'),
 module('m4','04 Parse and transform',[
 source('parse','Parse any JSON root and trace reviver traversal, deletion and root replacement.','Parse {"minutes":10,"draft":true}. Double minutes with a reviver, preserve every other value, then trace the final empty-string key call.','Return value * 2 for key minutes and value otherwise. Children are visited before their parent. Returning undefined deletes a property or replaces the entire root with undefined.'),
 source('bad-parse','Diagnose malformed strings, property names, commas and numbers.','Repair {"x":01,} and test that {"x":"01"} is syntactically valid. Explain why their values have different types.','Use {"x":1} for a number, or {"x":"01"} for a string. JSON.parse throws SyntaxError for the original. Error message wording and positions vary by engine.'),boundaries],[
 ('What does JSON.parse("null") return?',['null','The string null','An empty object'],0,'JSON root values can be primitives.'),
 ('What does returning undefined from a reviver usually do to a property?',['Keeps it unchanged','Deletes it','Makes its JSON spelling null'],1,'Always return unchanged values when you intend to preserve them.'),
 ('Which reviver visit occurs last?',['The first object member','The last leaf only','The root with an empty-string key'],2,'Reviver processing proceeds from descendants to the root.'),
 ('Does successful JSON.parse prove a payload has a required title?',['No; validate the parsed shape separately','Yes; parsing enforces application fields','Only if indentation is two spaces'],0,'Syntax validation is distinct from the application contract.'),
 ('What should be used to read untrusted JSON text?',['eval','JSON.parse','new Function'],1,'JSON is data; do not execute it as JavaScript.')],'Parsing and validation'),
 module('m5','05 Serialize deliberately',[
 source('stringify','Predict stringify output and use replacer, space and toJSON intentionally.','Serialize {title:"Syntax", minutes:10, token:"private"} with an allowlist containing title and minutes. Indent by two spaces.','JSON.stringify(value, ["title", "minutes"], 2) excludes token from this example. Such a filter is not a substitute for permission checks and an explicit data contract.'),roundtrip,
 source('cyclic','Distinguish cycles from repeated references and understand lossy replacements.','Compare const x={}; JSON.stringify([x,x]) with x.self=x; JSON.stringify(x).','Repeated references without a cycle serialize as separate empty objects. A self-reference throws TypeError. Replacing a cycle with a marker loses identity information.'),
 source('bigint','Handle BigInt serialization without accidental Number rounding.','Serialize {id:9007199254740993n} using a local replacer that returns a string for BigInt.','JSON.stringify(data, (key,value) => typeof value === "bigint" ? value.toString() : value). The receiver must know which string fields represent integers; avoid unnecessary global prototype changes.')],[
 ('What is JSON.stringify([undefined])?',['undefined','[null]','[]'],1,'Unsupported array entries become null.'),
 ('What is JSON.stringify({x:undefined})?',['{}','{"x":null}','A SyntaxError'],0,'An unsupported object property is omitted.'),
 ('What happens to NaN during ordinary stringify?',['It becomes a JSON NaN keyword','It is preserved exactly','It becomes null'],2,'JSON has no NaN or Infinity literals.'),
 ('Which is a default stringify failure?',['A boolean root','A circular object','An empty array'],1,'JSON does not encode cyclic references.'),
 ('What does a replacer array provide?',['An allowlist of property names','A browser permissions policy','Automatic reconstruction of Date objects'],0,'It filters names during serialization.'),
 ('What is the parsed type of an ordinarily serialized Date?',['Date','Temporal','String'],2,'The serializer emits a string and parsing does not revive its type automatically.')],'Serialization'),
 module('m6','06 Precision and modern methods',[
 precision,source('rawjson','Create primitive raw JSON and explain receiver precision requirements.','Feature-detect rawJSON, serialize the exact digits 9007199254740993, then explain why rawJSON("[]") fails.','A raw JSON wrapper preserves numeric source text during stringify. Objects and arrays cannot be used as rawJSON inputs; it throws SyntaxError. Ordinary numeric parsing may still lose precision.'),
 source('israwjson','Recognize genuine raw JSON wrappers without confusing shape with identity.','Feature-detect both rawJSON and isRawJSON. Compare a genuine wrapper with {rawJSON:"1"}.','isRawJSON returns true only for a genuine wrapper produced by rawJSON. Merely adding a rawJSON property does not create the internal brand.')],[
 ('Which portable representation protects a 20-digit identifier?',['A JavaScript Number','A decimal string','A rounded numeric literal'],1,'String IDs preserve digits without requiring Number precision.'),
 ('Which input is accepted by JSON.rawJSON?',['"[1,2]"','"{\"a\":1}"','"123"'],2,'Raw JSON accepts valid primitive JSON text, not containers.'),
 ('Does emitting exact digits guarantee ordinary JSON.parse preserves them?',['No; the receiver can still round','Yes; raw JSON changes all parsers','Only for an indented document'],0,'Serialization and parsing precision are separate concerns.'),
 ('What can modern reviver context.source provide?',['The original spelling of a primitive value','A network authentication token','The entire source repository'],0,'Primitive source access supports deliberate exact-value recovery.'),
 ('Does {rawJSON:"1"} pass JSON.isRawJSON?',['Yes, because the property exists','No, because it lacks the internal raw JSON brand','Only after Object.freeze'],1,'Structural resemblance does not create a genuine raw wrapper.')],'Precision and raw JSON'),
 module('m7','07 JSON at application boundaries',[
 source('response-json','Read a response body once and distinguish body parsing errors from other failures.','Explain why JSON.parse(await response.json()) is usually incorrect, then predict what a second read of the same body does.','response.json() already returns parsed data. The same body cannot normally be consumed twice; clone before consuming if a second reader is required. Invalid JSON rejects with SyntaxError.'),
 source('request-json','Parse incoming request body data and validate it separately.','Build a Request with method POST and body JSON.stringify({title:"Syntax"}). Read it with await request.json().','The promise resolves to {title:"Syntax"}; it is a parsed JavaScript value. Syntax success does not ensure the expected data shape or authorize the operation.'),
 source('skills','Practice nested reads and rendering rather than memorizing syntax.','Complete the MDN cat-and-kitten task locally. Keep the data input separate from the code that displays it. Use the linked starter and solution resources for self-review.','Use nested array iteration and dot/bracket access for the dataset. A JSON text input must be parsed first; a provided JavaScript object must not be parsed again. These tasks are self-assessed.')],[
 ('What does Request.json() return?',['A Promise resolving to parsed data','A synchronous JSON text string','An authenticated user automatically'],0,'The body read and parse are asynchronous.'),
 ('What is a sensible storage round trip for JSON-compatible data?',['Store the object directly as arbitrary localStorage bytes','stringify on write, parse on read','parse on write, stringify on read'],1,'localStorage stores strings. Handle missing and malformed stored data.'),
 ('Which approach displays an untrusted title as plain text?',['innerHTML = title','eval(title)','textContent = title'],2,'HTML-looking data should remain text when that is the intended display.')],'JSON integration'),
 module('m8','08 Capstone and final review',[capstone])]

# An independent final assessment: new scenarios rather than a duplicated module question bank.
final_questions=[
 ('A configuration contains comments and a trailing comma. What is the first issue?',['It is not strict JSON','It must use GET','It needs an account'],0,'Strict JSON excludes comments and trailing commas.'),
 ('A learner ID is "0012". Which representation preserves that spelling?',['Number 12','String "0012"','Numeric literal 0012'],1,'The leading zeros are part of the identifier, not a number.'),
 ('A parsed catalog has lessons:[{title:"A"},{title:"B"}]. Which yields B?',['catalog.lessons.title','catalog.lessons[2].title','catalog.lessons[1].title'],2,'Nested reads use the zero-based array index and member name.'),
 ('A reviver only returns a value for key minutes. Why did other members vanish?',['Missing returns produce undefined and delete members','The JSON parser sorts them away','Revivers cannot preserve strings'],0,'Return all untransformed values explicitly.'),
 ('An API supplies "minutes":"12". Parsing succeeds. What is next?',['Assume the field is numeric','Validate against the expected field type','Run eval to recover the original type'],1,'Parsing does not enforce application types or rules.'),
 ('An export is JSON.stringify({ready:false,missing:undefined}). Which output is expected?',['{"ready":false,"missing":null}','{}','{"ready":false}'],2,'False is preserved; undefined object members are omitted.'),
 ('An array export contains an undefined item. What appears at that position?',['null','The position is removed','undefined as JSON text'],0,'Array positions are retained using null for unsupported values.'),
 ('A replacer returns undefined for the root. What can stringify return?',['{}','undefined rather than JSON text','null in every case'],1,'Root filtering can prevent a JSON document from being produced.'),
 ('A pretty-print space argument is 20. What indentation does stringify use?',['20 spaces','No indentation','At most 10 spaces per level'],2,'Numeric indentation is clamped to ten.'),
 ('A class instance is serialized and parsed. What should you expect?',['Its encoded data, without automatically restoring its prototype','An identical instance with every method','Its constructor to run automatically'],0,'JSON does not encode arbitrary runtime behavior or prototype identity.'),
 ('A diagnostic export has the same child object in two separate branches but no cycle. What happens?',['It must throw','It serializes repeated data','It writes a reference pointer automatically'],1,'Repeated references are distinct from ancestor cycles; JSON does not preserve identity.'),
 ('A serializer encounters 9007199254740993n. What is the deliberate portable fix?',['Cast to Number blindly','Append n inside JSON text','Encode a decimal string with an agreed decoding contract'],2,'Ordinary BigInt serialization throws; Number conversion can lose precision.'),
 ('A long JSON number has already been converted to a rounded Number. Which modern feature can recover the original digits?',['Primitive reviver context.source','The Number toString method','Increasing pretty-print indentation'],0,'Source text access avoids relying on an already-rounded Number.'),
 ('A client lacks JSON.rawJSON. What should an exact-ID application do?',['Call it anyway','Use a compatible agreed string representation','Round every ID to the nearest safe integer'],1,'Feature detection and compatible contracts prevent broken or lossy exports.'),
 ('JSON.isRawJSON(Object.freeze({rawJSON:"123"})) produces what?',['true','A parsed number','false'],2,'Freezing an ordinary object does not add the internal raw JSON brand.'),
 ('A response body was already consumed by response.text(). What helps before a second consumer reads it?',['Clone the response before the first consumption','Change the JSON indentation','Parse the Response object directly'],0,'A clone must be made before the body is consumed; repeated reads fail.'),
 ('A title contains HTML markup but should display literally. What should rendering use?',['innerHTML','textContent','new Function'],1,'Parsing JSON is not HTML sanitization. textContent preserves literal text.'),
 ('Which statement best separates the courses?',['JSON defines API permissions','JSON replaces HTTP methods','JSON is the data format; HTTP transports messages; an API defines interaction'],2,'The concepts work together but have distinct responsibilities.')]
course=dict(schemaVersion=1,id='json-documentation-course-v1',title='JSON',description='Understand JSON syntax, nested data, parsing, serialization, precision and real application boundaries. Based on JSON.org and the MDN JSON documentation, with guided practice, module checks and a capstone.',sections=sections,settings=dict(passScore=80,allowRetakes=True,showLessonDetails=False,unlockAll=True,sequential=False,requireLessons=True,brand='#69d9b2',background='#0c0e12',surface='#14171d',text='#edf0f7',muted='#b4bac9',border='#343b49',fontScale=1,spacing=24,contentWidth=1000,radius=8,font='system',headingFont='system',lineHeight=1.65),finalQuiz=dict(id='json-final',type='quiz',title='Final assessment — JSON skills',skill='JSON integration',questions=[dict(id=f'final-q{i+1}',prompt=p,options=o,answer=a,explanation=e) for i,(p,o,a,e) in enumerate(final_questions)]))
data=json.dumps(course,ensure_ascii=False,indent=2)+'\n'
(ROOT/'course.json').write_text(data)
embedded=json.dumps(course,ensure_ascii=False).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
(ROOT/'index.html').write_text('<!doctype html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Learn JSON from JSON.org and MDN: syntax, parsing, serialization, precision, practice and assessments."><title>JSON</title><link rel="stylesheet" href="lms.css"><script src="vendor/marked.umd.js" defer></script><script src="lesson-markdown.js" defer></script><script src="lms-runtime.js" defer></script></head><body class="lms-export-body"><div id="lms-root"></div><script id="lms-course-data" type="application/json">'+embedded+'</script></body></html>\n')
manifest=dict(retrievedAt='2026-10-07',mdnCommit=COMMIT,scope='JSON.org format/grammar; MDN glossary, learner guide and skills tasks, JSON namespace and all static methods, JSON-related errors, Request/Response body JSON. Linked external libraries and unrelated HTTP/API docs are not reproduced.',sources=sources)
(ROOT/'source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
flat=[]
def walk(ns):
    for n in ns:
        if n['type']=='section': walk(n['children'])
        else: flat.append(n)
walk(sections)
print(json.dumps(dict(modules=len(sections),decks=sum(n['type']=='slides' for n in flat),slides=sum(len(n.get('slides',[])) for n in flat),quizzes=sum(n['type']=='quiz' for n in flat),moduleQuestions=sum(len(n.get('questions',[])) for n in flat),finalQuestions=len(final_questions),sources=len(sources))))
