This syntax file is for [KatePart][katepart], which is used in many KDE applications.
It can also be used by `pandoc`.

If you modify the `nestml-hightight.xml`, you can verify it by running

```bash
xmllint --noout --schema language.xsd nestml-highlighting.xml
```

For using it with Pandoc you need to give the extra `--syntax-definition` option:

```bash
pandoc --standalone --syntax-definition nestml-highlight.xml \
       -f markdown -t revealjs --slide-level=2 \
       Presentation.md  -o Presentation.html
```

with a file like
```markdown
# Section

## Slide

You can do the following

```nestml
neuron foo:
  state:
    V_abs mV = 0 mV
  end
  
  # ...
end
```

## Next Slide

...
```

[pandoc]: https://pandoc.org
[katepart]: https://docs.kde.org/stable5/en/applications/katepart/highlight.html#kate-highlight-default-styles
