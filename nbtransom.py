#!/usr/bin/env python
# encoding: utf-8

import ast
import inspect
import nbformat as nbf
import pprint
import re
import sys


######################################################################
## custom pretty printer

def min_pretty (x, level=0):
    return "\n".join(min_pretty_sub(x, level))


def min_pretty_sub (x, level, buf=[]):
    indent = " " * level

    if level > 1:
        buf.append(indent + str(x) + ",")

    elif isinstance(x, dict):
        if len(buf) < 1:
            buf.append("{")
        else:
            buf[-1] = buf[-1] + "{"

        for k, v in x.items():
            buf.append("'%s': " % k)
            min_pretty_sub(v, level + 1, buf)

        buf.append(indent + "}")

    elif isinstance(x, list):
        if len(buf) < 1:
            buf.append("[")
        else:
            buf[-1] = buf[-1] + "["

        for v in x:
            min_pretty_sub(v, level + 1, buf)

        buf.append(indent + "],")

    else:
        buf.append(indent + str(x) + ",")

    return buf


######################################################################
## https://gist.github.com/fperez/9716279
## http://stackoverflow.com/questions/13614783/programatically-add-cells-to-an-ipython-notebook-for-report-generation
## https://www.dataquest.io/blog/jupyter-notebook-tips-tricks-shortcuts/

def get_var_name (obj):
    """reflect the name of the given variable, from within the current frame"""
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is obj][0]


def find_cell (nb, cell_name):
    """find a named cell within a notebook"""
    for cell in nb.cells:
        if ("name" in cell.metadata) and (cell.metadata["name"] == cell_name):
            return nb.cells.index(cell), cell

    return None, None


def create_data_cell (var_name, val, formatter=pprint.pformat):
    """create a code cell to represent a variable"""
    data = var_name + " = " + formatter(val)
    cell = nbf.v4.new_code_cell(data.strip())
    cell.metadata["name"] = var_name

    return cell


def get_val (nb, var_name):
    """get the value for a named variable from a notebook"""
    idx, cell = find_cell(nb, var_name)

    if cell:
        s = cell["source"].replace("\n", " ").strip()
        p = re.compile("^[\w\d\_]+\s?\=\s?(.*)$")
        m = p.match(s)

        if m:
            try:
                return ast.literal_eval(m.group(1))
                #return eval(m.group(1))
            except SyntaxError:
                print("SyntaxError", "\n", m.group(0))
                print(cell["source"])
                sys.exit(1)
            
    return None


def set_val (nb, var_name, val, formatter=pprint.pformat):
    """set the value for a named variable in a notebook, appending a new cell if needed"""
    idx, cell = find_cell(nb, var_name)
    new_cell = create_data_cell(var_name, val, formatter)

    if cell:
        nb.cells[idx] = new_cell
    else:
        nb.cells.append(new_cell)


def put_df (nb, df_name, data, labels):
    """write a dataframe in a notebook, appending a new cell if needed"""
    # create a code cell to represent a pandas dataframe
    buf = []
    buf.append(df_name + " = pd.DataFrame.from_records(")
    buf.append(repr(data) + ", columns=" + repr(labels) + ")")
    buf.append(df_name)

    new_cell = nbf.v4.new_code_cell("\n".join(buf).strip())
    new_cell.metadata["name"] = df_name

    # lookup reference, then insert or rewrite the new cell
    idx, cell = find_cell(nb, df_name)

    if cell:
        nb.cells[idx] = new_cell
    else:
        nb.cells.append(new_cell)


def save_nb (nb, file_name):
    """write a notebook to a file"""
    with open(file_name, "w") as f:
        nbf.write(nb, f)


def open_nb (file_name):
    """read a notebook from a file"""
    with open(file_name) as f:
        return nbf.reads(f.read(), nbf.NO_CONVERT)


def create_nb ():
    ## Can also be run at the command line with:
    ##        jupyter nbconvert --execute --inplace test.ipynb

    nb = nbf.v4.new_notebook()
    text = "# My first automagic Jupyter Notebook"

    code = """\
%pylab inline
hist(normal(size=2000), bins=50);
"""

    cell_text = nbf.v4.new_markdown_cell(text.strip())
    cell_code = nbf.v4.new_code_cell(code.strip())
    cell_data = create_data_cell("foo", { "x": [ 2.31, 12.34 ], "y": 3 })

    nb["cells"] = [ cell_text, cell_code, cell_data ]
    return nb


if __name__ == "__main__":
    # let's try some examples
    file_name = "test.ipynb"

    foo = [1, 3, 4, 5, 9, 8, 5, 2, 7, 0, 1, 3, 4, 5, 9, 8, 5, 2, 7, 0, 1, 3, 4, 5, 9, 8, 5, 2, 7, 0, 1, 3, 4, 5, 9, 8, 5, 2, 7, 0, 1, 3, 4, 5, 9, 8, 5, 2, 7, 0, 1, 3, 4, 5, 9, 8, 5, 2, 7, 0]

    x = {
        'orm:Deep_Learning': [
            [ "9780128104095", "B9780128104088000158.xhtml", "Deep Learning for Medical Image Analysis" ],
            [ "9781491924570", "ch06.html", "Deep Learning" ],
            [ "9780128104095", "B9780128104088000110.xhtml", "Deep Learning for Medical Image Analysis" ],
            [ "9781491924570", "ch03.html", "Deep Learning" ],
            [ "9781491971444", "ch01.html", "Machine Learning for Designers" ],
        ],
        'orm:Edu_Psychology': [
            [ "9781522505136", "978-1-5225-0513-6.ch004.xhtml", "Handbook of Research on Serious Games for Educational Applications" ],
            [ "9781522505310", "978-1-5225-0531-0.ch008.xhtml", "Innovative Practices for Higher Education" ],
            [ "9781522504801", "978-1-5225-0480-1.ch011.xhtml", "Knowledge Visualization and Visual Literacy" ],
        ],
        'null': [
            [ "9780123973085", "CHP005.html", "General Aviation Aircraft Design" ],
            [ "9780132761772", "ch20.html", "Scala for the Impatient" ],
            [ "9780132885478", "ch05.html", "Basic Principles and Calculations in Chemical Engineering" ],
        ]
    }

    nb = create_nb()
    set_val(nb, get_var_name(foo), foo)
    put_df(nb, "my_df", [ [1, 2], [3, 4] ], ["a", "b"])

    set_val(nb, get_var_name(x), x, formatter=min_pretty)
    save_nb(nb, file_name)

    nb = open_nb(file_name)
    print(nb.cells)

    foo = get_val(nb, get_var_name(foo))
    print(foo[3])
