def main():
    with open("static/css/styles.css", "r", encoding="utf-8") as f:
        css = f.read()

    with open("templates/base.html", "r", encoding="utf-8") as f:
        html = f.read()

    target = '<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/styles.css\') }}">'
    replacement = f'{target}\n  <style id="embeddedStyles">\n{css}\n  </style>'

    if target in html and 'id="embeddedStyles"' not in html:
        html = html.replace(target, replacement)
        with open("templates/base.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Successfully embedded CSS directly into templates/base.html")
    else:
        print("Embedded styles already present or target not found")

if __name__ == "__main__":
    main()
