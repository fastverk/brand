\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{fastverk}[2026/06/24 fastverk brand document class]

% Pass unknown options through to article.
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass[11pt]{article}

\RequirePackage[a4paper,margin=22mm]{geometry}
\RequirePackage{amsmath}
\RequirePackage{graphicx}
\RequirePackage[dvipsnames]{xcolor}
\RequirePackage{tikz}
\RequirePackage{enumitem}
\RequirePackage{array}
\RequirePackage{parskip}
\RequirePackage{fontspec}

% Brand typeface. brand_doc stages the fonts at fonts/ relative to the
% tectonic working directory, so this Path resolves in any consuming repo.
\setmainfont{SpaceGrotesk-Medium.ttf}[
  Path = fonts/ ,
  BoldFont = SpaceGrotesk-SemiBold.ttf ]

% Brand palette (midnight — the canonical fastverk colors).
\definecolor{fvbg}{HTML}{15161A}
\definecolor{fvfg}{HTML}{ECE7DA}
\definecolor{fvaccent}{HTML}{E0A33E}
\definecolor{fvtertiary}{HTML}{4A565A}

% A labeled color swatch.
\newcommand{\fvswatch}[2]{%
  \begin{tikzpicture}[baseline]
    \fill[#1] (0,0) rectangle (1.1,1.1);
    \draw[black!30] (0,0) rectangle (1.1,1.1);
  \end{tikzpicture}\hspace{2pt}\texttt{\footnotesize #2}}

\pagestyle{empty}
\endinput
