import sys
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, load_lexer_from_file


def main(source_file, target_file):
    # Load the custom lexer
    lexer = load_lexer_from_file('/home/charl/julich/nestml-upstream/nestml/extras/syntax-highlighting/pygments/pygments_nestml.py', 'NESTMLLexer')

    # Read the source code file
    with open(source_file, 'r') as f:
        code = f.read()

    # Create the HTML formatter
    formatter = HtmlFormatter(full=True, style='colorful')

    # Highlight the code
    result = highlight(code, lexer, formatter)

    result += """

<div class="circ">⬤ ⬤ ⬤ </div>

<style>
.circ {
  position: absolute;
"""
    if "neuron" in source_file:
        result += """
  top: 47px;
  left: 80px;"""

    if "synapse" in source_file:
        result += """
  top: 58px;
  left: 70px;"""

    result += """
  transform: translateX(-50%);
  font-size: .8em; /* Adjust the size as needed */
font-family: Inter;
font-weight: 500;
letter-spacing: .32px;
color: hsla(0,0%,100%,.2);
  padding: 10px 0; /* Optional: Add padding if needed */
    transform: rotateX(20deg) rotateY(20deg);

}

</style>


<link href="https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap" rel="stylesheet">


<style>



body {
padding: 40px;
color: #FFFFFF;
/*background: linear-gradient(140deg, rgb(165, 142, 251), rgb(233, 191, 248));*/
background-color: #fff;

}

.highlight::before {
"""
    if "neuron" in source_file:
        result += """
  content: "Integrate-and-fire NESTML neuron model";
"""

    if "synapse" in source_file:
        result += """
  content: "STDP synapse NESTML model";
"""

    result += """
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-52%);
  text-align: center;
  width: 100%;
  font-size: .8em; /* Adjust the size as needed */
font-family: Inter;
font-weight: 500;
letter-spacing: .32px;
color: hsla(0,0%,100%,.6);
  padding: 10px 0; /* Optional: Add padding if needed */
}

.highlight {

box-shadow: 0 0 0 1px var(--frame-highlight-border),0 0 0 1.5px var(--frame-shadow-border),0 2.8px 2.2px rgba(0,0,0,.034),0 6.7px 5.3px rgba(0,0,0,.048),0 12.5px 10px rgba(0,0,0,.06),0 22.3px 17.9px rgba(0,0,0,.072),0 41.8px 33.4px rgba(0,0,0,.086),0 100px 80px rgba(0,0,0,.12);

border-radius: 10px;
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
    transform: rotateX(20deg) rotateY(20deg);
"""
    if "neuron" in source_file:
        result += """
    width: 800px;
"""

    if "synapse" in source_file:
        result += """
   width: 500px;
"""

    result += """
    padding: 40px 20px 20px 20px;
background-color: #2e273f;
}

.mf, .mi {
color: #7A7FFD !important;
}

.nb {
color: #d3c277 !important;
}

.c1 {
color: #807796 !important;
}

.k {
color: #FF659C !important;
}

.o {

color: #FF659C !important;
}

</style>"""

    with open(target_file, 'w') as f:
        f.write(result)

source_file = "/home/charl/julich/nestml_code_renders/nestml_code_render_neuron.nestml"
target_file = "/home/charl/julich/nestml_code_renders/nestml_code_render_neuron.html"
main(source_file, target_file)

source_file = "/home/charl/julich/nestml_code_renders/nestml_code_render_synapse.nestml"
target_file = "/home/charl/julich/nestml_code_renders/nestml_code_render_synapse.html"
main(source_file, target_file)
