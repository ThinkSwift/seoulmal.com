# seoulmal.com

Static site on GitHub Pages (ThinkSwift/seoulmal.com, branch `main`, root). No build step. DNS on Cloudflare, DNS only —
never proxied in front of Pages.

- Looks like the app: paper, ink, teal and the dancheong accents of SeoulMal `Theme.swift`. One look, no dark set.
- Copy lives in `js/strings.js` (en + 18, the apps' 19 UI locales). Change it through a patch:
  `python3 tools/strings.py patch js/strings.js <patch.json>` (it checks placeholders).
- Language pages `/<lang>/` are generated: after editing `index.html`, `js/strings.js` or the app's store listing
  (`~/Projects/SeoulMal/fastlane/metadata`), run `python3 tools/locale-pages.py`. Each page names its language in
  `<html data-lang>`; `js/i18n.js` reads that first. `<title>` and description come from the store listing.
- `privacy/` is the app's privacy policy (English, like the other apps) and the App Store privacy URL.
  `support/` is the App Store support URL.
- Events go to the shared web events endpoint as `seoulmal.com` (`js/track.js`, App Store taps).
- Until the app is live there is no App Store link: the button reads "Coming soon". On the day 1.0 is live in ASC, the
  link goes in with `?ct=web-sm-<place>` and the `apple-itunes-app` meta.
