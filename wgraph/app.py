#!/usr/bin/env python

from flask import Flask, escape, request

from wgraph.summary import go
from wgraph.graph import load, apply_styles


app = Flask(__name__)
GRAPH = load("../graph.tsv")


@app.route("/")
def home():
    return """
<form method="POST">
    <input name="word">
    <input type="submit" value="Enter a word">
</form>
"""


def sumup(word):
    # TODO - return error if no word specified
    graph = go(
        graph=GRAPH,
        word=word,
        max_depth=5,
        max_nodes=50,
        group_by_origin=True,
    )

    apply_styles(word, graph).render("output")
    with open("output.svg") as inputs:
        svg = inputs.read()
        start = svg.find("<svg ")
        if start != -1:
            svg = svg[start:]

        # TODO - return svg MIME type
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Wgraph {escape(word)}</title>
</head>
<body>
<div style="max-width: 100%">
{svg}
</div>
</body>
</html>
    """


@app.route("/", methods=["POST"])
def form():
    word = request.form["word"]
    return sumup(word)


@app.route("/summary", methods=["GET"])
def summary():
    word = request.args.get("word")
    return sumup(word)
