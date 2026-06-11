# Proposed Manuscript Content Changes for Reframing

This document contains the exact proposed changes to the text of `manuscript/d6mubOptimization.tex` for your review and approval. 

---

## 📝 1. Abstract (Lines 34–36)

### Original Text:
```latex
\begin{abstract}
The existence of a complete set of seven mutually unbiased bases in dimension six remains an open problem. A reproducible, precision-aware mathematical software workflow is presented to optimize unanchored approximate configurations using automatic differentiation. Candidate bases are parameterized using Lie-algebra exponentiation. A custom Taylor-series matrix exponentiation layer enables hardware acceleration on graphics processing units. Multi-seed experiments in dimension six reveal a structured transition as the number of bases increases. For three and four bases, the workflow recovers exact or partially exact configurations. For five or more bases, all optimized configurations are globally defective and frustrated. Double-precision arithmetic resolves multiple local minima in the six-basis landscape. In the present sample, single-precision execution tends to select a single low-loss basin. Multi-dimensional benchmarks show a clear execution speed crossover around dimension ninety. At this scale, parallelized graphics processing unit acceleration natively outpaces central processing unit caches.These findings provide reproducible numerical evidence, within the explored optimization workflow, of a transition to fully defective configurations beginning at five bases in dimension six. The generalized, highly portable workflow establishes a scalable framework for high-dimensional quantum combinatorial design searches.
\end{abstract}
```

### Proposed Revision:
```latex
\begin{abstract}
The search for mutually unbiased bases (MUBs) in composite dimensions remains a notorious challenge in quantum information theory, particularly in dimension six. We present a generalized, parameter-driven mathematical software workflow designed to optimize unanchored approximate MUB configurations across arbitrary dimensions $d$, candidate base counts $n$, and multi-seed sweeps. The underlying optimizer parameterizes unitary bases via Lie-algebra exponentiation, supported by a custom, hardware-accelerated complex Taylor-series layer for GPU compatibility. As a rigorous proof-of-work, we apply this software to study the optimization landscape in dimension six for varying numbers of candidate bases ($n=3$ to $6$). The experiments reveal a structured transition: the workflow recovers exact configurations for $n=3$ and $n=4$, while configurations for $n \ge 5$ become globally defective. Double-precision arithmetic resolves multiple local minima in the landscape, whereas single-precision is susceptible to basin selection effects. Performance scaling benchmarks demonstrate a hardware-acceleration crossover around dimension ninety. These results demonstrate the utility of our generalized, reproducible workflow as a scalable framework for high-dimensional quantum combinatorial searches.
\end{abstract}
```

---

## 📝 2. Introduction Reframing (Lines 49–59)

### Original Text:
```latex
This paper adopts a computational and software-focused perspective. We study approximate mutually unbiased basis (AMUB) configurations in dimension six using a reproducible numerical workflow. The focus is on understanding the structure of the underlying optimization landscape and on providing a reliable computational framework for future investigations.
...
The computational experiments target dimension six ($d=6$) for varying numbers of candidate bases ($n$). Multi-seed experiments are performed for $n=3,4,5,6$, allowing us to distinguish reproducible structural features from initialization-dependent effects. The experiments reveal a progression from exact or partially exact configurations at small $n$ to fully defective configurations at larger $n$. In particular, the results indicate that configurations with $n \ge 5$ candidate bases do not exhibit near-exact MUB pairs under the present workflow, while partial exactness is observed for $n=3$ and $n=4$.
...
Overall, this work contributes a reproducible, precision-aware computational framework for exploring AMUB configurations, together with numerical evidence about the structure of the optimization landscape in dimension six.
```

### Proposed Revision:
```latex
This paper adopts a software-engineering and computational physics perspective. We present a generalized, parameter-driven mathematical software workflow designed to find and study approximate mutually unbiased basis (AMUB) configurations in arbitrary dimensions. The focus is on providing a scalable, reliable computational framework for exploring high-dimensional MUB landscapes.
...
To demonstrate and validate the workflow, we target the notorious dimension six ($d=6$) case for varying numbers of candidate bases ($n$). Multi-seed campaigns are performed for $n=3,4,5,6$, allowing us to distinguish reproducible structural features from initialization-dependent effects. The experiments reveal a progression from exact configurations at small $n$ to fully defective configurations at larger $n$. In particular, the results indicate that configurations with $n \ge 5$ candidate bases do not exhibit near-exact MUB pairs under the present workflow, while exactness is recovered for $n=3$ and $n=4$.
...
Overall, this work contributes a generalized, reproducible computational framework for exploring AMUB configurations, together with extensive case-study evidence about the structure of the optimization landscape in dimension six.
```

