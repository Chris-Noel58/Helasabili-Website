from html import escape
from html.parser import HTMLParser
from urllib.parse import urlsplit


ALLOWED_TAGS = {
    'a', 'blockquote', 'br', 'em', 'h1', 'h2', 'li', 'ol', 'p', 's',
    'strong', 'u', 'ul',
}
VOID_TAGS = {'br'}


def _safe_href(value):
    value = value.strip()
    parsed = urlsplit(value)
    if parsed.scheme:
        return value if parsed.scheme.lower() in {'http', 'https', 'mailto'} else None
    if value.startswith('//'):
        return None
    return value


class _RichTextSanitizer(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.output = []
        self.open_tags = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag not in ALLOWED_TAGS:
            return

        if tag == 'li' and self.open_tags and self.open_tags[-1] in {'ol', 'ul'}:
            list_type = dict(attrs).get('data-list')
            desired_list_tag = {'bullet': 'ul', 'ordered': 'ol'}.get(list_type)
            current_list_tag = self.open_tags[-1]
            if desired_list_tag and desired_list_tag != current_list_tag:
                for index in range(len(self.output) - 1, -1, -1):
                    if self.output[index] == f'<{current_list_tag}>':
                        self.output[index] = f'<{desired_list_tag}>'
                        self.open_tags[-1] = desired_list_tag
                        break

        if tag == 'a':
            href = _safe_href(dict(attrs).get('href', ''))
            if href is not None:
                self.output.append(f'<a href="{escape(href, quote=True)}">')
            else:
                self.output.append('<a>')
        else:
            self.output.append(f'<{tag}>')

        if tag not in VOID_TAGS:
            self.open_tags.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag not in self.open_tags:
            return

        while self.open_tags:
            open_tag = self.open_tags.pop()
            self.output.append(f'</{open_tag}>')
            if open_tag == tag:
                break

    def handle_data(self, data):
        escaped_data = escape(data, quote=False)
        self.output.append(escaped_data.replace('\r\n', '\n').replace('\n', '<br>'))

    def get_html(self):
        while self.open_tags:
            self.output.append(f'</{self.open_tags.pop()}>')
        return ''.join(self.output)


def sanitize_rich_text(value):
    if not value:
        return ''

    sanitizer = _RichTextSanitizer()
    sanitizer.feed(str(value))
    return sanitizer.get_html()
