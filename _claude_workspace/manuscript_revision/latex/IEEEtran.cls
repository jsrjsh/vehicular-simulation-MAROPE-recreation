%%
%% IEEEtran.cls 2015/08/26 version V1.8b
%% 
%% This is the IEEEtran LaTeX class for authors of the Institute of 
%% Electrical and Electronics Engineers (IEEE) Transactions journals and
%% conferences.
%% 
%% Support sites:
%% http://www.michaelshell.org/tex/ieeetran/
%% http://www.ctan.org/pkg/ieeetran
%% and
%% http://www.ieee.org/
%%
%% Based on the original 1993 IEEEtran.cls, but with many bug fixes
%% and enhancements (from both JVH and MDS) over the 1996/7 version.
%%
%%
%% Contributors:
%% Gerry Murray (1993), Silvano Balemi (1993),
%% Jon Dixon (1996), Peter N"uchter (1996),
%% Juergen von Hagen (2000), and Michael Shell (2001-2014)
%% 
%% 
%% Copyright (c) 1993-2000 by Gerry Murray, Silvano Balemi, 
%%                         Jon Dixon, Peter N"uchter,
%%                         Juergen von Hagen
%%                         and
%% Copyright (c) 2001-2015 by Michael Shell
%%
%% Current maintainer (V1.3 to V1.8b): Michael Shell
%%                                     See:
%%                                     http://www.michaelshell.org/
%%                                     for current contact information.
%%
%% Special thanks to Peter Wilson (CUA) and Donald Arseneau
%% for allowing the inclusion of the \@ifmtarg command 
%% from their ifmtarg LaTeX package. 
%% 
%%*************************************************************************
%% Legal Notice:
%% This code is offered as-is without any warranty either expressed or
%% implied; without even the implied warranty of MERCHANTABILITY or
%% FITNESS FOR A PARTICULAR PURPOSE! 
%% User assumes all risk.
%% In no event shall the IEEE or any contributor to this code be liable for
%% any damages or losses, including, but not limited to, incidental,
%% consequential, or any other damages, resulting from the use or misuse
%% of any information contained here.
%%
%% All comments are the opinions of their respective authors and are not
%% necessarily endorsed by the IEEE.
%%
%% This work is distributed under the LaTeX Project Public License (LPPL)
%% ( http://www.latex-project.org/ ) version 1.3, and may be freely used,
%% distributed and modified. A copy of the LPPL, version 1.3, is included
%% in the base LaTeX documentation of all distributions of LaTeX released
%% 2003/12/01 or later.
%% Retain all contribution notices and credits.
%% ** Modified files should be clearly indicated as such, including  **
%% ** renaming them and changing author support contact information. **
%%
%% File list of work: IEEEtran.cls, IEEEtran_HOWTO.pdf, bare_adv.tex,
%%                    bare_conf.tex, bare_jrnl.tex, bare_conf_compsoc.tex,
%%                    bare_jrnl_compsoc.tex
%% 
%% Major changes to the user interface should be indicated by an 
%% increase in the version numbers. If a version is a beta, it will 
%% be indicated with a BETA suffix, i.e., 1.4 BETA.
%% Small changes can be indicated by appending letters to the version
%% such as "IEEEtran_v14a.cls".
%% In all cases, \Providesclass, any \typeout messages to the user,
%% \IEEEtransversionmajor and \IEEEtransversionminor must reflect the
%% correct version information.
%% The changes should also be documented via source comments.
%%*************************************************************************
%%
%
% Available class options 
% e.g., \documentclass[10pt,conference]{IEEEtran} 
% 
%             *** choose only one from each category ***
%
% 9pt, 10pt, 11pt, 12pt
%    Sets normal font size. The default is 10pt.
% 
% conference, journal, technote, peerreview, peerreviewca
%    determines format mode - conference papers, journal papers,
%    correspondence papers (technotes), or peer review papers. The user
%    should also select 9pt when using technote. peerreview is like
%    journal mode, but provides for a single-column "cover" title page for
%    anonymous peer review. The paper title (without the author names) is
%    repeated at the top of the page after the cover page. For peer review
%    papers, the \IEEEpeerreviewmaketitle command must be executed (will
%    automatically be ignored for non-peerreview modes) at the place the
%    cover page is to end, usually just after the abstract (keywords are
%    not normally used with peer review papers). peerreviewca is like
%    peerreview, but allows the author names to be entered and formatted
%    as with conference mode so that author affiliation and contact
%    information can be easily seen on the cover page.
%    The default is journal.
%
% draft, draftcls, draftclsnofoot, final
%    determines if paper is formatted as a widely spaced draft (for
%    handwritten editor comments) or as a properly typeset final version.
%    draftcls restricts draft mode to the class file while all other LaTeX
%    packages (i.e., \usepackage{graphicx}) will behave as final - allows
%    for a draft paper with visible figures, etc. draftclsnofoot is like
%    draftcls, but does not display the date and the word "DRAFT" at the foot
%    of the pages. If using one of the draft modes, the user will probably
%    also want to select onecolumn.
%    The default is final.
%
% letterpaper, a4paper, cspaper
%    determines paper size: 8.5in X 11in, 210mm X 297mm or 7.875in X 10.75in.
%    Changing the paper size in the standard journal and conference modes
%    will not alter the typesetting of the document - only the margins will
%    be affected. In particular, documents using the a4paper option will
%    have reduced side margins (A4 is narrower than US letter) and a longer
%    bottom margin (A4 is longer than US letter). For both cases, the top
%    margins will be the same and the text will be horizontally centered.
%    For the compsoc conference and draft modes, it is the margins that will
%    remain constant, and thus the text area size will vary, with changes in
%    the paper size.
%    The cspaper option is the special ``trim'' paper size (7.875in x 10.75in)
%    used in the actual publication of Computer Society journals. Under
%    compsoc journal mode, this option does not alter the typesetting of the
%    document. Authors should invoke the cspaper option only if requested to
%    do so by the editors of the specific journal they are submitting to.
%    For final submission to the IEEE, authors should generally use US letter 
%    (8.5 X 11in) paper unless otherwise instructed. Note that authors should
%    ensure that all post-processing (ps, pdf, etc.) uses the same paper
%    specificiation as the .tex document. Problems here are by far the number
%    one reason for incorrect margins. IEEEtran will automatically set the
%    default paper size under pdflatex (without requiring any change to
%    pdftex.cfg), so this issue is more important to dvips users. Fix
%    config.ps, config.pdf, or ~/.dvipsrc for dvips, or use the
%    dvips -t papersize option instead as needed. For the cspaper option,
%    the corresponding dvips paper name is "ieeecs".
%    See the testflow documentation
%    http://www.ctan.org/tex-archive/macros/latex/contrib/IEEEtran/testflow
%    for more details on dvips paper size configuration.
%    The default is letterpaper.
%
% oneside, twoside
%    determines if layout follows single sided or two sided (duplex)
%    printing. The only notable change is with the headings at the top of
%    the pages.
%    The default is oneside.
%
% onecolumn, twocolumn
%    determines if text is organized into one or two columns per page. One
%    column mode is usually used only with draft papers.
%    The default is twocolumn.
%
% comsoc, compsoc, transmag
%    Use the format of the IEEE Communications Society, IEEE Computer Society
%    or IEEE Transactions on Magnetics, respectively.
%
% romanappendices
%    Use the "Appendix I" convention when numbering appendices. IEEEtran.cls
%    now defaults to Alpha "Appendix A" convention - the opposite of what
%    v1.6b and earlier did.
%
% captionsoff
%    disables the display of the figure/table captions. Some IEEE journals
%    request that captions be removed and figures/tables be put on pages
%    of their own at the end of an initial paper submission. The endfloat
%    package can be used with this class option to achieve this format.
%
% nofonttune
%    turns off tuning of the font interword spacing. Maybe useful to those
%    not using the standard Times fonts or for those who have already "tuned"
%    their fonts.
%    The default is to enable IEEEtran to tune font parameters.
%
%
%----------
% Available CLASSINPUTs provided (all are macros unless otherwise noted):
% \CLASSINPUTbaselinestretch
% \CLASSINPUTinnersidemargin
% \CLASSINPUToutersidemargin
% \CLASSINPUTtoptextmargin
% \CLASSINPUTbottomtextmargin
%
% Available CLASSINFOs provided:
% \ifCLASSINFOpdf                       (TeX if conditional)
% \CLASSINFOpaperwidth                  (macro)
% \CLASSINFOpaperheight                 (macro)
% \CLASSINFOnormalsizebaselineskip      (length)
% \CLASSINFOnormalsizeunitybaselineskip (length)
%
% Available CLASSOPTIONs provided:
% all class option flags (TeX if conditionals) unless otherwise noted,
% e.g., \ifCLASSOPTIONcaptionsoff
% point size options provided as a single macro:
% \CLASSOPTIONpt
% which will be defined as 9, 10, 11, or 12 depending on the document's
% normalsize point size.
% also, class option peerreviewca implies the use of class option peerreview
% and classoption draft implies the use of class option draftcls





\ProvidesClass{IEEEtran}[2015/08/26 V1.8b by Michael Shell]
\typeout{-- See the "IEEEtran_HOWTO" manual for usage information.}
\typeout{-- http://www.michaelshell.org/tex/ieeetran/}
\NeedsTeXFormat{LaTeX2e}

% IEEEtran.cls version numbers, provided as of V1.3
% These values serve as a way a .tex file can
% determine if the new features are provided.
% The version number of this IEEEtrans.cls can be obtained from 
% these values. i.e., V1.4
% KEEP THESE AS INTEGERS! i.e., NO {4a} or anything like that-
% (no need to enumerate "a" minor changes here)
\def\IEEEtransversionmajor{1}
\def\IEEEtransversionminor{8}


% hook to allow easy changeover to IEEEtran.cls/tools.sty error reporting
\def\@IEEEclspkgerror{\ClassError{IEEEtran}}


% These do nothing, but provide them like in article.cls
\newif\if@restonecol
\newif\if@titlepage


% class option conditionals
\newif\ifCLASSOPTIONonecolumn       \CLASSOPTIONonecolumnfalse
\newif\ifCLASSOPTIONtwocolumn       \CLASSOPTIONtwocolumntrue

\newif\ifCLASSOPTIONoneside         \CLASSOPTIONonesidetrue
\newif\ifCLASSOPTIONtwoside         \CLASSOPTIONtwosidefalse

\newif\ifCLASSOPTIONfinal           \CLASSOPTIONfinaltrue
\newif\ifCLASSOPTIONdraft           \CLASSOPTIONdraftfalse
\newif\ifCLASSOPTIONdraftcls        \CLASSOPTIONdraftclsfalse
\newif\ifCLASSOPTIONdraftclsnofoot  \CLASSOPTIONdraftclsnofootfalse

\newif\ifCLASSOPTIONpeerreview      \CLASSOPTIONpeerreviewfalse
\newif\ifCLASSOPTIONpeerreviewca    \CLASSOPTIONpeerreviewcafalse

\newif\ifCLASSOPTIONjournal         \CLASSOPTIONjournaltrue
\newif\ifCLASSOPTIONconference      \CLASSOPTIONconferencefalse
\newif\ifCLASSOPTIONtechnote        \CLASSOPTIONtechnotefalse

\newif\ifCLASSOPTIONnofonttune      \CLASSOPTIONnofonttunefalse

\newif\ifCLASSOPTIONcaptionsoff     \CLASSOPTIONcaptionsofffalse

\newif\ifCLASSOPTIONcomsoc          \CLASSOPTIONcomsocfalse
\newif\ifCLASSOPTIONcompsoc         \CLASSOPTIONcompsocfalse
\newif\ifCLASSOPTIONtransmag        \CLASSOPTIONtransmagfalse

\newif\ifCLASSOPTIONromanappendices \CLASSOPTIONromanappendicesfalse


% class info conditionals

% indicates if pdf (via pdflatex) output
\newif\ifCLASSINFOpdf               \CLASSINFOpdffalse


% V1.6b internal flag to show if using a4paper
\newif\if@IEEEusingAfourpaper       \@IEEEusingAfourpaperfalse
% V1.6b internal flag to show if using cspaper
\newif\if@IEEEusingcspaper          \@IEEEusingcspaperfalse


% IEEEtran class scratch pad registers
% dimen
\newdimen\@IEEEtrantmpdimenA
\newdimen\@IEEEtrantmpdimenB
\newdimen\@IEEEtrantmpdimenC
% count
\newcount\@IEEEtrantmpcountA
\newcount\@IEEEtrantmpcountB
\newcount\@IEEEtrantmpcountC
% token list
\newtoks\@IEEEtrantmptoksA

% we use \CLASSOPTIONpt so that we can ID the point size (even for 9pt docs)
% as well as LaTeX's \@ptsize to retain some compatability with some
% external packages
\def\@ptsize{0}
% LaTeX does not support 9pt, so we set \@ptsize to 0 - same as that of 10pt
\DeclareOption{9pt}{\def\CLASSOPTIONpt{9}\def\@ptsize{0}}
\DeclareOption{10pt}{\def\CLASSOPTIONpt{10}\def\@ptsize{0}}
\DeclareOption{11pt}{\def\CLASSOPTIONpt{11}\def\@ptsize{1}}
\DeclareOption{12pt}{\def\CLASSOPTIONpt{12}\def\@ptsize{2}}



\DeclareOption{letterpaper}{\setlength{\paperwidth}{8.5in}%
                            \setlength{\paperheight}{11in}%
                            \@IEEEusingAfourpaperfalse
                            \@IEEEusingcspaperfalse
                            \def\CLASSOPTIONpaper{letter}%
                            \def\CLASSINFOpaperwidth{8.5in}%
                            \def\CLASSINFOpaperheight{11in}}


\DeclareOption{a4paper}{\setlength{\paperwidth}{210mm}%
                        \setlength{\paperheight}{297mm}%
                        \@IEEEusingAfourpapertrue
                        \@IEEEusingcspaperfalse
                        \def\CLASSOPTIONpaper{a4}%
                        \def\CLASSINFOpaperwidth{210mm}%
                        \def\CLASSINFOpaperheight{297mm}}

% special paper option for compsoc journals
\DeclareOption{cspaper}{\setlength{\paperwidth}{7.875in}%
                        \setlength{\paperheight}{10.75in}%
                        \@IEEEusingcspapertrue
                        \@IEEEusingAfourpaperfalse
                        \def\CLASSOPTIONpaper{ieeecs}%
                        \def\CLASSINFOpaperwidth{7.875in}%
                        \def\CLASSINFOpaperheight{10.75in}}

\DeclareOption{oneside}{\@twosidefalse\@mparswitchfalse
                        \CLASSOPTIONonesidetrue\CLASSOPTIONtwosidefalse}
\DeclareOption{twoside}{\@twosidetrue\@mparswitchtrue
                        \CLASSOPTIONtwosidetrue\CLASSOPTIONonesidefalse}

\DeclareOption{onecolumn}{\CLASSOPTIONonecolumntrue\CLASSOPTIONtwocolumnfalse}
\DeclareOption{twocolumn}{\CLASSOPTIONtwocolumntrue\CLASSOPTIONonecolumnfalse}

% If the user selects draft, then this class AND any packages
% will go into draft mode.
\DeclareOption{draft}{\CLASSOPTIONdrafttrue\CLASSOPTIONdraftclstrue
                      \CLASSOPTIONdraftclsnofootfalse} 
% draftcls is for a draft mode which will not affect any packages
% used by the document.
\DeclareOption{draftcls}{\CLASSOPTIONdraftfalse\CLASSOPTIONdraftclstrue
                         \CLASSOPTIONdraftclsnofootfalse} 
% draftclsnofoot is like draftcls, but without the footer.
\DeclareOption{draftclsnofoot}{\CLASSOPTIONdraftfalse\CLASSOPTIONdraftclstrue
                               \CLASSOPTIONdraftclsnofoottrue} 
\DeclareOption{final}{\CLASSOPTIONdraftfalse\CLASSOPTIONdraftclsfalse
                      \CLASSOPTIONdraftclsnofootfalse}

\DeclareOption{journal}{\CLASSOPTIONpeerreviewfalse\CLASSOPTIONpeerreviewcafalse
                        \CLASSOPTIONjournaltrue\CLASSOPTIONconferencefalse\CLASSOPTIONtechnotefalse}

\DeclareOption{conference}{\CLASSOPTIONpeerreviewfalse\CLASSOPTIONpeerreviewcafalse
                           \CLASSOPTIONjournalfalse\CLASSOPTIONconferencetrue\CLASSOPTIONtechnotefalse}

\DeclareOption{technote}{\CLASSOPTIONpeerreviewfalse\CLASSOPTIONpeerreviewcafalse
                         \CLASSOPTIONjournalfalse\CLASSOPTIONconferencefalse\CLASSOPTIONtechnotetrue}

\DeclareOption{peerreview}{\CLASSOPTIONpeerreviewtrue\CLASSOPTIONpeerreviewcafalse
                           \CLASSOPTIONjournalfalse\CLASSOPTIONconferencefalse\CLASSOPTIONtechnotefalse}

\DeclareOption{peerreviewca}{\CLASSOPTIONpeerreviewtrue\CLASSOPTIONpeerreviewcatrue
                             \CLASSOPTIONjournalfalse\CLASSOPTIONconferencefalse\CLASSOPTIONtechnotefalse}

\DeclareOption{nofonttune}{\CLASSOPTIONnofonttunetrue}

\DeclareOption{captionsoff}{\CLASSOPTIONcaptionsofftrue}

\DeclareOption{comsoc}{\CLASSOPTIONcomsoctrue\CLASSOPTIONcompsocfalse\CLASSOPTIONtransmagfalse}

\DeclareOption{compsoc}{\CLASSOPTIONcomsocfalse\CLASSOPTIONcompsoctrue\CLASSOPTIONtransmagfalse}

\DeclareOption{transmag}{\CLASSOPTIONtransmagtrue\CLASSOPTIONcomsocfalse\CLASSOPTIONcompsocfalse}

\DeclareOption{romanappendices}{\CLASSOPTIONromanappendicestrue}


% default to US letter paper, 10pt, twocolumn, one sided, final, journal
\ExecuteOptions{letterpaper,10pt,twocolumn,oneside,final,journal}
% overrride these defaults per user requests
\ProcessOptions



%% -- Command Argument Scanning Support Functions --

% Sets the category codes for punctuation to their normal values.
% For local use with argument scanning.
\def\IEEEnormalcatcodespunct{\catcode`\!=12 \catcode`\,=12 \catcode`\:=12
\catcode`\;=12 \catcode`\`=12 \catcode`\'=12 \catcode`\"=12 \catcode`\.=12
\catcode`\/=12 \catcode`\?=12 \catcode`\*=12 \catcode`\+=12 \catcode`\-=12
\catcode`\<=12 \catcode`\>=12 \catcode`\(=12 \catcode`\)=12 \catcode`\[=12
\catcode`\]=12 \catcode`\==12 \catcode`\|=12}
% Sets the category codes for numbers to their normal values.
% For local use with argument scanning.
\def\IEEEnormalcatcodesnum{\catcode`\0=12 \catcode`\1=12 \catcode`\2=12
\catcode`\3=12 \catcode`\4=12 \catcode`\5=12 \catcode`\6=12 \catcode`\7=12
\catcode`\8=12 \catcode`\9=12}
% combined action of \IEEEnormalcatcodespunct and \IEEEnormalcatcodesnum
\def\IEEEnormalcatcodes{\IEEEnormalcatcodespunct\IEEEnormalcatcodesnum}


% usage: \@IEEEextracttoken*{}
% \@IEEEextracttoken fully expands its argument (which it then stores in
% \@IEEEextracttokenarg) via \edef and then the meaning of the first
% nonbrace (but including the empty group) token found is assigned via \let
% to \@IEEEextractedtoken as well as stored in the macro
% \@IEEEextractedtokenmacro. Tokens that would otherwise be discarded during
% the acquisition of the first are stored in \@IEEEextractedtokensdiscarded,
% however their original relative brace nesting depths are not guaranteed to
% be preserved.
% If the argument is empty, or if a first nonbrace token does not exist (or
% is an empty group), \@IEEEextractedtoken will be \relax and
% \@IEEEextractedtokenmacro and \@IEEEextractedtokensdiscarded will be empty.
%
% For example:
% \@IEEEextracttoken{{{ab}{cd}}{{ef}g}}
% results in:
%
% \@IEEEextracttokenarg          ==> a macro containing {{ab}{cd}}{{ef}g}
% \@IEEEextractedtoken           ==> the letter a
% \@IEEEextractedtokenmacro      ==> a macro containing a
% \@IEEEextractedtokensdiscarded ==> a macro containing bcd{ef}g
%
% the *-star form, \@IEEEextracttoken*, does not expand its argument
% contents during processing.
\def\@IEEEextracttoken{\@ifstar{\let\@IEEEextracttokendef=\def\@@IEEEextracttoken}{\let\@IEEEextracttokendef=\edef\@@IEEEextracttoken}}

\def\@@IEEEextracttoken#1{\@IEEEextracttokendef\@IEEEextracttokenarg{#1}\relax
\def\@IEEEextractedtokensdiscarded{}\relax % initialize to empty
% if the macro is unchanged after being acquired as a single undelimited argument
% with anything after it being stripped off as a delimited argument
% we know we have one token without any enclosing braces. loop until this is true.
\let\@IEEEextracttokencurgroup\@IEEEextracttokenarg
\loop
  % trap case of an empty argument as this would cause a problem with
  % \@@@IEEEextracttoken's first (nondelimited) argument acquisition
  \ifx\@IEEEextracttokencurgroup\@empty
    \def\@IEEEextractedtokenmacro{}\relax
  \else
    \expandafter\@@@IEEEextracttoken\@IEEEextracttokencurgroup\@IEEEgeneralsequenceDELIMITER\relax
  \fi
  \ifx\@IEEEextractedtokenmacro\@IEEEextracttokencurgroup
  \else
    \let\@IEEEextracttokencurgroup=\@IEEEextractedtokenmacro
\repeat
% we can safely do a \let= here because there should be at most one token
% the relax is needed to handle the case of no token found
\expandafter\let\expandafter\@IEEEextractedtoken\@IEEEextractedtokenmacro\relax}

\def\@@@IEEEextracttoken#1#2\@IEEEgeneralsequenceDELIMITER{\def\@IEEEextractedtokenmacro{#1}\relax
\def\@@IEEEextractedtokensdiscarded{#2}\expandafter\expandafter\expandafter\def\expandafter\expandafter\expandafter
\@IEEEextractedtokensdiscarded\expandafter\expandafter\expandafter
{\expandafter\@@IEEEextractedtokensdiscarded\@IEEEextractedtokensdiscarded}}
%%
%% -- End of Command Argument Scanning Support Functions --



% Computer Society conditional execution command
\long\def\@IEEEcompsoconly#1{\relax\ifCLASSOPTIONcompsoc\relax#1\relax\fi\relax}
% inverse
\long\def\@IEEEnotcompsoconly#1{\relax\ifCLASSOPTIONcompsoc\else\relax#1\relax\fi\relax}
% compsoc conference
\long\def\@IEEEcompsocconfonly#1{\relax\ifCLASSOPTIONcompsoc\ifCLASSOPTIONconference\relax#1\relax\fi\fi\relax}
% compsoc not conference
\long\def\@IEEEcompsocnotconfonly#1{\relax\ifCLASSOPTIONcompsoc\ifCLASSOPTIONconference\else\relax#1\relax\fi\fi\relax}


% comsoc verify that newtxmath, mtpro2, mt11p or mathtime has been loaded
\def\@IEEEcomsocverifymathfont{\typeout{-- Verifying Times compatible math font.}\relax
  \@ifpackageloaded{newtxmath}{\typeout{-- newtxmath loaded, OK.}}{\@@IEEEcomsocverifymathfont}}
\def\@@IEEEcomsocverifymathfont{\@ifpackageloaded{mtpro2}{\typeout{-- mtpro2 loaded, OK.}}{\@@@IEEEcomsocverifymathfont}}
\def\@@@IEEEcomsocverifymathfont{\@ifpackageloaded{mt11p}{\typeout{-- mt11p2 loaded, OK.}}{\@@@@IEEEcomsocverifymathfont}}
\def\@@@@IEEEcomsocverifymathfont{\@ifpackageloaded{mathtime}{\typeout{-- mathtime loaded, OK.}}{\@IEEEcomsocenforcemathfont}}

% comsoc, if a Times math font was not loaded by user, enforce it
\def\@IEEEcomsocenforcemathfont{\typeout{** Times compatible math font not found, forcing.}\relax
\IfFileExists{newtxmath.sty}{\typeout{-- Found newtxmath, loading.}\RequirePackage{newtxmath}}{\@@IEEEcomsocenforcemathfont}}
\def\@@IEEEcomsocenforcemathfont{\IfFileExists{mtpro2.sty}{\typeout{-- Found mtpro2, loading.}\RequirePackage{mtpro2}}{\@@@IEEEcomsocenforcemathfont}}
\def\@@@IEEEcomsocenforcemathfont{\IfFileExists{mt11p.sty}{\typeout{-- Found mt11p, loading.}\RequirePackage{mt11p}}{\@@@@IEEEcomsocenforcemathfont}}
\def\@@@@IEEEcomsocenforcemathfont{\IfFileExists{mathtime.sty}{\typeout{-- Found mathtime, loading.}\RequirePackage{mathtime}}{\@@@@@IEEEcomsocenforcemathfont}}
% if no acceptable Times math font package found, error with newtxmath requirement
\def\@@@@@IEEEcomsocenforcemathfont{\typeout{** No Times compatible math font package found. newtxmath is required.}\RequirePackage{newtxmath}}


\ifCLASSOPTIONcomsoc
  % ensure that if newtxmath is used, the cmintegrals option is also invoked
  \PassOptionsToPackage{cmintegrals}{newtxmath}
  % comsoc requires a Times like math font
  % ensure this requirement is satisfied at document start
  \AtBeginDocument{\@IEEEcomsocverifymathfont}
\fi



% The IEEE uses Times Roman font, so we'll default to Times.
% These three commands make up the entire times.sty package.
\renewcommand{\sfdefault}{phv}
\renewcommand{\rmdefault}{ptm}
\renewcommand{\ttdefault}{pcr}

% V1.7 compsoc nonconference papers, use Palatino/Palladio as the main text font,
% not Times Roman.
\@IEEEcompsocnotconfonly{\renewcommand{\rmdefault}{ppl}}

% enable the selected main text font
\normalfont\selectfont


\ifCLASSOPTIONcomsoc
  \typeout{-- Using IEEE Communications Society mode.}
\fi

\ifCLASSOPTIONcompsoc
  \typeout{-- Using IEEE Computer Society mode.}
\fi


% V1.7 conference notice message hook
\def\@IEEEconsolenoticeconference{\typeout{}%
\typeout{** Conference Paper **}%
\typeout{Before submitting the final camera ready copy, remember to:}%
\typeout{}%
\typeout{ 1. Manually equalize the lengths of two columns on the last page}%
\typeout{ of your paper;}%
\typeout{}%
\typeout{ 2. Ensure that any PostScript and/or PDF output post-processing}%
\typeout{ uses only Type 1 fonts and that every step in the generation}%
\typeout{ process uses the appropriate paper size.}%
\typeout{}}


% we can send console reminder messages to the user here
\AtEndDocument{\ifCLASSOPTIONconference\@IEEEconsolenoticeconference\fi}


% warn about the use of single column other than for draft mode
\ifCLASSOPTIONtwocolumn\else%
  \ifCLASSOPTIONdraftcls\else%
   \typeout{** ATTENTION: Single column mode is not typically used with IEEE publications.}%
  \fi%
\fi


% V1.7 improved paper size setting code.
% Set pdfpage and dvips paper sizes. Conditional tests are similar to that
% of ifpdf.sty. Retain within {} to ensure tested macros are never altered,
% even if only effect is to set them to \relax.
% if \pdfoutput is undefined or equal to relax, output a dvips special
{\@ifundefined{pdfoutput}{\AtBeginDvi{\special{papersize=\CLASSINFOpaperwidth,\CLASSINFOpaperheight}}}{%
% pdfoutput is defined and not equal to \relax
% check for pdfpageheight existence just in case someone sets pdfoutput
% under non-pdflatex. If exists, set them regardless of value of \pdfoutput.
\@ifundefined{pdfpageheight}{\relax}{\global\pdfpagewidth\paperwidth
\global\pdfpageheight\paperheight}%
% if using \pdfoutput=0 under pdflatex, send dvips papersize special
\ifcase\pdfoutput
\AtBeginDvi{\special{papersize=\CLASSINFOpaperwidth,\CLASSINFOpaperheight}}%
\else
% we are using pdf output, set CLASSINFOpdf flag
\global\CLASSINFOpdftrue
\fi}}

% let the user know the selected papersize
\typeout{-- Using \CLASSINFOpaperwidth\space x \CLASSINFOpaperheight\space
(\CLASSOPTIONpaper)\space paper.}

\ifCLASSINFOpdf
\typeout{-- Using PDF output.}
\else
\typeout{-- Using DVI output.}
\fi


% The idea hinted here is for LaTeX to generate markleft{} and markright{}
% automatically for you after you enter \author{}, \journal{},
% \journaldate{}, journalvol{}, \journalnum{}, etc.
% However, there may be some backward compatibility issues here as
% well as some special applications for IEEEtran.cls and special issues
% that may require the flexible \markleft{}, \markright{} and/or \markboth{}.
% We'll leave this as an open future suggestion.
%\newcommand{\journal}[1]{\def\@journal{#1}}
%\def\@journal{}



% pointsize values
% used with ifx to determine the document's normal size
\def\@IEEEptsizenine{9}
\def\@IEEEptsizeten{10}
\def\@IEEEptsizeeleven{11}
\def\@IEEEptsizetwelve{12}



% FONT DEFINITIONS (No sizexx.clo file needed) 
% V1.6 revised font sizes, displayskip values and
%      revised normalsize baselineskip to reduce underfull vbox problems
%      on the 58pc = 696pt = 9.5in text height we want
%      normalsize     #lines/column  baselineskip (aka leading)
%             9pt     63             11.0476pt (truncated down)
%            10pt     58             12pt      (exact)
%            11pt     52             13.3846pt (truncated down)
%            12pt     50             13.92pt   (exact)
%

% we need to store the nominal baselineskip for the given font size
% in case baselinestretch ever changes.
% this is a dimen, so it will not hold stretch or shrink
\newdimen\@IEEEnormalsizeunitybaselineskip
\@IEEEnormalsizeunitybaselineskip\baselineskip



%% ******* WARNING! *******
%%
%% Authors should not alter font sizes, baselineskip ("leading"),
%% margins or other spacing values in an attempt to squeeze more
%% material on each page.
%%
%% The IEEE's own typesetting software will restore the correct
%% values when re-typesetting/proofing the submitted document,
%% possibly resulting in unexpected article over length charges.
%%
%% ******* WARNING! *******


% 9pt option defaults
\ifx\CLASSOPTIONpt\@IEEEptsizenine
\typeout{-- This is a 9 point document.}
\def\normalsize{\@setfontsize{\normalsize}{9}{11.0476pt}}
\setlength{\@IEEEnormalsizeunitybaselineskip}{11.0476pt}
\normalsize
\abovedisplayskip 1.5ex plus 3pt minus 1pt
\belowdisplayskip \abovedisplayskip
\abovedisplayshortskip 0pt plus 3pt
\belowdisplayshortskip 1.5ex plus 3pt minus 1pt
\def\small{\@setfontsize{\small}{8.5}{10pt}}
\def\footnotesize{\@setfontsize{\footnotesize}{8}{9pt}}
\def\scriptsize{\@setfontsize{\scriptsize}{7}{8pt}}
\def\tiny{\@setfontsize{\tiny}{5}{6pt}}
% sublargesize is the same as large - 10pt
\def\sublargesize{\@setfontsize{\sublargesize}{10}{12pt}}
\def\large{\@setfontsize{\large}{10}{12pt}}
\def\Large{\@setfontsize{\Large}{12}{14pt}}
\def\LARGE{\@setfontsize{\LARGE}{14}{17pt}}
\def\huge{\@setfontsize{\huge}{17}{20pt}}
\def\Huge{\@setfontsize{\Huge}{20}{24pt}}
\fi
%
% 10pt option defaults
\ifx\CLASSOPTIONpt\@IEEEptsizeten
\typeout{-- This is a 10 point document.}
\def\normalsize{\@setfontsize{\normalsize}{10}{12.00pt}}
\setlength{\@IEEEnormalsizeunitybaselineskip}{12pt}
\normalsize
\abovedisplayskip 1.5ex plus 4pt minus 2pt
\belowdisplayskip \abovedisplayskip
\abovedisplayshortskip 0pt plus 4pt
\belowdisplayshortskip 1.5ex plus 4pt minus 2pt
\def\small{\@setfontsize{\small}{9}{10pt}}
\def\footnotesize{\@setfontsize{\footnotesize}{8}{9pt}}
\def\scriptsize{\@setfontsize{\scriptsize}{7}{8pt}}
\def\tiny{\@setfontsize{\tiny}{5}{6pt}}
% sublargesize is a tad smaller than large - 11pt
\def\sublargesize{\@setfontsize{\sublargesize}{11}{13.4pt}}
\def\large{\@setfontsize{\large}{12}{14pt}}
\def\Large{\@setfontsize{\Large}{14}{17pt}}
\def\LARGE{\@setfontsize{\LARGE}{17}{20pt}}
\def\huge{\@setfontsize{\huge}{20}{24pt}}
\def\Huge{\@setfontsize{\Huge}{24}{28pt}}
\fi
%
% 11pt option defaults
\ifx\CLASSOPTIONpt\@IEEEptsizeeleven
\typeout{-- This is an 11 point document.}
\def\normalsize{\@setfontsize{\normalsize}{11}{13.3846pt}}
\setlength{\@IEEEnormalsizeunitybaselineskip}{13.3846pt}
\normalsize
\abovedisplayskip 1.5ex plus 5pt minus 3pt
\belowdisplayskip \abovedisplayskip
\abovedisplayshortskip 0pt plus 5pt
\belowdisplayshortskip 1.5ex plus 5pt minus 3pt
\def\small{\@setfontsize{\small}{10}{12pt}}
\def\footnotesize{\@setfontsize{\footnotesize}{9}{10.5pt}}
\def\scriptsize{\@setfontsize{\scriptsize}{8}{9pt}}
\def\tiny{\@setfontsize{\tiny}{6}{7pt}}
% sublargesize is the same as large - 12pt
\def\sublargesize{\@setfontsize{\sublargesize}{12}{14pt}}
\def\large{\@setfontsize{\large}{12}{14pt}}
\def\Large{\@setfontsize{\Large}{14}{17pt}}
\def\LARGE{\@setfontsize{\LARGE}{17}{20pt}}
\def\huge{\@setfontsize{\huge}{20}{24pt}}
\def\Huge{\@setfontsize{\Huge}{24}{28pt}}
\fi
%
% 12pt option defaults
\ifx\CLASSOPTIONpt\@IEEEptsizetwelve
\typeout{-- This is a 12 point document.}
\def\normalsize{\@setfontsize{\normalsize}{12}{13.92pt}}
\setlength{\@IEEEnormalsizeunitybaselineskip}{13.92pt}
\normalsize
\abovedisplayskip 1.5ex plus 6pt minus 4pt
\belowdisplayskip \abovedisplayskip
\abovedisplayshortskip 0pt plus 6pt
\belowdisplayshortskip 1.5ex plus 6pt minus 4pt
\def\small{\@setfontsize{\small}{10}{12pt}}
\def\footnotesize{\@setfontsize{\footnotesize}{9}{10.5pt}}
\def\scriptsize{\@setfontsize{\scriptsize}{8}{9pt}}
\def\tiny{\@setfontsize{\tiny}{6}{7pt}}
% sublargesize is the same as large - 14pt
\def\sublargesize{\@setfontsize{\sublargesize}{14}{17pt}}
\def\large{\@setfontsize{\large}{14}{17pt}}
\def\Large{\@setfontsize{\Large}{17}{20pt}}
\def\LARGE{\@setfontsize{\LARGE}{20}{24pt}}
\def\huge{\@setfontsize{\huge}{22}{26pt}}
\def\Huge{\@setfontsize{\Huge}{24}{28pt}}
\fi



% V1.8a compsoc font sizes
% compsoc font sizes use bp "Postscript" point units (1/72in) 
% rather than the traditional pt (1/72.27)
\ifCLASSOPTIONcompsoc
% -- compsoc defaults --
% ** will override some of these values later **
% 9pt
\ifx\CLASSOPTIONpt\@IEEEptsizenine
\def\normalsize{\@setfontsize{\normalsize}{9bp}{11bp}}
\setlength{\@IEEEnormalsizeunitybaselineskip}{11bp}
\normalsize
\abovedisplayskip 1.5ex plus 3bp minus 1bp
\belowdisplayskip \abovedisplayskip
\abovedisplayshortskip 0bp plus 3bp
\belowdisplayshortskip 1.5ex plus 3bp minus 1bp
\def\small{\@setfontsize{\small}{8.5bp}{10bp}}
\def\footnotesize{\@setfontsize{\footnotesize}{8bp}{9bp}}
\def\scriptsize{\@setfontsize{\scriptsize}{7bp}{8bp}}
\def\tiny{\@setfontsize{\tiny}{5bp}{6bp}}
% sublargesize is the same as large - 10bp
\def\sublargesize{\@setfontsize{\sublargesize}{10bp}{12bp}}
\def\large{\@setfontsize{\large}{10bp}{12bp}}
\def\Large{\@setfontsize{\Large}{12bp}{14bp}}
\def\LARGE{\@setfontsize{\LARGE}{14bp}{17bp}}
\def\huge{\@setfontsize{\huge}{17bp}{20bp}}
\def\Huge{\@setfontsize{\Huge}{20bp}{24bp}}
\fi
%
% 10pt
\ifx\CLASSOPTIONpt\@IEEEptsizeten
\def\normalsize{\@setfontsize{\normalsize}{10bp}{12bp}}
\setlength{\@IEEEnormalsizeunitybaselineskip}{12bp}
\normalsize
\abovedisplayskip 1.5ex plus 4bp minus 2bp
\belowdisplayskip \abovedisplayskip
\abovedisplayshortskip 0pt plus 4bp
\belowdisplayshortskip 1.5ex plus 4bp minus 2bp
\def\small{\@setfontsize{\small}{9bp}{10bp}}
\def\footnotesize{\@setfontsize{\footnotesize}{8bp}{9bp}}
\def\scriptsize{\@setfontsize{\scriptsize}{7bp}{8bp}}
\def\tiny{\@setfontsize{\tiny}{5bp}{6bp}}
% sublargesize is a tad smaller than large - 11bp
\def\sublargesize{\@setfontsize{\sublargesize}{11bp}{13.5bp}}
\def\large{\@setfontsize{\large}{12bp}{14bp}}
\def\Large{\@setfontsize{\Large}{14bp}{17bp}}
\def\LARGE{\@setfontsize{\LARGE}{17bp}{20bp}}
\def\huge{\@setfontsize{\huge}{20bp}{24bp}}
\def\Huge{\@setfontsize{\Huge}{24bp}{28bp}}
\fi
%
% 11pt
\ifx\CLASSOPTIONpt\@IEEEptsizeeleven
\def\normalsize{\@setfontsize{\normalsize}{11bp}{13.5bp}}
\setlength{\@IEEEnormalsizeunitybaselineskip}{13.5bp}
\normalsize
\abovedisplayskip 1.5ex plus 5bp minus 3bp
\belowdisplayskip \abovedisplayskip
\abovedisplayshortskip 0pt plus 5bp
\belowdisplayshortskip 1.5ex plus 5bp minus 3bp
\def\small{\@setfontsize{\small}{10bp}{12bp}}
\def\footnotesize{\@setfontsize{\footnotesize}{9bp}{10.5bp}}
\def\scriptsize{\@setfontsize{\scriptsize}{8bp}{9bp}}
\def\tiny{\@setfontsize{\tiny}{6bp}{7bp}}
% sublargesize is the same as large - 12bp
\def\sublargesize{\@setfontsize{\sublargesize}{12bp}{14bp}}
\def\large{\@setfontsize{\large}{12bp}{14bp}}
\def\Large{\@setfontsize{\Large}{14bp}{17bp}}
\def\LARGE{\@setfontsize{\LARGE}{17bp}{20bp}}
\def\huge{\@setfontsize{\huge}{20bp}{24bp}}
\def\Huge{\@setfontsize{\Huge}{24bp}{28bp}}
\fi
%
% 12pt
\ifx\CLASSOPTIONpt\@IEEEptsizetwelve
\def\normalsize{\@setfontsize{\normalsize}{12bp}{14bp}}%
\setlength{\@IEEEnormalsizeunitybaselineskip}{14bp}%
\normalsize
\abovedisplayskip 1.5ex plus 6bp minus 4bp
\belowdisplayskip \abovedisplayskip
\abovedisplayshortskip 0pt plus 6bp
\belowdisplayshortskip 1.5ex plus 6bp minus 4bp
\def\small{\@setfontsize{\small}{10bp}{12bp}}
\def\footnotesize{\@setfontsize{\footnotesize}{9bp}{10.5bp}}
\def\scriptsize{\@setfontsize{\scriptsize}{8bp}{9bp}}
\def\tiny{\@setfontsize{\tiny}{6bp}{7bp}}
% sublargesize is the same as large - 14bp
\def\sublargesize{\@setfontsize{\sublargesize}{14bp}{17bp}}
\def\large{\@setfontsize{\large}{14bp}{17bp}}
\def\Large{\@setfontsize{\Large}{17bp}{20bp}}
\def\LARGE{\@setfontsize{\LARGE}{20bp}{24bp}}
\def\huge{\@setfontsize{\huge}{22bp}{26bp}}
\def\Huge{\@setfontsize{\Huge}{24bp}{28bp}}
\fi
%
% -- override defaults: compsoc journals use special normalsizes --
\ifCLASSOPTIONconference
% 
% compsoc conferences
% 9pt
\ifx\CLASSOPTIONpt\@IEEEptsizenine
\def\normalsize{\@setfontsize{\normalsize}{9bp}{10.8bp}}
\setlength{\@IEEEnormalsizeunitybaselineskip}{10.8bp}
\normalsize
\abovedisplayskip 1.5ex plus 3bp minus 1bp
\belowdisplayskip \abovedisplayskip
\abovedisplayshortskip 0bp plus 3bp
\belowdisplayshortskip 1.5ex plus 3bp minus 1bp
\fi
% 10pt
\ifx\CLASSOPTIONpt\@IEEEptsizeten
\def\normalsize{\@setfontsize{\normalsize}{10bp}{11.2bp}}
\setlength{\@IEEEnormalsizeunitybaselineskip}{11.2bp}
\normalsize
\abovedisplayskip 1.5ex plus 4bp minus 2bp
\belowdisplayskip \abovedisplayskip
\abovedisplayshortskip 0pt plus 4bp
\belowdisplayshortskip 1.5ex plus 4bp minus 2bp
\fi
% 11pt
\ifx\CLASSOPTIONpt\@IEEEptsizeeleven
\def\normalsize{\@setfontsize{\normalsize}{11bp}{13.2bp}}
\setlength{\@IEEEnormalsizeunitybaselineskip}{13.2bp}
\normalsize
\abovedisplayskip 1.5ex plus 5bp minus 3bp
\belowdisplayskip \abovedisplayskip
\abovedisplayshortskip 0pt plus 5bp
\belowdisplayshortskip 1.5ex plus 5bp minus 3bp
\fi
% 12pt
\ifx\CLASSOPTIONpt\@IEEEptsizetwelve
\def\normalsize{\@setfontsize{\normalsize}{12bp}{14.4bp}}
\setlength{\@IEEEnormalsizeunitybaselineskip}{14.4bp}
\normalsize
\abovedisplayskip 1.5ex plus 6bp minus 4bp
\belowdisplayskip \abovedisplayskip
\abovedisplayshortskip 0pt plus 6bp
\belowdisplayshortskip 1.5ex plus 6bp minus 4bp
\fi
% 
% compsoc nonconferences
\else
% 9pt
\ifx\CLASSOPTIONpt\@IEEEptsizenine
\def\normalsize{\@setfontsize{\normalsize}{9bp}{10.8bp}}
\setlength{\@IEEEnormalsizeunitybaselineskip}{10.8bp}
\normalsize
\abovedisplayskip 1.5ex plus 3bp minus 1bp
\belowdisplayskip \abovedisplayskip
\abovedisplayshortskip 0bp plus 3bp
\belowdisplayshortskip 1.5ex plus 3bp minus 1bp
\fi
% 10pt
\ifx\CLASSOPTIONpt\@IEEEptsizeten
% the official spec is 9.5bp with 11.4bp leading for 10pt,
% but measurements of proofs suggest upto 11.723bp leading
% here we'll use 11.54bp which gives 61 lines per column
% with the standard compsoc margins
\def\normalsize{\@setfontsize{\normalsize}{9.5bp}{11.54bp}}
\setlength{\@IEEEnormalsizeunitybaselineskip}{11.54bp}
\normalsize
\abovedisplayskip 1.5ex plus 4bp minus 2bp
\belowdisplayskip \abovedisplayskip
\abovedisplayshortskip 0pt plus 4bp
\belowdisplayshortskip 1.5ex plus 4bp minus 2bp
\fi
% 11pt
\ifx\CLASSOPTIONpt\@IEEEptsizeeleven
\def\normalsize{\@setfontsize{\normalsize}{11bp}{13.2bp}}
\setlength{\@IEEEnormalsizeunitybaselineskip}{13.2bp}
\normalsize
\abovedisplayskip 1.5ex plus 5bp minus 3bp
\belowdisplayskip \abovedisplayskip
\abovedisplayshortskip 0pt plus 5bp
\belowdisplayshortskip 1.5ex plus 5bp minus 3bp
\fi
% 12pt
\ifx\CLASSOPTIONpt\@IEEEptsizetwelve
\def\normalsize{\@setfontsize{\normalsize}{12bp}{14.4bp}}
\setlength{\@IEEEnormalsizeunitybaselineskip}{14.4bp}
\normalsize
\abovedisplayskip 1.5ex plus 6bp minus 4bp
\belowdisplayskip \abovedisplayskip
\abovedisplayshortskip 0pt plus 6bp
\belowdisplayshortskip 1.5ex plus 6bp minus 4bp
\fi
\fi\fi




% V1.6 The Computer Modern Fonts will issue a substitution warning for
% 24pt titles (24.88pt is used instead, but the default and correct
% Times font will scale exactly as needed) increase the substitution
% tolerance to turn off this warning.
% 
% V1.8a, the compsoc bp font sizes can also cause bogus font substitution
% warnings with footnote or scriptsize math and the $\bullet$ itemized
% list of \IEEEcompsocitemizethanks. So, increase this to 1.5pt or more.
\def\fontsubfuzz{1.7bp}


% warn the user in case they forget to use the 9pt option with
% technote
\ifCLASSOPTIONtechnote%
 \ifx\CLASSOPTIONpt\@IEEEptsizenine\else%
  \typeout{** ATTENTION: Technotes are normally 9pt documents.}%
 \fi%
\fi


% V1.7
% Improved \textunderscore to provide a much better fake _ when used with
% OT1 encoding. Under OT1, detect use of pcr or cmtt \ttfamily and use
% available true _ glyph for those two typewriter fonts.
\def\@IEEEstringptm{ptm} % Times Roman family
\def\@IEEEstringppl{ppl} % Palatino Roman family
\def\@IEEEstringphv{phv} % Helvetica Sans Serif family
\def\@IEEEstringpcr{pcr} % Courier typewriter family
\def\@IEEEstringcmtt{cmtt} % Computer Modern typewriter family
\DeclareTextCommandDefault{\textunderscore}{\leavevmode
\ifx\f@family\@IEEEstringpcr\string_\else
\ifx\f@family\@IEEEstringcmtt\string_\else
\ifx\f@family\@IEEEstringptm\kern 0em\vbox{\hrule\@width 0.5em\@height 0.5pt\kern -0.3ex}\else
\ifx\f@family\@IEEEstringppl\kern 0em\vbox{\hrule\@width 0.5em\@height 0.5pt\kern -0.3ex}\else
\ifx\f@family\@IEEEstringphv\kern -0.03em\vbox{\hrule\@width 0.62em\@height 0.52pt\kern -0.33ex}\kern -0.03em\else
\kern 0.09em\vbox{\hrule\@width 0.6em\@height 0.44pt\kern -0.63pt\kern -0.42ex}\kern 0.09em\fi\fi\fi\fi\fi\relax}




% set the default \baselinestretch
\def\baselinestretch{1}
\ifCLASSOPTIONdraftcls
  \def\baselinestretch{1.5}% default baselinestretch for draft modes
\fi 


% process CLASSINPUT baselinestretch
\ifx\CLASSINPUTbaselinestretch\@IEEEundefined
\else
  \edef\baselinestretch{\CLASSINPUTbaselinestretch} % user CLASSINPUT override
  \typeout{** ATTENTION: Overriding \string\baselinestretch\space to
           \baselinestretch\space via \string\CLASSINPUT.}
\fi

\small\normalsize % make \baselinestretch take affect




% store the normalsize baselineskip
\newdimen\CLASSINFOnormalsizebaselineskip
\CLASSINFOnormalsizebaselineskip=\baselineskip\relax
% and the normalsize unity (baselinestretch=1) baselineskip
% we could save a register by giving the user access to
% \@IEEEnormalsizeunitybaselineskip. However, let's protect
% its read only internal status
\newdimen\CLASSINFOnormalsizeunitybaselineskip
\CLASSINFOnormalsizeunitybaselineskip=\@IEEEnormalsizeunitybaselineskip\relax
% store the nominal value of jot
\newdimen\IEEEnormaljot
\IEEEnormaljot=0.25\baselineskip\relax

% set \jot
\jot=\IEEEnormaljot\relax




% V1.6, we are now going to fine tune the interword spacing
% The default interword glue for Times under TeX appears to use a
% nominal interword spacing of 25% (relative to the font size, i.e., 1em)
% a maximum of 40% and a minimum of 19%.
% For example, 10pt text uses an interword glue of:
% 
% 2.5pt plus 1.49998pt minus 0.59998pt
% 
% However, the IEEE allows for a more generous range which reduces the need
% for hyphenation, especially for two column text. Furthermore, the IEEE
% tends to use a little bit more nominal space between the words.
% The IEEE's interword spacing percentages appear to be:
% 35% nominal
% 23% minimum
% 50% maximum
% (They may even be using a tad more for the largest fonts such as 24pt.)
% 
% for bold text, the IEEE increases the spacing a little more:
% 37.5% nominal
% 23% minimum
% 55% maximum

% here are the interword spacing ratios we'll use
% for medium (normal weight)
\def\@IEEEinterspaceratioM{0.35}
\def\@IEEEinterspaceMINratioM{0.23}
\def\@IEEEinterspaceMAXratioM{0.50}

% for bold
\def\@IEEEinterspaceratioB{0.375}
\def\@IEEEinterspaceMINratioB{0.23}
\def\@IEEEinterspaceMAXratioB{0.55}


% compsoc nonconference papers use Palatino,
% tweak settings to better match the proofs
\ifCLASSOPTIONcompsoc
\ifCLASSOPTIONconference\else
% for medium (normal weight)
\def\@IEEEinterspaceratioM{0.28}
\def\@IEEEinterspaceMINratioM{0.21}
\def\@IEEEinterspaceMAXratioM{0.47}
% for bold
\def\@IEEEinterspaceratioB{0.305}
\def\@IEEEinterspaceMINratioB{0.21}
\def\@IEEEinterspaceMAXratioB{0.52}
\fi\fi


% command to revise the interword spacing for the current font under TeX:
% \fontdimen2 = nominal interword space
% \fontdimen3 = interword stretch
% \fontdimen4 = interword shrink
% since all changes to the \fontdimen are global, we can enclose these commands
% in braces to confine any font attribute or length changes
\def\@@@IEEEsetfontdimens#1#2#3{{%
\setlength{\@IEEEtrantmpdimenB}{\f@size pt}% grab the font size in pt, could use 1em instead.
\setlength{\@IEEEtrantmpdimenA}{#1\@IEEEtrantmpdimenB}%
\fontdimen2\font=\@IEEEtrantmpdimenA\relax
\addtolength{\@IEEEtrantmpdimenA}{-#2\@IEEEtrantmpdimenB}%
\fontdimen3\font=-\@IEEEtrantmpdimenA\relax
\setlength{\@IEEEtrantmpdimenA}{#1\@IEEEtrantmpdimenB}%
\addtolength{\@IEEEtrantmpdimenA}{-#3\@IEEEtrantmpdimenB}%
\fontdimen4\font=\@IEEEtrantmpdimenA\relax}}

% revise the interword spacing for each font weight
\def\@@IEEEsetfontdimens{{%
\mdseries
\@@@IEEEsetfontdimens{\@IEEEinterspaceratioM}{\@IEEEinterspaceMAXratioM}{\@IEEEinterspaceMINratioM}%
\bfseries
\@@@IEEEsetfontdimens{\@IEEEinterspaceratioB}{\@IEEEinterspaceMAXratioB}{\@IEEEinterspaceMINratioB}%
}}

% revise the interword spacing for each font shape
% \slshape is not often used for IEEE work and is not altered here. The \scshape caps are
% already a tad too large in the free LaTeX fonts (as compared to what the IEEE uses) so we
% won't alter these either.
\def\@IEEEsetfontdimens{{%
\normalfont
\@@IEEEsetfontdimens
\normalfont\itshape
\@@IEEEsetfontdimens
}}

% command to revise the interword spacing for each font size (and shape
% and weight). Only the \rmfamily is done here as \ttfamily uses a 
% fixed spacing and \sffamily is not used as the main text of IEEE papers.
\def\@IEEEtunefonts{{\selectfont\rmfamily
\tiny\@IEEEsetfontdimens
\scriptsize\@IEEEsetfontdimens
\footnotesize\@IEEEsetfontdimens
\small\@IEEEsetfontdimens
\normalsize\@IEEEsetfontdimens
\sublargesize\@IEEEsetfontdimens
\large\@IEEEsetfontdimens
\LARGE\@IEEEsetfontdimens
\huge\@IEEEsetfontdimens
\Huge\@IEEEsetfontdimens}}

% if the nofonttune class option is not given, revise the interword spacing
% now - in case IEEEtran makes any default length measurements, and make
% sure all the default fonts are loaded
\ifCLASSOPTIONnofonttune\else
\@IEEEtunefonts
\fi

% and again at the start of the document in case the user loaded different fonts
\AtBeginDocument{\ifCLASSOPTIONnofonttune\else\@IEEEtunefonts\fi}





% -- V1.8a page setup commands --

% The default sample text for calculating margins
% Note that IEEE publications use \scriptsize for headers and footers.
\def\IEEEdefaultsampletext{\normalfont\normalsize gT}
\def\IEEEdefaultheadersampletext{\normalfont\scriptsize T}% IEEE headers default to uppercase
\def\IEEEdefaultfootersampletext{\normalfont\scriptsize gT}



% usage: \IEEEsettextwidth{inner margin}{outer margin}
% Sets \textwidth to allow the specified inner and outer margins
% for the current \paperwidth.
\def\IEEEsettextwidth#1#2{\@IEEEtrantmpdimenA\paperwidth
\@IEEEtrantmpdimenB#1\relax
\advance\@IEEEtrantmpdimenA by -\@IEEEtrantmpdimenB
\@IEEEtrantmpdimenB#2\relax
\advance\@IEEEtrantmpdimenA by -\@IEEEtrantmpdimenB
\textwidth\@IEEEtrantmpdimenA}



% usage: \IEEEsetsidemargin{mode: i, o, c, a}{margin/offset}
% Sets \oddsidemargin and \evensidemargin to yield the specified margin
% of the given mode.
% The available modes are:
% i = inner margin
% o = outer margin
% c = centered, with the given offset
% a = adjust the margins using the given offset
% For the offsets, positive values increase the inner margin.
% \textwidth should be set properly for the given margins before calling this
% function.
\def\IEEEsetsidemargin#1#2{\@IEEEtrantmpdimenA #2\relax
\@IEEEextracttoken{#1}\relax
% check for mode errors
\ifx\@IEEEextractedtokenmacro\@empty
  \@IEEEclspkgerror{Empty mode type in \string\IEEEsetsidemargin\space (line \the\inputlineno).\MessageBreak
  Defaulting to `i'}{Valid modes for \string\IEEEsetsidemargin\space are: i, o, c and a.}\relax
  \let\@IEEEextractedtoken=i\relax
  \def\@IEEEextractedtokenmacro{i}\relax
\else
  \ifx\@IEEEextractedtokensdiscarded\@empty\else
    \typeout{** WARNING: \string\IEEEsetsidemargin\space mode specifiers after the first in `\@IEEEextracttokenarg' ignored (line \the\inputlineno).}\relax
  \fi
\fi
% handle each mode
\if\@IEEEextractedtoken a\relax
  \advance\oddsidemargin by \@IEEEtrantmpdimenA\relax
\else
\if\@IEEEextractedtoken c\relax
  \oddsidemargin\paperwidth
  \advance\oddsidemargin by -\textwidth
  \divide\oddsidemargin by 2\relax
  \advance\oddsidemargin by -1in\relax
  \advance\oddsidemargin by \@IEEEtrantmpdimenA\relax
\else
\if\@IEEEextractedtoken o\relax
  \oddsidemargin\paperwidth
  \advance\oddsidemargin by -\textwidth
  \advance\oddsidemargin by -\@IEEEtrantmpdimenA
  \advance\oddsidemargin by -1in\relax
\else
  \if\@IEEEextractedtoken i\relax
  \else
    \@IEEEclspkgerror{Unknown mode type `\@IEEEextractedtokenmacro' in \string\IEEEsetsidemargin\space (line \the\inputlineno).\MessageBreak
    Defaulting to `i'}%
    {Valid modes for \string\IEEEsetsidemargin\space are: i, o, c  and a.}%
  \fi
  \oddsidemargin\@IEEEtrantmpdimenA
  \advance\oddsidemargin by -1in\relax
\fi\fi\fi
% odd and even side margins both mean "inner" for single sided pages
\evensidemargin\oddsidemargin
% but are mirrors of each other when twosided is in effect
\if@twoside
  \evensidemargin\paperwidth
  \advance\evensidemargin by -\textwidth
  \advance\evensidemargin by -\oddsidemargin
  % have to compensate for both the builtin 1in LaTex offset
  % and the fact we already subtracted this offset from \oddsidemargin
  \advance\evensidemargin -2in\relax
\fi}



% usage: \IEEEsettextheight[sample text]{top text margin}{bottom text margin}
% Sets \textheight based on the specified top margin and bottom margin.
% Takes into consideration \paperheight, \topskip, and (by default) the
% the actual height and depth of the \IEEEdefaultsampletext text. 
\def\IEEEsettextheight{\@ifnextchar [{\@IEEEsettextheight}{\@IEEEsettextheight[\IEEEdefaultsampletext]}}
\def\@IEEEsettextheight[#1]#2#3{\textheight\paperheight\relax
  \@IEEEtrantmpdimenA #2\relax
  \advance \textheight by -\@IEEEtrantmpdimenA% subtract top margin
  \@IEEEtrantmpdimenA #3\relax
  \advance \textheight by -\@IEEEtrantmpdimenA% subtract bottom margin
  \advance \textheight by \topskip% add \topskip
  % subtract off everything above the top, and below the bottom, baselines
  \settoheight{\@IEEEtrantmpdimenA}{\begingroup #1\relax\relax\relax\endgroup}\relax
  \advance \textheight by -\@IEEEtrantmpdimenA
  \settodepth{\@IEEEtrantmpdimenA}{\begingroup #1\relax\relax\relax\endgroup}\relax
  \advance \textheight by -\@IEEEtrantmpdimenA}



\newdimen\IEEEquantizedlength
\IEEEquantizedlength 0sp\relax
\newdimen\IEEEquantizedlengthdiff
\IEEEquantizedlengthdiff 0sp\relax
\def\IEEEquantizedlengthint{0}

% usage: \IEEEquantizelength{mode: d, c, i}{base unit}{length}
% Sets the length \IEEEquantizedlength to be an integer multiple of the given
% (nonzero) base unit such that \IEEEquantizedlength approximates the given
% length.
% \IEEEquantizedlengthdiff is a length equal to the difference between the
% \IEEEquantizedlength and the given length.
% \IEEEquantizedlengthint is a macro containing the integer number of base units
% in \IEEEquantizedlength.
% i.e., \IEEEquantizedlength =  \IEEEquantizedlengthint * base unit
% The mode determines how \IEEEquantizedlength is quantized:
% d = always decrease (always round down \IEEEquantizeint)
% c = use the closest match
% i = always increase (always round up \IEEEquantizeint)
% In anycase, if the given length is already quantized,
% \IEEEquantizedlengthdiff will be set to zero.
\def\IEEEquantizelength#1#2#3{\begingroup
% work in isolation so as not to externally disturb the \@IEEEtrantmp
% variables
% load the argument values indirectly via \IEEEquantizedlengthdiff
% in case the user refers to our \@IEEEtrantmpdimenX, \IEEEquantizedlength,
% etc. in the arguments. we also will work with these as counters,
% i.e., in sp units
% A has the base unit
\IEEEquantizedlengthdiff #2\relax\relax\relax\relax
\@IEEEtrantmpcountA\IEEEquantizedlengthdiff
% B has the input length
\IEEEquantizedlengthdiff #3\relax\relax\relax\relax
\@IEEEtrantmpcountB\IEEEquantizedlengthdiff
\@IEEEtrantmpdimenA\the\@IEEEtrantmpcountA sp\relax
\@IEEEtrantmpdimenB\the\@IEEEtrantmpcountB sp\relax
% \@IEEEtrantmpcountC will have the quantized int
% \IEEEquantizedlength will have the quantized length
% \@IEEEtrantmpdimenC will have the quantized diff
% initialize them to zero as this is what will be
% exported if an error occurs
\@IEEEtrantmpcountC 0\relax
\IEEEquantizedlength 0sp\relax
\@IEEEtrantmpdimenC 0sp\relax
% extract mode
\@IEEEextracttoken{#1}\relax
% check for mode errors
\ifx\@IEEEextractedtokenmacro\@empty
  \@IEEEclspkgerror{Empty mode type in \string\IEEEquantizelength\space (line \the\inputlineno).\MessageBreak
  Defaulting to `d'}{Valid modes for \string\IEEEquantizelength\space are: d, c and i.}\relax
  \let\@IEEEextractedtoken=d\relax
  \def\@IEEEextractedtokenmacro{d}\relax
\else
  \ifx\@IEEEextractedtokensdiscarded\@empty\else
    \typeout{** WARNING: \string\IEEEquantizelength\space mode specifiers after the first in `\@IEEEextracttokenarg' ignored (line \the\inputlineno).}\relax
  \fi
\fi
% check for base unit is zero error
\ifnum\@IEEEtrantmpcountA=0\relax
\@IEEEclspkgerror{Base unit is zero in \string\IEEEquantizelength\space (line \the\inputlineno).\MessageBreak
  \string\IEEEquantizedlength\space and \string\IEEEquantizedlengthdiff\space are set to zero}{Division by zero is not allowed.}\relax
\else% base unit is nonzero
  % \@IEEEtrantmpcountC carries the number of integer units
  % in the quantized length (integer length \ base)
  \@IEEEtrantmpcountC\@IEEEtrantmpcountB\relax
  \divide\@IEEEtrantmpcountC by \@IEEEtrantmpcountA\relax
  % \IEEEquantizedlength has the (rounded down) quantized length
  % = base * int
  \IEEEquantizedlength\@IEEEtrantmpdimenA\relax
  \multiply\IEEEquantizedlength by \@IEEEtrantmpcountC\relax
  % \@IEEEtrantmpdimenC has the difference
  % = quantized length - length
  \@IEEEtrantmpdimenC\IEEEquantizedlength\relax
  \advance\@IEEEtrantmpdimenC by -\@IEEEtrantmpdimenB\relax
  % trap special case of length being already quantized
  % to avoid a roundup under i option
  \ifdim\@IEEEtrantmpdimenC=0sp\relax
  \else % length not is already quantized
    % set dimenA to carry the upper quantized (absolute value) difference:
    % quantizedlength + base - length
    \advance\@IEEEtrantmpdimenA by \IEEEquantizedlength\relax
    \advance\@IEEEtrantmpdimenA by -\@IEEEtrantmpdimenB\relax
    % set dimenB to carry the lower quantized (absolute value) difference:
    % length - quantizedlength
    \advance\@IEEEtrantmpdimenB by -\IEEEquantizedlength\relax
    % handle each mode
    \if\@IEEEextractedtoken c\relax
      % compare upper and lower amounts, select upper if lower > upper
      \ifdim\@IEEEtrantmpdimenB>\@IEEEtrantmpdimenA\relax
        % use upper
        \advance\IEEEquantizedlength by \the\@IEEEtrantmpcountA sp\relax
        \advance\@IEEEtrantmpcountC by 1\relax
        \@IEEEtrantmpdimenC\@IEEEtrantmpdimenA
      \else% <=. uselower
        % no need to do anything for lower, use output values already setup
      \fi
    \else% not mode c
    \if\@IEEEextractedtoken i\relax
      % always round up under i mode
      \advance\IEEEquantizedlength by \the\@IEEEtrantmpcountA sp\relax
      \advance\@IEEEtrantmpcountC by 1\relax
      \@IEEEtrantmpdimenC\@IEEEtrantmpdimenA
    \else
      \if\@IEEEextractedtoken d\relax
      \else
        \@IEEEclspkgerror{Unknown mode type `\@IEEEextractedtokenmacro' in \string\IEEEquantizelength\space (line \the\inputlineno).\MessageBreak
        Defaulting to `d'}%
        {Valid modes for \string\IEEEquantizelength\space are: d, c, and i.}\relax
      \fi % if d
      % no need to do anything for d, use output values already setup
    \fi\fi % if i, c
  \fi % if length is already quantized
\fi% if base unit is zero
% globally assign the results to macros we use here to escape the enclosing
% group without needing to call \global on any of the \@IEEEtrantmp variables.
% \@IEEEtrantmpcountC has the quantized int
% \IEEEquantizedlength has the quantized length
% \@IEEEtrantmpdimenC has the quantized diff
\xdef\@IEEEquantizedlengthintmacro{\the\@IEEEtrantmpcountC}\relax
\@IEEEtrantmpcountC\IEEEquantizedlength\relax
\xdef\@IEEEquantizedlengthmacro{\the\@IEEEtrantmpcountC}\relax
\@IEEEtrantmpcountC\@IEEEtrantmpdimenC\relax
\xdef\@IEEEquantizedlengthdiffmacro{\the\@IEEEtrantmpcountC}\relax
\endgroup
% locally assign the outputs here from the macros
\expandafter\IEEEquantizedlength\@IEEEquantizedlengthmacro sp\relax
\expandafter\IEEEquantizedlengthdiff\@IEEEquantizedlengthdiffmacro sp\relax
\edef\IEEEquantizedlengthint{\@IEEEquantizedlengthintmacro}\relax}



\newdimen\IEEEquantizedtextheightdiff
\IEEEquantizedtextheightdiff 0sp\relax

% usage: \IEEEquantizetextheight[base unit]{mode: d, c, i}
% Sets \textheight to be an integer multiple of the current \baselineskip
% (or the optionally specified base unit) plus the first (\topskip) line.
% \IEEEquantizedtextheightdiff is a length equal to the difference between
% the new quantized and original \textheight.
% \IEEEquantizedtextheightlpc is a macro containing the integer number of
% lines per column under the quantized \textheight. i.e.,
% \textheight = \IEEEquantizedtextheightlpc * \baselineskip + \topskip
% The mode determines how \textheight is quantized:
% d = always decrease (always round down the number of lines per column)
% c = use the closest match
% i = always increase (always round up the number of lines per column)
% In anycase, if \textheight is already quantized, it will remain unchanged,
% and \IEEEquantizedtextheightdiff will be set to zero.
% Depends on: \IEEEquantizelength
\def\IEEEquantizetextheight{\@ifnextchar [{\@IEEEquantizetextheight}{\@IEEEquantizetextheight[\baselineskip]}}
\def\@IEEEquantizetextheight[#1]#2{\begingroup
% use our \IEEEquantizedtextheightdiff as a scratch pad
% we need to subtract off \topskip before quantization
\IEEEquantizedtextheightdiff\textheight
\advance\IEEEquantizedtextheightdiff by -\topskip\relax
\IEEEquantizelength{#2}{#1}{\IEEEquantizedtextheightdiff}
% add back \topskip line
\advance\IEEEquantizedlength by \topskip
\@IEEEtrantmpcountC\IEEEquantizedlengthint\relax
\advance\@IEEEtrantmpcountC by 1\relax
% globally assign the results to macros we use here to escape the enclosing
% group without needing to call \global on any of the \@IEEEtrantmp variables.
\xdef\@IEEEquantizedtextheightlpcmacro{\the\@IEEEtrantmpcountC}\relax
\@IEEEtrantmpcountC\IEEEquantizedlength\relax
\xdef\@IEEEquantizedtextheightmacro{\the\@IEEEtrantmpcountC}\relax
\@IEEEtrantmpcountC\IEEEquantizedlengthdiff\relax
\xdef\@IEEEquantizedtextheightdiffmacro{\the\@IEEEtrantmpcountC}\relax
\endgroup
% locally assign the outputs here from the macros
\textheight\@IEEEquantizedtextheightmacro sp\relax
\IEEEquantizedtextheightdiff\@IEEEquantizedtextheightdiffmacro sp\relax
\edef\IEEEquantizedtextheightlpc{\@IEEEquantizedtextheightlpcmacro}}



% usage: \IEEEsettopmargin[sample text]{mode: t, b, c, a, q}{margin/offset}
% Sets \topmargin based on the specified vertical margin.
% Takes into consideration the base 1in offset, \headheight, \headsep,
% \topskip, and (by default) the the actual height (or, for the bottom, depth)
% of the \IEEEdefaultsampletext text.
% The available modes are:
% t = top margin
% b = bottom margin
% c = vertically centered, with the given offset
% a = adjust the vertical margins using the given offset
% q = adjust the margins using \IEEEquantizedtextheightdiff and the given offset
% For the offsets, positive values increase the top margin.
% \headheight, \headsep, \topskip and \textheight should be set properly for the
% given margins before calling this function.
\def\IEEEsettopmargin{\@ifnextchar [{\@IEEEsettopmargin}{\@IEEEsettopmargin[\IEEEdefaultsampletext]}}
\def\@IEEEsettopmargin[#1]#2#3{\@IEEEtrantmpdimenA #3\relax
\@IEEEextracttoken{#2}\relax
% check for mode errors
\ifx\@IEEEextractedtokenmacro\@empty
  \@IEEEclspkgerror{Empty mode type in \string\IEEEsettopmargin\space (line \the\inputlineno).\MessageBreak
  Defaulting to `t'}{Valid modes for \string\IEEEsettopmargin\space are: t, b, c, a and q.}\relax
  \let\@IEEEextractedtoken=t\relax
  \def\@IEEEextractedtokenmacro{t}\relax
\else
  \ifx\@IEEEextractedtokensdiscarded\@empty\else
    \typeout{** WARNING: \string\IEEEsettopmargin\space mode specifiers after the first in `\@IEEEextracttokenarg' ignored (line \the\inputlineno).}\relax
  \fi
\fi
% handle each mode
\if\@IEEEextractedtoken a\relax
  \advance\topmargin by \@IEEEtrantmpdimenA\relax
\else
\if\@IEEEextractedtoken q\relax
  % we need to adjust by half the \IEEEquantizedtextheightdiff value
  \@IEEEtrantmpdimenB\IEEEquantizedtextheightdiff\relax
  \divide\@IEEEtrantmpdimenB by 2\relax
  % a positive \IEEEquantizedtextheightdiff means we need to reduce \topmargin
  % because \textheight has been lenghtened
  \advance\topmargin by -\@IEEEtrantmpdimenB\relax
  \advance\topmargin by \@IEEEtrantmpdimenA\relax
\else
\if\@IEEEextractedtoken c\relax
  \topmargin\paperheight
  \advance\topmargin by -\textheight
  % \textheight includes \topskip, but we should not count topskip whitespace here, backout
  \advance \topmargin by \topskip
  \settoheight{\@IEEEtrantmpdimenB}{\begingroup #1\relax\relax\relax\endgroup}\relax
  \advance\topmargin by -\@IEEEtrantmpdimenB\relax
  \settodepth{\@IEEEtrantmpdimenB}{\begingroup #1\relax\relax\relax\endgroup}\relax
  \advance\topmargin by -\@IEEEtrantmpdimenB\relax
  \divide\topmargin by 2\relax
  \advance\topmargin by \@IEEEtrantmpdimenA\relax
\else
\if\@IEEEextractedtoken b\relax
  \topmargin\paperheight
  \advance\topmargin by -\textheight
  % \textheight includes \topskip, but we should not count topskip whitespace here, backout
  \advance \topmargin by \topskip
  \settodepth{\@IEEEtrantmpdimenB}{\begingroup #1\relax\relax\relax\endgroup}\relax
  \advance\topmargin by -\@IEEEtrantmpdimenB\relax
  \advance\topmargin by -\@IEEEtrantmpdimenA\relax
\else
  \if\@IEEEextractedtoken t\relax
  \else
    \@IEEEclspkgerror{Unknown mode type `\@IEEEextractedtokenmacro' in \string\IEEEsettopmargin\space (line \the\inputlineno).\MessageBreak
    Defaulting to `t'}%
    {Valid modes for \string\IEEEsettopmargin\space are: t, b, c, a and q.}\relax
  \fi
  \topmargin\@IEEEtrantmpdimenA\relax
  \settoheight{\@IEEEtrantmpdimenB}{\begingroup #1\relax\relax\relax\endgroup}\relax
  \advance\topmargin by \@IEEEtrantmpdimenB\relax
\fi\fi % if t, b, c
% convert desired top margin into actual \topmargin
% this is not done for the q or a modes because they are only adjustments
\advance \topmargin by -\topskip
\advance \topmargin by -1in
\advance \topmargin by -\headheight
\advance \topmargin by -\headsep
\fi\fi % if q, a
}



% usage: \IEEEsetheadermargin[header sample][text sample]{mode: t, b, c, a}{margin/offset}
% Differentially adjusts \topmargin and \headsep (such that their sum is unchanged)
% based on the specified header margin.
% Takes into consideration the base 1in offset, \headheight, \topskip, and (by default)
% the actual height (or depth) of the \IEEEdefaultheadersampletext and
% \IEEEdefaultsampletext text.
% The available modes are:
% t = top margin (top of the header text to the top of the page)
% b = bottom margin (bottom of the header text to the top of the main text)
% c = vertically centered between the main text and the top of the page,
%     with the given offset
% a = adjust the vertical position using the given offset
% For the offsets, positive values move the header downward.
% \headheight, \headsep, \topskip and \topmargin should be set properly before
% calling this function.
\def\IEEEsetheadermargin{\@ifnextchar [{\@IEEEsetheadermargin}{\@IEEEsetheadermargin[\IEEEdefaultheadersampletext]}}
\def\@IEEEsetheadermargin[#1]{\@ifnextchar [{\@@IEEEsetheadermargin[#1]}{\@@IEEEsetheadermargin[#1][\IEEEdefaultsampletext]}}
\def\@@IEEEsetheadermargin[#1][#2]#3#4{\@IEEEtrantmpdimenA #4\relax
\@IEEEextracttoken{#3}\relax
% check for mode errors
\ifx\@IEEEextractedtokenmacro\@empty
  \@IEEEclspkgerror{Empty mode type in \string\IEEEsetheadermargin\space (line \the\inputlineno).\MessageBreak
  Defaulting to `t'}{Valid modes for \string\IEEEsetheadermargin\space are: t, b, c, and a.}\relax
  \let\@IEEEextractedtoken=t\relax
  \def\@IEEEextractedtokenmacro{t}\relax
\else
  \ifx\@IEEEextractedtokensdiscarded\@empty\else
    \typeout{** WARNING: \string\IEEEsetheadermargin\space mode specifiers after the first in `\@IEEEextracttokenarg' ignored (line \the\inputlineno).}\relax
  \fi
\fi
% handle each mode
\if\@IEEEextractedtoken a\relax
  % No need to do anything here and can pass through the adjustment
  % value as is. The end adjustment of \topmargin and \headsep will
  % do all that is needed
\else
\if\@IEEEextractedtoken c\relax
  % get the bottom margin
  \@IEEEtrantmpdimenB\headsep\relax
  \settodepth{\@IEEEtrantmpdimenC}{\begingroup #1\relax\relax\relax\endgroup}\relax
  \advance\@IEEEtrantmpdimenB by -\@IEEEtrantmpdimenC
  \advance\@IEEEtrantmpdimenB by \topskip
  \settoheight{\@IEEEtrantmpdimenC}{\begingroup #2\relax\relax\relax\endgroup}\relax
  \advance\@IEEEtrantmpdimenB by -\@IEEEtrantmpdimenC
  % at this point \@IEEEtrantmpdimenB has the actual header bottom margin
  % subtract from it the top header margin
  \advance\@IEEEtrantmpdimenB -1in\relax % take into consideration the system 1in offset of the top margin
  \advance\@IEEEtrantmpdimenB by -\topmargin
  \advance\@IEEEtrantmpdimenB by -\headheight
  \settoheight{\@IEEEtrantmpdimenC}{\begingroup #1\relax\relax\relax\endgroup}\relax
  \advance\@IEEEtrantmpdimenB by \@IEEEtrantmpdimenC
  % at this point \@IEEEtrantmpdimenB has the difference between the bottom and top margins
  % we need to adjust by half this amount to center the header
  \divide\@IEEEtrantmpdimenB by 2\relax
  % and add to offset
  \advance\@IEEEtrantmpdimenA by \@IEEEtrantmpdimenB
\else
\if\@IEEEextractedtoken b\relax
  \@IEEEtrantmpdimenB\headsep\relax
  \settodepth{\@IEEEtrantmpdimenC}{\begingroup #1\relax\relax\relax\endgroup}\relax
  \advance\@IEEEtrantmpdimenB by -\@IEEEtrantmpdimenC
  \advance\@IEEEtrantmpdimenB by \topskip
  \settoheight{\@IEEEtrantmpdimenC}{\begingroup #2\relax\relax\relax\endgroup}\relax
  \advance\@IEEEtrantmpdimenB by -\@IEEEtrantmpdimenC
  % at this point \@IEEEtrantmpdimenB has the actual header bottom margin
  % get the difference between the actual and the desired
  \advance\@IEEEtrantmpdimenB by -\@IEEEtrantmpdimenA
  \@IEEEtrantmpdimenA\@IEEEtrantmpdimenB
\else
  \if\@IEEEextractedtoken t\relax
  \else
    \@IEEEclspkgerror{Unknown mode type `\@IEEEextractedtokenmacro' in \string\IEEEsetheadermargin\space (line \the\inputlineno).\MessageBreak
    Defaulting to `t'}%
    {Valid modes for \string\IEEEsetheadermargin\space are: t, b, c and a.}\relax
  \fi
  \@IEEEtrantmpdimenB 1in\relax % take into consideration the system 1in offset of the top margin
  \advance\@IEEEtrantmpdimenB by \topmargin
  \advance\@IEEEtrantmpdimenB by \headheight
  \settoheight{\@IEEEtrantmpdimenC}{\begingroup #1\relax\relax\relax\endgroup}\relax
  \advance\@IEEEtrantmpdimenB by -\@IEEEtrantmpdimenC
  % at this point \@IEEEtrantmpdimenB has the actual header top margin
  % get the difference between the desired and the actual
  \advance\@IEEEtrantmpdimenA by -\@IEEEtrantmpdimenB
\fi\fi % if t, b, c
\fi % if a
% advance \topmargin by the needed amount and reduce \headsep by the same
% so as not to disturb the location of the main text
\advance\topmargin by \@IEEEtrantmpdimenA\relax
\advance\headsep by -\@IEEEtrantmpdimenA\relax
}



% usage: \IEEEsetfootermargin[footer sample][text sample]{mode: t, b, c, a}{margin/offset}
% Adjusts \footskip based on the specified footer margin.
% Takes into consideration the base 1in offset, \paperheight, \headheight,
% \headsep, \textheight and (by default) the actual height (or depth) of the
% \IEEEdefaultfootersampletext and \IEEEdefaultsampletext text.
% The available modes are:
% t = top margin (top of the footer text to the bottom of the main text)
% b = bottom margin (bottom of the footer text to the bottom of page)
% c = vertically centered between the main text and the bottom of the page,
%     with the given offset
% a = adjust the vertical position using the given offset
% For the offsets, positive values move the footer downward.
% \headheight, \headsep, \topskip, \topmargin, and \textheight should be set
% properly before calling this function.
\def\IEEEsetfootermargin{\@ifnextchar [{\@IEEEsetfootermargin}{\@IEEEsetfootermargin[\IEEEdefaultfootersampletext]}}
\def\@IEEEsetfootermargin[#1]{\@ifnextchar [{\@@IEEEsetfootermargin[#1]}{\@@IEEEsetfootermargin[#1][\IEEEdefaultsampletext]}}
\def\@@IEEEsetfootermargin[#1][#2]#3#4{\@IEEEtrantmpdimenA #4\relax
\@IEEEextracttoken{#3}\relax
% check for mode errors
\ifx\@IEEEextractedtokenmacro\@empty
  \@IEEEclspkgerror{Empty mode type in \string\IEEEsetfootermargin\space (line \the\inputlineno).\MessageBreak
  Defaulting to `t'}{Valid modes for \string\IEEEsetfootermargin\space are: t, b, c, and a.}\relax
  \let\@IEEEextractedtoken=t\relax
  \def\@IEEEextractedtokenmacro{t}\relax
\else
  \ifx\@IEEEextractedtokensdiscarded\@empty\else
    \typeout{** WARNING: \string\IEEEsetfootermargin\space mode specifiers after the first in `\@IEEEextracttokenarg' ignored (line \the\inputlineno).}\relax
  \fi
\fi
% handle each mode
\if\@IEEEextractedtoken a\relax
  % No need to do anything here and can pass through the adjustment
  % value as is. The end adjustment of \footskip will do all that
  % is needed
\else
\if\@IEEEextractedtoken c\relax
  % calculate the bottom margin
  \@IEEEtrantmpdimenB 1in\relax % system 1in offset
  \advance\@IEEEtrantmpdimenB\topmargin\relax
  \advance\@IEEEtrantmpdimenB\headheight\relax
  \advance\@IEEEtrantmpdimenB\headsep\relax
  \advance\@IEEEtrantmpdimenB\textheight\relax
  \advance\@IEEEtrantmpdimenB\footskip\relax
  \settodepth{\@IEEEtrantmpdimenC}{\begingroup #1\relax\relax\relax\endgroup}\relax
  \advance\@IEEEtrantmpdimenC by \@IEEEtrantmpdimenB
  \@IEEEtrantmpdimenB\paperheight
  \advance\@IEEEtrantmpdimenB by -\@IEEEtrantmpdimenC
  % at this point \@IEEEtrantmpdimenB has the actual footer bottom margin
  % now subtract off the footer top margin
  \advance\@IEEEtrantmpdimenB -\footskip\relax
  \settodepth{\@IEEEtrantmpdimenC}{\begingroup #2\relax\relax\relax\endgroup}\relax
  \advance\@IEEEtrantmpdimenB by \@IEEEtrantmpdimenC
  \settoheight{\@IEEEtrantmpdimenC}{\begingroup #1\relax\relax\relax\endgroup}\relax
  \advance\@IEEEtrantmpdimenB by \@IEEEtrantmpdimenC
  % at this point \@IEEEtrantmpdimenB has the difference between the bottom
  % and top footer margins
  % our adjustment must be half this value to center the footer
  \divide\@IEEEtrantmpdimenB by 2\relax
  % add to the offset
  \advance\@IEEEtrantmpdimenA by \@IEEEtrantmpdimenB
\else
\if\@IEEEextractedtoken b\relax
  % calculate the bottom margin
  \@IEEEtrantmpdimenB 1in\relax % system 1in offset
  \advance\@IEEEtrantmpdimenB\topmargin\relax
  \advance\@IEEEtrantmpdimenB\headheight\relax
  \advance\@IEEEtrantmpdimenB\headsep\relax
  \advance\@IEEEtrantmpdimenB\textheight\relax
  \advance\@IEEEtrantmpdimenB\footskip\relax
  \settodepth{\@IEEEtrantmpdimenC}{\begingroup #1\relax\relax\relax\endgroup}\relax
  \advance\@IEEEtrantmpdimenC by \@IEEEtrantmpdimenB
  \@IEEEtrantmpdimenB\paperheight
  \advance\@IEEEtrantmpdimenB by -\@IEEEtrantmpdimenC
  % at this point \@IEEEtrantmpdimenB has the actual footer bottom margin
  % get the difference between the actual and the desired
  \advance\@IEEEtrantmpdimenB by -\@IEEEtrantmpdimenA
  \@IEEEtrantmpdimenA\@IEEEtrantmpdimenB
\else
  \if\@IEEEextractedtoken t\relax
  \else
    \@IEEEclspkgerror{Unknown mode type `\@IEEEextractedtokenmacro' in \string\IEEEsetfootermargin\space (line \the\inputlineno).\MessageBreak
    Defaulting to `t'}%
    {Valid modes for \string\IEEEsetfootermargin\space are: t, b, c and a.}\relax
  \fi
  \@IEEEtrantmpdimenB\footskip\relax
  \settodepth{\@IEEEtrantmpdimenC}{\begingroup #2\relax\relax\relax\endgroup}\relax
  \advance\@IEEEtrantmpdimenB by -\@IEEEtrantmpdimenC
  \settoheight{\@IEEEtrantmpdimenC}{\begingroup #1\relax\relax\relax\endgroup}\relax
  \advance\@IEEEtrantmpdimenB by -\@IEEEtrantmpdimenC
  % at this point \@IEEEtrantmpdimenB has the actual footer top margin
  % get the difference between the desired and the actual
  \advance\@IEEEtrantmpdimenA by -\@IEEEtrantmpdimenB
\fi\fi % if t, b, c
\fi % if a
% advance \footskip by the needed amount
\advance\footskip by \@IEEEtrantmpdimenA\relax
}

% -- End V1.8a page setup commands --





% V1.6
% LaTeX is a little to quick to use hyphenations
% So, we increase the penalty for their use and raise
% the badness level that triggers an underfull hbox
% warning. The author may still have to tweak things,
% but the appearance will be much better "right out
% of the box" than that under V1.5 and prior.
% TeX default is 50
\hyphenpenalty=750
\ifCLASSOPTIONcompsoc
\hyphenpenalty 500
\fi
% If we didn't adjust the interword spacing, 2200 might be better.
% The TeX default is 1000
\hbadness=1350
% The IEEE does not use extra spacing after punctuation
\frenchspacing

% V1.7 increase this a tad to discourage equation breaks
\binoppenalty=1000 % default 700
\relpenalty=800     % default 500

% v1.8a increase these to discourage widows and orphans
\clubpenalty=1000          % default 150
\widowpenalty=1000         % default 150
\displaywidowpenalty=1000 % default  50


% margin note stuff
\marginparsep      10pt
\marginparwidth    20pt
\marginparpush     25pt


% if things get too close, go ahead and let them touch
\lineskip            0pt
\normallineskip      0pt
\lineskiplimit       0pt
\normallineskiplimit 0pt

% The distance from the lower edge of the text body to the
% footline
\footskip 0.4in

% normally zero, should be relative to font height.
% put in a little rubber to help stop some bad breaks (underfull vboxes)
\parskip 0ex plus 0.2ex minus 0.1ex

\parindent    1.0em
\ifCLASSOPTIONcompsoc
  \parindent    1.5em
\fi

\headheight   12pt
\headsep      18pt
% use the normal font baselineskip
% so that \topskip is unaffected by changes in \baselinestretch
\topskip=\@IEEEnormalsizeunitybaselineskip


% V1.8 \maxdepth defaults to 4pt, but should be font size dependent
\maxdepth=0.5\@IEEEnormalsizeunitybaselineskip
\textheight       58pc  % 9.63in, 696pt

% set the default top margin to 58pt
% which results in a \topmargin of -49.59pt for 10pt documents
\IEEEsettopmargin{t}{58pt}
% tweak textheight to a perfect integer number of lines/column.
% standard is: 9pt/63 lpc; 10pt/58 lpc; 11pt/52 lpc; 12pt/50 lpc
\IEEEquantizetextheight{c}
% tweak top margin so that the error is shared equally at the top and bottom
\IEEEsettopmargin{q}{0sp}


\columnsep         1pc
\textwidth        43pc   % 2 x 21pc + 1pc = 43pc

% set the default side margins to center the text
\IEEEsetsidemargin{c}{0pt}


% adjust margins for default conference mode
\ifCLASSOPTIONconference
 \textheight        9.25in % The standard for conferences (668.4975pt)
 \IEEEsettopmargin{t}{0.75in}
 % tweak textheight to a perfect integer number of lines/page.
 % standard is: 9pt/61 lpc; 10pt/56 lpc; 11pt/50 lpc; 12pt/48 lpc
 \IEEEquantizetextheight{c}
 % tweak top margin so that the error is shared equally at the top and bottom
 \IEEEsettopmargin{q}{0sp}
\fi


% compsoc text sizes, margins and spacings
\ifCLASSOPTIONcompsoc
 \columnsep         12bp
 % CS specs for \textwdith are 6.875in
 % \textwidth         6.875in
 % however, measurements from proofs show they are using 3.5in columns
 \textwidth         7in
 \advance\textwidth by \columnsep
 % set the side margins to center the text
 \IEEEsetsidemargin{c}{0pt}
 % top/bottom margins to center
 % could just set \textheight to 9.75in for all the different paper sizes
 % and then quantize, but we'll do it the long way here to allow for easy
 % future per-paper size adjustments
 \IEEEsettextheight{0.625in}{0.625in}% 11in - 2 * 0.625in = 9.75in is the standard text height for compsoc journals
 \IEEEsettopmargin{t}{0.625in}
 \if@IEEEusingcspaper
   \IEEEsettextheight{0.5in}{0.5in}% 10.75in - 2 * 0.5in = 9.75in
   \IEEEsettopmargin{t}{0.5in}
 \fi
 \if@IEEEusingAfourpaper
   \IEEEsettextheight{24.675mm}{24.675mm}% 297mm - 2 * 24.675mm = 247.650mm (9.75in)
   \IEEEsettopmargin{t}{24.675mm}
 \fi
 % tweak textheight to a perfect integer number of lines/page.
 %