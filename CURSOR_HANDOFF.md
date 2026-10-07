# JSON LMS handoff

This standalone JSON course uses JSON.org and a pinned MDN snapshot. README.md and source-manifest.json define scope and attribution. The GraphQL LMS supplies runtime, layout, Markdown, mobile navigation, reports and whole-course copying.

Authoring: scripts/build-course.py. Licensed MDN sources: docs/mdn. After edits, run the generator to synchronize course.json, embedded index.html data and source-manifest.json. Preserve source credits and CC BY-SA terms. Keep the course focused on JSON; full HTTP/API documentation belongs in separate courses.

Validation: node tests/course.test.cjs; with Playwright/Chromium installed, node tests/browser.test.cjs. Browser tests start their own server.

Learner state is browser-local. Viewing all slides enables completion. Final gating is optional and disabled by default; enabling it requires lesson and quiz completion. Source examples and exercises run outside this LMS. No code-execution service, shared accounts or server grading is included.
