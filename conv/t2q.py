#!/sw/bin/python
# -*- coding: utf-8 -*-
from lxml import etree
import sys

LATEXML_NAMESPACE = "http://dlmf.nist.gov/LaTeXML"
LATEXML = "{%s}" % LATEXML_NAMESPACE

NSMAP = {None : LATEXML_NAMESPACE} # the default namespace (no prefix)

# display math delimiters
DMBEGIN = " $$ " # or perhaps "\["
DMEND = " $$ "   # or perhaps "\]"
DMBR  = "<br/>"  # or ""

# inline math delimiters
IMBEGIN=" $$ " # or perhaps "$" "\("
IMEND=" $$ "   # or perhaps "$" "\)"
IMBR  = ""

def parseText(node):
    if node.tag==LATEXML+"equation":
        return parseText(node[0])
    elif node.tag==LATEXML+"Math":
        if node.get("mode")=="display":
            br=DMBR
            bm=DMBEGIN
            em=DMEND
        else: # if inline
            br=IMBR
            bm=IMBEGIN
            em=IMEND
        if node.tail!=None:
            return bm+node.get("tex")+em + node.tail + br
        else:
            return bm+node.get("tex")+em + br
    elif node.tag==LATEXML+"para":
        text=""
        for n in node:
            if parseText(n)!=None:
                text=text+parseText(n)
        return text+"<br/><br/>"
    elif node.tag==LATEXML+"p":
        text=""
        if node.text!=None:
            text=text+node.text
        for n in node:
            text=text+parseText(n)
        return text
    elif node.tag==LATEXML+"title":
        return ""
    elif node.tag==LATEXML+"enumerate": # actually, for questiontype=multichoice
        return ""
    else:
        text=""
        for n in node:
            text=text+parseText(n)
        return text


parser=etree.XMLParser(strip_cdata=False,remove_blank_text=True)
etree.set_default_parser(parser)

src=etree.parse(sys.stdin)
sroot=src.getroot()
root=etree.XML("<quiz></quiz>")

secs=sroot.findall(LATEXML+'section')
for s in secs:
    probtitle=s.find(LATEXML+'note').text # TODO: check class
#    print probtitle
    notes=s.xpath('t:theorem/t:note',namespaces={'t': LATEXML_NAMESPACE })
    for n in notes :
        if n.get("class")=="quiztype":
            questiontype=n.text
    parts=s.xpath('t:theorem',namespaces={'t': LATEXML_NAMESPACE })
    shortsol=""
    longsol=""
    for p in parts :
        if p.get("class")=="problem":
            questiontext=parseText(p)
#            print questiontext
        elif (p.get("class")=="answer") & (questiontype=="calculated"):
            shortsol=p[0][0][0].get("tex")
#            print shortsol
        elif p.get("class")=="solution":
            longsol=parseText(p)
#            print longsol

    q=etree.Element("question")
    q.set("type",questiontype)
    q.append(etree.fromstring("<name><text>"+ probtitle + "</text></name>"))
    q.append(etree.fromstring('<questiontext format="moodle_auto_format"><text><![CDATA[' + questiontext + ']]></text></questiontext>'))


    q.append(etree.fromstring("<image></image>"))
    q.append(etree.fromstring('<generalfeedback><text><![CDATA[' + longsol + ']]></text></generalfeedback>'))
    q.append(etree.fromstring('<defaultgrade>1</defaultgrade>'))
    q.append(etree.fromstring('<penalty>0</penalty>'))
    q.append(etree.fromstring('<hidden>0</hidden>'))
    q.append(etree.fromstring('<shuffleanswers>1</shuffleanswers>'))
 
    if questiontype=="calculated":
        str='''<answer fraction="100">
     <text>'''   + shortsol + '''</text>
     <tolerance>0.005</tolerance>
     <tolerancetype>2</tolerancetype>
     <correctanswerformat>1</correctanswerformat>
     <correctanswerlength>1</correctanswerlength>
     <feedback><text></text></feedback>
     </answer>'''

        q.append(etree.fromstring(str))
        q.append(etree.fromstring("<dataset_definitions></dataset_definitions>"))
    elif questiontype=="multichoice":
        q.append(etree.fromstring("<single>true</single>"))
        q.append(etree.fromstring("<shuffleanswers>true</shuffleanswers>"))
        q.append(etree.fromstring("<correctfeedback><text></text></correctfeedback>"))
        q.append(etree.fromstring("<partiallycorrectfeedback><text></text></partiallycorrectfeedback>"))
        q.append(etree.fromstring("<incorrectfeedback><text></text></incorrectfeedback>"))
        q.append(etree.fromstring("<answernumbering>none</answernumbering>"))
        cc=[p for p in parts if p.get("class")=="problem"]
        choices=cc[0].xpath('t:para/t:enumerate/t:item',namespaces={'t': LATEXML_NAMESPACE })
# +subs.xpath('t:para/t:itemize/t:item',namespaces={'t': LATEXML_NAMESPACE })
        t=[ x for x in choices if x[0].tag==LATEXML+"tag"]
        nt=0
        for y in t:
            if y[0].text=="true":
                nt=nt+1
        for y in t:
            if y[0].text=="true":
                 score=100/nt # aborts if len(t)=0
# Moodle 2.x , percentage
            else: # unselect
                 score=0
            str='''<answer fraction="''' + ("%s" % score) + '''">
                <text><![CDATA['''+ parseText(y)+''']]></text>
                <feedback><text></text></feedback>
                </answer>'''
# CDATA for Moodle 2.x
#            print str    
            q.append(etree.fromstring(str))
                
    root.append(q)
print(etree.tostring(root,xml_declaration=True,encoding='UTF-8',pretty_print=True))