---

## 📝 3. Contributions Reframing (Lines 67–68, 82–84)

### Original Text (Contribution 1 & 6):
```latex
\item \textbf{Reproducible computational workflow:}
We design and implement a structured workflow for optimizing approximate mutually unbiased bases, including explicit artifact generation (basis matrices, overlap tensors, diagnostics, optimization histories, and metadata). The workflow supports independent reproduction and extension of all reported results.
...
\item \textbf{Numerical evidence of a structural transition:}
The experiments provide reproducible numerical evidence, under the specified workflow, for a transition in the unanchored AMUB landscape: configurations with $n=3$ and $n=4$ exhibit exact or partially exact MUB relations, while all observed configurations for $n=5$ and $n=6$ are fully defective under the present workflow. This transition is observed across multiple independent runs.
```

### Proposed Revision:
```latex
\item \textbf{Generalized, reproducible computational workflow:}
We design and implement a fully parameterized, dimension-agnostic software workflow for optimizing approximate mutually unbiased bases in arbitrary dimensions. The workflow includes structured artifact generation (basis matrices, overlap tensors, diagnostics, optimization histories, and metadata) to support independent reproduction and expansion to higher-dimensional searches.
...
\item \textbf{Numerical case-study of a structural transition:}
As a validation case study, our optimization campaigns provide reproducible numerical evidence for a transition in the $d=6$ unanchored landscape: configurations with $n=3$ and $n=4$ exhibit exact MUB relations, while all observed configurations for $n=5$ and $n=6$ are fully defective under the present workflow. This transition is robustly observed across multiple independent runs.
```

---

## 📝 4. Conclusion Reframing (Line 768)

### Original Text:
```latex
This paper presented a reproducible, precision-aware workflow for unanchored approximate MUB optimization in dimension six. The workflow represents candidate bases by Lie-exponential unitary parameterizations, optimizes all bases simultaneously without fixing a reference basis, and records machine-readable artifacts including basis matrices, pairwise overlaps, diagnostics, optimization histories, and figure data.
```

### Proposed Revision:
```latex
This paper presented a generalized, reproducible mathematical software workflow for unanchored approximate MUB optimization. The workflow is dimension-agnostic, representing candidate bases by Lie-exponential unitary parameterizations, optimizing all bases simultaneously without fixing a reference basis, and recording machine-readable artifacts. As a validation case study, we successfully applied the framework to dimension six, recovering exact configurations for small basis counts and demonstrating a robust structural transition to fully defective configurations for five or more bases.
```

---

# 💻 Software Generalization Review and Recommendations

The core library (`src/amub`) is already mathematically dimension-agnostic. The model definition `UnanchoredAMUBModel` in `model.py` and the loss calculation in `loss.py` accept the dimension $d$ and number of bases $n$ as parameters and construct matrices accordingly.

However, to align the software with the reframed "generalized workflow" story, we recommend the following minimalist updates to the runner scripts and configurations:

## 1. CLI Override for Dimension and Basis Count
Currently, runner scripts like `scripts/run_single_seed_sweep.py` and `scripts/run_multiseed_campaign.py` read parameters entirely from static YAML files.
*   **Recommendation:** Add optional `--dimension` (`-d`) and `--n-bases` argparse arguments to `scripts/run_single_seed_sweep.py` and `scripts/run_multiseed_campaign.py` to allow users to run arbitrary dimensional sweeps directly from the terminal without editing configuration files.

## 2. Dynamic Taylor Order Safety Check
Our custom GPU-accelerated exponentiation layer uses a fixed Taylor series expansion order ($N=20$) in `src/amub/taylor_exp.py`. While highly accurate for the dimension six generators ($\|H\|_2 \approx 2.7$), higher dimensions or larger step sizes may produce generators with larger norms, causing the truncation error to grow.
*   **Recommendation:** Implement a warning or adaptive order mechanism in `src/amub/taylor_exp.py` if the input generator matrix norm $\|X\|_2$ exceeds a threshold (e.g. $\|X\|_2 > 3.0$), protecting truncation bounds in generalized, higher-dimensional searches.

## 3. Generalize the Diagnostic and Plotting Utilities
Certain functions in `src/amub/plotting.py` might contain layout or style elements optimized primarily for $d=6$ or small values of $n$.
*   **Recommendation:** Verify that color mappings, axis limits, and annotations scale gracefully when $d \ge 10$ or when the number of bases $n \ge 8$. Ensure labels and layout parameters are dynamically sized.

