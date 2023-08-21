"""
This is coppied from  https://nvbn.github.io/2015/04/04/python-html-dsl/
"""

class hBase(type):
    def __getattr__(cls, name):
        return cls(name)


class h(metaclass=hBase):
    def __init__(self, name, childs=None, attrs=None):
        self._name = name
        self._childs = childs
        self._attrs = attrs
        
    def __getitem__(self, childs):
        if not hasattr(childs, '__iter__'):
            childs = [childs]
        return type(self)(self._name, childs, self._attrs)
        
    def __call__(self, **attrs):
        return type(self)(self._name, self._childs, attrs)
        
    def _format_attr(self, name, val):
         if name == 'klass':
             name = 'class'
         return '{}="{}"'.format(name, str(val).replace('"', '\"'))
        
    def _format_attrs(self):
        if self._attrs:
            return ' ' + ' '.join([self._format_attr(name, val)
                                   for name, val in self._attrs.items()])
        else:
            return ''
        
    def _format_childs(self):
        if self._childs is None:
            return ''
        if isinstance(self._childs, str):
            return self._childs
        else:
            return '\n'.join(map(str, self._childs))
        
    def __str__(self):
        return '<{name}{attrs}>{childs}</{name}>'.format(
            name=self._name,
            attrs=self._format_attrs(),
            childs=self._format_childs())
            
    def __repr__(self):
        return str(self)

    
class s(metaclass=hBase):
    """the same as h, but for self closing elements, this was not in the source"""
    def __init__(self, name, attrs=None):
        self._name = name
        self._attrs = attrs
        
    def __call__(self, **attrs):
        return type(self)(self._name, attrs)
        
    def _format_attr(self, name, val):
         if name == 'klass':
             name = 'class'
         if name == 'http_equiv':
            name = 'http-equiv'
         return '{}="{}"'.format(name, str(val).replace('"', '\"'))
        
    def _format_attrs(self):
        if self._attrs:
            return ' ' + ' '.join([self._format_attr(name, val)
                                   for name, val in self._attrs.items()])
        else:
            return ''
        
    def __str__(self):
        return '<{name}{attrs}/>'.format(
            name=self._name,
            attrs=self._format_attrs())
            
    def __repr__(self):
        return str(self)
