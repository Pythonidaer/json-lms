# Source attribution and licenses

## MDN contributors

This course adapts the 13 MDN documents listed in `source-manifest.json`, from
mdn/content commit `bf7ff749b987d530e9a6c07f23ac66f94d968e57`, retrieved 2026-10-07.
Original titles, live source URLs, snapshot hashes and lesson mappings are in the
manifest; original Markdown and the full upstream license are in `docs/mdn/`.

MDN documentation text is licensed under Creative Commons Attribution-ShareAlike
2.5: https://creativecommons.org/licenses/by-sa/2.5/ . Course text, adaptations,
practice and assessments in `course.json` and embedded in `index.html` are made
available under that license. The upstream notice describes CC0 for code snippets
added on/after August 20, 2010 and MIT for older snippets. See the retained full
`docs/mdn/LICENSE.md` for those terms.

Changes: remove navigation and embed widgets; resolve MDN link macros; split
content at headings into slides; turn the prerequisites table into prose; link
the screenshot instead of embedding it; link current specification/compatibility
tables instead of copying generated data; add objectives, exercises and checks.
The MDN sample code is instructional, including deliberately invalid examples.
It is displayed as text, not executed by the LMS. Each adapted lesson attributes
MDN contributors and links its original source and license.

## JSON.org

Introducing JSON: https://www.json.org/json-en.html . Its format and grammar
concepts are summarized with original instructional examples and practice.
The site text, artwork, historical essays and third-party implementation directory
are not reproduced wholesale. JSON.org is credited within the course and manifest.

## Marked

The locally packaged Markdown renderer is Marked. Its MIT license is retained in
`vendor/marked.LICENSE.md`. The renderer/runtime/CSS were adapted from the user's
GraphQL LMS at commit `f78f87ddf7a1e8f14b2a6d2b3c025047e5190a50`.

This educational course is not endorsed by MDN, Mozilla or JSON.org.
