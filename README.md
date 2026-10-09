# Gabriel Rul-lan - CV project

| Part | Folder | Purpose |
| :--- | :--- | :--- |
| **Front** | [`web/`](web/) | Public Jekyll site published at [data-partner.xyz](https://www.data-partner.xyz) (ES/EN/CA portfolio). See [`web/README.md`](web/README.md). |
| **Back** | [`CV_gen/`](CV_gen/) | Private CV generation workspace: master CVs, job-offer tailoring, STAR Q&A bank, history, PDF exports and the build script. See [`CV_gen/README.md`](CV_gen/README.md). |

The two parts are independent: only `web/` is deployed (via `.github/workflows/pages.yml`), so nothing in `CV_gen/` (job offers, phone, Q&A, PDFs) is ever published.

## Web (front)

```bash
cd web
bundle exec jekyll serve   # local preview
```
Content lives in `web/_data/{es,en,ca}.yml`; layout in `web/_layouts/default.html`.

> **GitHub Pages setting:** *Settings -> Pages -> Source* must be set to **GitHub Actions** (the site is no longer at the repo root).

## CV generator (back)

```bash
python CV_gen/build.py                 # master CVs -> CV_gen/build/*.html (images embedded)
python CV_gen/build.py --pdf           # also export PDFs (needs Edge or Chrome)
python CV_gen/build.py "CV_gen/job offers/<file>.md" --pdf --out CV_gen/02_PDFs_Exportados
```
Standard library only; plain-markdown CVs additionally need `pip install markdown`. Conventions and AI-assistant rules (CSS preservation, no work-modality in CVs, location fixed) are in `CV_gen/README.md`.
