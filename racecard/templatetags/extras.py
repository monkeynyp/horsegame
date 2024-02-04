from django import template
register = template.Library()

@register.tag
def zip(parser, token):
# Parse the arguments
    args = token.split_contents()
# Check if the tag name is zip
    if args[0] != 'zip':
        raise template.TemplateSyntaxError("'%s' tag requires at least two list arguments" % args[0])
# Check if there are at least two list arguments
    if len(args) < 3:
        raise template.TemplateSyntaxError("'%s' tag requires at least two list arguments" % args[0])
# Check if the last argument is 'as'
    if args[-2] != 'as':
        raise template.TemplateSyntaxError("'%s' tag requires 'as' followed by a variable name" % args[0])
# Get the list arguments and the variable name
    lists = args[1:-2]
    var_name = args[-1]
# Convert the list arguments to actual lists
    lists = [parser.compile_filter(l) for l in lists]
# Return a ZipNode instance
    return ZipNode(lists, var_name)
class ZipNode(template.Node):
# Initialize the node with the list arguments and the variable name
    def __init__(self, lists, var_name):
        self.lists = [template.Variable(l) for l in lists]
        self.var_name = var_name
# Render the node
    def render(self, context):
# Resolve the list arguments in the context
        resolved_lists = [l.resolve(context) for l in self.lists]
# Zip the lists together
        zipped_list = list(zip(*resolved_lists))
# Set the variable name in the context with the zipped list
        context[self.var_name] = zipped_list
# Return an empty string
        return ''