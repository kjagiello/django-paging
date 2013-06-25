from paging.helpers import paginate as paginate_func

from django import template
from django.utils.safestring import mark_safe
from django.template import RequestContext

try:
    from coffin import template
    from coffin.shortcuts import render_to_string
    from jinja2 import Markup
    is_coffin = True
except ImportError:
    is_coffin = False

try:
    if not is_coffin:
        from django_jinja import library
        from jinja2 import Markup
        from django.template.loader import render_to_string
        is_django_jinja = True
except ImportError:
    is_django_jinja = False

from templatetag_sugar.register import tag
from templatetag_sugar.parser import Name, Variable, Constant, Optional, Model

register = template.Library()

if is_coffin or is_django_jinja:
    def paginate(request, queryset_or_list, per_page=25, is_endless=True):
        context_instance = RequestContext(request)
        context = paginate_func(request, queryset_or_list, per_page, endless=is_endless)
        paging = Markup(render_to_string('paging/pager.jinja', context, context_instance))
        return dict(objects=context['paginator'].get('objects', []), paging=paging)

    if is_coffin:
        register.object(paginate)
    else:
        library.Library().global_function(paginate)

@tag(register, [Variable('queryset_or_list'),
                Constant('from'), Variable('request'),
                Optional([Constant('as'), Name('asvar')]),
                Optional([Constant('per_page'), Variable('per_page')]),
                Optional([Variable('is_endless')])])
def paginate(context, queryset_or_list, request, asvar, per_page=25, is_endless=True):
    """{% paginate queryset_or_list from request as foo[ per_page 25][ is_endless False %}"""

    from django.template.loader import render_to_string

    context_instance = RequestContext(request)
    paging_context = paginate_func(request, queryset_or_list, per_page, endless=is_endless)
    paging = mark_safe(render_to_string('paging/pager.html', paging_context, context_instance))

    result = dict(objects=paging_context['paginator'].get('objects', []),
				  paging=paging, paginator=paging_context['paginator'])
    if asvar:
        context[asvar] = result
        return ''
    return result
