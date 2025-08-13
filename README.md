Latex-to-Anki is a Python script made to streamline Anki flashcard creation from a .tex LaTeX file. It is specifically
designed for LaTex math notes with environments such as definition, proposition, lemma, corollary, theorem, and proof.

The heading of the .tex should thus look similar to:

```
\usepackage{mdframed}
\newmdtheoremenv{theorem}{Theorem}[section]
\newmdtheoremenv{corollary}[theorem]{Corollary}
\newmdtheoremenv{lemma}[theorem]{Lemma}
\newmdtheoremenv{definition}[theorem]{Definition}
\newmdtheoremenv{proposition}[theorem]{Proposition}
```

so that statements are defined presented inside these theorem environments:

```
\begin{definition}
    The dimension of the image of a linear transformation is calld its \textbf{rank}.
\end{definition}
```

Terms bolded with `\textbf` inside definition environments are detected and are used to create corresponding cards.

Lemmas, corollaries, propositions, and theorems are treated in the same manner. These are typically followed by `proof`
environments:

```
\begin{theorem}[theorem name]
    ...
\end{theorem}
\begin{proof}
    ...
\end{proof}
```
Note that `theorem name` is optional.

For now, three types of cards are generated:

1. Cloze cards where all terms of a definition are clozed. Any content inside `\textbf` is considered a term.
2. Basic cards with the term on the front and the full definition on the back.
3. Basic cards with the theorem on the front and the proof on the back.
4. Basic cards with the theorem name on the front and the theorem on the back.

Given a file `name.tex`, two files are generated: `name_basic.txt` and `name_clozed.txt`, containing the basic and clozed cards respectively in `.txt` format.
To import these into Anki follow these steps:
1. Open Anki.
2. Select Import File.
3. Select the file.
4. Select the Pipe separator.
5. Enable "Allow HTML in fields".
6. Select the correct Note Type.
7. Select Import.