\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{fastverk-onepager}[2026/06/24 fastverk one-pager]

% Inherit the brand class (fonts + palette + helpers), then a tight one-page
% layout with a midnight header band and amber section headings.
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{fastverk}}
\ProcessOptions\relax
\LoadClass{fastverk}

\geometry{margin=16mm}  % geometry already loaded by fastverk.cls; just reconfigure
\RequirePackage{titlesec}

% \fvheader{title}{subtitle}: a midnight band (cream title + amber subtitle)
% closed by an amber rule.
\newcommand{\fvheader}[2]{%
  \noindent\colorbox{fvbg}{%
    \begin{minipage}[c][22mm][c]{\dimexpr\linewidth-2\fboxsep\relax}%
      \hspace{3mm}{\color{fvfg}\Huge\bfseries #1}\\[1.5mm]
      \hspace{3mm}{\color{fvaccent}\large #2}%
    \end{minipage}}\par
  \vskip1.5mm{\color{fvaccent}\rule{\linewidth}{1.4pt}}\par\vskip5mm}

\titleformat{\section}{\large\bfseries\color{fvaccent}}{}{0pt}{}
\titlespacing{\section}{0pt}{1.6ex}{0.5ex}

\endinput
