from django import template


register = template.Library()


@register.filter
def add_class(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter
def active_url(url, request):
    if url != request.get_full_path():
        return False
    return True


@register.filter
def cut_tag(list, str):
    if len(list) == 1:
        return ''
    new_list = [i for i in list if i != str]
    str = '&tags=' + '&tags='.join(new_list)
    return str


@register.filter
def add_tag(list, str):
    if len(list) == 0:
        str = '&tags=' + str
        return str
    new_list = [i for i in list]
    new_list.append(str)
    str = '&tags=' + '&tags='.join(new_list)
    return str


@register.filter
def to_str(value):
    return str(value)
