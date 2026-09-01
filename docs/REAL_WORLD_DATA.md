# REAL-WORLD EMPIRICAL DATASET PROVENANCE & SPECIFICATION

**Project**: Early-Warning Mathematics for Complex Systems  
**Stage**: Phase 4 Empirical Real-World Integration  
**Date**: September 2026  
**Auditor**: Principal Investigator & Hostile Scientific Reviewer  

---

## 1. Dataset Provenance & Metadata

| Field | Detail |
| :--- | :--- |
| **Dataset Title** | GISP2 Greenland Ice Sheet Project 2 delta-18-O Paleoclimate Record |
| **Target Transition** | Termination of the Younger Dryas (YD) Cold Stadial to Preboreal Holocene |
| **Transition Age** | ~11,700 yr Before Present (BP) (~11.7 ka BP) |
| **Primary Authors** | P. M. Grootes and M. Stuiver |
| **Canonical Citations**| Grootes, P.M., and Stuiver, M. (1997). *Oxygen 18/16 variability in Greenland snow and ice with 10-to-1000-year resolution.* **J. Geophys. Res.**, 102(C12), 26455–26470. [DOI: 10.1029/97JC00880](https://doi.org/10.1029/97JC00880); Stuiver, M., & Grootes, P. M. (2000). *GISP2 oxygen isotope ratios.* **Quaternary Research**, 53(3), 277–284. |
| **Host Repository** | NOAA National Centers for Environmental Information (NCEI) / World Data Service for Paleoclimatology |
| **Repository URL** | [https://www.ncei.noaa.gov/access/paleo-search/study/1785](https://www.ncei.noaa.gov/access/paleo-search/study/1785) |
| **License** | Public Domain (U.S. Government Open Scientific Data) |
| **Bundled File** | `data/real_world/gisp2_younger_dryas.csv` |

---

## 2. Paleoclimate Context & Critical Transition Characteristics

The termination of the Younger Dryas (~11,700 years BP) represents the most widely studied abrupt climatic transition in modern Earth science. During this event:
- North Atlantic atmospheric temperatures warmed by $7^\circ\text{C}$ to $10^\circ\text{C}$ within a few decades.
- The transition is hypothesized in climate dynamics literature (Dakos et al. 2008 *PNAS*; Lenton et al. 2012 *Phil. Trans. R. Soc.*) to represent a catastrophic saddle-node bifurcation of the Atlantic Meridional Overturning Circulation (AMOC) driven by shifting North Atlantic freshwater budgets.
- Because it possesses a definitive, verified historical collapse timestamp ($T_{\text{trans}} \approx 11,700\text{ yr BP}$), it provides a canonical real-world benchmark for testing whether early-warning indicators could have signaled the transition in advance.

---

## 3. Preprocessing Protocol

To prevent look-ahead bias and spurious artifacts:
1. **Chronological Alignment**: The time coordinate is arranged chronologically forward in time:
   $$t = 12900 - \text{Age}_{\text{BP}}$$
   starting from the Younger Dryas onset ($12,900\text{ yr BP}$, $t = 0\text{ yr}$) and progressing toward the Holocene warming ($11,700\text{ yr BP}$, $t = 1200\text{ yr}$).
2. **Causal Detrending**: To isolate the stochastic fluctuations from century-scale background climate trends without future look-ahead, a causal backward-looking rolling mean window ($W_{\text{detrend}} = 15$ steps, $300\text{ yr}$) is subtracted:
   $$r(t_k) = y(t_k) - \frac{1}{W} \sum_{j=0}^{W-1} y(t_{k-j})$$
3. **Exploratory Constraint**: Because real-world paleoclimate records constitute a single historical realization ($N=1$), **no claim of statistical generalizability or hypothesis rejection can be made from this dataset alone**. Results are reported strictly as an exploratory demonstration of observational applicability.
