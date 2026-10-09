# Gabriel Rul-lan CV Portfolio

This repository hosts my Data Partner CV and portfolio. It is automatically published to [data-partner.xyz](https://www.data-partner.xyz) using GitHub Pages.

## How to Maintain and Update the CV

The site has been refactored to use Jekyll (natively supported by GitHub Pages). You no longer need to edit HTML directly to update your CV!

### Updating Content

All the textual content, including your resume experience, skills, and translations, is stored in YAML data files in the `_data/` folder:

- `_data/es.yml` (Spanish - Main)
- `_data/en.yml` (English)
- `_data/ca.yml` (Catalan)

To add a new job or update a skill:
1. Open the corresponding `.yml` file in the `_data/` folder.
2. Find the `resume` or `skills` section.
3. Edit the text or add a new block using the same YAML syntax.
4. Commit your changes to the `main` branch. GitHub Actions will automatically rebuild the site.

### Updating the Layout

If you want to change the HTML structure, colors, or CSS classes, edit the single layout file:
- `_layouts/default.html`

This layout is automatically applied to `index.html`, `en/index.html`, and `ca/index.html`.
