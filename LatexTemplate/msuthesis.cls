% msuthesis.cls Mississippi State University thesis class
% Reference Guidelines, May 1999 (Page numbers given below.)
% revised 2012 Standards for Preparing Theses and Dissertations 6th Edition
%% this template by Edward B. Allen
%% revised by Edward B. Allen 10/19/12
%% revised by Edward B. Allen 5/10/12
%% revised by Matthew C. Funk 4/25/12
%% Acknowledgments
%%  ut-thesis.cls by Francois Pitt (fpitt@cs.utoronto.ca>,
%%  prior MSU thesis classes by:
%%    Puri Bangalore
%%    Edward Luke
%%    Jingwei Lu 
%%    Zhengzhu Feng
% Updates:
% 2/24/2003 added \Tablewithfigure, \Tabledblwithfigure, \rotatedtablewithfigure
% 2/24/2003 changed font of subsection and subsubsection per MSU library preference.
% 3/8/06 changed font of subsubsection to be italics, not bold per MSU library preference.
% 3/9/06 added vertical space between caption and table text to achieve one blank line per MSU
% 5/17/07 revise to conform to 2007 version of MSU  "Standards for Preparing Theses and Dissertations"
%          Reversed changes 2/24/03 and 3/8/06.
%          eba prefers arabic chapter numerals
% 4/23/08 per complaints from MSU library:
%          made top margin of title page 3.5in
%          made distance from author name to degree description on title page 1.5in
%          added blank line after chapter line in table of contents
%          left top margin of abstract at 1 inch per p.35 of Standard
%          left headings numbered in the same font instead of different fonts (e.g. italics) per p.55
% 6/11/09 revised to conform to current measurement practices of MSU Library
%          Top margin of  first page of each chapter and chapter-like heading
%          vertical spacing of title page
%          Top margin of abstract page
%          2 lines between chapter title and paragraph
% 4/25/12 revised to conform as much as possible  to MSU Standards 6th edition.
% 10/19/12 Made space 2 lines between List of Tables title and first entry and made space 2 lines between List of Figures title and first entry
% 10/19/12 Made space 3 lines between Chapter title and first paragraph and made space 2 lines between Chapter title and first section title 
% 12/7/12 Adjustments to make title page bottom margin exactly 1 in
% 7/10/13 added two lines from indentfirst.sty, deprecated camel-case Section commands, added \sectionnoparagraph etc.
% 7/11/13 edited \UpperBookTitle so that spacing on title page conforms to Standard 6th edition for short titles.
%7/12/13 added \Figurewithnotes and \Tablewithnotes.  Edited exfaq.tex and recompiled examplethesis.pdf
%8/14/13 Revised layout of signature page, per email and revised Standard

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{msuthesis}[2012/05/10 MSU thesis class]

%options%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{book}}
\ProcessOptions
\LoadClass[letterpaper,12pt,oneside,onecolumn,openany,final,titlepage]{book}

%12pt option%%%%%
%Large is 17pt
%\setlength{\parindent}{1.5em}  %bk12.clo default

%packages%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\RequirePackage{ifthen}
\RequirePackage{theorem}
\RequirePackage{xspace}             %MSU%%%for misc commands
\RequirePackage[strict]{changepage}
% examplethesis.tex has a choice of \usepackage[...]{graphicx} commands
%    depending on the types of graphics files to be used in the document
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\AtBeginDocument{%
\bibliographystyle{msucs}
\settocindents
}
\AtEndDocument{
\label{page:lastpage}
}

%declarations%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% The following removes the need for the CamelCase section commands which are now deprecated.
% It indents the first paragraph after each section title
%From indentfirst.sty by David Carlisle
%   --h/t to  Rikk Anderson
\let\@afterindentfalse\@afterindenttrue
\@afterindenttrue
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%margin declarations%%%%%thanks to Edward Luke.
%1 inch = 72pt
\setlength{\topmargin}{0in}
\setlength{\headheight}{0pt}
\setlength{\headsep}{0pt}
\setlength{\textheight}{630pt} %was 630 648pt = 9 inch
\setlength{\textwidth}{432pt}
\setlength{\oddsidemargin}{0.25in} %1in + 0.25in for 1.25in (L/R) margins
\setlength{\footskip}{18pt} %bottom of footer is 0.25in from bottom of text body
%\setlength{\footnotesep}{16.8pt}
%\setlength{\skip\footins}{2cm} %spacing between footnote and body
%\setlength{\paperwidth}{612pt}
%\setlength{\paperheight}{792pt}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% \newspacing changes line spacing on the fly.  For example:
%       \newspacing{1}   produces single spacing
%       \newspacing{2.5}   does 2 1/2 spacing
% and so on.   This takes effect for the current paragraph, and obeys the usual
% scoping rules.  Thus if you put it inside a {...} group or within some
% environment (like description, quote, etc) you'll revert to the previous line
% spacing when you leave the group or environment.
\def\newspacing#1{%
  \def\baselinestretch{#1}\ifx\@currsize\normalsize %
  \@normalsize \else \@currsize\fi%
}   
\newcommand{\singlespacing}{1}
\newcommand{\defaultspacing}{2} %MSU%%% double spacing
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%line breaking declarations%%%%%
\widowpenalty=50000      %MSU%%% widows and orphans not allowed
\clubpenalty=50000
\displaywidowpenalty=50000

