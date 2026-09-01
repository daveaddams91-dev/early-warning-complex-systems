# COMPREHENSIVE BIBLIOGRAPHY AUDIT & PRIMARY SOURCE VERIFICATION

**Project**: Early-Warning Mathematics for Complex Systems  
**Auditor**: Rajveersinh Vishal Pardeshi ([ORCID: 0009-0004-7838-4064](https://orcid.org/0009-0004-7838-4064))  
**Date**: September 2026  
**Verification Method**: Automated Crossref REST API query (`https://api.crossref.org/works/<doi>`) and primary publisher confirmation.

---

## 1. Executive Summary of Audit Findings

An exhaustive, item-by-item verification was conducted across all citations in the repository. Four significant metadata errors were identified in the preliminary AI-assisted bibliography, rigorously investigated, and resolved against the primary literature:

| Entry | Original Issue in Bibliography | Investigation & Root Cause | Corrected Primary Source & Verified DOI |
| :--- | :--- | :--- | :--- |
| **#9 (Weinans et al.)** | **Fabricated Mashup / Dead DOI (404)**: Listed as 2021 *Sci. Rep.* 11(1), 14977 with DOI `10.1038/s41598-021-94269-w` and invented co-author "Sloan, C." | Spliced two distinct papers by the same lead author: (a) 2019 *J. R. Soc. Interface* on leading PCA1 eigenvector projection, and (b) 2021 *Sci. Rep.* on multivariate indicator benchmarking. | **Disentangled into two verified citations**:<br>1. Weinans et al. (2019) *J. R. Soc. Interface* 16(159), 20190629. DOI: [`10.1098/rsif.2019.0629`](https://doi.org/10.1098/rsif.2019.0629).<br>2. Weinans et al. (2021) *Sci. Rep.* 11(1), 9148. DOI: [`10.1038/s41598-021-87839-y`](https://doi.org/10.1038/s41598-021-87839-y). |
| **#12 (Bury et al.)** | **Invented Co-Authors & Wrong Title**: Listed with invented co-authors "Früh, M." and "Zou, H.", "Anand, R. S." instead of "Anand, M.", omitted Scheffer and Bauch, and had title "critical transitions" instead of "tipping points". | DOI was genuine (`10.1073/pnas.2106140118`), but author list and title suffered AI hallucination. | Bury, T. M., Sujith, R. I., Pavithran, I., Scheffer, M., Lenton, T. M., Anand, M., & Bauch, C. T. (2021). *Deep learning for early warning signals of tipping points.* **PNAS**, 118(39), e2106140118. DOI: [`10.1073/pnas.2106140118`](https://doi.org/10.1073/pnas.2106140118). |
| **#15 (Boettiger et al. 2013)** | **Dead DOI (404)**: Listed with DOI `10.1007/s12080-013-0186-x`. | DOI had transposition error (`-0186-x` instead of `-0192-6`). | Boettiger, C., Ross, N., & Hastings, A. (2013). *Early warning signals: the charted and uncharted territories.* **Theoretical Ecology**, 6(3), 255–264. DOI: [`10.1007/s12080-013-0192-6`](https://doi.org/10.1007/s12080-013-0192-6). |
| **#16 (Ritchie & Sieber 2016)** | **Mismatched DOI (Radar Paper)**: Listed with DOI `10.1063/1.4962700`. | Resolved to a completely unrelated 2016 radar engineering paper by Quan et al. in *Rev. Sci. Instrum.* | Ritchie, P., & Sieber, J. (2016). *Early-warning indicators for rate-induced tipping.* **Chaos**, 26(9), 093116. DOI: [`10.1063/1.4963012`](https://doi.org/10.1063/1.4963012). |

---

## 2. Complete 24-Entry Crossref Verification Table

Every single entry in the bibliography has been verified live against the Crossref database. All 24 citations are active, resolve correctly, and match primary source publications:

| # | Citation Key | First Author & Year | Journal / Venue | Verified Resolving DOI / URL | Status |
| :---: | :--- | :--- | :--- | :--- | :---: |
| 1 | `scheffer2009early` | Scheffer et al. (2009) | *Nature* 461, 53–59 | [`10.1038/nature08227`](https://doi.org/10.1038/nature08227) | **VERIFIED** |
| 2 | `dakos2008slowing` | Dakos et al. (2008) | *PNAS* 105, 14308–14312 | [`10.1073/pnas.0802430105`](https://doi.org/10.1073/pnas.0802430105) | **VERIFIED** |
| 3 | `carpenter2006rising` | Carpenter & Brock (2006) | *Ecol. Lett.* 9, 311–318 | [`10.1111/j.1461-0248.2005.00877.x`](https://doi.org/10.1111/j.1461-0248.2005.00877.x) | **VERIFIED** |
| 4 | `may1977thresholds` | May (1977) | *Nature* 269, 471–477 | [`10.1038/269471a0`](https://doi.org/10.1038/269471a0) | **VERIFIED** |
| 5 | `stommel1961thermohaline` | Stommel (1961) | *Tellus* 13, 224–230 | [`10.1111/j.2153-3490.1961.tb00079.x`](https://doi.org/10.1111/j.2153-3490.1961.tb00079.x) | **VERIFIED** |
| 6 | `bandt2002permutation` | Bandt & Pompe (2002) | *Phys. Rev. Lett.* 88, 174102 | [`10.1103/PhysRevLett.88.174102`](https://doi.org/10.1103/PhysRevLett.88.174102) | **VERIFIED** |
| 7 | `adams2007bayesian` | Adams & MacKay (2007) | *arXiv preprint* | [`arXiv:0710.3742`](https://arxiv.org/abs/0710.3742) | **VERIFIED** |
| 8 | `delong1988comparing` | DeLong et al. (1988) | *Biometrics* 44, 837–845 | [`10.2307/2531595`](https://doi.org/10.2307/2531595) | **VERIFIED** |
| 9 | `kendall1954note` | Kendall (1954) | *Biometrika* 41, 403–404 | [`10.1093/biomet/41.3-4.403`](https://doi.org/10.1093/biomet/41.3-4.403) | **VERIFIED** |
| 10 | `weinans2019finding` | Weinans et al. (2019) | *J. R. Soc. Interface* 16, 20190629 | [`10.1098/rsif.2019.0629`](https://doi.org/10.1098/rsif.2019.0629) | **VERIFIED** |
| 11 | `weinans2021evaluating` | Weinans et al. (2021) | *Sci. Rep.* 11, 9148 | [`10.1038/s41598-021-87839-y`](https://doi.org/10.1038/s41598-021-87839-y) | **VERIFIED** |
| 12 | `chen2012detecting` | Chen et al. (2012) | *Sci. Rep.* 2, 342 | [`10.1038/srep00342`](https://doi.org/10.1038/srep00342) | **VERIFIED** |
| 13 | `dakos2014critical` | Dakos & Bascompte (2014) | *PNAS* 111, 17546–17551 | [`10.1073/pnas.1406326111`](https://doi.org/10.1073/pnas.1406326111) | **VERIFIED** |
| 14 | `bury2021deep` | Bury et al. (2021) | *PNAS* 118, e2106140118 | [`10.1073/pnas.2106140118`](https://doi.org/10.1073/pnas.2106140118) | **VERIFIED** |
| 15 | `kleinen2003potential` | Kleinen et al. (2003) | *Ocean Dynamics* 53, 53–63 | [`10.1007/s10236-002-0023-6`](https://doi.org/10.1007/s10236-002-0023-6) | **VERIFIED** |
| 16 | `lenton2012early` | Lenton et al. (2012) | *Phil. Trans. R. Soc. A* 370, 1185–1204 | [`10.1098/rsta.2011.0304`](https://doi.org/10.1098/rsta.2011.0304) | **VERIFIED** |
| 17 | `ashwin2012tipping` | Ashwin et al. (2012) | *Phil. Trans. R. Soc. A* 370, 1166–1184 | [`10.1098/rsta.2011.0306`](https://doi.org/10.1098/rsta.2011.0306) | **VERIFIED** |
| 18 | `boettiger2012early` | Boettiger & Hastings (2012) | *Proc. R. Soc. B* 279, 4734–4739 | [`10.1098/rspb.2012.2085`](https://doi.org/10.1098/rspb.2012.2085) | **VERIFIED** |
| 19 | `boettiger2013early` | Boettiger et al. (2013) | *Theor. Ecol.* 6, 255–264 | [`10.1007/s12080-013-0192-6`](https://doi.org/10.1007/s12080-013-0192-6) | **VERIFIED** |
| 20 | `ritchie2016early` | Ritchie & Sieber (2016) | *Chaos* 26, 093116 | [`10.1063/1.4963012`](https://doi.org/10.1063/1.4963012) | **VERIFIED** |
| 21 | `kefi2014early` | Kéfi et al. (2014) | *PLoS ONE* 9, e92097 | [`10.1371/journal.pone.0092097`](https://doi.org/10.1371/journal.pone.0092097) | **VERIFIED** |
| 22 | `bauch2016early` | Bauch et al. (2016) | *PNAS* 113, 14560–14567 | [`10.1073/pnas.1604978113`](https://doi.org/10.1073/pnas.1604978113) | **VERIFIED** |
| 23 | `grootes1997oxygen` | Grootes & Stuiver (1997) | *J. Geophys. Res.* 102, 26455–26470 | [`10.1029/97JC00880`](https://doi.org/10.1029/97JC00880) | **VERIFIED** |
| 24 | `stuiver2000gisp2` | Stuiver & Grootes (2000) | *Quat. Res.* 53, 277–284 | [`10.1006/qres.2000.2127`](https://doi.org/10.1006/qres.2000.2127) | **VERIFIED** |
