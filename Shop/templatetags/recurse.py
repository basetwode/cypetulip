from django import template

register = template.Library()


class RecurseNode(template.Node):
    def __init__(self, var, name, child, nodeList):
        self.var = var
        self.name = name
        self.child = child
        self.nodeList = nodeList

    def __repr__(self):
        return '<RecurseNode>'

    def renderCallback(self, context, vals, level):
        output = []
        try:
            if len(vals):
                pass
        except:
            vals = [vals]
        if len(vals):
            if 'loop' in self.nodeList:
                output.append(self.nodeList['loop'].render(context))
            for val in vals:
                context.push()
                context['level'] = level
                context[self.name] = val
                if 'child' in self.nodeList:
                    output.append(self.nodeList['child'].render(context))
                    child = self.child.resolve(context)
                    if child:
                        output.append(self.renderCallback(context, child, level + 1))
                if 'endloop' in self.nodeList:
                    output.append(self.nodeList['endloop'].render(context))
                else:
                    output.append(self.nodeList['endrecurse'].render(context))
                context.pop()
            if 'endloop' in self.nodeList:
                output.append(self.nodeList['endrecurse'].render(context))
        return ''.join(output)

    def render(self, context):
        vals = self.var.resolve(context)
        output = self.renderCallback(context, vals, 1)
        return output


def do_recurse(parser, token):
    bits = list(token.split_contents())
    if len(bits) != 6 and bits[2] != 'with' and bits[4] != 'as':
        raise template.TemplateSyntaxError(
            "Invalid tag syxtax expected '{% recurse [childVar] with [parents] as [parent] %}'")
    child = parser.compile_filter(bits[1])
    var = parser.compile_filter(bits[3])
    name = bits[5]

    nodeList = {}
    while len(nodeList) < 4:
        temp = parser.parse(('child', 'loop', 'endloop', 'endrecurse'))
        tag = parser.tokens[0].contents
        nodeList[tag] = temp
        parser.delete_first_token()
        if tag == 'endrecurse':
            break

    return RecurseNode(var, name, child, nodeList)


from django.contrib.auth.models import Group
from django.template import resolve_variable


@register.tag()
def ifusergroup(parser, token):
    """ Check to see if the currently logged in user belongs to a specific
    group. Requires the Django authentication contrib app and middleware.

    Usage: {% ifusergroup Admins %} ... {% endifusergroup %}

    """
    try:
        tag, group = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("Tag 'ifusergroup' requires 1 argument.")
    nodelist = parser.parse(('endifusergroup',))
    parser.delete_first_token()
    return GroupCheckNode(group, nodelist)


class GroupCheckNode(template.Node):
    def __init__(self, group, nodelist):
        self.group = group
        self.nodelist = nodelist

    def render(self, context):
        user = resolve_variable('user', context)
        if not user.is_authenticated:
            return ''
        try:
            group = Group.objects.get(name=self.group)
        except Group.DoesNotExist:
            return ''
        if group in user.groups.all():
            return self.nodelist.render(context)
        return ''


@register.tag()
def multiply(value, arg):
    return value * arg


@register.filter()
def get_type(value):
    return type(value)

@register.filter()
def check_type(value, arg):
    return str(type(value)) == str(arg)

do_recurse = register.tag('recurse', do_recurse)