%float declarations%%%%%%%
\setcounter{topnumber}{10}        %MSU%%%very large number of floats per page
\setcounter{bottomnumber}{10}     %MSU%%%very large number of floats per page
\setcounter{totalnumber}{10}      %MSU%%%very large number of floats per page
\renewcommand{\topfraction}{0.5}  %MSU%%% largest float is 50% of page if paragraphs on same page
\renewcommand{\bottomfraction}{0.5}
\renewcommand{\textfraction}{0.4}
\renewcommand{\floatpagefraction}{0.5}
\setlength{\floatsep}{2\baselineskip} %MSU%%% 2 blank lines around float
\setlength{\textfloatsep}{2\baselineskip}
\setlength{\intextsep}{2\baselineskip} 
\setlength{\dblfloatsep}{2\baselineskip}
\setlength{\dbltextfloatsep}{2\baselineskip}
\newlength{\figwidth}
\newlength{\tabwidth}
\newlength{\tmplen}

%definitions%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\newcommand{\dedicationname}{Dedication}
\newcommand{\acknowledgmentsname}{Acknowledgements} %British (older) spelling
\renewcommand{\contentsname}{Table of Contents}
\renewcommand{\listfigurename}{List of Figures}
\renewcommand{\listtablename}{List of Tables}
\newcommand{\listofsymbolsname}{List of Symbols}
\renewcommand{\bibname}{References}
\renewcommand{\figurename}{Figure}
\renewcommand{\tablename}{Table}
\renewcommand{\chaptername}{Chapter}
\renewcommand{\appendixname}{Appendix}


%definitions for major subdivisions%%%%%%%%%%%%%%%%%%%%%%%%
%
\renewcommand\frontmatter{%
\clearpage
\@mainmatterfalse
\pagenumbering{roman}
\pagestyle{empty}
}
\renewcommand\mainmatter{%
\clearpage
\@mainmattertrue
\newspacing{\defaultspacing}
\pagenumbering{arabic}
\markright{}
\pagestyle{plain} %%%MSU all page number bottom center
\addtocontents{toc}{\par\mbox{}} %MSU%%%blank line 
\addtocontents{toc}{\par\noindent\MakeUppercase{\protect\chaptername}}
}
\renewcommand\backmatter{%
\clearpage
\@mainmatterfalse
}
\renewcommand\appendix{ 
%MSU/CSE Dept%%%appendices should be placed after references i.e. backmatter
\@mainmattertrue            %appendix similar to chapter
\setcounter{chapter}{0}%
\setcounter{section}{0}%
\renewcommand\@chapapp{\appendixname}%
\renewcommand{\thechapter}{\Alph{chapter}}
\renewcommand{\thesection}{\thechapter.\arabic{section}}
\renewcommand{\thetable}{\thechapter.\arabic{table}}
\renewcommand{\thefigure}{\thechapter.\arabic{figure}}
\renewcommand{\theequation}{\thechapter.\arabic{equation}} %MSU%%%A is prefix.
\addtocontents{toc}{\par\mbox{}} %MSU%%%blank line
\addtocontents{toc}{\par\noindent\MakeUppercase{\protect\appendixname}}
}

%%%title page definitions%%%MSU%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
\newcommand{\booktitle}{}
\newcommand{\booktitletwo}{}
\newcommand{\booktitlethree}{}
\newcommand{\authorname}{***authorname missing***}
\newcommand{\doctypearticle}{A\xspace} %A or An
\newcommand{\doctype}{***Doctype missing***} %Dissertation, Thesis, Project, etc.
\newcommand{\university}{Mississippi State University} %default
\newcommand{\department}{***Department missing****}
\newcommand{\major}{***major missing***}
\newcommand{\degree}{***degree missing****}
\newcommand{\city}{Mississippi State}  %default
\newcommand{\state}{Mississippi}       %default
\newcommand{\degreemonth}{***degreemonth missing***}
\newcommand{\degreeyear}{***degreeyear missing***}
\newcommand{\kwlist}{} %%%%MSU key words allowed
\newcommand{\UpperBookTitle}{%            %%%MSU title not all caps
   \settowidth{\tmplen}{\protect\booktitle}
   \ifthenelse{\tmplen>0}{%
   {\booktitle}
   }{**** title is missing *****}
    \settowidth{\tmplen}{\protect\booktitletwo}
   \ifthenelse{\tmplen>0}{%
   \\
   {\booktitletwo}
   }{}
   \settowidth{\tmplen}{\booktitlethree}
   \ifthenelse{\tmplen>0}{%
   \\
   {\booktitlethree}
   }{}
}

\newlength{\titletopspace}
\setlength{\titletopspace}{1.85in} %default to achieve 3.5 to 4.0 inches.
%%%12/7/12 changed from 1.80in to 1.85in to make bottom margin exactly 1in 
\newcommand{\maketitlepage}{%
\setlength{\textheight}{637pt} %overall document is 630 648pt = 9 inch
%12/7/12 changed to 637pt to make bottom margin exactly 1 in.
\clearpage
\changepage{18pt}{}{}{}{}{}{}{}{-18pt}  
%this page counts as page i %MSU
\newspacing{\defaultspacing}
\null
\vspace{0.21in}
\vspace{\titletopspace}
\begin{center}
\UpperBookTitle
\par\vspace{0.8in} %6th ed std. calls for 1in, 0.8in gives best result
By\\
\authorname
\par\vspace{1.5in} %%%MSU 
\newspacing{\singlespacing}
\doctypearticle \doctype\\
Submitted to the Faculty of\\
Mississippi State University\\
in Partial Fulfillment of the Requirements\\
for the Degree of {\degree}\\
in {\major}\\
in the {\department}
\par\vspace{2\baselineskip}
Mississippi State, Mississippi\\
\vspace{\baselineskip}
{\degreemonth}\ {\degreeyear}
\end{center}
\changepage{-18pt}{}{}{}{}{}{}{}{18pt}
\setlength{\textheight}{630pt} %set textheight for rest of document at 630 648pt = 9 inch
}

