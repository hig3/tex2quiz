tex2quiz
========

Moodle Question Converter from LaTeX to Moodle XML

Convert a single LaTeX source into handouts, slides (latex-beamer), and Moodle Quizzes by a python script. Maintain your item bank on a file system as a collection of latex files (a barbarian's way).

Conversion to problem books, solution books, slides (in latex-beamer), and static web pages with MathML equations are also supported with supplementary latex styles.

Presentation at MoodleMoot Japan 2012 in Mie Poster at PC Conference 2012 in Kyoto U


# List of Files

Files | Description
----------------------------
src/example-*.tex|	目的別のサンプル. 
src/itembank/*.tex|	個々の問題. これを example-*.tex が input している. また, これをそのまま latex することもできる.
src/dpreamble.tex|	個々の問題を単独で latex するときに使われる.
src/t2q.sty|	かならず usepackage するパッケージ
src/t2q-*.sty|	タイプセット目的に応じて usepackage するパッケージ
src/t2q-*.sty.ltxml|	LaTeXML に対して, sty 内の定義の変換方法を知らせるもの
conv/t2q.py|	example-latexml.tex を LaTeXML で変換して得られる中間 XML を変換する Python script


#使い方

##前提

-LaTeXML (perl script)
-lxml (python library)
-src, src/itembankにTEXINPUTSが通っている

##ハンドアウト, 試験問題, 作成者用ドラフトのPDFを作る

example-{handout,exam,draft}.tex に問題のファイルを \input して, LaTeX でタイプセットする.

##問題1個単位のドラフトのPDFを作る

itembank内の*.texを単独でLaTeXでタイプセットする.

##LaTeX Beamerのスライドを作る

example-beamer.tex に問題のファイルを \input して, LaTeX でタイプセットする. multichoice タイプの問題の場合, overlay で正解が表示されるようになる. 配付資料との使い分けについては[もんたメソッド](https://github.com/hig3/monta-method-latex-beamer)も参照.

##静的Webページを作る

LaTeXMLの機能をそのまま使うだけです.

example-latexml.tex を (LaTeXでタイプセットするのでなく) LaTeXML A LaTeX to XML ConverterでZMLに変換する.
```
latexml --preload=t2q.sty --inputencoding=UTF-8 --noparse --nocomments --destination=intermediate.xml example-latexml.tex  2> conversiont.log
```
後処理する.
```
latexmlpost --format=xhtml --dest=web.xhtml intermediate.xml
```
format には次の可能性.

Format|Description
------------------
xhtml|MathMLが使われる. Webサーバの設定で, ヘッダを Content-Type:application/xhtml+xml にしないといけない. PHPのheader関数でするのが簡単かも. また, <title/> となってブラウザによってはエラーになるので手で編集する必要がある.
html|数式は, LaTeXでイメージファイルとして作られるので, これらを DocumentRoot下に同時にコピーする必要がある
html5|未検証

LaTeXML付属のスタイルファイル (/opt/local/lib/perl5/site_perl/5.12.3/LaTeXML/style/*) もDocumentRoot下にコピーする必要. (macports の ver ... で検証している)
##Moodle XMLに変換してMoodleにインポート

```
latexml --preload=t2q.sty --inputencoding=UTF-8 --noparse --nocomments --destination=intermediate.xml example-latexml.tex  2> conversiont.log
cat intermediate.xml | python t2q.py > import2moodle.xml
```
これを問題バンクでインポート
数式については, Moodle側の表示方法が, MathJax, TeXfilter, MathML などいろいろありうる. その結果, delimiter も様々となる. これらは, t2q.py 内の定数定義で調節する.

2.xになって少し仕様が変わった.
