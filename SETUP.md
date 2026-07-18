# Setup — devanshgupta11's animated GitHub profile

Everything is already built and tested against your real GitHub data
(356 contributions, 3-day current streak, 13-day longest streak as of
today). `contrib-heatmap.svg` and `info-card.svg` in this folder are
already generated and ready to commit. You only need to add your
own portrait.

## 1. Create the magic repo (skip if it already exists)

Your profile shows a `Readme.md` already at the top, so you likely have
this repo — just clone it instead of creating a new one:

```bash
git clone https://github.com/devanshgupta11/devanshgupta11.git
cd devanshgupta11
```

If it doesn't exist yet:

```bash
gh repo create devanshgupta11 --public --clone
cd devanshgupta11
```

## 2. Copy these files in

Copy everything from this folder into your cloned repo, preserving
structure:

```
devanshgupta11/
├── README.md
├── contrib-heatmap.svg      ← already generated, real data
├── info-card.svg            ← already generated, your profile info
├── data/contributions.json  ← already generated
├── scripts/
│   ├── requirements.txt
│   ├── requirements-heatmap.txt
│   ├── prep_photo.py
│   ├── make_ascii_svg.py
│   ├── make_info_card.py
│   ├── fetch_contributions.py
│   └── render_heatmap_svg.py
└── .github/workflows/update-profile-art.yml
```

## 3. Add your portrait

You need one photo of yourself (a clear, front-facing shot works best).
Put it in the repo root as `source-photo.jpg`, then:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r scripts/requirements.txt
python scripts/prep_photo.py source-photo.jpg      # writes source-prepped.png
python scripts/make_ascii_svg.py                    # writes devansh-ascii.svg
```

The first run downloads rembg's background-removal model (~176MB, one-time).

Open `devansh-ascii.svg` in a browser to preview it. If your face reads
as a dark blob, retake the photo with more even, front-facing light —
CLAHE helps but can't invent detail that isn't in the source.

## 4. Review the info card content

`scripts/make_info_card.py` already has your real "Now / Prev / Stack /
Learning / Highlights" content pulled from your GitHub profile. Edit the
`ROWS` list at the top of that file with anything you want to change,
then regenerate:

```bash
python scripts/make_info_card.py
```

## 5. Commit and push everything

```bash
git add .
git commit -m "feat: animated terminal-style profile README"
git push
```

Your profile page will now show the layout live.

## 6. Turn on the daily refresh

The workflow at `.github/workflows/update-profile-art.yml` is already
wired to re-scrape your contributions and re-render the heatmap every
day at ~06:17 UTC, using only `requests` + `beautifulsoup4` (no token
needed — it reads the same public HTML your profile page uses).

After pushing, go to your repo's **Actions** tab and manually run
"Update profile art" once (`workflow_dispatch`) to confirm it commits
a fresh `contrib-heatmap.svg`.

## Notes specific to your setup

- Your account has 25 repos, 5 followers — the info card highlights line
  reflects that; update it as those numbers change, or leave it as a
  point-in-time snapshot.
- Because your current README already has a purple gradient banner and
  emoji sections, decide whether to fully replace it (this README.md
  does) or merge the new terminal section below your existing banner —
  just paste the `<div align="center">...</div>` block from README.md
  into your current file if you want to keep both.
- GitHub strips `style=""` attributes and blocks external CSS/JS in
  READMEs, but does run SMIL/CSS-keyframe animation *inside* SVGs
  embedded via `<img>` — which is why the animation lives entirely
  inside each `.svg` file rather than in the README markup.