%%%copyright page definitions%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
\newcommand{\copyrightholder}{\authorname}
\newcommand{\copyrightyear}{\degreeyear}
\newcommand{\copyrightpage}{
\clearpage
\thispagestyle{empty}
\newspacing{\defaultspacing}
\vspace*{\fill}   %MSU%%%vertically centered
\begin{center}
\thispagestyle{empty} 
\addtocounter{page}{-1} %MSU%%%don't count this page
Copyright by \\
{\copyrightholder} \\
{\copyrightyear} \\
\mbox{}
\end{center}
\vspace*{\fill}
}

%%%approval page definitions%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
\newlength{\sigwidth}
\setlength{\sigwidth}{2.8in}       %MSU%%%default
\newlength{\sigheight}
\setlength{\sigheight}{0.5in}      %MSU%%%default
% the following length adjusts the distance from the title to the author's name. 
\newlength{\sigtitletoauthor}
\setlength{\sigtitletoauthor}{\baselineskip} %MSU to achieve 3 blank lines
% the following length sets the distance from the author name to the word
% ``approved'', for the same purpose as \sigtitletoauthor
\newlength{\sigauthortoapproved}
\setlength{\sigauthortoapproved}{-\baselineskip} %MSU to achieve one blank line
\newcommand{\approvals}{%
\clearpage
\thispagestyle{empty} 
\newspacing{\defaultspacing}
\addtocounter{page}{-1}  %MSU%%%don't count this page
\begin{center}
\UpperBookTitle            %MSU
\par\vspace{\sigtitletoauthor}
By\\                       %MSU
\authorname                %MSU%%%p.15
\end{center}
\vspace{\sigauthortoapproved}
\par\noindent{\raggedright Approved:}
\par\newspacing{\singlespacing}
}
\newcommand{\signature}[4]{%
  \parbox[t]{\sigwidth}{%
    \rule{0in}{\sigheight}\rule{\sigwidth}{1pt}
    \centering
    \settowidth{\tmplen}{#1}
    \ifthenelse{\tmplen>0}{#1}{}  
    \settowidth{\tmplen}{#2}
    \ifthenelse{\tmplen>0}{\\#2}{}  
    \settowidth{\tmplen}{#3}
    \ifthenelse{\tmplen>0}{\\#3}{}  
    \settowidth{\tmplen}{#4}
    \ifthenelse{\tmplen>0}{\\#4}{}  
  }
}

%%%abstract page definitions%%%MSU%%%%%%%%%%%%%%%%%%%%%%%%%
%
\newcommand{\degreeday}{***degreeday missing***}
\newcommand{\majorprofessor}{***majorprofessor missing***}
\newcommand{\thesisdirector}{} %default same as major professor
\newcommand{\abstracttitle}{%
   {\booktitle}
   {\booktitletwo}
   {\booktitlethree}
}
\newcommand{\abstractpage}{%
  \clearpage
  \newspacing{\defaultspacing}
%MSU%%%top margin 1.0in No special adjustment needed
\par\noindent 
Name: \authorname \\
Date of Degree: \degreemonth\ \degreeday, \degreeyear \\
Institution: \university \\
Major Field: \major \\
Major Professor: \majorprofessor \\
\settowidth{\tmplen}{\thesisdirector}
\ifthenelse{\tmplen>0}{%
   Director of \doctype: 
   \thesisdirector \\
   }{}
\setlength{\tmplen}{\textwidth}
\addtolength{\tmplen}{-1.2in}
Title of Study: \parbox[t]{\tmplen}{%
\newspacing{\singlespacing}
\abstracttitle\\ \mbox
}\\
Pages of Study: \pageref{page:lastpage} \\
Candidate for Degree of \degree  
\par\vspace{0.5\baselineskip}   %MSU%%%to achieve two blank lines before abstract
}{
%abstract text follows abstract command
}

%%%dedication page definitions%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
\newcommand{\dedication}{  
\newspacing{\defaultspacing}
\chapter*{\dedicationname}%
%abstract was end of pages without page numbers
\setcounter{page}{2} %MSU%%%title page is page 1, other pages not counted
\pagestyle{plain}    %MSU%%%show page number at bottom of page
\addtocontents{toc}{\par\mbox{}} %MSU%%%blank line 
\addcontentsline{toc}{chapter}%
   {\MakeUppercase{\protect\dedicationname}}%
\vspace{-0.5\baselineskip}  %MSU%%%2 blank lines between title and paragraph
}

%%%acknowledgments page definitions%%%%%%%%%%%%%%%%%%%%%%%%
%
\newcommand{\acknowledgments}{%
\newspacing{\defaultspacing}
\chapter*{\acknowledgmentsname}
\pagestyle{plain}
\addtocontents{toc}{\par\mbox{}} %MSU%%%blank line 
\addcontentsline{toc}{chapter}%
   {\MakeUppercase{\protect\acknowledgmentsname}}%
\vspace{-0.5\baselineskip}  %MSU%%%2 blank lines between title and paragraph
}

%%%toc, lot, lof, los definitions%%%%%%%%%%%%%%%%%%%%%%%%%%
%
\setcounter{tocdepth}{3}  %MSU/CSE Dept default
%MSU/CS%%% spacing in toc 
\newlength{\tocspace}
\newlength{\maxchapwidth}
\newlength{\maxsectwidth}
\newlength{\maxsubsectwidth}
\newlength{\maxsubsubsectwidth}
\newlength{\maxtabnowidth}
\newlength{\maxfignowidth}
\newlength{\tocchapindent}
\newlength{\tocsectindent}
\newlength{\tocsubsectindent}
\newlength{\tocsubsubsectindent}
\newlength{\tocparaindent}
\newlength{\tocsubparaindent}
\newlength{\tocchaptitleindent}
\newlength{\tocsecttitleindent}
\newlength{\tocsubsecttitleindent}
\newlength{\tocsubsubsecttitleindent}
\newlength{\tocparatitleindent}
\newlength{\tocsubparatitleindent}
\setlength{\tocspace}{1em}
\settowidth{\maxchapwidth}{\normalfont 00.}            %default
\settowidth{\maxsectwidth}{\normalfont 00.00}             %default
\settowidth{\maxsubsectwidth}{\normalfont 00.00.00}       %default
\settowidth{\maxsubsubsectwidth}{\normalfont 00.00.00.00} %default
\settowidth{\maxtabnowidth}{00.00}                        %default
\settowidth{\maxfignowidth}{00.00}                        %default

%MSU%%%chapter numbers aligned on period: adjust lengths.
%MSU%%%sections indented
\newcommand{\settocindents}{%
%calculate chap indents
\setlength{\tocchapindent}{0em}
\setlength{\tocchaptitleindent}{\maxchapwidth}
\addtolength{\tocchaptitleindent}{\tocspace}
%calculate section indents
\setlength{\tocsectindent}{\tocchapindent}
\addtolength{\tocsectindent}{\tocchaptitleindent}
\setlength{\tocsecttitleindent}{\maxsectwidth}
\addtolength{\tocsecttitleindent}{\tocspace}
%calculate subsection indents
\setlength{\tocsubsectindent}{\tocsectindent}
\addtolength{\tocsubsectindent}{0.25in} %MSU for numbered sections which is CSE Dept style 
\setlength{\tocsubsecttitleindent}{\maxsubsectwidth}
\addtolength{\tocsubsecttitleindent}{\tocspace}
%calculate subsubsection indents
\setlength{\tocsubsubsectindent}{\tocsubsectindent}
\addtolength{\tocsubsubsectindent}{0.25in}
\setlength{\tocsubsubsecttitleindent}{\maxsubsubsectwidth}
\addtolength{\tocsubsubsecttitleindent}{\tocspace}
%calculate paragraph indents
\setlength{\tocparaindent}{\tocsubsubsectindent}
\addtolength{\tocparaindent}{0.25in}
\setlength{\tocparatitleindent}{\tocspace}
%calculate subparagraph indents
\setlength{\tocsubparaindent}{\tocparaindent}
\addtolength{\tocsubparaindent}{0.25in}
\setlength{\tocsubparatitleindent}{\tocspace}
%dottedtocline args={level}{margin to section number}{begin section number to title}
\renewcommand{\l@chapter}{\@dottedtocline{0}{\tocchapindent}{\tocchaptitleindent}}
\renewcommand*\l@section{\@dottedtocline{1}{\tocsectindent}{\tocsecttitleindent}}
\renewcommand*\l@subsection{\@dottedtocline{2}{\tocsubsectindent}{\tocsubsecttitleindent}}
\renewcommand*\l@subsubsection{\@dottedtocline{3}{\tocsubsubsectindent}{\tocsubsubsecttitleindent}}
\renewcommand*\l@paragraph{\@dottedtocline{4}{\tocparaindent}{\tocparatitleindent}}
\renewcommand*\l@subparagraph{\@dottedtocline{5}{\tocsubparaindent}{\tocsubparatitleindent}}
\renewcommand*\l@figure{\@dottedtocline{1}{\tocchapindent}{\tocsecttitleindent}}
\renewcommand*\l@table{\@dottedtocline{1}{\tocchapindent}{\tocsecttitleindent}}
}

\renewcommand\tableofcontents{%
    \@restonecolfalse
    \newspacing{\defaultspacing}
    \chapter*{\contentsname}%
    \vspace{-0.5\baselineskip}  %MSU%%%2 blank lines between title and heading
	\newspacing{\singlespacing}
	%MSU%%% toc line does not appear in table of contents
    \@starttoc{toc}%
    }
\renewcommand{\thetable}{\arabic{chapter}.\arabic{table}}
\renewcommand\listoftables{%
    \@restonecolfalse
    \newspacing{\defaultspacing}
    \chapter*{\listtablename}%
%MSU%%%10/19/12 2 blank lines between title and heading --- no \vspace needed
    \addtocontents{toc}{\par\mbox{}} %MSU%%%blank line
    \addcontentsline{toc}{chapter}%
        {\MakeUppercase{\protect\listtablename}}%
    \newspacing{\singlespacing}  %MSU for multiline captions
    \@starttoc{lot}%
}
\renewcommand{\thefigure}{\arabic{chapter}.\arabic{figure}}
\renewcommand\listoffigures{%
    \@restonecolfalse
    \newspacing{\defaultspacing}
    \chapter*{\listfigurename}%
%MSU%%%10/19/12 2 blank lines between title and heading -- no \vspace needed
    \addtocontents{toc}{\par\mbox{}} %MSU%%%blank line 
    \addcontentsline{toc}{chapter}%
        {\MakeUppercase{\protect\listfigurename}}%
    \newspacing{\singlespacing}  %MSU for multiline captions
    \@starttoc{lof}%
}
\newcommand{\listofsymbols}{  
\newspacing{\defaultspacing}
\chapter*{\listofsymbolsname}%
\addtocontents{toc}{\par\mbox{}} %MSU%%%blank line 
\addcontentsline{toc}{chapter}%
   {\MakeUppercase{\protect\listofsymbolsname}}%
\vspace{-0.5\baselineskip}  %MSU%%%2 blank lines between title and paragraph
}

%%%preface%%%
%%%not implemented%%%

%chapter/section definitions%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
\renewcommand{\thechapter}{\arabic{chapter}} %%%MSU arabic allowed.  CSE Dept preference
\renewcommand{\thesection}{\arabic{chapter}.\arabic{section}}
\renewcommand{\thesubsection}{\thesection.\arabic{subsection}}
\renewcommand{\thesubsubsection}{\thesubsection.\arabic{subsubsection}}
\setcounter{secnumdepth}{3}   %subsubsection is in toc

%MSU%%%assume option: oneside,onecolumn,openany
%MSU%%% special chapter heading format
\renewcommand\chapter{%
\clearpage
\global\@topnum\z@
\@afterindenttrue         %MSU%%% first paragraph indented
\secdef\@chapter\@schapter
}
\def\@chapter[#1]#2{%
\ifnum \c@secnumdepth >\m@ne
   \if@mainmatter
      \refstepcounter{chapter}%
      \typeout{\@chapapp\space\thechapter.}%
	  \addtocontents{toc}{\par\mbox{}} %MSU%%%blank line prior to chapter toc entry 
      \addcontentsline{toc}{chapter}%
	     %MSU%%%chapter number align on period
         {\protect\numberline{\hfill\thechapter.\hspace{\tocspace}}\MakeUppercase{\protect#1}}%
	  \addtocontents{toc}{\par\mbox{}} %MSU%%%blank line after chapter toc entry 
   \else
      \addcontentsline{toc}{chapter}{\MakeUppercase{\protect#1}}%
   \fi
\else
   \addcontentsline{toc}{chapter}{\MakeUppercase{\protect#1}}%
\fi
\chaptermark{\MakeUppercase{#1}}%
%\addtocontents{lof}{\protect\addvspace{10\p@}}% %MSU%%%double space all lof entries
%\addtocontents{lot}{\protect\addvspace{10\p@}}% %MSU%%%double space all lot entries
\@makechapterhead{#2}%
\@afterheading
%%MSU%%% 10/19/12 3 blank lines between chapter title and double spaced paragraph or 2 blank lines between chapter and section title --- no \vspace needed
}
\def\@makechapterhead#1{%   
  \vspace*{0.6in}%         %MSU
  {\parindent \z@ \centering \normalfont \normalsize %%%MSU
     \ifnum \c@secnumdepth >\m@ne
        \if@mainmatter
           \MakeUppercase{\@chapapp}\space \thechapter  
           \par\nobreak
         \fi
     \fi
     \MakeUppercase{#1} 
	 \par\nobreak
  }
  \vspace{\baselineskip} %%%MSU 
}
%MSU%%% special heading format for chapter*
\def\@makeschapterhead#1{%
  \vspace*{0.6in}%        %MSU
  {\parindent \z@ \centering \normalfont \normalsize %%%MSU
    \MakeUppercase{#1}
	\par\nobreak
  }
  \vspace{\baselineskip}  %%%MSU
}
%MSU/CS%%% font for section headings 
\renewcommand\section{%
   \@startsection {section}{1}{\z@}%
      {-5.5ex \@plus -1ex \@minus -.2ex}%   %%MSU 
%      {2.3ex \@plus .2ex}%  %%original latex for line below
      {0.3ex \@plus .2ex}%   %%%%%MSU standard spacing below section title 7/10/13 for Standard Sixth Edition "one blank line"
      {\normalfont\normalsize\bfseries\newspacing{\singlespacing}}%
}
\renewcommand\subsection{%
\@startsection{subsection}{2}{\z@}%
      {-5.5ex\@plus -1ex \@minus -.2ex}%MSU 
%      {1.5ex \@plus .2ex}%  %%%original latex
      {0.3ex \@plus .2ex}%   %%%%%MSU standard spacing below section title
      {\normalfont\normalsize\bfseries\newspacing{\singlespacing}} %%%MSU 
}
\renewcommand\subsubsection{%
\@startsection{subsubsection}{3}{\z@}%
      {-5.5ex\@plus -1ex \@minus -.2ex}%MSU 
%      {1.5ex \@plus .2ex}%  %%original latex
      {0.3ex \@plus .2ex}%   %%%%%MSU standard spacing below section title
      {\normalfont\normalsize\bfseries\newspacing{\singlespacing}} %%%MSU
}
\newcommand{\sectionnoparagraph}[1]{\section{#1}\vspace{0.5\baselineskip}}  %%%MSU
\newcommand{\subsectionnoparagraph}[1]{\subsection{#1}\vspace{0.5\baselineskip}}  %%%MSU
\newcommand{\subsubsectionnoparagraph}[1]{\subsubsection{#1}\vspace{0.5\baselineskip}}  %%%MSU


%%%MSU%the following camel-case commands are deprecated due to lines from indentfirst.sty at top 7/10/13 %%%
%MSU%%% first paragraph indented 
\newcommand{\Section}[1]{%
\section{#1}\mbox{}%
}
%MSU%%% if section has no paragraph then one blank line between section titles
\newcommand{\SectionNoParagraph}[1]{%
\section{#1}\mbox{}\vspace{-1.75\baselineskip}%
}
\newcommand{\SubSection}[1]{\subsection{#1}\mbox{}}
\newcommand{\SubSectionNoParagraph}[1]{\subsection{#1}\mbox{}\vspace{-1.75\baselineskip}}
\newcommand{\SubSubSection}[1]{\subsubsection{#1}\mbox{}}
\newcommand{\SubSubSectionNoParagraph}[1]{\subsubsection{#1}\mbox{}\vspace{-1.75\baselineskip}}
%MSU end deprecated commands %%%


%%%Definitions for compatibility with various journals%%%%%
%
\DeclareRobustCommand*{\etc}{etc.\xspace}
\DeclareRobustCommand*{\ie}{i.e.\xspace}
\DeclareRobustCommand*{\eg}{e.g.\xspace}
\DeclareRobustCommand*{\etal}{et al.\xspace}
\DeclareRobustCommand*{\vs}{{\em vs.}\xspace}


%footnote definitions%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%MSU%%%singlespace footnotes with blank line between
\renewcommand\@makefntext[1]{%
    \newspacing{\singlespacing} %MSU
    \parindent 1em%
    \noindent
    \hb@xt@1.8em{\hss\@makefnmark}#1%
}

%%%%% figure and table definitions %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%% MSU \Figurewithnotes and \Tablewithnotes is not documented in examplethesis.pdf but faq explains how to do it 7/12/13
\newcommand{\Figurewithnotes}[4]{
   \newspacing{\singlespacing}\par
   \begin{figure}
   \begin{center}
   \noindent
   \includegraphics[width=#2]{#1}  %%%MSU
   \end{center}
   \caption{#3}
   \settowidth{\tmplen}{\protect{#4}}
   \ifthenelse{\tmplen>0}{%
   \begin{quote}
     #4
   \end{quote}
   }{} %end if
   \addtocontents{lof}{\vspace{\baselineskip}} 
%MSU for multiline caption
   \label{fig:#1}
   \end{figure}
   \newspacing{\defaultspacing}
}
\newcommand{\Tablewithnotes}[3]{%
\newspacing{\singlespacing}\par
\begin{table}
\caption{#2}
\addtocontents{lot}{\vspace{\baselineskip}} 
%MSU for multiline caption 
\label{tab:#1}
\begin{center}
\input{#1}
\settowidth{\tmplen}{\protect{#3}}
\ifthenelse{\tmplen>0}{%
   \begin{quote}
   #3
   \end{quote}
}{} %end if
\end{center}
\end{table}
\par\newspacing{\defaultspacing}
}












\setlength\abovecaptionskip{\headsep}
%%%%\setlength\belowcaptionskip{0\p@} %original LaTeX value
\setlength\belowcaptionskip{0.5\baselineskip} %MSU blank line between captiontext/tableorfig
\long\def\@makecaption#1#2{%
  \vskip\abovecaptionskip
%%%%%%%  \sbox\@tempboxa{#1 #2}% %MSU obsolete Table number text on same line
  \sbox\@tempboxa{#2}% %MSU%no colon. Table/Fig number above caption text
  \ifdim \wd\@tempboxa >\hsize
    \centering{#1} \\ \mbox{} \\  %%%MSU thesis 
    %%%%%%%%%%%%double space caption number/caption text%%%%
    #2\par               %%%%MSU thesis%%%%
  \else
    \global \@minipagefalse
    \centering{#1} \\ \mbox{} \\  %%MSU%%%Table/Fig number above caption text
    %%%%%%%%%%%%double space caption number/caption text%%%%
    \hb@xt@\hsize{\hfil\box\@tempboxa\hfil}%
  \fi
  \vskip\belowcaptionskip
}
%%%figure definitions%%%%%%%%%%%%%%%%%%%%
%
\def\fps@figure{htbp} %%%%%MSU thesis%%%%%
%MSU%%%special commands to support MSU style figures
\DeclareRobustCommand*{\figureref}[1]{Figure~\ref{fig:#1}}
\DeclareRobustCommand*{\Figureref}[1]{Figure~\ref{fig:#1}} %at start of sentence
\DeclareRobustCommand*{\Figure}[3]{
   \newspacing{\singlespacing}\par
   \begin{figure}
   \begin{center}
   \noindent
   \includegraphics[width=#2]{#1}  %%%MSU
   \end{center}
   \caption{#3}
   \addtocontents{lof}{\vspace{\baselineskip}} 
%MSU multiline caption singlespaced blank line between entries
   \label{fig:#1}
   \end{figure}
   \newspacing{\defaultspacing}
}
%MSU%%%Figuredbl produces the same result in a thesis as Figure.
%   It is provided here for compatibility with two-column paper.
\DeclareRobustCommand*{\Figuredbl}[3]{
   \newspacing{\singlespacing}\par
   \begin{figure*}
   \begin{center}
   \noindent
   \includegraphics[width=#2]{#1}  %%%MSU 
   \end{center}
   \caption{#3}
   \addtocontents{lof}{\vspace{\baselineskip}} 
%MSU multiline caption singlespaced blank line between entries
   \label{fig:#1}
   \end{figure*}
   \newspacing{\defaultspacing}
}
\DeclareRobustCommand*{\rotatedfigure}[3]{
   \newspacing{\singlespacing}\par
   \begin{figure}[p]
   \rotatebox{90}{
   \begin{minipage}[t]{\figwidth}
      \begin{center}
      \noindent
      \includegraphics[width=#2]{#1}  %%%MSU
      \end{center}
      \protect\caption{#3}
      \addtocontents{lof}{\vspace{\baselineskip}} 
%MSU multiline caption singlespaced blank line between entries
      \label{fig:#1}
   \end{minipage}
   } %end rotatebox
   \end{figure}
   \newspacing{\defaultspacing}
}

%%%%% table definitions %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
\def\fps@table{htbp}  %MSU
\renewenvironment{table}{%
   \@float{table}
}{%
   \end@float
}
\renewenvironment{table*}{%
   \@dblfloat{table}
}{%
   \end@dblfloat
}
%MSU%%%the following support MSU style tables
\DeclareRobustCommand*{\tableref}[1]{Table~\ref{tab:#1}}
\DeclareRobustCommand*{\Tableref}[1]{Table~\ref{tab:#1}} %at start of sentence
\newcommand{\Table}[2]{%
\newspacing{\singlespacing}\par
\begin{table}
\caption{#2}
\addtocontents{lot}{\vspace{\baselineskip}} 
%MSU multiline caption singlespaced blank line between entries
\label{tab:#1}
\begin{center}
\input{#1}
\end{center}
\end{table}
\par\newspacing{\defaultspacing}
}
%MSU%%%Tabledbl produces the same result in a thesis as Table.
%   It is provided here for compatibility with a two-column publication.
\newcommand{\Tabledbl}[2]{%
\newspacing{\singlespacing}\par
\begin{table*}
\caption{#2}
\addtocontents{lot}{\vspace{\baselineskip}} 
%MSU multiline caption single spaced; blank line between entries
\label{tab:#1}
\begin{center}
\input{#1}
\end{center}
\end{table*}
\par\newspacing{\defaultspacing}
}
\DeclareRobustCommand*{\rotatedtable}[2]{%
   \newspacing{\singlespacing}\par
   \begin{table}[p]
   \rotatebox{90}{
      \begin{minipage}[t]{\tabwidth}
      \protect\caption{#2}
      \addtocontents{lot}{\vspace{\baselineskip}} 
%MSU multiline caption single spaced; blank line between entries
      \label{tab:#1}
      \begin{center}
      \noindent
      \input{#1}
      \end{center}
   \end{minipage}
   } %end rotatebox
   \end{table}
   \newspacing{\defaultspacing}
}
\DeclareRobustCommand*{\rotateddbltable}[2]{%
   \newspacing{\singlespacing}\par
   \begin{table*}[p]
   \rotatebox{90}{
      \begin{minipage}[t]{\tabwidth}
      \protect\caption{#2}
      \addtocontents{lot}{\vspace{\baselineskip}} 
%MSU multiline caption single spaced; blank line between entries     
      \label{tab:#1}
      \begin{center}
      \noindent
      \input{#1}
      \end{center}
   \end{minipage}
   } %end rotatebox
   \end{table*}
   \newspacing{\defaultspacing}
}
\newcommand{\Tablewithfigure}[3]{%
\newspacing{\singlespacing}\par
\begin{table}
\caption{#3}
\addtocontents{lot}{\vspace{\baselineskip}} 
%MSU multiline caption single spaced; blank line between entries
\label{tab:#1}
\begin{center}
\noindent
\includegraphics[width=#2]{#1}  %%%MSU 
\end{center}
\end{table}
\par\newspacing{\defaultspacing}
}
\newcommand{\Tabledblwithfigure}[3]{%
\newspacing{\singlespacing}\par
\begin{table*}
\caption{#3}
\addtocontents{lot}{\vspace{\baselineskip}} 
%MSU multiline caption single spaced; blank line between entries
\label{tab:#1}
\begin{center}
\noindent
\includegraphics[width=#2]{#1}  %%%MSU 
\end{center}
\end{table*}
\par\newspacing{\defaultspacing}
}
\DeclareRobustCommand*{\rotatedtablewithfigure}[3]{%
   \newspacing{\singlespacing}\par
   \begin{table}[p]
   \rotatebox{90}{
      \begin{minipage}[t]{\tabwidth}
      \protect\caption{#3}
      \addtocontents{lot}{\vspace{\baselineskip}} 
%MSU multiline caption single spaced; blank line between entries
      \label{tab:#1}
      \begin{center}
      \noindent
      \includegraphics[width=#2]{#1}  %%%MSU
      \end{center}
   \end{minipage}
   } %end rotatebox
   \end{table}
   \newspacing{\defaultspacing}
}
\newcommand{\Tablecontinued}[2]{%
\addtocounter{table}{-1}
\newspacing{\singlespacing}\par
\begin{table}
\caption{#2}
\addtocontents{lot}{\vspace{\baselineskip}} 
%MSU multiline caption single spaced; blank line between entries
\label{tab:#1}
\begin{center}
\input{#1}
\end{center}
\end{table}
\par\newspacing{\defaultspacing}
} 


%math definitions%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
\DeclareRobustCommand*{\eqnref}[1]{Equation~(\ref{eq:#1})} % for ordinary article
\DeclareRobustCommand*{\eqnsref}[1]{Equations~(\ref{eq:#1})} % for ordinary article
\DeclareRobustCommand*{\Eqnref}[1]{Equation~(\ref{eq:#1})} %at start of sentence
\DeclareRobustCommand*{\Eqnsref}[1]{Equations~(\ref{eq:#1})} %at start of sentence
\DeclareRobustCommand*{\andeqnref}[1]{and~(\ref{eq:#1})}  % for use with \eqnsref
%
%%%MSU default LaTeX fonts for theorem style is ok
\renewcommand{\theequation}{\arabic{chapter}.\arabic{equation}} %MSU%%%A is prefix.
\newcommand{\qed}{\rule{1ex}{1ex}}
%%%Macros for compatibility with Elsevier (eslart.cls)%%%
\theoremstyle{break}\newtheorem{thm}{Theorem}
\theoremstyle{break}\newtheorem{lem}{Lemma}
\theoremstyle{break}\newtheorem{cor}{Corollary}
\theoremstyle{break}\newtheorem{defn}{Definition}
\theoremstyle{plain}\newtheorem{case}{Case}
%%%environment pf required by Elsevier and Kluwer%%%
\newenvironment{pf}{%
\par\noindent{Proof:\xspace}%
}{%
\hspace*{\fill}\qed%
}  

%list environment definitions%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%%%MSU%%%%single space list environements
%(original def's are in latex.ltx)
%
\def\enumerate{%
  \ifnum \@enumdepth >\thr@@\@toodeep\else
    \par\newspacing{\singlespacing} %MSU%%%singlespacing 
    \advance\@enumdepth\@ne
    \edef\@enumctr{enum\romannumeral\the\@enumdepth}%
      \expandafter
      \list
        \csname label\@enumctr\endcsname
        {\usecounter\@enumctr\def\makelabel##1{\hss\llap{##1}}}%
  \fi
}
\def\itemize{%
  \ifnum \@itemdepth >\thr@@\@toodeep\else
    \par\newspacing{\singlespacing} %MSU%%%singlespacing 
    \advance\@itemdepth\@ne
    \edef\@itemitem{labelitem\romannumeral\the\@itemdepth}%
    \expandafter
    \list
      \csname\@itemitem\endcsname
      {\def\makelabel##1{\hss\llap{##1}}}%
  \fi
}
\renewenvironment{description}
   {\par\list{}{%
      \labelwidth\z@ \itemindent-\leftmargin
      \let\makelabel\descriptionlabel
	  \newspacing{\singlespacing} %MSU%%%%
      }
   }
   {\endlist}
\renewenvironment{verse}
               {\par\let\\\@centercr
                \list{}{%
	               \newspacing{\singlespacing} %MSU%%%%
				   \itemsep      \z@
                   \itemindent   -1.5em%
                   \listparindent\itemindent
                   \rightmargin  \leftmargin
                   \advance\leftmargin 1.5em
				}%
                \item\relax}
               {\endlist}
\renewenvironment{quotation}
               {\par\list{}{
	              \newspacing{\singlespacing} %MSU%%%
			      \listparindent 1.5em%
                  \itemindent    \listparindent
                  \rightmargin   \leftmargin
                  \parsep        \z@ \@plus\p@
				}%
                \item\relax}
               {\endlist}
\renewenvironment{quote}
               {\par\list{}{%
	              \newspacing{\singlespacing} %MSU%%%
			      \rightmargin\leftmargin
			      }%
               \item\relax}
               {\endlist}

%%% bibliography definitions %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%for compatibility with journals: 
%   Here cite is prior to punctuation; some journals require after punctuation
\DeclareRobustCommand*{\spacecite}[1]{\ \cite{#1}\xspace} % for space delimited [1]
\DeclareRobustCommand*{\commacite}[1]{ \cite{#1},} % for inline [1], style
\DeclareRobustCommand*{\periodcite}[1]{ \cite{#1}.} % for inline [1], style
%

%prevent entries split across two pages
\let\oldbibitem=\bibitem
\renewcommand{\bibitem}{%
\filbreak
\oldbibitem
}

\newcommand{\msubibliography}[1]{%
     \addtocontents{toc}{\par\mbox{}} %MSU%%%blank line
     \addcontentsline{toc}{chapter}%
        {\MakeUppercase{\protect\bibname}}%  %MSU%%% bibliography in toc
\bibliography{#1}
}
\setlength\bibindent{\parindent} %MSU
\renewenvironment{thebibliography}[1]{%
   \chapter*{\bibname \@mkboth{\MakeUppercase\bibname}{\MakeUppercase\bibname}}%
   \newspacing{\singlespacing} %MSU%%bibliography single spaced
   \list{\@biblabel{\@arabic\c@enumiv}}{%
      \settowidth\labelwidth{\@biblabel{#1}}%
      \leftmargin\labelwidth
      \advance\leftmargin\labelsep
      \@openbib@code
      \usecounter{enumiv}%
      \let\p@enumiv\@empty
      \renewcommand\theenumiv{\@arabic\c@enumiv}
   }%
   \sloppy
   \clubpenalty50000    %MSU%%% no widows and orphans (was 4000)
   \@clubpenalty \clubpenalty
   \widowpenalty50000%  %MSU%%% no widows and orphans (was 4000}
   \sfcode`\.\@m
}{%
   \def\@noitemerr
   {\@latex@warning{Empty `thebibliography' environment}}%
   \endlist  
   \newspacing{\defaultspacing} %MSU%%%bibliography single spaced
}


%end msuthesis.cls

