name: Generate contribution snake

on:
  schedule:
    - cron: "0 6 * * *"   # once a day
  workflow_dispatch:       # lets you run it by hand from the Actions tab
  push:
    branches: [main]

permissions:
  contents: write

jobs:
  generate:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: Platane/snk@v3
        with:
          github_user_name: ${{ github.repository_owner }}
          outputs: |
            dist/snake-light.svg?color_snake=#FF9933&color_dots=#ebedf0,#d4d4d4,#a3a3a3,#525252,#000000
            dist/snake-dark.svg?palette=github-dark&color_snake=#FF9933&color_dots=#161b22,#3a3a3a,#6b6b6b,#a3a3a3,#ffffff

      - uses: crazy-max/ghaction-github-pages@v4
        with:
          target_branch: output
          build_dir: dist
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
