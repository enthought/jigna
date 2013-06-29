<%def name="indent(s, level, unit_indent=4)">
    <%
     from textwrap import dedent
     dedented = dedent(s)
     indented = ""
     for line in dedented.splitlines():
         indented += " "*unit_indent*level + line
     %>
${indented}
</%def>
