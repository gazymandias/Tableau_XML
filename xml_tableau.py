import xml.etree.ElementTree as ET
import re
import html

new_security = 'IF      (ISMEMBEROF(&quot;Info-BI-PID_NOTSS&quot;)= TRUE and      ' \
               '[DivisionLocalID]=1300) &#9; THEN&#9; [ReplaceMe]&#13;&#10;' \
               'ELSEIF  (ISMEMBEROF(&quot;Info-BI-PID_MRC&quot;)= TRUE and        ' \
               '[DivisionLocalID]=1200)  &#9; THEN&#9; [ReplaceMe]&#13;&#10;' \
               'ELSEIF  (ISMEMBEROF(&quot;Info-BI-PID_SUON&quot;)=TRUE and        ' \
               '[DivisionLocalID]=1400) &#9; THEN&#9; [ReplaceMe]&#13;&#10;' \
               'ELSEIF  (ISMEMBEROF(&quot;Info-BI-PID_CSS&quot;)=TRUE and         ' \
               '[DivisionLocalID]=1000)&#9;         THEN&#9; [ReplaceMe]&#13;&#10;' \
               'ELSEIF  (ISMEMBEROF(&quot;Info-BI-PID_Trust&quot;)= TRUE )                                    ' \
               '&#9; THEN&#9; [ReplaceMe]&#13;&#10;'

new_security_ELSE = 'ELSE [ReplaceELSE]&#9;&#9;&#13;&#10;&#9;&#9;&#13;&#10;END'


# pretty print method
def indent(elem, level=0):
    i = "\n" + level * "  "
    j = "\n" + (level - 1) * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            indent(subelem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = j
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = j
    return elem


# Define filepaths (defining both as the same will overwrite)
input_file = r'C:\SVN\Tableau\Orbit Plus Data Sources\Master Outpatient Datasource.twb'
output_file = r'C:\SVN\Tableau\Orbit Plus Data Sources\Master Outpatient Datasource.twb'

# Define some XML basics
tree = ET.parse(input_file)
root = tree.getroot()

# Regular Expression to find fields using the security model
old_security = 'ISMEMBEROF'

for column in root.iter('column'):
    if column.find('.//calculation') is None:
        caption = ''
    else:
        # prints here in case a problem: sometimes calculations created in older versions of tableau can break this code
        print(column.tag, column.attrib)
        formula = column.find('.//calculation').get('formula')
        if re.search(old_security, formula):
            field_to_secure = re.split('\s+ELSEIF', re.split('THEN\s+(?=[\["])', formula)[1], 1)
            print(field_to_secure)
            ELSE_Value = re.split('\s+END', re.split('ELSE ', formula)[1], 1)
            print(ELSE_Value)
            updated_security = new_security.replace("[ReplaceMe]", field_to_secure[0])
            updated_security_ELSE = new_security_ELSE.replace("[ReplaceELSE]", ELSE_Value[0])
            updated_Security_Final = updated_security + updated_security_ELSE
            column.find('.//calculation').set('formula', html.unescape(updated_Security_Final))
            print('\n' + column.get('caption') + '\n' + '\n', column.find('.//calculation').get('formula') + '\n')

        else:
            pass

tree = ET.ElementTree(indent(root))
tree.write(output_file, xml_declaration=True, encoding='utf-8')
