# JSON LMS

Live course: https://pythonidaer.github.io/json-lms/

A focused, self-paced course from JSON.org and MDN using the GraphQL LMS reference: **8 modules, 20 lesson decks, 195 slides, 6 module quizzes (26 questions), and an independent 18-question final assessment.**

## Curriculum

1. Orientation and study strategy
2. JSON.org format/grammar: objects, arrays, strings, escapes, numbers and whitespace
3. Nested data, the JSON namespace and complete formal grammar
4. JSON.parse, revivers, errors, shape checks and safe handling
5. JSON.stringify, replacers, indentation, toJSON, round trips, cycles and BigInt
6. Precision, exact-number contracts, JSON.rawJSON and JSON.isRawJSON
7. Request/Response JSON body methods and MDN practice
8. Lesson-catalog capstone and final review

JSON remains separate from a full HTTP/API course. Fetch examples explain how JSON enters an application. Each MDN chapter retains technical source sections and code examples, with an original objective, exercise and worked check. Exercises are self-assessed in a local project or browser console; the LMS does not execute arbitrary lesson code.

## Source coverage

`source-manifest.json` maps 14 source entries: JSON.org's format/grammar introduction plus 13 MDN pages (glossary, guide, skills task, namespace, all four static methods, three JSON error references, Request.json and Response.json). It includes the exact MDN commit, source hashes and lesson IDs. Original Markdown and the full upstream license are retained in `docs/mdn/`.

JSON.org's external library directory and historical essays are linked, not reproduced. MDN navigation and live embed widgets are removed. Generated specification and compatibility tables link to live MDN sections; they are not frozen. The complete formal grammar is retained. Newer JavaScript features have feature-detection examples and portable alternatives. JSON Schema's separate specification, third-party library manuals and unrelated API/HTTP pages are outside this JSON-focused snapshot.

MDN-derived course content is attributed to MDN contributors under CC BY-SA 2.5. See `THIRD_PARTY_NOTICES.md` and `docs/mdn/LICENSE.md`.

## Run and maintain

No build/install step is required to use the course. Run `python3 -m http.server 8000`, then open http://localhost:8000 . Course text, quizzes and Markdown rendering are local; source links and remote examples require connectivity. The embedded index.html also opens directly, but local-file storage/clipboard behavior varies by browser.

Edit `scripts/build-course.py` for authored lessons and `docs/mdn/*.md` when updating the source snapshot. Run `python3 scripts/build-course.py` to synchronize course.json, embedded index.html data and the manifest. Keep IDs stable; changed lesson content resets that lesson's saved progress.

## Validation

Run `node tests/course.test.cjs` for source hashes, embedded parity, runtime readiness, code fences, JSON examples and assessment integrity.

Install Playwright and Chromium in your development environment, then run `node tests/browser.test.cjs`. It starts its own local server and checks 390/768/1440px layouts, mobile menu, safe Markdown, all 195 slides, saved completion/notes, quiz grading, skill reports, final gating and complete clipboard copying with a manual fallback.

## Learner features and limits

The outline collapses on every device. Small screens use an animated hamburger/X menu beside the outline toggle. The JSON title returns to the first lesson. Skill reports support CSV export and separate sample data from actual progress.

All content is open by default. Disable **Unlock all lessons and quizzes** in Settings to require lesson/module-quiz completion before the final. Passing is 80%, with retakes enabled.

**Copy entire course**, below the final assessment, includes all sections, slides, examples, sources, choices, answers and explanations, even if collapsed or locked. Personal notes and progress are excluded.

Progress, notes and settings stay in this browser. There is no authentication, shared backend, instructor dashboard, verified certificate or exam-secure grading. Answers ship in the client; results are personal study feedback.
