# Licensing

This repository holds two kinds of work, on different terms. The code is open. The model, the pictures and the books made from it are not.

FlyGACA is an independent educational project. It is not affiliated with, endorsed by or operated by the General Authority of Civil Aviation (GACA), Textron Aviation (Cessna) or Lycoming.

FlyGACA مشروع تعليمي مستقل. ليس تابعًا للهيئة العامة للطيران المدني ولا لـ Textron Aviation (Cessna) أو Lycoming، وليس معتمدًا منها.

## 1. Code: MIT

The [MIT License](LICENSE) covers the software only:

- the viewers and the simulation: `shared/js/`, and the `js` and `css` folders and HTML pages of each phase;
- the site and the checks: `scripts/`, `site/site.css`, `test/`, `tests/`, each phase's own `tests` folder, `.github/`;
- the builders of pages and PDFs: `09_book_figures/build.mjs`, `11_training_handbook/build.mjs`, `content/study-visuals/build.py` and their helpers;
- the parts catalogue's page and builders: `09_book_figures/parts/index.html`, `09_book_figures/parts/parts.js`, `09_book_figures/parts/parts.css`, `09_book_figures/parts/build.py` and `09_book_figures/parts/render_all.py`.

## 2. The model, the pictures and the books: all rights reserved

Copyright © 2026 BDA Company International / شركة بدع الدولية. All rights reserved.

This covers:

- **the three-dimensional model of the aeroplane in every form**: the `.blend` and `.glb` files of every phase, the model of each system in the parts catalogue (`09_book_figures/parts/m/`), their textures (`08_realistic_digital_twin/assets/`), and the scripts that generate the model (`07_kinematic_twin/build/`, `08_realistic_digital_twin/blender/`, `09_book_figures/blender/`);
- **every picture made from the model**: renders, figures, plates, covers, cards and study visuals (`09_book_figures/out/`, `09_book_figures/handbook/out/`, `09_book_figures/renders/`, `09_book_figures/atlas/`, the picture sheets of the parts catalogue (`09_book_figures/parts/t/`, `09_book_figures/parts/l/`, `09_book_figures/parts/p/`), `08_realistic_digital_twin/docs/` pictures, `11_training_handbook/figures/`, `content/study-visuals/out/`, `site/hero.webp`);
- **the FlyGACA C172N Training Handbook**: its text (`11_training_handbook/content.mjs`) and its PDF and web editions (`11_training_handbook/out/`, `11_training_handbook/index.html`);
- the text of the lessons, notes and guides written for the twin.

You may look at this work here and on FlyGACA's sites, and study from it yourself. You may not copy it, redistribute it, sell it, publish it elsewhere or build a product on it without written permission from the copyright holder. To ask: i@flygaca.com.

هذه الأعمال (النموذج ثلاثي الأبعاد بكل صوره، وكل صورة مأخوذة منه، ودليل التدريب لطائرة C172N، ونصوص الدروس) جميع حقوقها محفوظة لشركة بدع الدولية. يجوز الاطلاع عليها هنا وفي مواقع FlyGACA والدراسة منها شخصيًا، ولا يجوز نسخها ولا إعادة توزيعها ولا بيعها ولا نشرها في مكان آخر ولا بناء منتج عليها إلا بإذن مكتوب. للطلب: i@flygaca.com.

## 3. What is not FlyGACA's

- Values quoted from the Cessna Model 172N Pilot's Operating Handbook remain their publisher's material. Nothing here licenses them.
- Third-party code keeps its own licence, for example the vendored Three.js build (`08_realistic_digital_twin/vendor/three/LICENSE`).
- `site/ufuq/` is copied from FlyGACA/UFUQ, and the Fly GACA mark is not licensed for reuse.
- Open data used in some figures keeps its source's terms (NASA SRTM, Copernicus Sentinel, OpenStreetMap), as each figure's notes say.
- Values taken from the AIP of the Kingdom of Saudi Arabia belong to its publisher.

## 4. Earlier versions

Until the commit that added this file, the repository's `README.md` offered "the project's own code and models" under the MIT License. That grant stands for the versions published before this change, for anyone who took a copy of them. Sections 1 and 2 apply from this commit on.

## 5. Where a file's place is unclear

A file not named above follows the kind of thing it is: program code is under section 1, and a model, a picture or a text written to be read is under section 2. The archived packages of phases 01 to 06 are kept unchanged for the record; their models and pictures are under section 2.
